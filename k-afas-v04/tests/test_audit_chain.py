"""감사로그 SHA-256 해시체인 무결성 테스트."""
import unittest
import tempfile
from pathlib import Path

from kafas.layers.audit import append_audit_log, verify_audit_chain


class TestAuditChain(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.log = Path(self._tmp.name) / "audit.jsonl"

    def tearDown(self):
        self._tmp.cleanup()

    def _case(self, cid: str) -> dict:
        return {"candidate": {"candidate_id": cid}}

    def test_chain_ok_after_multiple_appends(self):
        for i in range(5):
            append_audit_log(self._case(f"C{i}"), self.log)
        ok, reason = verify_audit_chain(self.log)
        self.assertTrue(ok, msg=reason)

    def test_chain_detects_tampering(self):
        for i in range(3):
            append_audit_log(self._case(f"C{i}"), self.log)
        # 의도적 변조: 두 번째 라인의 case 내용을 바꿔치기.
        lines = self.log.read_text(encoding="utf-8").splitlines()
        lines[1] = lines[1].replace("C1", "X1")
        self.log.write_text("\n".join(lines) + "\n", encoding="utf-8")
        ok, reason = verify_audit_chain(self.log)
        self.assertFalse(ok)
        self.assertIn("hash_mismatch", reason)


if __name__ == "__main__":
    unittest.main()
