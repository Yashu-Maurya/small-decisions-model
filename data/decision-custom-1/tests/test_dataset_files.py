"""End-to-end file writing and validation."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from decisiongen import config
from decisiongen.generator import build_records, write_dataset
from decisiongen.validate import validate


class TestDatasetFiles(unittest.TestCase):
    def test_write_and_validate(self) -> None:
        records, metas = build_records()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "dataset"
            manifest = write_dataset(out, records, metas)
            self.assertEqual(manifest["totals"]["records"], config.TOTAL)
            self.assertEqual(len(manifest["files"]), config.TOTAL // config.BATCH_SIZE)
            for entry in manifest["files"]:
                self.assertEqual(entry["records"], config.BATCH_SIZE)
                self.assertEqual(entry["counts"], {
                    "general_valid": 6_500,
                    "general_decline": 1_000,
                    "tool_valid": 2_000,
                    "tool_decline": 500,
                })
            result = validate(out, deep=False, write=False)
            self.assertEqual(result["status"], "passed", result["errors"])


if __name__ == "__main__":
    unittest.main()
