#!/usr/bin/env python3
"""
preflight_context.py — session context card from Mnemosyne canonical slots.

The real self-awareness gap: the standing rules (port 8081 off-limits, soak-approval
required, AEON-default-filing, USB32 policy) are never loaded automatically, while the
345 task:progress slots carry WIP state. This prints both as one compact markdown card.

Read-only. No writes to the DB.

Usage:
    python3 scripts/preflight_context.py            # full card (rules + recent WIP)
    python3 scripts/preflight_context.py --task rtk # filter WIP by name substring
    python3 scripts/preflight_context.py --json     # machine-readable
    python3 scripts/preflight_context.py --wip 12   # show top-N WIP (default 8)
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path.home() / "mnemosyne"))
from mnemosyne.core.canonical import CanonicalStore, _default_db_path

# Rule categories: standing rules/preferences/policies that apply every session.
RULE_CATS = [
    "system-policy", "preference", "workflow", "storage",
    "convention", "hermes-config", "identity", "project", "project:prompro",
    "fact", "voice",
]


def load_slots():
    store = CanonicalStore(_default_db_path())
    return store.list(owner_id="default")


def recent_wip(slots, n):
    tp = [s for s in slots if s["category"] == "task:progress"]
    tp.sort(key=lambda s: s.get("created_at") or "", reverse=True)
    return tp[:n]


def age_days(ts):
    try:
        dt = datetime.fromisoformat((ts or "").split(".")[0])
        return (datetime.now() - dt).days
    except Exception:
        return None


def build_card(slots, wip_n=8, task_filter=None, max_body=280, full=False):
    rules = [s for s in slots if s["category"] in RULE_CATS]
    rules.sort(key=lambda s: (RULE_CATS.index(s["category"]), s["name"]))
    wip = recent_wip(slots, wip_n)
    if task_filter:
        wip = [s for s in wip if task_filter.lower() in s["name"].lower()]

    def clip(b):
        b = " ".join((b or "").split())  # collapse newlines/multiple spaces to one line
        return b if full or len(b) <= max_body else b[:max_body].rstrip() + " […]"

    card = {
        "rule_slots": [
            {"category": s["category"], "name": s["name"], "body": clip(s["body"])}
            for s in rules
        ],
        "wip": [
            {"name": s["name"], "created_at": s.get("created_at"),
             "age_days": age_days(s.get("created_at")), "body": clip(s["body"])}
            for s in wip
        ],
    }
    return card


def render_markdown(card):
    out = ["# Session Context Card (Mnemosyne canonical slots)", ""]
    out.append(f"## Standing rules ({len(card['rule_slots'])})")
    out.append("")
    cur = None
    for r in card["rule_slots"]:
        if r["category"] != cur:
            cur = r["category"]
            out.append(f"### {cur}")
        out.append(f"- **{r['name']}** — {r['body'].strip()}")
    out.append("")
    out.append(f"## LIKELY-LIVE WIP ({len(card['wip'])}) — recency proxy, verify don't assume")
    out.append("")
    for w in card["wip"]:
        age = f"{w['age_days']}d" if w["age_days"] is not None else "?"
        out.append(f"- [{age}] **{w['name']}** — {w['body'].strip()}")
    out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Session context card from canonical slots")
    ap.add_argument("--task", help="filter WIP names by substring")
    ap.add_argument("--wip", type=int, default=8, help="number of recent WIP entries (default 8)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    ap.add_argument("--full", action="store_true", help="do not truncate rule bodies")
    args = ap.parse_args()

    slots = load_slots()
    card = build_card(slots, wip_n=args.wip, task_filter=args.task, full=args.full)

    if args.json:
        print(json.dumps(card, indent=2))
    else:
        print(render_markdown(card))


if __name__ == "__main__":
    main()
