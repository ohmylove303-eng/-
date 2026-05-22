"""K-AFAS v0.4 통합 파이프라인 (Human-in-the-loop Decision Flow).

흐름:
  ingest -> normalize -> COP -> detection(candidate) -> evidence packet ->
  coord_support -> risk_gate -> decision -> human review -> audit -> AAR

매 단계 후 harness.evaluate_case() 호출 가능. REJECT 즉시 중단.
"""
from __future__ import annotations
from typing import Any
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta

from kafas.layers import (
    ingest as L1,
    normalize as L2,
    cop as L3,
    detection as L4,
    coord_support as L5,
    risk_gate as L6,
    decision as L7,
    audit as L8,
)
from kafas.harness import evaluate_case, HarnessReport

KST = timezone(timedelta(hours=9))



@dataclass
class PipelineResult:
    """파이프라인 단일 후보 처리 결과."""
    case: dict[str, Any] = field(default_factory=dict)
    cop_entry: dict[str, Any] = field(default_factory=dict)
    harness: HarnessReport | None = None
    halted_at: str | None = None     # 중단 단계명
    audit_path: str | None = None    # JSONL 경로

    def status(self) -> str:
        # 게이트 REJECT 또는 하네스 REJECT는 가장 강한 신호.
        if self.case.get("risk", {}).get("gate_result") == "REJECT":
            return "REJECT"
        if self.harness and self.harness.is_reject():
            return "REJECT"
        if self.halted_at:
            return f"HALTED@{self.halted_at}"
        if self.harness and self.harness.verdict == "HOLD":
            return "HOLD"
        return "PASS"


def _make_evidence_packet(
    candidate_id: str,
    seq: int,
    evidence_count: int,
    diversity: str,
    summary: str,
) -> dict[str, Any]:
    now = datetime.now(KST)
    status = "SUFFICIENT" if evidence_count >= 2 else "INSUFFICIENT"
    return {
        "packet_id": f"EVID-{now:%Y%m%d}-{seq:04d}",
        "candidate_id": candidate_id,
        "source_diversity": diversity,
        "evidence_count": evidence_count,
        "analyst_summary": summary,
        "evidence_status": status,
    }



