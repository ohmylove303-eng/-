"""계층별 단위 테스트."""
import unittest
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

KST = timezone(timedelta(hours=9))


class TestL1L5(unittest.TestCase):

    def test_ingest_invalid_source(self):
        with self.assertRaises(ValueError):
            L1.ingest_record({}, "bogus")

    def test_normalize_confidence_band(self):
        self.assertEqual(L2.to_confidence_band(0.1), "LOW")
        self.assertEqual(L2.to_confidence_band(0.5), "MEDIUM")
        self.assertEqual(L2.to_confidence_band(0.95), "HIGH")

    def test_freshness(self):
        now = datetime(2026, 5, 22, 10, 0, 0, tzinfo=KST)
        s = L3.freshness_status("2026-05-22T09:30:00+09:00", now=now)
        self.assertEqual(s, "RED")  # 30분 경과

    def test_detect_creates_candidate_only(self):
        normalized = {
            "observed_at_kst": "2026-05-22T10:00:00+09:00",
            "source_type": "uav_video",
            "confidence_band": "HIGH",
            "raw_evidence_reference": "secured",
        }
        c = L4.detect_candidate(normalized, seq=1)
        self.assertEqual(c["status"], "CANDIDATE")
        self.assertTrue(c["candidate_id"].startswith("CAND-"))

    def test_coord_quality_grade(self):
        self.assertEqual(L5.coordinate_quality_grade(10), "HIGH")
        self.assertEqual(L5.coordinate_quality_grade(80), "MEDIUM")
        self.assertEqual(L5.coordinate_quality_grade(200), "LOW")



class TestL6L8(unittest.TestCase):

    def _coord(self):
        return {
            "candidate_id": "CAND-1",
            "coordinate_quality": "HIGH",
            "freshness_status": "GREEN",
            "coordinate_use_policy":
                "NO_FIRING_DATA__NO_BALLISTIC_CALC__HUMAN_REVIEW_ONLY",
        }

    def test_risk_gate_pass(self):
        ev = {
            "evidence_status": "SUFFICIENT",
            "source_diversity": "MULTI_SOURCE",
        }
        r = L6.evaluate_risk_gates(
            ev, self._coord(),
            civilian_risk="LOW", friendly_risk="LOW",
            roe_status="CLEAR", deconfliction_status="CLEAR",
        )
        self.assertEqual(r["gate_result"], "PASS")

    def test_risk_gate_reject_high_civilian(self):
        ev = {"evidence_status": "SUFFICIENT", "source_diversity": "MULTI_SOURCE"}
        r = L6.evaluate_risk_gates(
            ev, self._coord(),
            civilian_risk="HIGH",
        )
        self.assertEqual(r["gate_result"], "REJECT")

    def test_decision_locked(self):
        risk = {"gate_result": "PASS"}
        d = L7.build_decision("CAND-1", risk, "EVID-1", seq=1)
        self.assertEqual(d["weapon_control_link"], "NOT_ALLOWED")
        self.assertEqual(d["firing_data"], "NOT_ALLOWED")
        self.assertEqual(d["ballistic_calculation"], "NOT_ALLOWED")

    def test_review_invalid_role(self):
        with self.assertRaises(ValueError):
            L8.make_review_log("CAND-1", "hacker", "HOLD", "x")

    def test_aar_outcome_validation(self):
        with self.assertRaises(ValueError):
            L8.make_aar("CAND-1", "WEIRD")


if __name__ == "__main__":
    unittest.main()
