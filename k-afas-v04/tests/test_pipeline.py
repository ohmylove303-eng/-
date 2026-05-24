"""파이프라인 통합 시나리오 테스트."""
import unittest
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

from kafas.pipeline import KAFASPipeline

KST = timezone(timedelta(hours=9))


def _now_iso() -> str:
    return datetime.now(KST).isoformat(timespec="seconds")


class TestPipeline(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.audit = Path(self._tmp.name) / "audit.jsonl"
        self.p = KAFASPipeline(audit_path=str(self.audit))

    def tearDown(self):
        self._tmp.cleanup()

    def test_happy_path_pass(self):
        result = self.p.run(
            raw={"observed_at_kst": _now_iso(), "confidence_score": 0.85},
            source_type="uav_video",
            cep_meters=20.0,
            evidence_count=3,
            source_diversity="MULTI_SOURCE",
            analyst_summary="2 trucks (provisional)",
            civilian_risk="LOW",
            friendly_risk="LOW",
            roe_status="CLEAR",
            deconfliction_status="CLEAR",
            human_decision=("commander", "APPROVE_FOR_NEXT_REVIEW", "ok"),
        )
        self.assertEqual(result.status(), "PASS")
        self.assertTrue(self.audit.exists())



    def test_high_civilian_risk_rejects(self):
        result = self.p.run(
            raw={"observed_at_kst": _now_iso(), "confidence_score": 0.85},
            source_type="uav_video",
            cep_meters=20.0,
            evidence_count=2,
            source_diversity="MULTI_SOURCE",
            analyst_summary="ok",
            civilian_risk="HIGH",
            friendly_risk="LOW",
            roe_status="CLEAR",
            deconfliction_status="CLEAR",
            human_decision=None,
        )
        # 게이트가 REJECT이면 의사결정 권고도 REJECT,
        # 인간검토 부재 + 위험게이트 REJECT가 최종 REJECT를 만든다.
        self.assertEqual(result.status(), "REJECT")
        self.assertEqual(result.case["decision"]["system_recommendation"], "REJECT")

    def test_no_human_yields_hold(self):
        result = self.p.run(
            raw={"observed_at_kst": _now_iso(), "confidence_score": 0.85},
            source_type="uav_video",
            cep_meters=20.0,
            evidence_count=2,
            source_diversity="MULTI_SOURCE",
            analyst_summary="ok",
            civilian_risk="LOW",
            friendly_risk="LOW",
            roe_status="CLEAR",
            deconfliction_status="CLEAR",
            human_decision=None,
        )
        self.assertEqual(result.halted_at, "awaiting_human_review")

    def test_aar_submission(self):
        r = self.p.run(
            raw={"observed_at_kst": _now_iso(), "confidence_score": 0.85},
            source_type="uav_video",
            cep_meters=20.0,
            evidence_count=2,
            source_diversity="MULTI_SOURCE",
            analyst_summary="ok",
            civilian_risk="LOW", friendly_risk="LOW",
            roe_status="CLEAR", deconfliction_status="CLEAR",
            human_decision=("commander", "APPROVE_FOR_NEXT_REVIEW", "ok"),
        )
        aar = self.p.submit_aar(r.case, "CONFIRMED")
        self.assertFalse(aar["model_update_allowed"])
        self.assertTrue(aar["audit_replay_required"])


if __name__ == "__main__":
    unittest.main()
