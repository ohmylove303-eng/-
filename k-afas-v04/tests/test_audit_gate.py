"""Audit Gate (L9) 테스트."""
import unittest
import tempfile
from pathlib import Path

from kafas.layers.audit_gate import evaluate_audit_gate
from kafas.layers.audit import append_audit_log


def _full_case() -> dict:
    return {
        "candidate": {"candidate_id": "C1"},
        "evidence":  {"packet_id": "E1"},
        "coord":     {"candidate_id": "C1"},
        "risk":      {"gate_result": "PASS"},
        "decision":  {"weapon_control_link": "NOT_ALLOWED"},
    }


class TestAuditGate(unittest.TestCase):
    def test_complete_case_pass(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "a.jsonl"
            append_audit_log(_full_case(), p)
            r = evaluate_audit_gate(_full_case(), log_path=p)
            self.assertEqual(r["gate_result"], "PASS")

    def test_missing_keys_reject(self):
        bad = {"candidate": {"candidate_id": "C1"}}
        r = evaluate_audit_gate(bad, log_path=None)
        self.assertEqual(r["gate_result"], "REJECT")
        self.assertIn("evidence", r["missing_keys"])

    def test_no_log_holds(self):
        r = evaluate_audit_gate(_full_case(), log_path=None)
        self.assertEqual(r["gate_result"], "HOLD")


if __name__ == "__main__":
    unittest.main()
