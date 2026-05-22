"""금지 표현 정규식 강화 테스트 (우회 시도 차단 회귀)."""
import unittest

from kafas.harness import invariant_semantic_collision


class TestForbiddenStrict(unittest.TestCase):
    def test_space_bypass_blocked(self):
        v, _ = invariant_semantic_collision("kill   chain plan")
        self.assertEqual(v, "REJECT")

    def test_punct_bypass_blocked(self):
        v, _ = invariant_semantic_collision("fire,command panel")
        self.assertEqual(v, "REJECT")

    def test_case_bypass_blocked(self):
        v, _ = invariant_semantic_collision("AUTO sa-Geuk")  # 자동사격 우회 X
        # 한국어 자모 분리는 다루지 않음. 영어 케이스 변형만 확인.
        v2, _ = invariant_semantic_collision("Autonomous   FIRE")
        self.assertEqual(v2, "REJECT")

    def test_korean_no_space_blocked(self):
        v, _ = invariant_semantic_collision("이건 발사명령 패널이다")
        self.assertEqual(v, "REJECT")

    def test_safe_text_pass(self):
        v, _ = invariant_semantic_collision("trucks observed by UAV; review queued")
        self.assertEqual(v, "PASS")


if __name__ == "__main__":
    unittest.main()
