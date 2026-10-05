# Phase 1: Canonical Slot Triggers

## Status: COMPLETE

## What Was Built

### `scripts/check_canonical.py`

Python script that queries Mnemosyne canonical slots and generates workflow suggestions.

**Modes:**
- `python3 scripts/check_canonical.py` — Full report (all categories + actionable slots + recent task:progress)
- `python3 scripts/check_canonical.py --recent` — Recent task:progress only (last 7 days)
- `python3 scripts/check_canonical.py --prefs` — Preference slots only
- `python3 scripts/check_canonical.py --suggest` — Workflow suggestions only

**API used:** `mnemosyne.core.canonical.CanonicalStore` (Python API, not MCP tools)
- `store.list(owner_id="default")` — List all slots
- `store.recall(owner_id, category, name)` — Point lookup
- `store.search(owner_id, query)` — Substring search

### `scripts/preflight.sh` — Updated

Added two new checks:
- `Mnemosyne DB exists` — Verifies `~/.hermes/mnemosyne/data/mnemosyne.db` exists
- `Mnemosyne canonical slots queryable` — Verifies the Python API can read slots

## Key Findings

### Actual Canonical Slot Data (381 slots)

| Category | Count | Description |
|----------|-------|-------------|
| task:progress | 344 | Session progress records (not actionable as triggers) |
| preference | 7 | User preferences (actionable) |
| pickup | 6 | PR pickup tracking |
| research:call | 3 | Research call checkpoints |
| hermes-config | 2 | Config snapshots |
| identity | 2 | Model identity |
| project | 2 | Project states |
| workflow | 2 | Workflow rules |
| storage | 2 | Storage policies |
| rhagent-bot-registry | 2 | Bot registry (empty) |
| audit/audit-complete/beichtstuhl/convention/fact/model:project/project:prompro/system-policy/voice | 1 each | Various |

### Adaptation from Handoff Plan

The handoff assumed status slots like `bekko-model-status`, `wiki-status`, `a16-status`, `local-models-status` exist. **They don't.** The 381 canonical slots are overwhelmingly `task:progress` (344 session records). The remaining 37 are preferences, workflow rules, project states, and config snapshots.

**Adaptation:** Instead of checking non-existent status slots, the script:
1. Surfaces all non-task:progress slots as "actionable" (preferences, workflow rules, project states)
2. Shows recent task:progress entries for context awareness
3. Generates workflow suggestions based on preferences and workflow rules

### Workflow Suggestions Generated

The script generates 8 workflow suggestions from canonical data:

1. **AEON filing** — Standing operator instruction to use AEON for all GitHub filing
2. **Soak approval** — Require explicit approval before long-running soaks
3. **Memory backend** — Mnemosyne is the durable backend (do not replace)
4. **Reviewer finding handling** — Verify each finding against authoritative source
5. **Measured figure corrections** — Verify measured figures when reviewer notes differ
6. **Stealth-copilot-bridge** — Private fork, check for updates
7. **Delegation model** — Current delegation config snapshot
8. **Active work** — Recent task:progress indicates active sessions

## Verification

### Test Results

```
$ python3 scripts/check_canonical.py --suggest
→ 8 suggestions generated correctly

$ python3 scripts/check_canonical.py --prefs
→ 7 preference slots displayed

$ python3 scripts/check_canonical.py --recent
→ 25 recent task:progress entries (last 7 days)

$ bash scripts/preflight.sh
→ 8/10 passed (2 expected failures: a16 unreachable, no OpenRouter key)
→ Both new Mnemosyne checks PASS
```

### Evidence

See `evidence/phase1-test-results.txt` for full test output.

## Success Criteria Status

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Canonical slot triggers | 4+ slots actively used | 8 suggestions from preferences/workflows | ✅ Exceeded |
| Workflow time savings | 30 min/session | TBD (qualitative) | ⏳ Pending |

## Next Steps

- Phase 2: Knowledge Graph Dependencies (expand 73-entry KG for workflow paths)
- Phase 3: Memoria Facts for Decision Support
- Phase 4: Instructions to Scripts
- Phase 5: Preferences to Defaults
