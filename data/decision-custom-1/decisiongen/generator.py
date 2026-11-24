"""Deterministic dataset generator."""
from __future__ import annotations

import hashlib
import json
import math
import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import config
from .lexicon import DECLINE, NAMES, PLACES, QUESTIONS, RELATIONS, TIMES, WRONG
from .quotas import largest_remainder, split_counts
from .schema import norm_text, validate_record
from .seeds_decline import DECLINE_CARDS
from .seeds_general import PATTERNS
from .seeds_apps import (ANIMATIONS, APP_DEFAULT_SLOTS, APP_PATTERNS,
                         BINARY_FALSE, BINARY_TRUE, HOME_ACTIONS)
from .seeds_tools import SPECIAL_TOOLS, TOOLS
from .seeds_tools_extra import POLICIES, SPECIAL_PATTERNS, TOOL_DECLINE_PATTERNS

PH = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")
DEFAULT_SLOTS = {"name": NAMES, "time": TIMES, "place": PLACES, "relation": RELATIONS}
CTX_TIMES = [
    "Monday morning", "Monday afternoon", "Tuesday morning", "Tuesday evening",
    "Wednesday afternoon", "Thursday morning", "Friday afternoon", "Saturday morning",
    "Sunday afternoon", "just after lunch", "around noon", "before work", "after work",
    "rush hour", "the end of the day", "first thing in the morning", "the weekend",
]
CTX = 4 * len(NAMES) * len(PLACES) * len(CTX_TIMES)
ROOM_PLACES = {
    "the kitchen", "the living room", "the break room", "the bedroom", "the bathroom",
    "the hallway", "the garage", "the dining room", "the basement", "the copy room",
    "the conference room", "the waiting room", "the lobby",
}

def _where(place: str) -> str:
    return ("in " if place in ROOM_PLACES else "at ") + place


def _user_text(request: str, context: str) -> str:
    """Turn a tool request plus context into a first-person user message."""
    q = " ".join(request.split())
    if q.endswith("?"):
        body = q
    elif q.startswith(("I ", "The ", "My ", "We ")):
        body = q
    elif q.startswith("At ") and "," in q:
        head, rest = q.split(",", 1)
        core = rest.strip().rstrip(".")
        body = f"Can you {core[0].lower()}{core[1:]} {head[3:].strip()}?"
    else:
        core = q.rstrip(".")
        body = f"Can you {core[0].lower()}{core[1:]}?"
    return f"{body} {context}"

def _ctx(index: int):
    style = index % 4; index //= 4
    name = NAMES[index % len(NAMES)]; index //= len(NAMES)
    place = PLACES[index % len(PLACES)]; index //= len(PLACES)
    when = CTX_TIMES[index % len(CTX_TIMES)]; index //= len(CTX_TIMES)
    return style, {"name": name, "place": place, "time": when}, index

@dataclass
class Card:
    id: str
    domain: str
    kind: str
    pairs: list[tuple[str, str]]
    questions: list[str]
    best: list[str]
    wrong: list[str]
    wrong_extra: list[str]
    slots: dict[str, list[str]]
    capacity: int = 0
    space: int = 0

    @property
    def source_id(self) -> str:
        return f"card:{self.id}"


@dataclass
class Raw:
    source_id: str
    kind: str
    domain: str
    text1: str
    text2: str
    question: str
    best: list[str] = field(default_factory=list)
    wrong: list[str] = field(default_factory=list)
    reason: str = ""
    behavior: str = ""
    tool: str = ""
    policy: str = ""
    context: str = ""
    answer: int = -1


def _slots(card: Card) -> dict[str, list[str]]:
    used: set[str] = set()
    for a, b in card.pairs:
        used.update(PH.findall(a + b))
    for q in card.questions:
        used.update(PH.findall(q))
    for t in card.best + card.wrong_extra:
        used.update(PH.findall(t))
    out: dict[str, list[str]] = {}
    for k in sorted(used):
        pool = card.slots.get(k) or DEFAULT_SLOTS.get(k)
        if not pool:
            raise ValueError(f"{card.id}: no slot pool for {{{k}}}")
        out[k] = list(pool) if not isinstance(pool, str) else [pool]
    return out


def _placeholders(texts: list[str]) -> list[str]:
    used: set[str] = set()
    for t in texts:
        used.update(PH.findall(t))
    return sorted(used)


