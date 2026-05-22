"""TypedDict 스키마 형식 검증."""
import unittest

from kafas import schemas as S


class TestSchemas(unittest.TestCase):

    def test_target_candidate_minimal(self):
        c: S.TargetCandidate = {
            "candidate_id": "CAND-20260522-0001",
            "status": "CANDIDATE",
            "observed_at_kst": "2026-05-22T10:00:00+09:00",
            "source_type": "uav_video",
            "classification": "vehicle_candidate",
            "confidence_band": "MEDIUM",
            "raw_evidence_reference": "secured_reference_only",
        }
        self.assertEqual(c["status"], "CANDIDATE")

    def test_decision_locked_fields(self):
        d: S.DecisionSupport = {
            "candidate_id": "CAND-20260522-0001",
            "system_recommendation": "REVIEW",
            "reason": "ok",
            "review_package_id": "REVPKG-20260522-0001",
            "evidence_packet_id": "EVID-20260522-0001",
            "weapon_control_link": "NOT_ALLOWED",
            "firing_data": "NOT_ALLOWED",
            "ballistic_calculation": "NOT_ALLOWED",
        }
        # 무기제어 관련 필드는 모두 NOT_ALLOWED 고정.
        self.assertEqual(d["weapon_control_link"], "NOT_ALLOWED")
        self.assertEqual(d["firing_data"], "NOT_ALLOWED")
        self.assertEqual(d["ballistic_calculation"], "NOT_ALLOWED")


if __name__ == "__main__":
    unittest.main()
