#!/usr/bin/env python3
"""
check_canonical.py — Query Mnemosyne canonical slots and suggest workflows.

Phase 1 of mnemosyne-memory-optimization project.
Adapted to actual canonical slot data (381 slots, mostly task:progress).

Usage:
    python3 scripts/check_canonical.py              # Full report
    python3 scripts/check_canonical.py --recent     # Recent task:progress only
    python3 scripts/check_canonical.py --prefs      # Preferences only
    python3 scripts/check_canonical.py --suggest    # Workflow suggestions only
"""

import sys
import os
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# Add mnemosyne to path
sys.path.insert(0, str(Path.home() / "mnemosyne"))

from mnemosyne.core.canonical import CanonicalStore, _default_db_path


def get_store():
    """Initialize CanonicalStore with default DB path."""
    db_path = _default_db_path()
    if not db_path.exists():
        print(f"ERROR: Mnemosyne DB not found at {db_path}")
        sys.exit(1)
    return CanonicalStore(db_path)


def list_all_slots(store):
    """List all canonical slots for the default owner."""
    return store.list(owner_id="default")


def categorize_slots(slots):
    """Group slots by category."""
    cats = defaultdict(list)
    for slot in slots:
        cats[slot["category"]].append(slot)
    return dict(cats)


def format_slot(slot, max_body=200):
    """Format a slot for display."""
    body = slot.get("body", "")
    if len(body) > max_body:
        body = body[:max_body] + "..."
    body = body.replace("\n", " ")
    return f"  [{slot['id']}] {slot['name']}: {body}"


def show_full_report(store):
    """Show full canonical slot report."""
    slots = list_all_slots(store)
    cats = categorize_slots(slots)

    print("=" * 70)
    print("MNEMOSYNE CANONICAL SLOT REPORT")
    print("=" * 70)
    print(f"Total slots: {len(slots)}")
    print(f"Categories: {len(cats)}")
    print()

    # Summary by category
    print("--- Category Summary ---")
    for cat in sorted(cats.keys()):
        print(f"  {cat}: {len(cats[cat])}")
    print()

    # Non-task:progress slots (the actionable ones)
    print("--- Actionable Slots (non-task:progress) ---")
    for cat in sorted(cats.keys()):
        if cat == "task:progress":
            continue
        print(f"\n[{cat}]")
        for slot in cats[cat]:
            print(format_slot(slot, max_body=300))

    # Recent task:progress (last 7 days)
    print("\n--- Recent task:progress (last 7 days) ---")
    cutoff = datetime.now() - timedelta(days=7)
    recent = []
    for slot in cats.get("task:progress", []):
        # Try to parse created_at or valid_from
        ts = slot.get("created_at") or slot.get("valid_from", "")
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00").split("+")[0])
            if dt > cutoff:
                recent.append(slot)
        except:
            pass

    if recent:
        for slot in sorted(recent, key=lambda s: s.get("created_at", ""), reverse=True)[:15]:
            print(format_slot(slot, max_body=200))
    else:
        print("  (none in last 7 days)")

    print()


def show_recent(store):
    """Show recent task:progress entries."""
    slots = list_all_slots(store)
    cats = categorize_slots(slots)

    print("=" * 70)
    print("RECENT TASK:PROGRESS (last 7 days)")
    print("=" * 70)

    cutoff = datetime.now() - timedelta(days=7)
    recent = []
    for slot in cats.get("task:progress", []):
        ts = slot.get("created_at") or slot.get("valid_from", "")
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00").split("+")[0])
            if dt > cutoff:
                recent.append(slot)
        except:
            pass

    if not recent:
        print("No task:progress entries in last 7 days.")
        return

    for slot in sorted(recent, key=lambda s: s.get("created_at", ""), reverse=True):
        print(format_slot(slot, max_body=300))
    print()


def show_prefs(store):
    """Show preference slots."""
    slots = list_all_slots(store)
    cats = categorize_slots(slots)

    print("=" * 70)
    print("PREFERENCE SLOTS")
    print("=" * 70)

    prefs = cats.get("preference", [])
    if not prefs:
        print("No preference slots found.")
        return

    for slot in prefs:
        print(format_slot(slot, max_body=400))
    print()


