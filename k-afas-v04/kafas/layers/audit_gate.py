"""Audit Gate (안전게이트 9번).

감사로그 완전성과 해시체인 무결성을 검사한다.
SRD 명세 누락분을 보완.
"""
from __future__ import annotations
from typing import Any
from pathlib import Path

from kafas.layers.audit import verify_audit_chain

# case에 반드시 존재해야 하는 키 (감사 완전성)
_REQUIRED_KEYS = ("candidate", "evidence", "coord", "risk", "decision")


def evaluate_audit_gate(
    case: dict[str, Any],
    log_path: str | Path | None = None,
) -> dict[str, Any]:
    """case 완전성 + 로그 체인 무결성을 평가.

    Returns: dict
        {
          "completeness": "PASS" | "REJECT",
          "missing_keys": [...],
          "chain_ok": bool,
          "chain_reason": str,
          "gate_result": "PASS" | "REJECT" | "HOLD",
        }
    """
    missing = [k for k in _REQUIRED_KEYS if not case.get(k)]
    completeness = "REJECT" if missing else "PASS"

    chain_ok = True
    chain_reason = "skip"
    if log_path is not None and Path(log_path).exists():
        chain_ok, chain_reason = verify_audit_chain(log_path)

    if completeness == "REJECT":
        gate = "REJECT"
    elif log_path is not None and not chain_ok:
        gate = "REJECT"
    elif log_path is None:
        gate = "HOLD"  # 로그 미연결이면 보류
    else:
        gate = "PASS"

    return {
        "completeness": completeness,
        "missing_keys": missing,
        "chain_ok": chain_ok,
        "chain_reason": chain_reason,
        "gate_result": gate,
    }
