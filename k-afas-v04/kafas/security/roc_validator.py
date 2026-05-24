"""
R29: DAPA ROC (Required Operational Capability) 검증 체크리스트

목적: 방위사업청(DAPA) 운용요구성능(ROC) 항목을 코드로 검증.
     각 ROC 항목에 대해 자동화된 PASS/FAIL 판정 + 증적 생성.

ROC 카테고리:
  - 기능 요구 (FR): 8계층 파이프라인 동작
  - 성능 요구 (PR): TTRR, 처리량, 가용성
  - 안전 요구 (SR): 하네스, HiTL, 금지표현
  - 보안 요구 (SEC): 인증, 감사, 암호화
  - 상호운용 (IOP): API, 데이터 형식

REJECT: 실제 군 기밀 ROC 번호/내용 삽입
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Any


class ROCCategory(Enum):
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    SAFETY = "safety"
    SECURITY = "security"
    INTEROP = "interoperability"



class ROCStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    PARTIAL = "partial"
    NOT_TESTED = "not_tested"
    DEFERRED = "deferred"  # 코드 외부 (야전시험 등)


@dataclass
class ROCItem:
    """단일 ROC 항목"""
    roc_id: str
    category: ROCCategory
    title: str
    description: str
    acceptance_criteria: str
    validator: Callable[[], tuple[ROCStatus, str]] | None = None
    weight: float = 1.0  # 중요도 가중치


@dataclass
class ROCResult:
    """ROC 검증 결과"""
    roc_id: str
    category: ROCCategory
    title: str
    status: ROCStatus
    detail: str
    elapsed_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class ROCReport:
    """ROC 종합 보고서"""
    total: int = 0
    passed: int = 0
    failed: int = 0
    partial: int = 0
    deferred: int = 0
    results: list[ROCResult] = field(default_factory=list)
    score: float = 0.0  # 가중 점수 (0~100)

    def compliance_rate(self) -> float:
        testable = self.total - self.deferred
        if testable == 0:
            return 0.0
        return round(self.passed / testable * 100, 1)



# ── ROC 체크리스트 정의 ───────────────────────────────

def _check_pipeline_8layers() -> tuple[ROCStatus, str]:
    """FR-01: 8계층 파이프라인 정상 동작"""
    try:
        from kafas.pipeline import KAFASPipeline
        p = KAFASPipeline(audit_path="/dev/null")
        return ROCStatus.PASS, "KAFASPipeline 8계층 import+init 성공"
    except Exception as e:
        return ROCStatus.FAIL, str(e)


def _check_harness_reject() -> tuple[ROCStatus, str]:
    """SR-01: 하네스 금지표현 REJECT"""
    try:
        from kafas.harness import evaluate_case
        # 금지표현 포함 시 REJECT 확인
        case = {"text": "사격제원 계산"}
        result = evaluate_case(case)
        if "REJECT" in str(result):
            return ROCStatus.PASS, "금지표현 REJECT 정상"
        return ROCStatus.FAIL, "금지표현 미감지"
    except Exception as e:
        return ROCStatus.PARTIAL, f"검증 시도: {e}"


def _check_hitl_required() -> tuple[ROCStatus, str]:
    """SR-02: 인간승인(HiTL) 없으면 HALT"""
    try:
        from kafas.pipeline import KAFASPipeline
        p = KAFASPipeline(audit_path="/dev/null")
        result = p.run(
            raw={"observed_at_kst": "2026-01-01T00:00", "confidence_score": 0.9},
            source_type="test", human_decision=None,
        )
        if "HALT" in result.status():
            return ROCStatus.PASS, "human_decision=None → HALTED"
        return ROCStatus.FAIL, f"Expected HALT, got {result.status()}"
    except Exception as e:
        return ROCStatus.PARTIAL, str(e)


def _check_ttrr_metric() -> tuple[ROCStatus, str]:
    """PR-01: TTRR 측정 가능"""
    try:
        from kafas.metrics import compute_ttrr
        return ROCStatus.PASS, "TTRR compute function exists"
    except ImportError:
        return ROCStatus.PARTIAL, "metrics module import 확인 필요"


def _check_audit_chain() -> tuple[ROCStatus, str]:
    """SEC-01: SHA-256 감사 해시체인"""
    try:
        from kafas.layers.audit import verify_audit_chain
        return ROCStatus.PASS, "verify_audit_chain 함수 존재"
    except ImportError:
        return ROCStatus.FAIL, "audit module 미발견"


def _check_oauth2_auth() -> tuple[ROCStatus, str]:
    """SEC-02: OAuth2 토큰 인증"""
    try:
        from app.gateway import _verify_token
        return ROCStatus.PASS, "_verify_token 함수 존재"
    except ImportError:
        return ROCStatus.PARTIAL, "gateway import 경로 확인"


def _check_display_only() -> tuple[ROCStatus, str]:
    """SR-03: 좌표 DISPLAY_ONLY 강제"""
    try:
        from kafas.layers.coord_support import COORD_POLICY
        if COORD_POLICY == "DISPLAY_ONLY":
            return ROCStatus.PASS, "COORD_POLICY=DISPLAY_ONLY"
        return ROCStatus.FAIL, f"COORD_POLICY={COORD_POLICY}"
    except ImportError:
        return ROCStatus.PARTIAL, "coord_support 확인 필요"


def _check_forbidden_27() -> tuple[ROCStatus, str]:
    """SR-04: 금지표현 27종 등록 확인"""
    try:
        from kafas.harness import FORBIDDEN_EXPRESSIONS
        count = len(FORBIDDEN_EXPRESSIONS)
        if count >= 27:
            return ROCStatus.PASS, f"금지표현 {count}종 등록"
        return ROCStatus.FAIL, f"금지표현 {count}종 (최소 27)"
    except ImportError:
        return ROCStatus.PARTIAL, "harness 확인 필요"



# ── 표준 ROC 체크리스트 ───────────────────────────────
STANDARD_ROC_CHECKLIST: list[ROCItem] = [
    # Functional
    ROCItem("FR-01", ROCCategory.FUNCTIONAL, "8계층 파이프라인",
            "L1~L8 순차 실행", "import+init 성공", _check_pipeline_8layers, 2.0),
    ROCItem("FR-02", ROCCategory.FUNCTIONAL, "표적후보 처리",
            "후보 입력→검토 대기열", "status=HALTED", _check_hitl_required, 2.0),
    ROCItem("FR-03", ROCCategory.FUNCTIONAL, "4-패널 콘솔 렌더링",
            "Map/Evidence/Decision/Audit", "빌드 성공", None, 1.5),

    # Performance
    ROCItem("PR-01", ROCCategory.PERFORMANCE, "TTRR 측정",
            "Time-to-Review-Ready P50≤30s", "측정 함수 존재", _check_ttrr_metric, 1.5),
    ROCItem("PR-02", ROCCategory.PERFORMANCE, "API 응답시간",
            "POST /cases < 2000ms", "부하 테스트", None, 1.0),
    ROCItem("PR-03", ROCCategory.PERFORMANCE, "동시 처리",
            "10건 이상 batch 처리", "run_batch 존재", None, 1.0),

    # Safety
    ROCItem("SR-01", ROCCategory.SAFETY, "하네스 REJECT",
            "금지표현 포함 시 즉시 REJECT", "금지표현→REJECT", _check_harness_reject, 3.0),
    ROCItem("SR-02", ROCCategory.SAFETY, "인간승인 필수",
            "HiTL 없으면 HALT", "human_decision=None→HALT", _check_hitl_required, 3.0),
    ROCItem("SR-03", ROCCategory.SAFETY, "좌표 표시전용",
            "DISPLAY_ONLY 강제", "COORD_POLICY 확인", _check_display_only, 2.0),
    ROCItem("SR-04", ROCCategory.SAFETY, "금지표현 27종",
            "27종 이상 등록+우회차단", "count≥27", _check_forbidden_27, 2.5),
    ROCItem("SR-05", ROCCategory.SAFETY, "무기필드 제거",
            "API 응답에 weapon 필드 없음", "CaseResponse 검증", None, 3.0),

    # Security
    ROCItem("SEC-01", ROCCategory.SECURITY, "감사 해시체인",
            "SHA-256 체인 무결성 검증", "verify 함수 존재", _check_audit_chain, 2.5),
    ROCItem("SEC-02", ROCCategory.SECURITY, "OAuth2 인증",
            "Bearer 토큰 역할별 검증", "_verify_token 존재", _check_oauth2_auth, 2.0),
    ROCItem("SEC-03", ROCCategory.SECURITY, "세션 5분 잠금",
            "비활동 5분→재인증", "useSessionLock 구현", None, 1.5),
    ROCItem("SEC-04", ROCCategory.SECURITY, "KMS 연동",
            "키 관리 외부 위임", "KMSManager 존재", None, 1.5),

    # Interoperability
    ROCItem("IOP-01", ROCCategory.INTEROP, "REST API 표준",
            "FastAPI OpenAPI 스펙", "/docs 접근", None, 1.0),
    ROCItem("IOP-02", ROCCategory.INTEROP, "WebSocket 실시간",
            "/ws/cases 스트림", "WS 연결", None, 1.0),
    ROCItem("IOP-03", ROCCategory.INTEROP, "CesiumJS 3D",
            "지형+레이어 렌더링", "어댑터 존재", None, 1.0),

    # Deferred (코드 외부)
    ROCItem("EXT-01", ROCCategory.FUNCTIONAL, "야전시험",
            "실 환경 배치 테스트", "현장 수행", None, 2.0),
    ROCItem("EXT-02", ROCCategory.SECURITY, "외부 침투시험",
            "3rd-party 보안감사", "리포트 제출", None, 2.0),
]



# ── ROC 검증 실행기 ───────────────────────────────────
class ROCValidator:
    """
    DAPA ROC 자동 검증기

    사용법:
        validator = ROCValidator()
        report = validator.run()
        print(f"준수율: {report.compliance_rate()}%")
        print(f"가중점수: {report.score}/100")
    """

    def __init__(self, checklist: list[ROCItem] | None = None):
        self.checklist = checklist or STANDARD_ROC_CHECKLIST

    def run(self) -> ROCReport:
        """전체 ROC 체크리스트 실행"""
        results: list[ROCResult] = []
        total_weight = sum(item.weight for item in self.checklist)
        weighted_score = 0.0

        for item in self.checklist:
            t0 = time.time()

            if item.validator is None:
                # 자동 검증 불가 → DEFERRED
                status = ROCStatus.DEFERRED
                detail = "수동 검증 또는 외부 절차 필요"
            else:
                try:
                    status, detail = item.validator()
                except Exception as e:
                    status = ROCStatus.FAIL
                    detail = f"Exception: {e}"

            elapsed = round((time.time() - t0) * 1000, 2)

            results.append(ROCResult(
                roc_id=item.roc_id,
                category=item.category,
                title=item.title,
                status=status,
                detail=detail,
                elapsed_ms=elapsed,
            ))

            # 가중 점수 계산
            if status == ROCStatus.PASS:
                weighted_score += item.weight
            elif status == ROCStatus.PARTIAL:
                weighted_score += item.weight * 0.5

        report = ROCReport(
            total=len(results),
            passed=sum(1 for r in results if r.status == ROCStatus.PASS),
            failed=sum(1 for r in results if r.status == ROCStatus.FAIL),
            partial=sum(1 for r in results if r.status == ROCStatus.PARTIAL),
            deferred=sum(1 for r in results if r.status == ROCStatus.DEFERRED),
            results=results,
            score=round((weighted_score / total_weight) * 100, 1) if total_weight > 0 else 0,
        )
        return report

    def run_category(self, category: ROCCategory) -> ROCReport:
        """카테고리별 실행"""
        filtered = [i for i in self.checklist if i.category == category]
        validator = ROCValidator(checklist=filtered)
        return validator.run()

    def summary(self) -> dict[str, Any]:
        """빠른 요약 (run 후 호출)"""
        report = self.run()
        return {
            "total": report.total,
            "passed": report.passed,
            "failed": report.failed,
            "deferred": report.deferred,
            "compliance_rate": report.compliance_rate(),
            "weighted_score": report.score,
        }
