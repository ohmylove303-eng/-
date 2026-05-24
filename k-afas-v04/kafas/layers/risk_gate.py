"""L6 좌표품질·위험게이트 계층 (Coordinate Quality & Risk Gate Layer).

10개 안전게이트를 평가한다:
  Evidence / Freshness / CoordinateQuality / CivilianRisk / FriendlyRisk
  / ROE / Deconfliction / HumanApproval / Audit / WeaponSeparation
"""
from __future__ import annotations
from typing import Any

# 게이트별 (PASS, HOLD, REJECT) 라벨 — 의미: 우선순위 highest -> REJECT
_FRESHNESS_HOLD = {"YELLOW", "RED"}
_FRESHNESS_REJECT = {"BLACK"}


def _evidence_gate(ev: dict[str, Any]) -> str:
    status = ev.get("evidence_status")
    if status == "CONFLICTING":
        return "REJECT"
    if status == "INSUFFICIENT":
        return "HOLD"
    if ev.get("source_diversity") == "SINGLE_SOURCE":
        return "HOLD"
    return "PASS"


def _freshness_gate(coord: dict[str, Any]) -> str:
    f = coord.get("freshness_status")
    if f in _FRESHNESS_REJECT:
        return "REJECT"
    if f in _FRESHNESS_HOLD:
        return "HOLD"
    return "PASS"


def _coord_quality_gate(coord: dict[str, Any]) -> str:
    q = coord.get("coordinate_quality")
    if q == "LOW":
        return "REJECT"
    if q == "MEDIUM":
        return "HOLD"
    return "PASS"



def _risk_label_gate(value: str) -> str:
    if value == "HIGH":
        return "REJECT"
    if value in ("MEDIUM", "UNKNOWN"):
        return "HOLD"
    return "PASS"


def _roe_gate(roe_status: str) -> str:
    if roe_status == "HOLD":
        return "REJECT"
    if roe_status == "REVIEW_REQUIRED":
        return "HOLD"
    return "PASS"


def _deconfliction_gate(value: str) -> str:
    if value == "CONFLICT":
        return "REJECT"
    if value == "UNKNOWN":
        return "HOLD"
    return "PASS"


def _weapon_separation_gate(coord: dict[str, Any]) -> str:
    """좌표 정책이 변경되면 즉시 REJECT (무기제어 시도로 간주)."""
    expected = "NO_FIRING_DATA__NO_BALLISTIC_CALC__HUMAN_REVIEW_ONLY"
    if coord.get("coordinate_use_policy") != expected:
        return "REJECT"
    return "PASS"


def _aggregate(gates: dict[str, str]) -> str:
    if any(v == "REJECT" for v in gates.values()):
        return "REJECT"
    if any(v == "HOLD" for v in gates.values()):
        return "HOLD"
    return "PASS"



def evaluate_risk_gates(
    evidence: dict[str, Any],
    coord: dict[str, Any],
    civilian_risk: str = "UNKNOWN",
    friendly_risk: str = "UNKNOWN",
    roe_status: str = "REVIEW_REQUIRED",
    deconfliction_status: str = "UNKNOWN",
) -> dict[str, Any]:
    """10개 안전게이트 평가 결과를 RiskGate 객체로 반환.

    인간승인(I5)·감사(I9)는 파이프라인 후속 단계에서 평가하므로
    여기서는 8개 데이터 게이트 + 무기분리(I10) 결과만 산출한다.
    """
    gates = {
        "evidence":           _evidence_gate(evidence),
        "freshness":          _freshness_gate(coord),
        "coord_quality":      _coord_quality_gate(coord),
        "civilian_risk":      _risk_label_gate(civilian_risk),
        "friendly_risk":      _risk_label_gate(friendly_risk),
        "roe":                _roe_gate(roe_status),
        "deconfliction":      _deconfliction_gate(deconfliction_status),
        "weapon_separation":  _weapon_separation_gate(coord),
    }
    aggregated = _aggregate(gates)

    return {
        "candidate_id": coord.get("candidate_id", ""),
        "civilian_risk": civilian_risk,
        "friendly_risk": friendly_risk,
        "roe_status": roe_status,
        "deconfliction_status": deconfliction_status,
        "gate_result": aggregated,
        "_gate_details": gates,  # 진단용 (감사로그에 보존)
    }