def _capacity(pairs, questions, texts, slots) -> int:
    keys = _placeholders([a + b for a, b in pairs] + list(questions) + list(texts))
    n = len(pairs) * len(questions)
    for k in keys:
        pool = slots.get(k) or DEFAULT_SLOTS.get(k)
        if not pool:
            raise ValueError(f"missing slot {k}")
        n *= len(pool)
    return n


def build_cards() -> list[Card]:
    cards: list[Card] = []
    for p in PATTERNS:
        for i, row in enumerate(p["rows"]):
            slots = dict(p.get("slots", {}))
            for k, v in row.get("slots", {}).items():
                slots[k] = [v] if isinstance(v, str) else list(v)
            best = row.get("best", [])
            best = [best] if isinstance(best, str) else list(best)
            wrong = row.get("wrong", p["wrong"])
            wrong = [wrong] if isinstance(wrong, str) else list(wrong)
            extra = row.get("wrong_extra", [])
            extra = [extra] if isinstance(extra, str) else list(extra)
            c = Card(
                id=f"{p['id']}-{i:02d}", domain=row.get("domain", p["domain"]),
                kind="valid", pairs=p["clauses"], questions=p["questions"],
                best=best, wrong=wrong, wrong_extra=extra, slots=slots,
            )
            cap = _capacity(c.pairs, c.questions, c.best + c.wrong_extra, c.slots)
            c.space = cap
            c.capacity = min(config.MAX_PER_CARD, cap)
            cards.append(c)
    for i, d in enumerate(DECLINE_CARDS):
        c = Card(
            id=f"decline-{i:02d}", domain=d["domain"], kind="decline",
            pairs=d["pairs"], questions=d["questions"], best=[],
            wrong=[d["pool"]], wrong_extra=[], slots={"place": d["places"]},
        )
        cap = _capacity(c.pairs, c.questions, [], c.slots)
        c.space = cap
        c.capacity = min(config.MAX_PER_CARD, cap)
        cards.append(c)
    return cards


def _alloc(total: int, cards: list[Card], seed: str) -> dict[str, int]:
    caps = sum(c.capacity for c in cards)
    if total > caps:
        raise ValueError(f"capacity {caps} < needed {total} for {seed}")
    cards = list(cards)
    random.Random(seed).shuffle(cards)
    out = {c.id: 0 for c in cards}
    left = total
    i = 0
    while left:
        c = cards[i % len(cards)]
        if out[c.id] < c.capacity:
            out[c.id] += 1
            left -= 1
        i += 1
    return out


def _render(t: str, slots: dict[str, str]) -> str:
    return t.format_map(slots)


def _looks_first_person(text: str) -> bool:
    return bool(re.search(r"\b(I|I'm|I've|I'll|my|My)\b", text)) and not bool(
        re.search(r"\b(you|your|You|Your)\b", text)
    )


def _first_person_question(q: str) -> str:
    q = q.replace("What would you do?", "What should I do?")
    q = re.sub(r"\bYou're\b", "I'm", q)
    q = re.sub(r"\bYour\b", "My", q)
    q = re.sub(r"\bYou\b", "I", q)
    q = re.sub(r"\byour\b", "my", q)
    q = re.sub(r"\byou\b", "I", q)
    return q


def _decode(idx: int, pairs, questions, pools: list[tuple[str, list[str]]]):
    slots: dict[str, str] = {}
    for name, pool in pools:
        slots[name] = pool[idx % len(pool)]
        idx //= len(pool)
    pair = idx % len(pairs)
    idx //= len(pairs)
    q = idx % len(questions)
    return pair, q, slots


