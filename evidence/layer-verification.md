# Independent Verification — Layer Noise Claim

**Verifier:** researcher subagent (glm-5.3-flash, read-only), deleg_9813ef47 task-0, 2026-10-05
**Claim under test:** "Mnemosyne's structured layers are dominated by extraction fragments, not clean structured facts."

## Verdict: **PARTIAL**

The claim is CONFIRMED for four layers and REFUTED for two. The correct reframe is *not*
"memoria_* is all noise" but a per-layer disposition.

## Confirmed debris

| Layer | Noise fraction | Evidence |
|-------|---------------|----------|
| `memoria_facts` | ~98% | 4,826 `iso_date` rows over only 146 distinct dates (avg 33× dup); broken metric n-grams (`drop_dramatically_minimum_pct`, `usb_intact_rpi_user = 5user`); sequence keys are connectors (then/first/next); 5,199 exact-dup rows |
| `memoria_kg` | 96% | 70/73 subjects literally "user", predicates decision(56)/negation, objects truncated mid-sentence ("up cleanly:", "what that implies") |
| `consolidated_facts` | ~95% | highest-confidence rows are the worst: `("A pass that does nothing")--is-->("missed") mc=177`, `("The request")--is-->("open") mc=103`. Consolidation **amplified** noise via mention_count |
| `triples` (open) | 1,612/1,733 | `occurred_on` (843): subjects are 16-hex hashes, only 1 of 843 resolves to a memory row (dangling). `mentions` (769): 47% stopword objects |

## Refuted (recoverable / clean)

| Layer | Verdict | Evidence |
|-------|---------|----------|
| `memoria_instructions` | **~50% usable rules** (440/814 active) | Real operational rules present: "never push the gopass root store to a PUBLIC or unnamed remote (67 secrets would be published)", "Always `git symbolic-ref refs/remotes/origin/HEAD` before first push", "Niemals Alpenland/Skidata". All 868 rows carry a `context_snippet`, so even fragments are recoverable. Noise is subjectless predicate fragments + past-tense narration. |
| `memoria_preferences` | **63.5% duplication**, not fragmentation | 290 unique texts among 795 rows. Boilerplate "user wants you to learn a reusable skill..." repeated 97×. The 290 uniques are largely genuine preferences. |
| `canonical_facts` | **CLEAN** | 377/382 current rows usable; task:progress are rich status records; the 22 rule slots are high-value structured facts. Caveat: 1,456 superseded history rows (verbosity, not fragments). |

## Count corrections (parent figures off by 1–2)

- `graph_edges` total = **3,163** (3,162 ctx + 1 supersedes), not 3,162.
- `canonical_facts` = **1,838**, with **345** current `task:progress` rows (1,798 incl. superseded), not 344.
- `triples` semantic minority: **66** clean open rows (e.g. `(prompro)--trading-pair->(cbBTC/USDC)`, `(jinar/indicator)--license->(AGPL-3.0)`).

## Impact on dispositions

- P2 (KG) stays **closed negative** — the KG is debris/index-metadata.
- P3 (memoria_facts) stays **reframed** — that layer is unusable.
- P4 (instructions) is **reframed, not closed** — the layer holds ~440 real rules; it is a
  dedup+filter maintenance task, and the durable subset is already the 22 canonical rule slots.
- P5 (preferences) is **subsumed** — the unique texts are genuine but not machine-actionable;
  the actionable subset is the canonical preference slots.

Read-only throughout; no files created or modified by the verifier.
