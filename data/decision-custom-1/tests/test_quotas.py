"""Quota helper tests."""
from __future__ import annotations

import unittest

from decisiongen.quotas import largest_remainder, split_counts


class TestQuotas(unittest.TestCase):
    def test_largest_remainder_exact(self) -> None:
        got = largest_remainder(100, {"a": 1, "b": 1, "c": 1})
        self.assertEqual(sum(got.values()), 100)
        self.assertLessEqual(max(got.values()) - min(got.values()), 1)

    def test_largest_remainder_weighted(self) -> None:
        got = largest_remainder(1_000, {"a": 3, "b": 2, "c": 5})
        self.assertEqual(sum(got.values()), 1_000)
        self.assertEqual(got, {"a": 300, "b": 200, "c": 500})

    def test_split_counts(self) -> None:
        got = split_counts(10, ["a", "b", "c"])
        self.assertEqual(sum(got.values()), 10)
        self.assertEqual(got["a"], 4)
        self.assertEqual(got["b"], 3)
        self.assertEqual(got["c"], 3)


if __name__ == "__main__":
    unittest.main()
