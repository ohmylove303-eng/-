"""L4 인공지능 후보탐지 계층 (AI Candidate Detection Layer).

영상분석·후보분류·불확실성·오탐위험을 추정한다.
출력은 항상 '후보(candidate)'이며 표적확정(confirm)은 금지.
"""
from __future__ import annotations
from typing import Any
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))


def _next_candidate_id(seq: int, now: datetime | None = None) -> str:
    now = now or datetime.now(KST)
    return f"CAND-{now:%Y%m%d}-{seq:04d}"


def detect_candidate(
    normalized: dict[str, Any],
    seq: int,
    classification: str = "unknown",
    now: datetime | None = None,
) -> dict[str, Any]:
    """정규화된 증거에서 표적 '후보'를 생성한다.

    중요: 이 함수는 '후보(Candidate)'만 만든다.
          표적 확정/사격승인은 절대 수행하지 않는다.
    """
    valid_classes = {"vehicle_candidate", "equipment_candidate", "unknown"}
    if classification not in valid_classes:
        classification = "unknown"

    candidate = {
        "candidate_id": _next_candidate_id(seq, now),
        "status": "CANDIDATE",
        "observed_at_kst": normalized["observed_at_kst"],
        "source_type": normalized["source_type"],
        "classification": classification,
        "confidence_band": normalized["confidence_band"],
        "raw_evidence_reference": normalized["raw_evidence_reference"],
    }
    return candidate
