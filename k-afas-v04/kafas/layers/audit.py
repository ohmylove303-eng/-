"""L8 인간승인·감사 계층 (Human Approval & Audit Layer).

HumanReviewLog 작성, 감사로그 적재, AfterActionReview 생성.
"""
from __future__ import annotations
from typing import Any
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))


def make_review_log(
    candidate_id: str,
    reviewer_role: str,
    decision: str,
    decision_reason: str,
    seq: int = 1,
) -> dict[str, Any]:
    """인간 검토자의 결정을 기록한다."""
    valid_roles = {"commander", "analyst", "safety_officer", "auditor"}
    valid_decisions = {
        "REQUEST_MORE_EVIDENCE", "HOLD",
        "REJECT", "APPROVE_FOR_NEXT_REVIEW",
    }
    if reviewer_role not in valid_roles:
        raise ValueError(f"invalid reviewer_role:{reviewer_role}")
    if decision not in valid_decisions:
        raise ValueError(f"invalid decision:{decision}")

    now = datetime.now(KST)
    return {
        "review_id": f"REV-{now:%Y%m%d}-{seq:04d}",
        "candidate_id": candidate_id,
        "reviewer_role": reviewer_role,
        "decision": decision,
        "reviewed_at_kst": now.isoformat(timespec="seconds"),
        "decision_reason": decision_reason,
    }



def make_aar(
    candidate_id: str,
    outcome: str,
    seq: int = 1,
) -> dict[str, Any]:
    """사후평가(AAR) 객체 생성. 모델 자동 갱신은 항상 금지."""
    valid = {"CONFIRMED", "UNCONFIRMED", "FALSE_POSITIVE", "INSUFFICIENT_DATA"}
    if outcome not in valid:
        raise ValueError(f"invalid outcome:{outcome}")
    now = datetime.now(KST)
    return {
        "aar_id": f"AAR-{now:%Y%m%d}-{seq:04d}",
        "candidate_id": candidate_id,
        "outcome": outcome,
        "model_update_allowed": False,
        "review_required_before_training": True,
        "audit_replay_required": True,
    }


def append_audit_log(
    case: dict[str, Any],
    log_path: str | Path = "logs/audit.jsonl",
) -> Path:
    """전체 case를 JSONL 파일에 append (감사재생용)."""
    p = Path(log_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "logged_at_kst": datetime.now(KST).isoformat(timespec="seconds"),
        "case": case,
    }
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return p
