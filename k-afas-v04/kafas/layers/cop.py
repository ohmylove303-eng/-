"""L3 공통작전상황도 계층 (Common Operational Picture Layer).

표적후보·아군위험·민간위험·제한구역·정보신선도를 지도 레이어로 묶는다.
display-only: 좌표는 표시용일 뿐 사격제원으로 사용 금지.
"""
from __future__ import annotations
from typing import Any
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))


def _parse_kst(s: str) -> datetime:
    return datetime.fromisoformat(s)


def freshness_status(observed_at_kst: str, now: datetime | None = None) -> str:
    """관측 시각 대비 신선도 등급 산출.
    GREEN  <= 5분
    YELLOW <= 15분
    RED    <= 60분
    BLACK  > 60분
    """
    obs = _parse_kst(observed_at_kst)
    now = now or datetime.now(KST)
    delta_min = (now - obs).total_seconds() / 60.0
    if delta_min <= 5:
        return "GREEN"
    if delta_min <= 15:
        return "YELLOW"
    if delta_min <= 60:
        return "RED"
    return "BLACK"


def build_cop_entry(normalized: dict[str, Any]) -> dict[str, Any]:
    """정규화 결과로부터 COP 항목을 만든다 (display-only)."""
    return {
        "freshness_status": freshness_status(normalized["observed_at_kst"]),
        "source_type": normalized["source_type"],
        "confidence_band": normalized["confidence_band"],
        "display_only": True,  # 좌표 표시 전용
    }
