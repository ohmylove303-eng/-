"""런타임 dict 검증 (pydantic 없이 표준 라이브러리만 사용).

TypedDict는 정적 검사용이라 잘못된 dict가 들어와도 KeyError만 발생.
이 모듈은 진입점에서 명시적 검증을 수행해 ValidationError를 던진다.
"""
from __future__ import annotations
from typing import Any


class ValidationError(ValueError):
    """K-AFAS 데이터 검증 실패 시 발생."""


_CANDIDATE_REQUIRED = (
    "candidate_id", "status", "observed_at_kst",
    "source_type", "classification", "confidence_band",
    "raw_evidence_reference",
)
_DECISION_LOCKED = {
    "weapon_control_link": "NOT_ALLOWED",
    "firing_data": "NOT_ALLOWED",
    "ballistic_calculation": "NOT_ALLOWED",
}
_COORD_POLICY = "NO_FIRING_DATA__NO_BALLISTIC_CALC__HUMAN_REVIEW_ONLY"


def validate_candidate(c: dict[str, Any]) -> None:
    if not isinstance(c, dict):
        raise ValidationError("candidate_must_be_dict")
    missing = [k for k in _CANDIDATE_REQUIRED if k not in c]
    if missing:
        raise ValidationError(f"candidate_missing:{missing}")
    if c["status"] not in (
        "CANDIDATE", "PROBABLE", "VALIDATED", "HOLD", "REJECTED"
    ):
        raise ValidationError(f"candidate_status_invalid:{c['status']}")


def validate_decision(d: dict[str, Any]) -> None:
    if not isinstance(d, dict):
        raise ValidationError("decision_must_be_dict")
    for k, expected in _DECISION_LOCKED.items():
        if d.get(k, expected) != expected:
            raise ValidationError(f"decision_field_locked:{k}={d.get(k)}")


def validate_coord(c: dict[str, Any]) -> None:
    if not isinstance(c, dict):
        raise ValidationError("coord_must_be_dict")
    if c.get("coordinate_use_policy") != _COORD_POLICY:
        raise ValidationError("coord_policy_locked_violation")


def validate_case(case: dict[str, Any]) -> None:
    """파이프라인 진입 직전 호출. 핵심 3개 객체를 검증."""
    if "candidate" in case:
        validate_candidate(case["candidate"])
    if "decision" in case:
        validate_decision(case["decision"])
    if "coord" in case:
        validate_coord(case["coord"])