class KAFASPipeline:
    """인간승인형 의사결정 흐름 오케스트레이터.

    사용 예:
        p = KAFASPipeline(audit_path="logs/audit.jsonl")
        result = p.run(
            raw={"observed_at_kst": "...", "confidence_score": 0.8},
            source_type="uav_video",
            cep_meters=22.0,
            evidence_count=2,
            source_diversity="MULTI_SOURCE",
            analyst_summary="2 stationary trucks (provisional)",
            civilian_risk="LOW",
            friendly_risk="LOW",
            roe_status="CLEAR",
            deconfliction_status="CLEAR",
            human_decision=("commander", "APPROVE_FOR_NEXT_REVIEW", "ok"),
        )
    """

    def __init__(self, audit_path: str = "logs/audit.jsonl") -> None:
        self.audit_path = audit_path
        self._seq = 0

    def _next_seq(self) -> int:
        self._seq += 1
        return self._seq

    # 1) 자료수집 → 정규화 → COP → 후보 → 좌표지원
    def _l1_to_l5(
        self,
        raw: dict[str, Any],
        source_type: str,
        cep_meters: float,
        movement_risk: str,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        ingested = L1.ingest_record(raw, source_type)
        # 자료수집 시각이 없으면 정규화에 사용할 observed_at_kst 보강
        if "observed_at_kst" not in ingested:
            ingested["observed_at_kst"] = ingested["ingest_at_kst"]
        normalized = L2.normalize(ingested)
        cop_entry = L3.build_cop_entry(normalized)
        candidate = L4.detect_candidate(
            normalized,
            seq=self._next_seq(),
            classification=raw.get("classification", "unknown"),
        )
        coord = L5.build_coord_support(
            candidate_id=candidate["candidate_id"],
            cep_meters=cep_meters,
            freshness_status=cop_entry["freshness_status"],
            movement_risk=movement_risk,
        )
        return candidate, cop_entry, coord



    def run(
        self,
        raw: dict[str, Any],
        source_type: str,
        cep_meters: float,
        evidence_count: int,
        source_diversity: str,
        analyst_summary: str,
        civilian_risk: str = "UNKNOWN",
        friendly_risk: str = "UNKNOWN",
        roe_status: str = "REVIEW_REQUIRED",
        deconfliction_status: str = "UNKNOWN",
        movement_risk: str = "UNKNOWN",
        human_decision: tuple[str, str, str] | None = None,
    ) -> PipelineResult:
        """단일 후보를 8계층을 통과시켜 처리한다.

        human_decision = (reviewer_role, decision, reason)
        """
        result = PipelineResult()

        # L1~L5
        candidate, cop_entry, coord = self._l1_to_l5(
            raw, source_type, cep_meters, movement_risk
        )
        result.cop_entry = cop_entry

        # L6: 증거패킷 + 위험게이트
        evidence = _make_evidence_packet(
            candidate_id=candidate["candidate_id"],
            seq=self._next_seq(),
            evidence_count=evidence_count,
            diversity=source_diversity,
            summary=analyst_summary,
        )
        risk = L6.evaluate_risk_gates(
            evidence=evidence,
            coord=coord,
            civilian_risk=civilian_risk,
            friendly_risk=friendly_risk,
            roe_status=roe_status,
            deconfliction_status=deconfliction_status,
        )

        # L7: 시스템 권고
        decision = L7.build_decision(
            candidate_id=candidate["candidate_id"],
            risk=risk,
            evidence_packet_id=evidence["packet_id"],
            seq=self._next_seq(),
        )

        case: dict[str, Any] = {
            "candidate": candidate,
            "evidence": evidence,
            "coord": coord,
            "risk": risk,
            "decision": decision,
            "review": None,
            "aar": None,
        }
        result.case = case

        # 위험게이트 REJECT는 인간검토 이전이라도 즉시 종결.
        if risk.get("gate_result") == "REJECT":
            report = evaluate_case(case, text_corpus=decision.get("reason", ""))
            result.harness = report
            result.halted_at = "risk_gate_reject"
            result.audit_path = str(L8.append_audit_log(case, self.audit_path))
            return result

        # 하네스 1차 검증
        report = evaluate_case(case, text_corpus=decision.get("reason", ""))
        result.harness = report
        if report.is_reject():
            result.halted_at = "harness_pre_human"
            result.audit_path = str(L8.append_audit_log(case, self.audit_path))
            return result



        # L8: 인간검토 (선택). 없으면 HOLD 상태로 감사기록 후 종료.
        if human_decision is None:
            result.halted_at = "awaiting_human_review"
            result.audit_path = str(L8.append_audit_log(case, self.audit_path))
            return result

        role, decision_label, reason = human_decision
        review = L8.make_review_log(
            candidate_id=candidate["candidate_id"],
            reviewer_role=role,
            decision=decision_label,
            decision_reason=reason,
            seq=self._next_seq(),
        )
        case["review"] = review

        # 하네스 2차 검증 (인간승인 포함)
        report2 = evaluate_case(case, text_corpus=decision.get("reason", ""))
        result.harness = report2

        # AAR은 운용 사이클 후속 단계에서 입력 (여기서는 placeholder)
        case["aar"] = None

        # 감사로그 적재
        result.audit_path = str(L8.append_audit_log(case, self.audit_path))
        return result

    # 사후평가는 별도 트리거 (실제 결과 확인 후 호출)
    def submit_aar(
        self,
        case: dict[str, Any],
        outcome: str,
    ) -> dict[str, Any]:
        cand_id = case.get("candidate", {}).get("candidate_id", "")
        aar = L8.make_aar(cand_id, outcome, seq=self._next_seq())
        case["aar"] = aar
        L8.append_audit_log(case, self.audit_path)
        return aar
