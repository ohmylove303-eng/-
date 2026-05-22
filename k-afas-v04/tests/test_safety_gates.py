"""안전게이트 + 무기분리 시도 차단 회귀 테스트."""
import unittest
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

from kafas.pipeline import KAFASPipeline
from kafas.harness import evaluate_case
from kafas.layers import risk_gate as L6

KST = timezone(timedelta(hours=9))


def _now_iso() -> str:
    return datetime.now(KST).isoformat(timespec="seconds")


class TestSafetyGates(unittest.TestCase):

    def test_low_coord_quality_rejects(self):
        ev = {"evidence_status": "SUFFICIENT", "source_diversity": "MULTI_SOURCE"}
        coord = {
            "candidate_id": "CAND-1",
            "coordinate_quality": "LOW",
            "freshness_status": "GREEN",
            "coordinate_use_policy":
                "NO_FIRING_DATA__NO_BALLISTIC_CALC__HUMAN_REVIEW_ONLY",
        }
        r = L6.evaluate_risk_gates(
            ev, coord,
            civilian_risk="LOW", friendly_risk="LOW",
            roe_status="CLEAR", deconfliction_status="CLEAR",
        )
        self.assertEqual(r["gate_result"], "REJECT")

    def test_freshness_black_rejects(self):
        ev = {"evidence_status": "SUFFICIENT", "source_diversity": "MULTI_SOURCE"}
        coord = {
            "candidate_id": "CAND-1",
            "coordinate_quality": "HIGH",
            "freshness_status": "BLACK",
            "coordinate_use_policy":
                "NO_FIRING_DATA__NO_BALLISTIC_CALC__HUMAN_REVIEW_ONLY",
        }
        r = L6.evaluate_risk_gates(ev, coord)
        self.assertEqual(r["gate_result"], "REJECT")



    def test_weapon_separation_lock_blocks_tampering(self):
        """누군가 case의 정책 필드를 바꿔치기해도 하네스가 REJECT."""
        case = {
            "candidate": {
                "candidate_id": "CAND-1",
                "source_type": "uav_video",
                "observed_at_kst": "2026-05-22T10:00:00+09:00",
            },
            "evidence": {
                "packet_id": "EVID-1",
                "evidence_status": "SUFFICIENT",
                "source_diversity": "MULTI_SOURCE",
            },
            "coord": {
                "candidate_id": "CAND-1",
                "coordinate_use_policy": "ALLOW_FIRING",  # ← 변조 시도
            },
            "decision": {
                "weapon_control_link": "NOT_ALLOWED",
                "firing_data": "NOT_ALLOWED",
                "ballistic_calculation": "NOT_ALLOWED",
            },
            "review": {"decision": "APPROVE_FOR_NEXT_REVIEW"},
        }
        report = evaluate_case(case)
        self.assertEqual(report.verdict, "REJECT")
        self.assertTrue(any("weapon_separation" in v for v in report.violations))

    def test_forbidden_phrase_in_reason(self):
        """의사결정 이유에 금지 표현이 있으면 REJECT."""
        case = {
            "candidate": {
                "candidate_id": "CAND-1",
                "source_type": "uav_video",
                "observed_at_kst": "2026-05-22T10:00:00+09:00",
            },
            "evidence": {
                "packet_id": "EVID-1",
                "evidence_status": "SUFFICIENT",
                "source_diversity": "MULTI_SOURCE",
            },
            "coord": {
                "candidate_id": "CAND-1",
                "coordinate_use_policy":
                    "NO_FIRING_DATA__NO_BALLISTIC_CALC__HUMAN_REVIEW_ONLY",
            },
            "decision": {
                "weapon_control_link": "NOT_ALLOWED",
                "firing_data": "NOT_ALLOWED",
                "ballistic_calculation": "NOT_ALLOWED",
                "reason": "kill chain optimization",  # 금지 표현
            },
            "review": {"decision": "APPROVE_FOR_NEXT_REVIEW"},
        }
        report = evaluate_case(case, text_corpus=case["decision"]["reason"])
        self.assertEqual(report.verdict, "REJECT")


if __name__ == "__main__":
    unittest.main()
