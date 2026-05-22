"""L7 의사결정 지원 계층 (Decision Support Layer).

게이트 결과를 시스템 권고(REVIEW/RECHECK/HOLD/REJECT)로 변환한다.
무기제어/사격제원/탄도계산은 항상 NOT_ALLOWED.
"""
from __future__ import annotations
from typing import Any
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))


def _next_pkg_id(seq: int, now: datetime | None = None) -> str:
    now = now or datetime.now(KST)
    return f"REVPKG-{now:%Y%m%d}-{seq:04d}"


def map_recommendation(gate_result: str) -> str:
    """게이트 결과 -> 시스템 권고 매핑."""
    return {
        "PASS": "REVIEW",        # 사람이 검토하도록 큐에 넣는다
        "HOLD": "HOLD",
        "REJECT": "REJECT",
    }.get(gate_result, "RECHECK")


def build_decision(
    candidate_id: str,
    risk: dict[str, Any],
    evidence_packet_id: str,
    seq: int = 1,
    reason: str = "",
) -> dict[str, Any]:
    """DecisionSupport 객체 생성 — 무기연동 필드는 NOT_ALLOWED 고정."""
    rec = map_recommendation(risk.get("gate_result", "HOLD"))
    if not reason:
        reason = f"derived_from_gate_result:{risk.get('gate_result')}"
    return {
        "candidate_id": candidate_id,
        "system_recommendation": rec,
        "reason": reason,
        "review_package_id": _next_pkg_id(seq),
        "evidence_packet_id": evidence_packet_id,
        "weapon_control_link": "NOT_ALLOWED",
        "firing_data": "NOT_ALLOWED",
        "ballistic_calculation": "NOT_ALLOWED",
    }
