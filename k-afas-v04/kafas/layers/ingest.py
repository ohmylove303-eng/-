"""L1 자료수집 계층 (Data Ingest Layer).

원천: UAV 영상 / 관측보고 / 센서 이벤트 / 위성·항공영상 / 기상·지형.
산출: dict[str, Any]  (정규화 전 원시 레코드)
"""
from __future__ import annotations
from typing import Any
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))


def ingest_record(
    raw: dict[str, Any],
    source_type: str,
) -> dict[str, Any]:
    """원시 입력을 받아 source_type/observed_at_kst/ingest_at_kst를 부여한다.

    중요: observed_at_kst가 raw에 없으면 ValueError 발생.
          관측시각과 수집시각을 혼동하지 않기 위함 (감사 무결성).
    """
    if not isinstance(raw, dict):
        raise TypeError("raw must be dict")
    valid_sources = {
        "uav_video", "observer_report", "sensor_event",
        "satellite_image", "fixed_camera", "weather_terrain",
    }
    if source_type not in valid_sources:
        raise ValueError(f"invalid source_type:{source_type}")
    if "observed_at_kst" not in raw or not raw["observed_at_kst"]:
        raise ValueError("observed_at_kst_required (no fallback allowed)")

    return {
        **raw,
        "source_type": source_type,
        "ingest_at_kst": datetime.now(KST).isoformat(timespec="seconds"),
    }
