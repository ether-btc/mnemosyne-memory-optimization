#!/usr/bin/env python3
"""
wip_hygiene.py — retire CLOSED task:progress canonical slots so "active WIP"
becomes a queryable fact instead of a recency proxy.

Background: task:progress slots are never retired, so preflight_context.py can
only label recent ones "LIKELY-LIVE WIP (recency proxy)". This script stamps
`valid_until` on slots whose body carries a STRONG terminal marker near the
start, so `store.list()` current-set shrinks to genuinely open work.

Fail-closed by design:
  - Default is DRY-RUN (prints what it would retire; changes nothing).
  - Only slots with a STRONG terminal marker in the first 180 chars AND no
    "open-ish" word anywhere in the body are eligible ("clean" set).
  - Slots with a marker but an open-ish word are reported AMBIGUOUS and are
    NEVER auto-retired — review them and retire by name if truly done.
  - Retirement is via CanonicalStore.forget() which only stamps valid_until;
    nothing is deleted and history is preserved.

Usage:
    python3 scripts/wip_hygiene.py                 # dry-run (default)
    python3 scripts/wip_hygiene.py --list-ambiguous
    python3 scripts/wip_hygiene.py --apply         # retire the clean set
    python3 scripts/wip_hygiene.py --retire NAME   # retire one slot by name
"""
import sys
import re
import argparse
from pathlib import Path

sys.path.insert(0, str(Path.home() / "mnemosyne"))
from mnemosyne.core.canonical import CanonicalStore, _default_db_path

STRONG = re.compile(
    r"\b(COMPLETE|COMPLETED|CLOSED|CONCLUDED|SESSION CLOSED|SESSION CONCLUDED|"
    r"WOUND DOWN|FINAL CLOSEOUT|CLOSED NEGATIVELY|TERMINAL|SHELVED|RETIRED|"
    r"NO OPEN ITEMS|NOTHING IS OPEN|NO OPEN ACTIONS|ALL ITEMS VERIFIED)\b",
    re.IGNORECASE,
)
OPENISH = re.compile(
    r"\b(open item|still open|remains open|pending|next step|next session|"
    r"to do|TODO|not yet|partially diagnosed|residual|in flight|in-flight)\b",
    re.IGNORECASE,
)


def load_task_slots(store):
    return [s for s in store.list(owner_id="default") if s["category"] == "task:progress"]


def classify(slots):
    clean, ambiguous, active = [], [], []
    for s in slots:
        head_marker = STRONG.search(s["body"][:180])
        openish = OPENISH.search(s["body"])
        if head_marker and not openish:
            clean.append(s)
        elif head_marker and openish:
            ambiguous.append(s)
        else:
            active.append(s)
    return clean, ambiguous, active


def main():
    ap = argparse.ArgumentParser(description="Retire closed task:progress slots (dry-run default)")
    ap.add_argument("--apply", action="store_true", help="actually stamp valid_until on the clean set")
    ap.add_argument("--list-ambiguous", action="store_true", help="list the ambiguous slots for review")
    ap.add_argument("--retire", metavar="NAME", help="retire one slot by exact name")
    args = ap.parse_args()

    store = CanonicalStore(_default_db_path())

    if args.retire:
        ok = store.forget(owner_id="default", category="task:progress", name=args.retire)
        print(f"{'retired' if ok else 'NOT retired (already empty or not found)'}: {args.retire}")
        return

    slots = load_task_slots(store)
    clean, ambiguous, active = classify(slots)

    print(f"task:progress slots: {len(slots)}")
    print(f"  CLEAN closed (safe to retire): {len(clean)}")
    print(f"  AMBIGUOUS (marker + open-ish word): {len(ambiguous)}")
    print(f"  NO marker (active/unknown): {len(active)}")

    if args.list_ambiguous:
        print("\n=== AMBIGUOUS (review; NOT auto-retired) ===")
        for s in ambiguous:
            print(f"  {s['name']}: {s['body'][:110].replace(chr(10), ' ')}")
        return

    if args.apply:
        n = 0
        for s in clean:
            if store.forget(owner_id="default", category="task:progress", name=s["name"]):
                n += 1
        print(f"\nRETIRED {n} closed slots (valid_until stamped; nothing deleted).")
        print(f"Current task:progress would drop to {len(ambiguous) + len(active)}.")
    else:
        print("\nDRY-RUN (nothing changed). First 15 of the clean set:")
        for s in clean[:15]:
            print(f"  {s['name']}: {s['body'][:90].replace(chr(10), ' ')}")
        print("\nRe-run with --apply to retire the clean set.")


if __name__ == "__main__":
    main()