def _general_raw(seen: set[str]) -> list[Raw]:
    cards = build_cards()
    by_cat: dict[str, list[Card]] = {}
    for c in cards:
        by_cat.setdefault(c.domain, []).append(c)
    alloc: dict[str, int] = {}
    for cat, (total, decline) in config.GENERAL.items():
        valid_cards = [c for c in by_cat.get(cat, []) if c.kind == "valid"]
        decline_cards = [c for c in by_cat.get(cat, []) if c.kind == "decline"]
        if not valid_cards or not decline_cards:
            raise ValueError(f"{cat}: missing valid or decline cards")
        alloc.update(_alloc(total, valid_cards, f"alloc:{cat}:valid"))
        alloc.update(_alloc(decline, decline_cards, f"alloc:{cat}:decline"))

    raws: list[Raw] = []
    for c in cards:
        n = alloc.get(c.id, 0)
        if not n:
            continue
        pools = list(_slots(c).items())
        if n > c.capacity:
            raise ValueError(f"{c.id}: {n}>{c.capacity}")
        rng = random.Random(f"{config.SEED}:{c.id}")
        used: set[int] = set()
        count = attempts = 0
        while count < n:
            if attempts > n * 200:
                raise ValueError(f"{c.id}: exhausted unique texts ({count}/{n})")
            idx = rng.randrange(c.space)
            attempts += 1
            if idx in used:
                continue
            used.add(idx)
            pair_i, q_i, slots = _decode(idx, c.pairs, c.questions, pools)
            a, b = c.pairs[pair_i]
            t1, t2, tq = _render(a, slots), _render(b, slots), _render(c.questions[q_i], slots)
            if _looks_first_person(f"{t1} {t2}"):
                tq = _first_person_question(tq)
            core = norm_text(f"{t1} {t2} {tq}")
            if core in seen:
                continue
            seen.add(core)
            best = [_render(t, slots) for t in c.best]
            wrong: list[str] = []
            for key in c.wrong:
                pool = WRONG.get(key) if c.kind == "valid" else DECLINE.get(key)
                if pool is None:
                    raise ValueError(f"{c.id}: unknown pool {key}")
                wrong.extend(pool)
            wrong.extend(_render(t, slots) for t in c.wrong_extra)
            reason = c.wrong[0] if c.kind == "decline" else ""
            raws.append(Raw(
                source_id=c.source_id, kind=c.kind, domain=c.domain,
                text1=t1, text2=t2, question=tq, best=best,
                wrong=wrong, reason=reason,
            ))
            count += 1
    return raws


def _tool_name_pools() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for name, t in TOOLS.items():
        out.setdefault(t["domain"], []).append(name)
    return out


def _tool_space(t: dict[str, Any]) -> int:
    reqs = t["requests"]
    keys = _placeholders(reqs)
    n = len(reqs)
    for k in keys:
        pool = t["slots"].get(k)
        if not pool:
            raise ValueError(f"tool missing slot {k}")
        n *= len(pool)
    return n


def _direct_tool_raw(seen: set[str]) -> list[Raw]:
    domain_tools = _tool_name_pools()
    spaces = {n: _tool_space(t) for n, t in TOOLS.items()}
    caps = {n: min(config.MAX_PER_TOOL, spaces[n] * CTX) for n in TOOLS}
    alloc: dict[str, int] = {}
    for dom, total in config.TOOL_DOMAINS.items():
        names = domain_tools.get(dom, [])
        if not names:
            raise ValueError(f"no tools for {dom}")
        caps_sum = sum(caps[n] for n in names)
        if total > caps_sum:
            raise ValueError(f"{dom}: capacity {caps_sum} < {total}")
        random.Random(f"{config.SEED}:toolalloc:{dom}").shuffle(names)
        left = total
        i = 0
        while left:
            n = names[i % len(names)]
            if alloc.get(n, 0) < caps[n]:
                alloc[n] = alloc.get(n, 0) + 1
                left -= 1
            i += 1

    raws: list[Raw] = []
    for name, t in TOOLS.items():
        n = alloc.get(name, 0)
        if not n:
            continue
        reqs = t["requests"]
        pools = [(k, list(t["slots"][k])) for k in _placeholders(reqs)]
        rng = random.Random(f"{config.SEED}:tool:{name}")
        count = attempts = 0
        while count < n:
            raw_idx = rng.randrange(spaces[name] * CTX)
            style, ctx, idx = _ctx(raw_idx)
            ri = idx % len(reqs)
            idx //= len(reqs)
            slots: dict[str, str] = {}
            for k, pool in pools:
                slots[k] = pool[idx % len(pool)]
                idx //= len(pool)
            if "city1" in slots and "city2" in slots and slots["city1"] == slots["city2"]:
                slots["city2"] = next(c for c in t["slots"]["city2"] if c != slots["city1"])
            request = _render(reqs[ri], slots)
            context = f"I'm {ctx['name']}, and I'm {_where(ctx['place'])}. It's {ctx['time']} here."
            core = norm_text(request + " " + context)
            attempts += 1
            if core in seen:
                if attempts > n * 200:
                    raise ValueError(f"tool:{name}: exhausted unique texts")
                continue
            seen.add(core)
            raws.append(Raw(
                source_id=f"tool:{name}", kind="valid", domain=t["domain"],
                text1=request, text2="", question="", tool=name, behavior="direct",
                context=context,
            ))
            count += 1
    return raws


