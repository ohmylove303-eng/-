"""Runtime dict 검증기 테스트."""
import unittest

from kafas.validators import (
    ValidationError, validate_candidate, validate_decision,
    validate_coord, validate_case,
)


class TestValidators(unittest.TestCase):
    def test_candidate_missing_field(self):
        with self.assertRaises(ValidationError):
            validate_candidate({"candidate_id": "C1"})

    def test_decision_locked_field_violation(self):
        with self.assertRaises(ValidationError):
            validate_decision({
                "weapon_control_link": "ALLOWED",
                "firing_data": "NOT_ALLOWED",
                "ballistic_calculation": "NOT_ALLOWED",
            })

    def test_coord_policy_locked(self):
        with self.assertRaises(ValidationError):
            validate_coord({"coordinate_use_policy": "ALLOW_FIRING"})

    def test_validate_case_skips_when_missing(self):
        # 빈 case는 통과 (각 키는 옵셔널).
        validate_case({})


if __name__ == "__main__":
    unittest.main()
