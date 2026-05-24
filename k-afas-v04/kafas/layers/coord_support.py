"""L5 자동화된 표적 표시·좌표화 지원 계층
    (Automated Target Display and Coordinate Support Layer).

위치 단서/좌표품질/이동위험을 산출한다.
정책: NO_FIRING_DATA / NO_BALLISTIC_CALC / HUMAN_REVIEW_ONLY (고정).
"""
from __future__ import annotations
from typing import Any

# 좌표 사용 정책 (고정 Literal — 절대 변경 금지)
POLICY = "NO_FIRING_DATA__NO_BALLISTIC_CALC__HUMAN_REVIEW_ONLY"


def coordinate_quality_grade(meters_cep: float) -> str:
    """원형공산오차(CEP, m)로 좌표품질 등급 산출.
    HIGH  : <= 25m
    MEDIUM: <= 100m
    LOW   : > 100m
    """
    if meters_cep <= 25:
        return "HIGH"
    if meters_cep <= 100:
        return "MEDIUM"
    return "LOW"


def build_coord_support(
    candidate_id: str,
    cep_meters: float,
    freshness_status: str,
    movement_risk: str = "UNKNOWN",
) -> dict[str, Any]:
    """좌표화 지원 객체 생성. 항상 review-required로 시작."""
    quality = coordinate_quality_grade(cep_meters)
    cue = "REVIEW_REQUIRED" if quality != "HIGH" else "DISPLAY_ONLY"
    return {
        "candidate_id": candidate_id,
        "location_cue": cue,
        "coordinate_quality": quality,
        "freshness_status": freshness_status,
        "movement_risk": movement_risk,
        "coordinate_use_policy": POLICY,
    }
