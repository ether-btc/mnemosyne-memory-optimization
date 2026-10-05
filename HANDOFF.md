# Mnemosyne Memory Optimization — Project Handoff

## Project Overview

**Goal:** Leverage Mnemosyne's ~10K structured facts (canonical slots, memoria facts, knowledge graph) to make workflows self-aware and adaptive.

**Starting Point:** The Mnemosyne Operability study (complete) identified that Mnemosyne is used correctly 6/6 times when invoked. This project extends that finding: instead of relying on the agent to remember to use Mnemosyne, we make Mnemosyne the orchestrator of workflow decisions.

**Date:** 2026-10-05
**Status:** READY TO START

---

## Current Mnemosyne State (measured 2026-10-05)

| Layer | Count | Description |
|-------|-------|-------------|
| Working memories | 12,332 | Raw session data (386 unconsolidated) |
| Episodic memories | 2,648 | Consolidated summaries |
| Canonical slots | 381 | Single-source-of-truth facts |
| Memoria facts | 9,867 | Extracted structured facts |
| Knowledge graph | 73 | Relationship mappings |
| Instructions | 867 | Behavioral rules |
| Preferences | 793 | User preferences |

**Key Insight:** 381 canonical slots + 9,867 memoria facts = ~10K structured facts that could inform workflow decisions, but are currently passive (only queried when the agent remembers to).

---

## Optimization Opportunities (priority order)

### P1: Canonical Slot Triggers (High impact, Low effort)

**What:** Use canonical slots as automatic workflow triggers.

**Why:** Canonical slots are already the "single source of truth" for stable facts. Using them as triggers makes workflows self-aware.

**Example:**
```
IF canonical_slot["bekko-model-status"] == "trained"
THEN auto-suggest: "Model ready for deployment — run test-local.sh"
```

**Implementation:**
- Add canonical slot checks to `preflight.sh`
- Create `scripts/check-canonical.sh` that queries slots and suggests workflows
- Map slot values to workflow scripts

**Slots to use:**
- `bekko-model-status`: trained / not-trained / deployed
- `wiki-status`: clean / dirty / needs-reconciliation
- `a16-status`: reachable / unreachable
- `local-models-status`: available / unavailable

### P2: Knowledge Graph Workflow Dependencies (High impact, Medium effort)

**What:** Expand the 73-entry knowledge graph to map workflow dependencies.

**Why:** KG traversal can auto-generate workflow steps.

**Example triples:**
```
("bekko-model", "requires", "a16-training")
("a16-training", "produces", "model-checkpoint")
("model-checkpoint", "requires", "transfer-to-pi")
("transfer-to-pi", "produces", "local-model")
("local-model", "requires", "container-deployment")
("container-deployment", "produces", "operational-model")
```

**Implementation:**
- Add workflow dependency triples via `mnemosyne_triple_add`
- Create `scripts/kg-workflow.sh` that traverses the graph and outputs workflow steps
- Use `mnemosyne_graph_query` to find paths from current state to goal

### P3: Memoria Facts for Decision Support (Medium impact, Low effort)

**What:** Query memoria facts to pre-select workflow options.

**Why:** 9,867 facts contain historical workflow knowledge.

**Example:**
```
Before starting a review workflow:
  mnemosyne_recall "review process"
  → Returns: "3 rounds, 3 bots, parallel dispatch"
  → Auto-suggest: dispatch-review.sh
```

**Implementation:**
- Add memoria fact queries to `preflight.sh`
- Create `scripts/suggest-workflow.sh` that queries facts and suggests scripts
- Cache frequently-used facts in canonical slots

### P4: Instructions to Automated Workflows (Medium impact, Medium effort)

**What:** Convert frequently-used instructions into scripted workflows.

**Why:** 867 instructions store behavioral rules that are currently manual.

**Example:**
```
Instruction: "Always check disk space before building containers"
→ Script: preflight.sh (already implemented)
→ Trigger: Auto-run before podman build
```

**Implementation:**
- Identify top 10 most-referenced instructions
- Convert each to a script
- Add to `scripts/` directory

### P5: Preferences to Personalized Defaults (Low impact, Low effort)

**What:** Use preferences to customize workflow defaults.

**Why:** 793 preferences store user settings that could streamline workflows.

**Example:**
```
Preference: "parallel reviews"
→ Default: dispatch-review.sh (3 bots in parallel)
→ Instead of: sequential review dispatch
```

