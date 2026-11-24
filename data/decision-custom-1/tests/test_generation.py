"""Generation invariants."""
from __future__ import annotations

import unittest
from collections import Counter

from decisiongen import config
from decisiongen.generator import build_records
from decisiongen.schema import norm_text, validate_record
from decisiongen.seeds_apps import APP_PATTERNS
from decisiongen.seeds_tools import SPECIAL_TOOLS, TOOLS
from decisiongen.seeds_tools_extra import SPECIAL_PATTERNS


class TestBuildRecords(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records, cls.metas = build_records()

    def test_totals(self) -> None:
        self.assertEqual(len(self.records), config.TOTAL)
        self.assertEqual(sum(m["kind"] == "tool" for m in self.metas),
                         config.TOOL_VALID + sum(config.TOOL_DECLINE.values()))
        self.assertEqual(sum(m["decline"] for m in self.metas),
                         config.GENERAL_DECLINE + sum(config.TOOL_DECLINE.values()))

    def test_schema(self) -> None:
        for i, rec in enumerate(self.records):
            self.assertEqual(validate_record(rec), [], f"record {i}")

    def test_unique_inputs(self) -> None:
        self.assertEqual(len({norm_text(r["input"]) for r in self.records}), len(self.records))

    def test_line_counts(self) -> None:
        counts = Counter(r["input"].count("\n") + 1 for r in self.records)
        self.assertEqual(dict(counts), config.LINE_COUNTS)

    def test_choice_counts(self) -> None:
        counts = Counter(len(r["choices"]) for r in self.records)
        self.assertEqual(dict(counts), config.CHOICE_COUNTS)

    def test_index_balance(self) -> None:
        for n in config.CHOICE_COUNTS:
            counts = Counter(
                m["answer"] for r, m in zip(self.records, self.metas)
                if not m["decline"] and len(r["choices"]) == n
            )
            vals = [counts[i] for i in range(n)]
            self.assertLessEqual(max(vals) - min(vals), 1, f"{n} choices: {vals}")

    def test_decline_answers(self) -> None:
        for r, m in zip(self.records, self.metas):
            if m["decline"]:
                self.assertEqual(m["answer"], -1)
                self.assertEqual(r["out"], [-1] * len(r["choices"]))

    def test_confidence_scores(self) -> None:
        for r, m in zip(self.records, self.metas):
            if m["decline"]:
                continue
            scores = r["out"]
            self.assertEqual(len(scores), len(r["choices"]))
            self.assertAlmostEqual(sum(scores), 1.0, places=6)
            self.assertEqual(max(range(len(scores)), key=lambda i: scores[i]), m["answer"])
            self.assertGreaterEqual(scores[m["answer"]], 0.5)

    def test_tool_answers(self) -> None:
        for r, m in zip(self.records, self.metas):
            if m["decline"] or m["kind"] != "tool":
                continue
            self.assertTrue(set(r["choices"]) <= set(TOOLS) | set(SPECIAL_TOOLS))
            if m["source_id"].startswith("tool:"):
                correct = m["source_id"].split(":", 1)[1]
            else:
                _, behavior, pi = m["source_id"].split(":")
                pats = [p for p in SPECIAL_PATTERNS if p["behavior"] == behavior]
                correct = pats[int(pi)]["correct"]
            self.assertEqual(r["choices"][m["answer"]], correct)

    def test_application_answers(self) -> None:
        for r, m in zip(self.records, self.metas):
            if not m["source_id"].startswith("app:"):
                continue
            _, domain, pi = m["source_id"].split(":")
            pats = [p for p in APP_PATTERNS if p["domain"] == domain]
            self.assertEqual(r["choices"][m["answer"]], pats[int(pi)]["correct"])
            self.assertEqual(len(r["choices"]), config.APPLICATION_CHOICES[domain])
            if domain == "binary":
                self.assertEqual(set(r["choices"]), {"true", "false"})

    def test_tool_behaviour_counts(self) -> None:
        counts = Counter(m["behavior"] for m in self.metas if m["kind"] == "tool" and not m["decline"])
        self.assertEqual(dict(counts), config.TOOL_BEHAVIOUR)

    def test_tool_decline_counts(self) -> None:
        counts = Counter(m["behavior"] for m in self.metas if m["kind"] == "tool" and m["decline"])
        self.assertEqual(dict(counts), {k: v for k, v in config.TOOL_DECLINE.items() if v})

    def test_general_domain_counts(self) -> None:
        counts = Counter(m["domain"] for m in self.metas if m["kind"] == "general")
        expected = {k: v[0] + v[1] for k, v in config.GENERAL.items()}
        expected.update(config.APPLICATIONS)
        self.assertEqual(dict(counts), expected)


if __name__ == "__main__":
    unittest.main()