def _pattern_space(p) -> int:
    keys = _placeholders([p["request"]])
    return math.prod(len(p["slots"][k]) for k in keys)

def _alloc_patterns(total: int, pats: list[dict], seed: str) -> list[int]:
    caps = [min(config.MAX_PER_SPECIAL, _pattern_space(p) * CTX) for p in pats]
    if total > sum(caps):
        raise ValueError(f"pattern capacity {sum(caps)} < {total} for {seed}")
    out = [0] * len(pats)
    i = 0
    left = total
    while left:
        j = i % len(pats)
        if out[j] < caps[j]:
            out[j] += 1
            left -= 1
        i += 1
    return out

def _special_raw(behavior: str, total: int, seen: set[str]) -> list[Raw]:
    pats = [p for p in SPECIAL_PATTERNS if p["behavior"] == behavior]
    if not pats:
        raise ValueError(f"no patterns for {behavior}")
    counts = _alloc_patterns(total, pats, behavior)
    raws: list[Raw] = []
    for pi, p in enumerate(pats):
        n = counts[pi]
        if not n:
            continue
        keys = _placeholders([p["request"]])
        pools = [(k, list(p["slots"][k])) for k in keys]
        space = _pattern_space(p)
        rng = random.Random(f"{config.SEED}:special:{behavior}:{pi}")
        count = attempts = 0
        while count < n:
            raw_idx = rng.randrange(space * CTX)
            style, ctx, idx = _ctx(raw_idx)
            slots = {}
            for k, pool in pools:
                slots[k] = pool[idx % len(pool)]
                idx //= len(pool)
            request = _render(p["request"], slots)
            context = f"I'm {ctx['name']}, and I'm {_where(ctx['place'])}. It's {ctx['time']} here."
            core = norm_text(request + " " + context)
            attempts += 1
            if core in seen:
                if attempts > n * 200:
                    raise ValueError(f"special:{behavior}:{pi}: exhausted unique texts")
                continue
            seen.add(core)
            raws.append(Raw(
                source_id=f"special:{behavior}:{pi}", kind="valid", domain="tool",
                text1=request, text2="", question="",
                tool=p["correct"], behavior=behavior, wrong=p["tools"],
                policy=p.get("policy") or "", context=context,
            ))
            count += 1
    return raws


def _tool_decline_raw(seen: set[str]) -> list[Raw]:
    raws: list[Raw] = []
    for reason, total in config.TOOL_DECLINE.items():
        pats = [p for p in TOOL_DECLINE_PATTERNS if p["reason"] == reason]
        if not pats:
            raise ValueError(f"no decline patterns for {reason}")
        counts = _alloc_patterns(total, pats, reason)
        for pi, p in enumerate(pats):
            n = counts[pi]
            if not n:
                continue
            keys = _placeholders([p["request"]])
            pools = [(k, list(p["slots"][k])) for k in keys]
            space = _pattern_space(p)
            rng = random.Random(f"{config.SEED}:tooldecline:{reason}:{pi}")
            count = attempts = 0
            while count < n:
                raw_idx = rng.randrange(space * CTX)
                style, ctx, idx = _ctx(raw_idx)
                slots = {}
                for k, pool in pools:
                    slots[k] = pool[idx % len(pool)]
                    idx //= len(pool)
                request = _render(p["request"], slots)
                context = f"I'm {ctx['name']}, and I'm {_where(ctx['place'])}. It's {ctx['time']} here."
                core = norm_text(request + " " + context)
                attempts += 1
                if core in seen:
                    if attempts > n * 200:
                        raise ValueError(f"tooldecline:{reason}:{pi}: exhausted unique texts")
                    continue
                seen.add(core)
                raws.append(Raw(
                    source_id=f"tooldecline:{reason}:{pi}", kind="decline", domain="tool",
                    text1=request, text2="", question="",
                    tool="", behavior=reason, wrong=p["tools"],
                    reason=reason, policy=p.get("policy") or "", context=context,
                ))
                count += 1
    return raws


APP_DESCS = {
    **{k: v["desc"] for k, v in TOOLS.items()},
    **{k: v["desc"] for k, v in SPECIAL_TOOLS.items()},
    **HOME_ACTIONS,
    **ANIMATIONS,
}


def _catalog(choices: list[str]) -> str:
    bits = []
    for c in choices:
        d = APP_DESCS[c]
        bits.append(f"{c} ({d})")
    return "; ".join(bits)


