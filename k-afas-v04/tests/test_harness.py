"""하네스 6개 불변조건 검증."""
import unittest

from kafas.harness import (
    evaluate_case,
    invariant_goal_lock,
    invariant_option_set,
    invariant_semantic_collision,
    invariant_evidence_ledger,
    invariant_human_approval,
    invariant_weapon_separation,
)


def _good_case() -> dict:
    return {
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
        },
        "review": {
            "decision": "APPROVE_FOR_NEXT_REVIEW",
        },
    }



class TestHarness(unittest.TestCase):

    def test_I1_goal_lock_pass(self):
        v, _ = invariant_goal_lock(_good_case())
        self.assertEqual(v, "PASS")

    def test_I1_goal_lock_reject(self):
        case = _good_case()
        case["decision"]["firing_data"] = "ALLOWED"
        v, n = invariant_goal_lock(case)
        self.assertEqual(v, "REJECT")
        self.assertIn("firing_data", n)

    def test_I2_option_set_reject(self):
        v, _ = invariant_option_set({"HOLD", "REJECT"})  # 누락
        self.assertEqual(v, "REJECT")

    def test_I3_semantic_collision_reject(self):
        v, _ = invariant_semantic_collision("이건 자동사격 시나리오입니다")
        self.assertEqual(v, "REJECT")

    def test_I4_evidence_missing_source(self):
        case = _good_case()
        case["candidate"]["source_type"] = ""
        v, _ = invariant_evidence_ledger(case)
        self.assertEqual(v, "REJECT")

    def test_I5_human_required(self):
        case = _good_case()
        case["review"] = None
        v, _ = invariant_human_approval(case)
        self.assertEqual(v, "HOLD")

    def test_I6_weapon_policy_violation(self):
        case = _good_case()
        case["coord"]["coordinate_use_policy"] = "ALLOW_FIRING"
        v, _ = invariant_weapon_separation(case)
        self.assertEqual(v, "REJECT")

    def test_evaluate_case_pass(self):
        report = evaluate_case(_good_case(), text_corpus="ok")
        self.assertEqual(report.verdict, "PASS")

    def test_evaluate_case_reject_overrides_hold(self):
        case = _good_case()
        case["review"] = None  # HOLD
        case["decision"]["firing_data"] = "ALLOWED"  # REJECT
        r = evaluate_case(case)
        self.assertEqual(r.verdict, "REJECT")


if __name__ == "__main__":
    unittest.main()
