"""K-AFAS v0.4 데이터 스키마 (Data Schema).

7개 핵심 객체:
  1) TargetCandidate     - 표적후보
  2) EvidencePacket      - 증거패킷
  3) CoordinateSupport   - 자동화된 표적 표시·좌표화 지원
  4) RiskGate            - 위험게이트
  5) DecisionSupport     - 의사결정 지원
  6) HumanReviewLog      - 인간검토로그
  7) AfterActionReview   - 사후평가

REJECT: 자동사격, 사격제원, 탄도계산, 무기 직접연동.
"""
from __future__ import annotations
from typing import TypedDict, Literal, Optional


# 1) 표적후보 (Target Candidate)
class TargetCandidate(TypedDict):
    candidate_id: str                    # CAND-YYYYMMDD-NNNN
    status: Literal[
        "CANDIDATE", "PROBABLE", "VALIDATED", "HOLD", "REJECTED"
    ]
    observed_at_kst: str                 # ISO8601 with +09:00
    source_type: Literal[
        "uav_video", "observer_report", "sensor_event",
        "satellite_image", "fixed_camera",
    ]
    classification: Literal[
        "vehicle_candidate", "equipment_candidate", "unknown"
    ]
    confidence_band: Literal["LOW", "MEDIUM", "HIGH"]
    raw_evidence_reference: str          # 원본 참조 (보안 토큰)



# 2) 증거패킷 (Evidence Packet)
class EvidencePacket(TypedDict):
    packet_id: str                       # EVID-YYYYMMDD-NNNN
    candidate_id: str
    source_diversity: Literal["SINGLE_SOURCE", "MULTI_SOURCE"]
    evidence_count: int                  # 증거 항목 수
    analyst_summary: str                 # 분석관 요약
    evidence_status: Literal[
        "SUFFICIENT", "INSUFFICIENT", "CONFLICTING"
    ]


# 3) 자동화된 표적 표시·좌표화 지원
#    (Automated Target Display and Coordinate Support)
class CoordinateSupport(TypedDict):
    candidate_id: str
    location_cue: Literal["DISPLAY_ONLY", "REVIEW_REQUIRED"]
    coordinate_quality: Literal["LOW", "MEDIUM", "HIGH"]
    freshness_status: Literal["GREEN", "YELLOW", "RED", "BLACK"]
    movement_risk: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"]
    # 정책: 사격제원·탄도계산·무기연동 절대 금지 (강제 고정값)
    coordinate_use_policy: Literal[
        "NO_FIRING_DATA__NO_BALLISTIC_CALC__HUMAN_REVIEW_ONLY"
    ]


# 4) 위험게이트 (Risk Gate)
class RiskGate(TypedDict):
    candidate_id: str
    civilian_risk: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"]
    friendly_risk: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"]
    roe_status: Literal["CLEAR", "REVIEW_REQUIRED", "HOLD"]
    deconfliction_status: Literal["CLEAR", "CONFLICT", "UNKNOWN"]
    gate_result: Literal["PASS", "HOLD", "REJECT"]



# 5) 의사결정 지원 (Decision Support)
#    무기제어/사격제원/탄도계산 필드는 "NOT_ALLOWED" 고정.
class DecisionSupport(TypedDict):
    candidate_id: str
    system_recommendation: Literal[
        "REVIEW", "RECHECK", "HOLD", "REJECT"
    ]
    reason: str
    review_package_id: str               # REVPKG-YYYYMMDD-NNNN
    evidence_packet_id: str
    weapon_control_link: Literal["NOT_ALLOWED"]
    firing_data: Literal["NOT_ALLOWED"]
    ballistic_calculation: Literal["NOT_ALLOWED"]


# 6) 인간검토로그 (Human Review Log)
class HumanReviewLog(TypedDict):
    review_id: str                       # REV-YYYYMMDD-NNNN
    candidate_id: str
    reviewer_role: Literal[
        "commander", "analyst", "safety_officer", "auditor"
    ]
    decision: Literal[
        "REQUEST_MORE_EVIDENCE", "HOLD",
        "REJECT", "APPROVE_FOR_NEXT_REVIEW",
    ]
    reviewed_at_kst: str
    decision_reason: str


# 7) 사후평가 (After Action Review)
class AfterActionReview(TypedDict):
    aar_id: str                          # AAR-YYYYMMDD-NNNN
    candidate_id: str
    outcome: Literal[
        "CONFIRMED", "UNCONFIRMED",
        "FALSE_POSITIVE", "INSUFFICIENT_DATA",
    ]
    model_update_allowed: bool           # 항상 False 권장
    review_required_before_training: bool  # 항상 True
    audit_replay_required: bool          # 항상 True


# 한 후보의 모든 단계 산출물을 묶은 케이스(Case) 컨테이너.
class Case(TypedDict, total=False):
    candidate: TargetCandidate
    evidence: EvidencePacket
    coord: CoordinateSupport
    risk: RiskGate
    decision: DecisionSupport
    review: Optional[HumanReviewLog]
    aar: Optional[AfterActionReview]