def _app_raw(seen: set[str]) -> list[Raw]:
    """Generate home-control, animation and binary classification records."""
    raws: list[Raw] = []
    for domain, total in config.APPLICATIONS.items():
        pats = [p for p in APP_PATTERNS if p["domain"] == domain]
        caps, spaces = [], []
        for p in pats:
            keys = _placeholders([p["template"], p.get("question") or ""])
            space = 1
            for k in keys:
                pool = p["slots"].get(k) or APP_DEFAULT_SLOTS.get(k)
                if not pool:
                    raise ValueError(f"app {domain}: missing slot {k}")
                space *= len(pool)
            spaces.append(space)
            caps.append(min(config.MAX_PER_SPECIAL, space))
        if total > sum(caps):
            raise ValueError(f"app {domain}: capacity {sum(caps)} < {total}")
        counts = _alloc_capped(total, caps, f"app:{domain}")

        if domain == "home_control":
            all_choices = list(HOME_ACTIONS)
        elif domain == "animation":
            all_choices = list(ANIMATIONS)
        else:
            all_choices = [BINARY_TRUE, BINARY_FALSE]

        for pi, (p, n, space) in enumerate(zip(pats, counts, spaces)):
            if not n:
                continue
            keys = _placeholders([p["template"], p.get("question") or ""])
            pools = [(k, list(p["slots"].get(k) or APP_DEFAULT_SLOTS[k])) for k in keys]
            rng = random.Random(f"{config.SEED}:app:{domain}:{pi}")
            used: set[int] = set()
            count = attempts = 0
            while count < n:
                idx = rng.randrange(space)
                attempts += 1
                if idx in used:
                    if attempts > n * 200:
                        raise ValueError(f"app {domain}:{pi}: exhausted unique slots")
                    continue
                used.add(idx)
                slots: dict[str, str] = {}
                for k, pool in pools:
                    slots[k] = pool[idx % len(pool)]
                    idx //= len(pool)
                text = _render(p["template"], slots)
                if domain == "animation" and _looks_first_person(text):
                    q = "Which animation should I use?"
                elif domain == "animation":
                    q = "Which animation should you use?"
                elif domain == "home_control":
                    q = "Which action should I take?"
                else:
                    q = _render(p["question"], slots)
                core = norm_text(f"{text} {q}")
                if core in seen:
                    if attempts > n * 200:
                        raise ValueError(f"app {domain}:{pi}: exhausted unique texts")
                    continue
                seen.add(core)
                correct = p["correct"]
                raws.append(Raw(
                    source_id=f"app:{domain}:{pi}", kind="valid", domain=domain,
                    text1=text, text2="", question=q, best=[correct],
                    wrong=[c for c in all_choices if c != correct],
                ))
                count += 1
    return raws


def _alloc_capped(total: int, caps: list[int], seed: str) -> list[int]:
    out = [0] * len(caps)
    rng = random.Random(seed)
    order = list(range(len(caps)))
    rng.shuffle(order)
    left = total
    i = 0
    while left:
        j = order[i % len(order)]
        if out[j] < caps[j]:
            out[j] += 1
            left -= 1
        i += 1
    return out


def _format_general(r: Raw, line: int) -> str:
    a, b, q = r.text1, r.text2, r.question
    if line == 1:
        s = f"{a} {b} {q}"
    elif line == 2:
        s = f"{a} {b}\n{q}"
    else:
        s = f"{a}\n{b}\n{q}"
    return "\n".join(" ".join(x.split()) for x in s.split("\n"))


def _format_tool(r: Raw, line: int, policy: str, choices: list[str]) -> str:
    cat = _catalog(choices)
    user = _user_text(r.text1, r.context)
    if line == 1:
        s = f"User: {user} Tools: {cat}"
    elif line == 2:
        s = f"User: {user}\nTools: {cat}"
    else:
        s = f"Policy: {policy}\nUser: {user}\nTools: {cat}"
    return "\n".join(" ".join(x.split()) for x in s.split("\n"))


def _format_app(r: Raw, line: int) -> str:
    body = f"{r.text1} {r.question}"
    if r.domain == "home_control":
        label, cat = "Actions", _catalog(list(HOME_ACTIONS))
    elif r.domain == "animation":
        label, cat = "Animations", _catalog(list(ANIMATIONS))
    else:
        label, cat = "Options", "true (yes) | false (no)"
    if line == 1:
        s = f"User: {body} {label}: {cat}"
    elif line == 2:
        s = f"User: {body}\n{label}: {cat}"
    else:
        s = f"User: {r.text1}\n{r.question}\n{label}: {cat}"
    return "\n".join(" ".join(x.split()) for x in s.split("\n"))