def show_suggestions(store):
    """Generate workflow suggestions based on canonical state."""
    slots = list_all_slots(store)
    cats = categorize_slots(slots)

    print("=" * 70)
    print("WORKFLOW SUGGESTIONS")
    print("=" * 70)

    suggestions = []

    # Check preferences for workflow defaults
    prefs = {s["name"]: s["body"] for s in cats.get("preference", [])}

    if "aeon-is-the-filing-system" in prefs:
        suggestions.append({
            "trigger": "preference/aeon-is-the-filing-system",
            "suggestion": "Use AEON for all filing operations (standing operator instruction)",
            "script": "aeon"
        })

    if "long_running_soak_approval" in prefs:
        suggestions.append({
            "trigger": "preference/long_running_soak_approval",
            "suggestion": "Require explicit approval before starting any long-running soak",
            "script": "preflight.sh"
        })

    if "memory-backend" in prefs:
        suggestions.append({
            "trigger": "preference/memory-backend",
            "suggestion": "Mnemosyne is the durable memory backend — do not replace",
            "script": None
        })

    # Check workflow rules
    workflows = {s["name"]: s["body"] for s in cats.get("workflow", [])}

    if "reviewer-finding-handling" in workflows:
        suggestions.append({
            "trigger": "workflow/reviewer-finding-handling",
            "suggestion": "Verify each reviewer finding against authoritative source before acting",
            "script": None
        })

    if "measured-figure-corrections" in workflows:
        suggestions.append({
            "trigger": "workflow/measured-figure-corrections",
            "suggestion": "Verify measured figures against authoritative source when reviewer notes differ",
            "script": None
        })

    # Check project states
    projects = {s["name"]: s["body"] for s in cats.get("project", [])}

    if "stealth-copilot-bridge" in projects:
        suggestions.append({
            "trigger": "project/stealth-copilot-bridge",
            "suggestion": "Private fork ether-btc/stealth_copilot_bridge — check for updates",
            "script": None
        })

    # Check hermes-config
    hermes_cfg = {s["name"]: s["body"] for s in cats.get("hermes-config", [])}

    if "delegation-model" in hermes_cfg:
        suggestions.append({
            "trigger": "hermes-config/delegation-model",
            "suggestion": f"Delegation model configured: {hermes_cfg['delegation-model'][:100]}",
            "script": None
        })

    # Check recent task:progress for active work
    cutoff = datetime.now() - timedelta(days=3)
    recent_tasks = []
    for slot in cats.get("task:progress", []):
        ts = slot.get("created_at") or slot.get("valid_from", "")
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00").split("+")[0])
            if dt > cutoff:
                recent_tasks.append(slot)
        except:
            pass

    if recent_tasks:
        suggestions.append({
            "trigger": f"task:progress ({len(recent_tasks)} recent)",
            "suggestion": "Active work in progress — check recent sessions for context",
            "script": None
        })

    # Print suggestions
    if not suggestions:
        print("No workflow suggestions generated.")
        return

    for i, s in enumerate(suggestions, 1):
        print(f"\n{i}. [{s['trigger']}]")
        print(f"   → {s['suggestion']}")
        if s["script"]:
            print(f"   → Script: {s['script']}")

    print()


def main():
    parser = argparse.ArgumentParser(description="Query Mnemosyne canonical slots")
    parser.add_argument("--recent", action="store_true", help="Show recent task:progress only")
    parser.add_argument("--prefs", action="store_true", help="Show preferences only")
    parser.add_argument("--suggest", action="store_true", help="Show workflow suggestions only")
    args = parser.parse_args()

    store = get_store()

    if args.recent:
        show_recent(store)
    elif args.prefs:
        show_prefs(store)
    elif args.suggest:
        show_suggestions(store)
    else:
        show_full_report(store)


if __name__ == "__main__":
    main()
