"""L8 인간승인·감사 계층 (Human Approval & Audit Layer).

- HumanReviewLog 작성 (역할 검증 + 토큰 인증)
- 감사로그 적재 (SHA-256 해시 체인으로 변조 탐지)
- AfterActionReview 생성
"""
from __future__ import annotations
from typing import Any
import os
import json
import hashlib
import hmac
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))

# 환경변수로 권한 토큰 매핑 주입 (예: KAFAS_TOKEN_COMMANDER=xxx).
# 운영시 Vault/HSM/PKI 등으로 대체 권장.
_ROLE_ENV_MAP = {
    "commander":      "KAFAS_TOKEN_COMMANDER",
    "analyst":        "KAFAS_TOKEN_ANALYST",
    "safety_officer": "KAFAS_TOKEN_SAFETY",
    "auditor":        "KAFAS_TOKEN_AUDITOR",
}


def _verify_reviewer(role: str, token: str | None) -> None:
    """역할 토큰을 환경변수와 hmac.compare_digest로 비교.
    토큰이 환경변수에 설정되지 않은 환경(개발/테스트)에서는 건너뛴다.
    """
    if role not in _ROLE_ENV_MAP:
        raise ValueError(f"invalid reviewer_role:{role}")
    expected = os.environ.get(_ROLE_ENV_MAP[role])
    if expected is None:
        return  # dev mode (env not set)
    if not token or not hmac.compare_digest(expected, token):
        raise PermissionError(f"reviewer_token_invalid:{role}")



def make_review_log(
    candidate_id: str,
    reviewer_role: str,
    decision: str,
    decision_reason: str,
    seq: int = 1,
    reviewer_token: str | None = None,
) -> dict[str, Any]:
    """인간 검토자의 결정을 기록한다. 토큰이 있으면 검증."""
    valid_decisions = {
        "REQUEST_MORE_EVIDENCE", "HOLD",
        "REJECT", "APPROVE_FOR_NEXT_REVIEW",
    }
    if decision not in valid_decisions:
        raise ValueError(f"invalid decision:{decision}")
    _verify_reviewer(reviewer_role, reviewer_token)

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



# ── 감사로그 해시 체인 (Audit Hash Chain) ───────────────────
GENESIS_PREV_HASH = "0" * 64


def _hash_record(prev_hash: str, payload: dict[str, Any]) -> str:
    """이전 해시 + 현재 payload(JSON canonical) → SHA-256."""
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    h = hashlib.sha256()
    h.update(prev_hash.encode("utf-8"))
    h.update(b"|")
    h.update(canonical.encode("utf-8"))
    return h.hexdigest()


def _read_last_hash(p: Path) -> str:
    """JSONL 마지막 라인의 hash를 읽는다. 없으면 GENESIS."""
    if not p.exists() or p.stat().st_size == 0:
        return GENESIS_PREV_HASH
    last_line = ""
    with p.open("rb") as f:
        f.seek(-1, 2)
        if f.read(1) == b"\n":
            try:
                f.seek(-2, 2)
            except OSError:
                f.seek(0)
        # 안전한 fallback: 전체 라인 읽고 마지막 사용
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                last_line = line
    if not last_line:
        return GENESIS_PREV_HASH
    try:
        rec = json.loads(last_line)
        return rec.get("hash", GENESIS_PREV_HASH)
    except json.JSONDecodeError:
        return GENESIS_PREV_HASH


def append_audit_log(
    case: dict[str, Any],
    log_path: str | Path = "logs/audit.jsonl",
) -> Path:
    """전체 case를 JSONL 파일에 append. 이전 라인의 hash와 체인."""
    p = Path(log_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    prev_hash = _read_last_hash(p)
    payload = {
        "logged_at_kst": datetime.now(KST).isoformat(timespec="seconds"),
        "prev_hash": prev_hash,
        "case": case,
    }
    payload["hash"] = _hash_record(prev_hash, payload)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return p



def verify_audit_chain(log_path: str | Path) -> tuple[bool, str]:
    """JSONL 전체 해시체인을 처음부터 끝까지 재계산해 일치 여부 검증.

    Returns: (ok, reason)
    """
    p = Path(log_path)
    if not p.exists():
        return False, "log_not_found"
    prev = GENESIS_PREV_HASH
    with p.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                return False, f"json_decode_error_at_line:{i}"
            stored_hash = rec.get("hash")
            stored_prev = rec.get("prev_hash")
            if stored_prev != prev:
                return False, f"prev_hash_mismatch_at_line:{i}"
            recompute = {k: v for k, v in rec.items() if k != "hash"}
            expected = _hash_record(prev, recompute)
            if expected != stored_hash:
                return False, f"hash_mismatch_at_line:{i}"
            prev = stored_hash
    return True, "chain_ok"
