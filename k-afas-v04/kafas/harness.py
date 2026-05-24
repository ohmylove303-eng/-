"""K-AFAS v0.4 하네스 검증 (Harness Verification).

6개 불변조건(Invariants):
  I1 GoalInvariantLock        - 의사결정 지원체계만 허용
  I2 OptionSetIntegrity       - HOLD/REJECT/REQUEST_MORE_EVIDENCE 보장
  I3 SemanticCollisionDetector- 금지 표현 탐지
  I4 EvidenceLedger           - 출처/시간/증거패킷 강제
  I5 HumanApprovalLock        - 인간검토 없이 다음 단계 불가
  I6 WeaponSeparationLock     - 무기 직접연동 절대 금지

판정: PASS | HOLD | REJECT
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Iterable

# ── 금지 표현 (의미 충돌 탐지용) ──────────────────────────
# 정규식 우회 방지: 띄어쓰기/구두점/대소문자를 제거한 후 비교한다.
FORBIDDEN_PHRASES: tuple[str, ...] = (
    "자동사격", "사격제원", "탄도계산", "사격지시", "발사지시",
    "무기직접연동", "포탑제어", "발사명령", "타격명령",
    "특정표적공격절차", "재밍회피구현", "사격승인",
    "automatedcoordinategeneration",
    "killchain", "strikeplanning", "strikeauthorization",
    "autonomousfire", "firingdata", "firingsolution",
    "ballisticcalculation", "directweaponcontrol",
    "turretcontrol", "firecommand", "fireorder",
    "engageorder", "weaponrelease",
)


def _normalize_for_collision(text: str) -> str:
    """공백/구두점/대소문자 차이를 제거해 우회 시도를 차단."""
    if not text:
        return ""
    out = []
    for ch in text.lower():
        if ch.isalnum() or ord(ch) > 127:  # 한글/한자 보존
            out.append(ch)
    return "".join(out)

# 허용된 의사결정 옵션 (선택지 무결성)
REQUIRED_OPTIONS: frozenset[str] = frozenset({
    "HOLD", "REJECT", "REQUEST_MORE_EVIDENCE",
})

# 허용 판정 결과
Verdict = str  # "PASS" | "HOLD" | "REJECT"



@dataclass
class HarnessReport:
    """하네스 검증 결과 보고서."""
    verdict: Verdict                      # PASS / HOLD / REJECT
    invariant_results: dict[str, Verdict] = field(default_factory=dict)
    violations: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def is_pass(self) -> bool:
        return self.verdict == "PASS"

    def is_reject(self) -> bool:
        return self.verdict == "REJECT"


# ── I1. 목표불변잠금 (Goal Invariant Lock) ─────────────
def invariant_goal_lock(case: dict[str, Any]) -> tuple[Verdict, str]:
    """K-AFAS는 의사결정 지원체계여야만 한다.
    decision.weapon_control_link / firing_data / ballistic_calculation 가
    'NOT_ALLOWED' 외 값이면 REJECT.
    """
    decision = case.get("decision") or {}
    locked_fields = (
        "weapon_control_link", "firing_data", "ballistic_calculation",
    )
    for f in locked_fields:
        v = decision.get(f)
        if v is not None and v != "NOT_ALLOWED":
            return "REJECT", f"goal_lock_violation:{f}={v}"
    return "PASS", "goal_lock_ok"


# ── I2. 선택지 무결성 (Option Set Integrity) ──────────
def invariant_option_set(allowed_options: Iterable[str]) -> tuple[Verdict, str]:
    """검토자에게 제시된 선택지에 HOLD/REJECT/REQUEST_MORE_EVIDENCE가
    반드시 포함되어야 한다.
    """
    options = set(allowed_options)
    missing = REQUIRED_OPTIONS - options
    if missing:
        return "REJECT", f"missing_required_options:{sorted(missing)}"
    return "PASS", "options_ok"



# ── I3. 의미충돌 탐지 (Semantic Collision Detector) ─────
def invariant_semantic_collision(text_corpus: str) -> tuple[Verdict, str]:
    """문서/추천/이유 등 텍스트에 금지 표현이 포함되면 REJECT.

    띄어쓰기/구두점/대소문자 우회 시도를 차단하기 위해 정규화 후 비교.
    """
    if not text_corpus:
        return "PASS", "no_text"
    normalized = _normalize_for_collision(text_corpus)
    hits = [p for p in FORBIDDEN_PHRASES if p in normalized]
    if hits:
        return "REJECT", f"forbidden_phrase:{hits[:3]}"
    return "PASS", "semantic_ok"


# ── I4. 증거 원장 (Evidence Ledger) ──────────────────
def invariant_evidence_ledger(case: dict[str, Any]) -> tuple[Verdict, str]:
    """모든 후보는 출처(source_type)·관측시각·증거패킷 식별자를 가져야 함."""
    cand = case.get("candidate") or {}
    ev = case.get("evidence") or {}
    if not cand.get("source_type"):
        return "REJECT", "candidate.source_type_missing"
    if not cand.get("observed_at_kst"):
        return "REJECT", "candidate.observed_at_kst_missing"
    if not ev.get("packet_id"):
        return "HOLD", "evidence.packet_id_missing"
    if ev.get("evidence_status") == "INSUFFICIENT":
        return "HOLD", "evidence_insufficient"
    return "PASS", "ledger_ok"


# ── I5. 인간승인 잠금 (Human Approval Lock) ──────────
def invariant_human_approval(case: dict[str, Any]) -> tuple[Verdict, str]:
    """다음 단계로 진행하려면 HumanReviewLog가 존재하고
    decision != REJECT여야 한다. 없으면 자동 진행 차단.
    """
    review = case.get("review")
    if review is None:
        return "HOLD", "human_review_required"
    if review.get("decision") == "REJECT":
        return "REJECT", "human_rejected"
    return "PASS", "human_approval_ok"



# ── I6. 무기분리 잠금 (Weapon Separation Lock) ─────────
def invariant_weapon_separation(case: dict[str, Any]) -> tuple[Verdict, str]:
    """case 내 어떤 필드도 무기제어/사격제원/탄도계산을 허용해서는 안 된다.
    coord.coordinate_use_policy는 단일 Literal로 고정되어 있어야 한다.
    """
    coord = case.get("coord") or {}
    expected = "NO_FIRING_DATA__NO_BALLISTIC_CALC__HUMAN_REVIEW_ONLY"
    policy = coord.get("coordinate_use_policy")
    if policy and policy != expected:
        return "REJECT", f"coord_policy_violation:{policy}"
    decision = case.get("decision") or {}
    for f in ("weapon_control_link", "firing_data", "ballistic_calculation"):
        if decision.get(f) not in (None, "NOT_ALLOWED"):
            return "REJECT", f"weapon_separation_break:{f}"
    return "PASS", "weapon_separation_ok"


# ── 통합 검증 ────────────────────────────────────────
def evaluate_case(
    case: dict[str, Any],
    text_corpus: str = "",
    allowed_options: Iterable[str] = REQUIRED_OPTIONS,
) -> HarnessReport:
    """6개 불변조건을 모두 검사해 통합 판정."""
    report = HarnessReport(verdict="PASS")

    checks = (
        ("I1_goal_lock",          invariant_goal_lock(case)),
        ("I2_option_set",         invariant_option_set(allowed_options)),
        ("I3_semantic_collision", invariant_semantic_collision(text_corpus)),
        ("I4_evidence_ledger",    invariant_evidence_ledger(case)),
        ("I5_human_approval",     invariant_human_approval(case)),
        ("I6_weapon_separation",  invariant_weapon_separation(case)),
    )

    has_reject = False
    has_hold = False
    for name, (verdict, note) in checks:
        report.invariant_results[name] = verdict
        report.notes.append(f"{name}:{verdict}:{note}")
        if verdict == "REJECT":
            has_reject = True
            report.violations.append(f"{name}:{note}")
        elif verdict == "HOLD":
            has_hold = True

    if has_reject:
        report.verdict = "REJECT"
    elif has_hold:
        report.verdict = "HOLD"
    return report
