"""L2 증거정규화 계층 (Evidence Normalization Layer).

시간(KST), 좌표계(WGS84), 출처, 신뢰도, 원본참조를 표준화한다.
"""
from __future__ import annotations
from typing import Any


_CONFIDENCE_MAP = {
    (0.0, 0.4): "LOW",
    (0.4, 0.7): "MEDIUM",
    (0.7, 1.01): "HIGH",
}


def to_confidence_band(score: float) -> str:
    """0.0~1.0 점수를 LOW/MEDIUM/HIGH 밴드로 변환."""
    s = max(0.0, min(1.0, float(score)))
    for (lo, hi), band in _CONFIDENCE_MAP.items():
        if lo <= s < hi:
            return band
    return "LOW"


def normalize(record: dict[str, Any]) -> dict[str, Any]:
    """수집 레코드를 정규화된 표준 형태로 변환."""
    if "observed_at_kst" not in record:
        raise ValueError("observed_at_kst_missing")
    if "source_type" not in record:
        raise ValueError("source_type_missing")

    score = float(record.get("confidence_score", 0.0))
    return {
        "observed_at_kst": record["observed_at_kst"],
        "source_type": record["source_type"],
        "coord_ref": record.get("coord_ref", "WGS84"),
        "confidence_band": to_confidence_band(score),
        "raw_evidence_reference": record.get(
            "raw_evidence_reference", "secured_reference_only"
        ),
    }
