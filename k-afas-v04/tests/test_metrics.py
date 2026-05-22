"""KPI 측정 모듈 테스트."""
import unittest

from kafas.metrics import MetricsAggregator, time_to_review_ready


class TestMetrics(unittest.TestCase):
    def test_ttrr_basic(self):
        t = time_to_review_ready(
            "2026-05-22T10:00:00+09:00",
            "2026-05-22T10:00:42+09:00",
        )
        self.assertEqual(t, 42.0)

    def test_aggregator_report(self):
        agg = MetricsAggregator()
        agg.record(
            "2026-05-22T10:00:00+09:00",
            "2026-05-22T10:00:30+09:00",
            "PASS", True,
        )
        agg.record(
            "2026-05-22T10:00:00+09:00",
            "2026-05-22T10:01:00+09:00",
            "HOLD", True,
        )
        rep = agg.report()
        self.assertEqual(rep["candidates_total"], 2)
        self.assertEqual(rep["passed_to_review"], 1)
        self.assertEqual(rep["held"], 1)
        self.assertEqual(rep["audit_completeness"], 1.0)
        self.assertGreater(rep["ttrr_p95_sec"], 30)


if __name__ == "__main__":
    unittest.main()
