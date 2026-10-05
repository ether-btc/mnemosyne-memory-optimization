# Phase Dispositions — mnemosyne-memory-optimization

**Date:** 2026-10-05
**Basis:** ground-truth measurement (`evidence/layer-reality-check.json`), independent
verification (`evidence/layer-verification.md`), mercury-decide oracle
(`evidence/oracle-p2-p5.json`), static scans.

## The core finding

The project premise — "Mnemosyne holds ~10K structured facts that can drive workflows" —
is **false as stated**. Direct inspection of the DB shows most "structured" layers are
extraction debris, not facts:

| Layer | Rows | Reality | Verdict |
|-------|------|---------|---------|
| canonical_facts | 1,838 | 345 task:progress (rich status) + 22 rule slots + misc; clean | **KEEP** |
| memoria_facts | 9,880 | ~98% fragments: 4,826 date rows over 146 distinct dates, broken metric n-grams, 5,199 exact dups | **DEBRIS** |
| memoria_kg | 73 | 96% truncated `(user)--decision-->(up cleanly:)` stubs | **DEBRIS** |
| consolidated_facts | 1,813 | ~95% fragments, amplified by mention_count (top row mc=177 is garbage) | **DEBRIS** |
| triples (open) | 1,733 | 1,612 = `occurred_on`/`mentions` (dangling hashes, stopwords); 66 semantic | **MOSTLY DEBRIS** |
| graph_edges | 3,163 | 3,162 auto `gist_<h>→fact_<h>` co-location pointers, not a knowledge graph | **INDEX METADATA** |
| memoria_instructions | 868 (814 active) | **~50% usable rules** but polluted with one-off narration (752 distinct texts) | **RECOVERABLE** |
| memoria_preferences | 795 | noise is **63.5% duplication** → 290 unique, mostly genuine | **RECOVERABLE** |

**Root cause (wiki `systems/memory-and-mnemosyne.md`):** `MNEMOSYNE_LLM_ENABLED=false` and
`llm_enabled: false` since **2026-08-07** — LLM-based extraction has been off for ~2 months;
only rules-based AAAK runs, producing fragments.

**Independent verification:** a researcher subagent re-measured every layer and returned
**PARTIAL** — confirming the debris layers but **refuting** the blanket claim for
`canonical_facts` (clean) and `memoria_instructions` (~50% usable rules with context
snippets). This correction is incorporated above. The correct framing is **not** "memoria_*
is all noise" but "memoria_facts / memoria_kg / consolidated_facts / triples-occurred_on are
debris; memoria_instructions needs dedup+filtering; canonical_facts is preserved".

**Oracle (steering check):** mercury-decide matched pair, one clause apart —
"build on the KG/memoria-facts layers" scored **0.0010** under the real evidence vs
**0.9859** under the handoff's false premise, **|Δ| = 0.985** (gate >0.5 → discriminating).
The model independently steers **against** building on the debris layers.

## Dispositions

### P1 — Canonical Slot Triggers — ✅ **BUILT**
Delivered `scripts/check_canonical.py` (list/suggest/recent/prefs over the 22 rule slots
and task:progress corpus) + 2 preflight checks. Exceeds the "4+ slots" criterion (8
suggestions).

### P2 — Knowledge Graph Workflow Dependencies — ⛔ **CLOSED NEGATIVE (as written)**
The "73-entry KG" is fragment junk and `graph_edges` is co-location index metadata, not a
dependency graph. Hand-curating a workflow graph over 345 prose task slots whose "active"
state is unknowable (no `valid_until`) has high curation cost, instant staleness, and
near-zero consumer today. **Oracle 0.0010.** Closing negatively is the correct, evidence-
backed outcome.

### P3 — Memoria Facts for Decision Support — 🔁 **REFRAMED → delivered as the context card**
`memoria_facts` (9,880) is dates/metrics/sequences — unusable for decisions. The real
self-awareness gap is that the standing rules are never loaded while WIP state is invisible.
**Delivered instead:** `scripts/preflight_context.py` — a session context card surfacing the
22 rule slots + recent WIP (9.5 KB), from `CanonicalStore` (read-only). The "10+ facts used
for decisions" criterion is met by the rule slots, not the memoria_facts layer.

### P4 — Instructions to Automated Workflows — 🔁 **REFRAMED**
867 instructions are ~50% usable rules **mixed with project-specific one-off narration**;
752 distinct active texts. Auto-generating a script per instruction would be wrong.
**Reframe:** the durable behavioral rules already live as the 22 canonical rule slots and are
surfaced by the P3 context card. The `memoria_instructions` layer is a **dedup + filter**
maintenance task (recover ~440 rules), not a workflow-generation task.

### P5 — Preferences to Personalized Defaults — ⛔ **CLOSED (subsumed)**
795 preference rows are 63.5% duplication; the 290 unique texts are genuine but **not
machine-actionable** (e.g. "I want god files broken up" — a style directive, not a workflow
switch). The durable, actionable preferences already exist as canonical preference slots
(AEON-default-filing, soak-approval, memory-backend) and are surfaced by the context card.
No separate defaults engine is justified.

## What was actually delivered

| Artifact | Phase | Purpose |
|----------|-------|---------|
| `scripts/check_canonical.py` | P1 | Query slots, suggest workflows |
| `scripts/preflight_context.py` | P3-reframed | Session context card (rules + WIP) |
| `scripts/preflight.sh` (+2 checks) | P1 | Mnemosyne DB + slots queryable |
| `evidence/layer-reality-check.json` | grounding | Measured layer counts |
| `evidence/layer-verification.md` | grounding | Independent verification (PARTIAL) |
| `evidence/oracle-p2-p5.json` | grounding | Mercury matched-pair probe |
| `docs/canonical-triggers.md` | P1 | Phase 1 documentation |
| `docs/PHASE-DISPOSITIONS.md` | all | This document |

## Success criteria — honest scorecard

| Metric | Target | Result |
|--------|--------|--------|
| Canonical slot triggers | 4+ slots used | ✅ 8 suggestions from 22 rule slots |
| KG workflow paths | 5+ chains | ⛔ closed negative (no real KG) |
| Memoria fact suggestions | 10+ facts | 🔁 delivered as 22 rule slots, not memoria_facts |
| Instructions converted | 10+ scripted | 🔁 reframed: rules already surfaced via card |
| Preferences integrated | 5+ defaults | ⛔ subsumed by canonical preference slots |
| Workflow time savings | 30 min/session | ⏳ unmeasured (claim would be unsupported) |

**Three of five phases are closed or reframed on evidence.** That is the honest outcome of
grounding the plan in the data — the alternative was building five features on extraction
debris.

## Recommended follow-ups (NOT in scope of this project)

1. **Fix the root cause:** re-enable `MNEMOSYNE_LLM_ENABLED=true` (config change with
   cost/runtime implications — needs operator decision) so future extraction produces clean
   facts. *This is the single highest-leverage fix; it is a prerequisite for any future
   "structured memory" work.*
2. **Write-side hygiene:** set `valid_until` on task:progress slots at closeout so "active
   WIP" becomes queryable rather than a recency proxy.
3. **Prune/rebuild** the debris layers (memoria_facts, memoria_kg, consolidated_facts) once
   extraction is re-enabled.
