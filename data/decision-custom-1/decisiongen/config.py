"""Dataset configuration. Keep this deterministic and dependency-free."""
from __future__ import annotations

SEED = 20261124
TOTAL = 1_010_000
BATCH_SIZE = 10_000
VERSION = "2.0.0"

# Top-level slices (101 files x 10,000 records)
GENERAL_VALID = 656_500
GENERAL_DECLINE = 101_000
TOOL_VALID = 202_000
TOOL_DECLINE = 50_500

# Real-world application decisions carved out of GENERAL_VALID.
# Each forces its own choice count: binary=2, animation=8, home_control=10.
APPLICATIONS = {
    "binary": 50_000,
    "animation": 40_000,
    "home_control": 60_000,
}
APPLICATION_CHOICES = {"binary": 2, "animation": 8, "home_control": 10}

# General category -> (valid, decline). Valid totals exclude APPLICATIONS.
GENERAL = {
    "social": (88_832, 6_060),
    "everyday": (78_702, 9_090),
    "work": (77_144, 11_110),
    "health": (48_312, 18_180),
    "money": (49_871, 16_160),
    "travel": (49_092, 7_070),
    "learning": (48_312, 8_080),
    "communication": (39_741, 9_090),
    "ethics": (26_494, 16_160),
}

# Valid tool domain quotas for direct routing (161.6k; specials add 40.4k).
TOOL_DOMAINS = {
    "calendar_email": 25_856,
    "search_web": 19_392,
    "files_code": 19_392,
    "shopping_payments": 19_392,
    "travel_maps": 16_160,
    "messaging": 12_928,
    "data_crm": 12_928,
    "smart_home": 9_696,
    "health": 6_464,
    "productivity": 6_464,
    "other": 12_928,
}

# Tool behaviour quotas (202k)
TOOL_BEHAVIOUR = {
    "direct": 161_600,
    "clarify_confirm": 20_200,
    "read_only": 10_100,
    "multi_step": 10_100,
}

# Tool decline reason quotas (50.5k)
TOOL_DECLINE = {
    "unsafe_destructive": 15_150,
    "missing_args": 12_120,
    "no_suitable_tool": 8_080,
    "policy_privacy": 7_070,
    "ambiguous": 5_050,
    "already_done": 3_030,
}

# Line counts: 1, 2, 3
LINE_COUNTS = {1: 505_000, 2: 303_000, 3: 202_000}

# Choice counts: 2 (true/false), 3-6, 8 (animations), 10 (home actions)
CHOICE_COUNTS = {2: 50_000, 3: 101_000, 4: 557_000, 5: 151_500,
                 6: 50_500, 8: 40_000, 10: 60_000}

MAX_PER_CARD = 4_000
MAX_PER_TOOL = 5_000
MAX_PER_SPECIAL = 5_000

# Audit splits are card/tool-disjoint. Kept small and report-only.
SPLIT_VAL = 20_000
SPLIT_TEST = 20_000

FORMAT = "jsonl"
