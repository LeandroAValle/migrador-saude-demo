import unittest

from health_demo.pipeline import WriteGuardError, build_snapshot, ensure_writable


class PipelineTests(unittest.TestCase):
    def test_read_only_environment_blocks_operation(self):
        with self.assertRaises(WriteGuardError):
            ensure_writable("production")
        with self.assertRaises(WriteGuardError):
            build_snapshot("production")

    def test_deterministic_and_reconciled(self):
        first, second = build_snapshot(), build_snapshot()
        self.assertEqual(first, second)
        self.assertEqual(first["metrics"]["total"], first["metrics"]["success"] + first["metrics"]["errors"])
        self.assertEqual(first["metrics"]["total"], sum(item["total"] for item in first["byService"]))

    def test_pending_or_sent_is_never_final_success(self):
        for record in build_snapshot()["control"]:
            if record["status"] == "SUCESSO":
                self.assertEqual("SUCESSO", record["history"][-1])
                self.assertIn("ENVIADO", record["history"])
            if not record["payloadPrepared"]:
                self.assertNotIn("ENVIADO", record["history"])


if __name__ == "__main__":
    unittest.main()
