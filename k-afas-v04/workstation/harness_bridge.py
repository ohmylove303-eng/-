"""
K-AFAS 하네스 브리지 — AI 등급별 라우팅 + 토큰 효율 수치화

불변조건:
  - 단순 확인/조회 → TIER_LOW (mini/Flash) 자동 위임
  - 복합 추론/설계 → TIER_HIGH (Sonnet/Opus) 제한 사용
  - 모든 호출에 토큰 사용량 측정 + 효율 수치 기록
  - 재확인/중복 호출 REJECT
  - 개인정보 포함 프롬프트 REJECT
"""
from __future__ import annotations
import time
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Any


# ── AI 등급 정의 ──────────────────────────────────────
class Tier(Enum):
    LOW = "low"        # mini, Flash — 단순 확인, 상태 조회, 포맷 변환
    MID = "mid"        # Sonnet-lite — 코드 수정, 요약, 단일 파일 분석
    HIGH = "high"      # Sonnet/Opus — 설계, 복합 추론, 다중 파일 아키텍처


# ── 작업 분류 규칙 ─────────────────────────────────────
TASK_TIER_MAP: dict[str, Tier] = {
    # LOW: 토큰 극소화 대상
    "status_check": Tier.LOW,
    "file_read": Tier.LOW,
    "format_convert": Tier.LOW,
    "log_query": Tier.LOW,
    "config_lookup": Tier.LOW,
    "simple_confirm": Tier.LOW,
    # MID: 중간 복잡도
    "code_edit_single": Tier.MID,
    "summarize": Tier.MID,
    "test_run": Tier.MID,
    "bug_fix_simple": Tier.MID,
    # HIGH: 고차원만 허용
    "architecture_design": Tier.HIGH,
    "multi_file_refactor": Tier.HIGH,
    "complex_reasoning": Tier.HIGH,
    "security_audit": Tier.HIGH,
}


# ── 토큰 비용 모델 (상대단위) ─────────────────────────
TOKEN_COST_PER_1K: dict[Tier, float] = {
    Tier.LOW: 0.1,    # $0.1/1K (mini급)
    Tier.MID: 1.0,    # $1.0/1K (Sonnet급)
    Tier.HIGH: 5.0,   # $5.0/1K (Opus급)
}


# ── 효율 측정 레코드 ──────────────────────────────────
@dataclass
class UsageRecord:
    task_type: str
    tier: Tier
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_units: float          # 상대 비용
    efficiency_score: float    # 0~1 (높을수록 효율적)
    timestamp: float = field(default_factory=time.time)
    prompt_hash: str = ""      # 중복 감지용


# ── 중복 호출 감지 ────────────────────────────────────
class DuplicateDetector:
    """최근 N개 프롬프트 해시 캐시 — 동일 요청 REJECT"""

    def __init__(self, window: int = 50):
        self._cache: list[str] = []
        self._window = window

    def check(self, prompt: str) -> bool:
        """True면 중복 → REJECT"""
        h = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        if h in self._cache:
            return True
        self._cache.append(h)
        if len(self._cache) > self._window:
            self._cache.pop(0)
        return False

    def hash_of(self, prompt: str) -> str:
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]


# ── 개인정보 필터 ─────────────────────────────────────
PII_PATTERNS = [
    "주민등록", "전화번호", "계좌번호", "비밀번호",
    "resident_id", "phone_number", "account_number", "password",
    "ssn", "credit_card",
]


def contains_pii(text: str) -> bool:
    low = text.lower()
    return any(p in low for p in PII_PATTERNS)


# ── 하네스 브리지 코어 ────────────────────────────────
class HarnessBridge:
    """
    단계별 구동:
      1. classify(task) → Tier 결정
      2. validate(prompt) → PII/중복 체크
      3. route(tier) → 적절 AI 선택
      4. execute(prompt) → 결과 + 측정
      5. measure() → 효율 수치화 기록
    """

    def __init__(self):
        self.detector = DuplicateDetector()
        self.history: list[UsageRecord] = []
        self._total_tokens = 0
        self._total_cost = 0.0

    def classify(self, task_type: str) -> Tier:
        """작업 유형 → AI 등급 라우팅"""
        return TASK_TIER_MAP.get(task_type, Tier.MID)

    def validate(self, prompt: str) -> tuple[bool, str]:
        """
        프롬프트 검증.
        Returns: (pass여부, 사유)
        """
        if contains_pii(prompt):
            return False, "REJECT: 개인정보 포함"
        if self.detector.check(prompt):
            return False, "REJECT: 중복 호출 감지"
        return True, "PASS"

    def route(self, tier: Tier) -> str:
        """등급별 AI 모델 선택"""
        mapping = {
            Tier.LOW: "gpt-4o-mini",       # 또는 gemini-flash
            Tier.MID: "claude-sonnet",      # 중간
            Tier.HIGH: "claude-opus",       # 고차원
        }
        return mapping[tier]

    def measure(
        self,
        task_type: str,
        tier: Tier,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float,
        prompt: str,
    ) -> UsageRecord:
        """효율 수치화 + 기록"""
        total = input_tokens + output_tokens
        cost = (total / 1000) * TOKEN_COST_PER_1K[tier]

        # 효율 점수: (결과 품질 가중) / (비용 × 지연)
        # 단순화: LOW일수록 효율 높음, 지연 짧을수록 높음
        tier_weight = {Tier.LOW: 1.0, Tier.MID: 0.7, Tier.HIGH: 0.5}
        latency_factor = max(0.1, 1.0 - (latency_ms / 10000))
        efficiency = tier_weight[tier] * latency_factor

        record = UsageRecord(
            task_type=task_type,
            tier=tier,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            cost_units=round(cost, 4),
            efficiency_score=round(efficiency, 4),
            prompt_hash=self.detector.hash_of(prompt),
        )

        self.history.append(record)
        self._total_tokens += total
        self._total_cost += cost
        return record

    def stats(self) -> dict[str, Any]:
        """누적 통계"""
        if not self.history:
            return {"calls": 0, "tokens": 0, "cost": 0, "avg_efficiency": 0}

        avg_eff = sum(r.efficiency_score for r in self.history) / len(self.history)
        tier_dist = {}
        for r in self.history:
            tier_dist[r.tier.value] = tier_dist.get(r.tier.value, 0) + 1

        return {
            "calls": len(self.history),
            "total_tokens": self._total_tokens,
            "total_cost_units": round(self._total_cost, 4),
            "avg_efficiency": round(avg_eff, 4),
            "tier_distribution": tier_dist,
        }