**Implementation:**
- Add preference checks to `preflight.sh`
- Create `scripts/load-preferences.sh` that sets workflow defaults

---

## Implementation Plan

### Phase 1: Canonical Slot Triggers (Week 1)

1. Create `scripts/check-canonical.sh`
2. Add canonical slot checks to `preflight.sh`
3. Test with existing slots
4. Document in `docs/canonical-triggers.md`

### Phase 2: Knowledge Graph Dependencies (Week 2)

1. Add workflow dependency triples
2. Create `scripts/kg-workflow.sh`
3. Test graph traversal
4. Document in `docs/kg-workflows.md`

### Phase 3: Memoria Facts Integration (Week 3)

1. Create `scripts/suggest-workflow.sh`
2. Add fact queries to `preflight.sh`
3. Test with historical workflow data
4. Document in `docs/memoria-decisions.md`

### Phase 4: Instructions to Scripts (Week 4)

1. Identify top 10 instructions
2. Convert to scripts
3. Test each script
4. Document in `docs/instruction-scripts.md`

### Phase 5: Preferences Integration (Week 5)

1. Create `scripts/load-preferences.sh`
2. Add preference checks to `preflight.sh`
3. Test with existing preferences
4. Document in `docs/preference-defaults.md`

---

## Scripts to Create

| Script | Purpose | Phase |
|--------|---------|-------|
| `check-canonical.sh` | Query canonical slots and suggest workflows | P1 |
| `kg-workflow.sh` | Traverse knowledge graph for workflow steps | P2 |
| `suggest-workflow.sh` | Query memoria facts for workflow suggestions | P3 |
| `load-preferences.sh` | Load user preferences as workflow defaults | P4 |

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Canonical slot triggers | 4+ slots actively used |
| KG workflow paths | 5+ dependency chains |
| Memoria fact suggestions | 10+ facts used for decisions |
| Instructions converted | 10+ instructions scripted |
| Preferences integrated | 5+ preferences as defaults |
| Workflow time savings | Additional 30 min/session |

---

## How to Verify

1. **Canonical slots:** Run `check-canonical.sh` and verify it suggests correct workflows
2. **KG traversal:** Run `kg-workflow.sh` and verify it outputs valid workflow steps
3. **Memoria facts:** Run `suggest-workflow.sh` and verify suggestions match historical data
4. **Instructions:** Run each converted script and verify it matches the instruction
5. **Preferences:** Run `load-preferences.sh` and verify defaults are applied

---

## Existing Assets

**From Mnemosyne Operability study:**
- `scripts/preflight.sh` — Pre-flight checks
- `scripts/check-model-capability.sh` — Model capability verification
- `scripts/dispatch-review.sh` — Parallel review dispatch
- `scripts/transfer-model.sh` — Binary-safe model transfer
- `scripts/test-local.sh` — Local model testing
- `scripts/batch-commit.sh` — Batch git commits
- `scripts/cleanup.sh` — Automated cleanup
- `scripts/retry.sh` — Exponential backoff retry

**Mnemosyne tools available:**
- `mnemosyne_recall` — Search memories
- `mnemosyne_recall_canonical` — Read canonical slots
- `mnemosyne_triple_add` — Add knowledge graph edges
- `mnemosyne_graph_query` — Traverse knowledge graph
- `mnemosyne_remember` — Store new memory
- `mnemosyne_stats` — Get memory statistics

---

## Quick Start

```bash
# 1. Check current Mnemosyne state
mnemosyne_stats

# 2. Query canonical slots
mnemosyne_recall_canonical

# 3. Search for workflow-related memories
mnemosyne_recall "workflow optimization"

# 4. Check knowledge graph
mnemosyne_graph_query --seed-memory-id <id>

# 5. Run preflight checks
bash scripts/preflight.sh
```

---

## Key Files

| File | Purpose |
|------|---------|
| `HANDOFF.md` | This document |
| `scripts/` | Workflow automation scripts |
| `docs/` | Detailed documentation per phase |
| `evidence/` | Test results and measurements |

---

## Next Session Start

1. Read this handoff
2. Run `mnemosyne_stats` to verify current state
3. Start Phase 1: Create `scripts/check-canonical.sh`
4. Test with existing canonical slots
5. Document results in `docs/canonical-triggers.md`