def _confidence(target: int, n: int, rng: random.Random) -> list[float]:
    """Integer weights summing to 10,000 -> four-decimal confidence scores."""
    if target == -1:
        return [-1] * n
    top = rng.randint(8200, 9700)
    rest = 10000 - top
    others = [i for i in range(n) if i != target]
    floor = 10
    spare = rest - floor * len(others)
    cuts = sorted(rng.randint(0, spare) for _ in range(len(others) - 1))
    parts: list[int] = []
    prev = 0
    for cut in cuts:
        parts.append(cut - prev + floor)
        prev = cut
    parts.append(spare - prev + floor)
    weights = [0] * n
    weights[target] = top
    for i, part in zip(others, parts):
        weights[i] = part
    assert sum(weights) == 10000
    return [round(w / 10000, 4) for w in weights]


def _make_choices(r: Raw, n: int, target: int | None, rng: random.Random) -> tuple[list[str], int]:
    if r.kind == "decline":
        pool = list(dict.fromkeys(r.wrong))
        if len(pool) < n:
            raise ValueError(f"not enough decline choices {r.source_id}")
        return rng.sample(pool, n), -1
    assert target is not None
    if r.tool or r.domain == "tool":
        correct = r.tool
        pool = list(dict.fromkeys([x for x in r.wrong if x != correct]))
        # Special patterns carry their own candidate list; direct tools use all tools.
        if not r.wrong:
            pool = [x for x in TOOLS if x != correct]
        rng.shuffle(pool)
        need = n - 1
        if len(pool) < need:
            extra = [x for x in TOOLS if x != correct and x not in pool]
            pool.extend(extra)
        choices = [correct] + pool[:need]
        rng.shuffle(choices)
        # Ensure the correct tool is at the requested target.
        i = choices.index(correct)
        choices[i], choices[target] = choices[target], choices[i]
        return choices, target
    best = rng.choice(r.best)
    pool = list(dict.fromkeys([x for x in r.wrong if norm_text(x) != norm_text(best)]))
    rng.shuffle(pool)
    if len(pool) < n - 1:
        raise ValueError(f"not enough wrong choices {r.source_id}")
    choices = [best] + pool[: n - 1]
    rng.shuffle(choices)
    i = choices.index(best)
    choices[i], choices[target] = choices[target], choices[i]
    return choices, target


def _balance_indices(total: int, n: int) -> list[int]:
    base, rem = divmod(total, n)
    out = []
    for i in range(n):
        out.extend([i] * (base + (1 if i < rem else 0)))
    return out


def _split_groups(raws: list[Raw], metas: list[dict[str, Any]]) -> None:
    groups: dict[str, int] = {}
    for m in metas:
        groups[m["source_id"]] = groups.get(m["source_id"], 0) + 1
    items = list(groups.items())
    random.Random(f"{config.SEED}:split").shuffle(items)
    val, test = [], []
    vc = tc = 0
    for sid, count in items:
        if vc < config.SPLIT_VAL:
            val.append(sid); vc += count
        elif tc < config.SPLIT_TEST:
            test.append(sid); tc += count
    split = {sid: "train" for sid, _ in items}
    for sid in val:
        split[sid] = "val"
    for sid in test:
        split[sid] = "test"
    for m in metas:
        m["split"] = split[m["source_id"]]


def build_records() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    seen: set[str] = set()
    general = _general_raw(seen)
    apps = _app_raw(seen)
    tools = _direct_tool_raw(seen) + _special_raw("clarify_confirm", config.TOOL_BEHAVIOUR["clarify_confirm"], seen)
    tools += _special_raw("read_only", config.TOOL_BEHAVIOUR["read_only"], seen)
    tools += _special_raw("multi_step", config.TOOL_BEHAVIOUR["multi_step"], seen)
    tdecl = _tool_decline_raw(seen)

    valid = [r for r in general + apps + tools if r.kind == "valid"]
    decline = [r for r in general + tools + tdecl if r.kind == "decline"]
    if len(valid) != config.GENERAL_VALID + config.TOOL_VALID:
        raise ValueError(f"valid={len(valid)}")
    if len(decline) != config.GENERAL_DECLINE + sum(config.TOOL_DECLINE.values()):
        raise ValueError(f"decline={len(decline)}")
    raws = general + apps + tools + tdecl

    rng = random.Random(f"{config.SEED}:demand")
    lines = [1] * config.LINE_COUNTS[1] + [2] * config.LINE_COUNTS[2] + [3] * config.LINE_COUNTS[3]
    forced = {config.APPLICATION_CHOICES[d]: c for d, c in config.APPLICATIONS.items()}
    choices_d: list[int] = []
    for n, count in config.CHOICE_COUNTS.items():
        choices_d.extend([n] * (count - forced.get(n, 0)))
    rng.shuffle(lines)
    rng.shuffle(choices_d)
    non_app = sum(1 for r in raws if r.domain not in config.APPLICATIONS)
    if len(lines) != len(raws) or len(choices_d) != non_app:
        raise ValueError(f"choice/line quotas do not match record count: {len(lines)}/{len(choices_d)}/{len(raws)}")
    ns: list[int] = []
    for r in raws:
        ns.append(config.APPLICATION_CHOICES[r.domain] if r.domain in config.APPLICATIONS else choices_d.pop())
    valid_counts = {n: 0 for n in config.CHOICE_COUNTS}
    for r, n in zip(raws, ns):
        if r.kind == "valid":
            valid_counts[n] += 1
    idx_pool = {n: _balance_indices(valid_counts[n], n) for n in config.CHOICE_COUNTS}
    for n in idx_pool:
        random.Random(f"{config.SEED}:idx:{n}").shuffle(idx_pool[n])

    records: list[dict[str, Any]] = []
    metas: list[dict[str, Any]] = []
    for ri, (r, line, n) in enumerate(zip(raws, lines, ns)):
        target = None
        if r.kind == "valid":
            target = idx_pool[n].pop()
        rr = random.Random(f"{config.SEED}:choices:{r.source_id}:{ri}")
        choices, answer = _make_choices(r, n, target, rr)
        r.answer = answer
        conf = _confidence(answer, n, rr)
        if r.tool or r.domain == "tool":
            policy = r.policy or ("Do not take action when no tool fits the request." if r.kind == "decline" else rr.choice(POLICIES))
            inp = _format_tool(r, line, policy, choices)
        elif r.domain in config.APPLICATIONS:
            inp = _format_app(r, line)
        else:
            inp = _format_general(r, line)
        rec = {"input": inp, "choices": choices, "out": conf}
        errs = validate_record(rec)
        if errs:
            raise ValueError(f"bad record {r.source_id}: {errs} {rec}")
        records.append(rec)
        metas.append({
            "source_id": r.source_id, "kind": "tool" if (r.tool or r.domain == "tool") else "general",
            "decline": r.kind == "decline", "domain": r.domain, "answer": answer,
            "reason": r.reason, "behavior": r.behavior, "line": line, "choices": n,
        })
    _split_groups(raws, metas)
    return records, metas


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def write_dataset(out: Path, records: list[dict[str, Any]], metas: list[dict[str, Any]]) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    audit_dir = out / "audit"
    audit_dir.mkdir(exist_ok=True)
    # Assign files by slice, then chunk exactly.
    slices: dict[str, list[int]] = {"general_valid": [], "general_decline": [], "tool_valid": [], "tool_decline": []}
    for i, m in enumerate(metas):
        key = ("tool" if m["kind"] == "tool" else "general") + ("_decline" if m["decline"] else "_valid")
        slices[key].append(i)
    files: list[list[int]] = [[] for _ in range(config.TOTAL // config.BATCH_SIZE)]
    for key, ids in slices.items():
        random.Random(f"{config.SEED}:files:{key}").shuffle(ids)
        per = len(ids) // len(files)
        for fi in range(len(files)):
            files[fi].extend(ids[fi * per:(fi + 1) * per])
    for fi in range(len(files)):
        random.Random(f"{config.SEED}:shuffle:{fi}").shuffle(files[fi])

    file_entries = []
    for fi, ids in enumerate(files):
        name = f"decisions-{fi:05d}.jsonl"
        path = out / name
        lines = []
        alines = []
        for i in ids:
            lines.append(json.dumps(records[i], ensure_ascii=False, separators=(",", ":")) + "\n")
            alines.append(json.dumps(metas[i], ensure_ascii=False, separators=(",", ":")) + "\n")
        payload = "".join(lines).encode("utf-8")
        apayload = "".join(alines).encode("utf-8")
        path.write_bytes(payload)
        (audit_dir / (name.replace(".jsonl", ".meta.jsonl"))).write_bytes(apayload)
        counts = {"general_valid": 0, "general_decline": 0, "tool_valid": 0, "tool_decline": 0}
        for i in ids:
            key = ("tool" if metas[i]["kind"] == "tool" else "general") + ("_decline" if metas[i]["decline"] else "_valid")
            counts[key] += 1
        file_entries.append({"path": name, "records": len(ids), "bytes": len(payload),
                             "sha256": _sha(payload), "counts": counts})

    # Preview: every Nth record, stratified-ish.
    step = max(1, len(records) // 500)
    preview = [records[i] for i in range(0, len(records), step)][:500]
    (out / "preview.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in preview), encoding="utf-8")

    manifest = _manifest(out, records, metas, file_entries)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "stats.json").write_text(json.dumps(manifest["distribution"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    checks = "".join(f"{e['sha256']}  {e['path']}\n" for e in file_entries)
    (out / "checksums.sha256").write_text(checks, encoding="utf-8")
    _write_report(out, manifest, records)
    return manifest


def _count(metas, pred):
    return sum(1 for m in metas if pred(m))


def _manifest(out: Path, records, metas, file_entries) -> dict[str, Any]:
    line = {k: _count(metas, lambda m, k=k: m["line"] == k) for k in (1, 2, 3)}
    choices = {k: _count(metas, lambda m, k=k: m["choices"] == k) for k in (3, 4, 5, 6)}
    domains: dict[str, int] = {}
    for m in metas:
        if m["kind"] == "general":
            domains[m["domain"]] = domains.get(m["domain"], 0) + 1
    tool_domains: dict[str, int] = {}
    behaviors: dict[str, int] = {}
    general_declines: dict[str, int] = {}
    tool_declines: dict[str, int] = {}
    for m in metas:
        if m["kind"] == "tool":
            behaviors[m["behavior"]] = behaviors.get(m["behavior"], 0) + 1
            if m["behavior"] == "direct":
                td = TOOLS[m["source_id"].split(":", 1)[1]]["domain"]
                tool_domains[td] = tool_domains.get(td, 0) + 1
        if m["decline"]:
            bucket = tool_declines if m["kind"] == "tool" else general_declines
            bucket[m["reason"]] = bucket.get(m["reason"], 0) + 1
    return {
        "dataset": "decision-custom-1", "version": config.VERSION, "seed": config.SEED,
        "format": config.FORMAT, "records": len(records),
        "schema": {
            "input": "string (1-3 lines)",
            "choices": "array[2-10] of distinct strings",
            "out": "array[number] of length len(choices); scores in [0,1] summing to 1, or all -1 for decline",
        },
        "totals": {
            "records": len(records), "files": len(file_entries),
            "bytes": sum(e["bytes"] for e in file_entries),
            "tool": _count(metas, lambda m: m["kind"] == "tool"),
            "decline": _count(metas, lambda m: m["decline"]),
        },
        "distribution": {"lines": line, "choices": choices, "general_domains": domains,
                         "tool_domains": tool_domains, "tool_behaviors": behaviors,
                         "general_decline_pools": general_declines, "tool_decline_reasons": tool_declines},
        "files": file_entries,
        "validation": {"status": "pending"},
    }


def _write_report(out: Path, manifest, records):
    s = []
    s.append("# Decision Dataset v1\n")
    s.append(f"- Records: {manifest['totals']['records']:,}\n- Files: {manifest['totals']['files']}\n")
    s.append(f"- Tool: {manifest['totals']['tool']:,} ({manifest['totals']['tool']/manifest['totals']['records']:.1%})\n")
    s.append(f"- Decline: {manifest['totals']['decline']:,} ({manifest['totals']['decline']/manifest['totals']['records']:.1%})\n")
    s.append("\n## Distribution\n\n")
    for k, v in manifest["distribution"].items():
        s.append(f"### {k}\n")
        for a, b in sorted(v.items()):
            s.append(f"- {a}: {b:,}\n")
        s.append("\n")
    s.append("## Samples\n\n")
    for r in records[:30]:
        s.append(f"- `{r['input'].replace(chr(10), ' / ')}` -> {r['choices']} => **{r['out']}**\n")
    (out / "REPORT.md").write_text("".join(s), encoding="utf-8")
