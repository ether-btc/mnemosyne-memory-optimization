# Self-Execution Prompt — mnemosyne-memory-optimization (P2–P5)

## Mission

Complete the `mnemosyne-memory-optimization` project honestly. The stated goal is to
leverage Mnemosyne's "~10K structured facts" (canonical slots, knowledge graph, memoria
facts, instructions, preferences) so workflows become self-aware. **Phase 1 is complete.**
Ground-truth inspection of the data (2026-10-05) shows the P2–P5 premises rest on layers
that are largely extraction noise. Determine, with evidence and independent review, which
of P2–P5 are buildable as written, which must be reframed, and which should be closed
negatively — then build the parts that genuinely deliver value.

**Done = ** every phase has an explicit, evidence-backed disposition (built / reframed /
closed-negative), the artifacts are committed locally, filed to the wiki, pushed to
GitHub, and progress is saved to Mnemosyne.

## Ground Truth (measured 2026-10-05, evidence/layer-reality-check.json)

| Layer | Rows | Reality |
|-------|------|---------|
| canonical_facts | 1,837 | **344 task:progress + 40 actionable** — only clean structured layer (P1 used it) |
| memoria_facts | 9,880 | **date 4,991 / metric 3,031 / sequence 1,190 / version 668** — extraction artifacts, no workflow value |
| memoria_kg | 73 | Fragment junk: `(user) --decision--> (up cleanly:)` |
| triples (open) | 1,733 | **1,612 = `occurred_on`/`mentions` noise**; ~120 semantic |
| graph_edges | 3,162 | **3,161 `ctx` gist→fact pointers + 1 supersedes** — NOT a knowledge graph |
| consolidated_facts | 1,813 | Fragment junk: `A pass that does nothing --is--> missed` |
| memoria_instructions | 868 | Fragment topics: "shutdown indefinately", "restored" |
| memoria_preferences | 795 | Fragment topics: "you to learn a reusable skill from..." |

**Root cause (wiki `systems/memory-and-mnemosyne.md`):** `MNEMOSYNE_LLM_ENABLED=false` and
`llm_enabled: false` since 2026-08-07 — LLM extraction has been OFF for ~2 months; only
rules-based AAAK runs. Hence fragments, not clean rules/facts.

**Implication:** the handoff's "~10K structured facts" premise is FALSE. P2 (KG has no
dependency edges), P3 (memoria_facts are dates/metrics), P4 (instructions are fragments)
are not buildable as written. The real leverage is the 40 actionable canonical slots
(done, P1) and the working/episodic prose layer (already served by recall).

## Tools Available

- **mercury oracle** — `~/projects/mercury-decide-client/mercury.py` (reuse; POST
  `https://openrouter.ai/api/alpha/decisions`, model `inception/mercury-decide:free`,
  key from `gopass show -o hermes/openrouter-api-key`). Read DELTAS between matched pairs,
  never absolutes. Use `choice` for named alternatives.
- **bot team** — profiles under `~/.hermes/profiles/` (researcher, reviewer,
  thinking-partner, vibe-coding-expert, technical-cofounder, arbiter). `delegate_task` for
  independent read-only review; `message_agent` to DM (fire-and-forget).
- **ocr** — `~/.local/bin/ocr scan . --offline --no-score` (static scan of new code).
- **repomix** — pack a repo for analysis (only if needed).
- **ruff / bandit** — Python lint + security on new scripts.
- **sqlite3 -readonly** — query `~/.hermes/mnemosyne/data/mnemosyne.db`.
- **ponytail** (skill) — laziest solution that works; question whether the task needs to exist.

## Steps

1. **Write this prompt to disk** → `SELF-EXECUTION-PROMPT.md` (progress checkpoint).
2. **Independently verify the noise finding** — dispatch a researcher/verifier subagent to
   sample each layer and confirm the noise fractions, so a wrong "it's all noise" verdict
   cannot silently reframe the whole project. → `evidence/layer-verification.md`
3. **Run the mercury oracle** on the phase-disposition decision as a matched-pair/choice
   probe. Record the raw response. → `evidence/oracle-p2-p5.json`
4. **Disposition each phase** (built / reframed / closed-negative) in
   `docs/PHASE-DISPOSITIONS.md`, with the evidence and the oracle read.
5. **Build what survives** — expected: a `suggest-workflow` script (P3-reframed) over the
   40 actionable canonical slots + working-memory keyword search; P2/P4 closed-negative
   with the measured reason; P5 only if the preferences have signal.
6. **Static-scan new code** — `ocr scan . --offline --no-score` + `ruff` + `bandit`.
7. **Update HANDOFF.md** phase log with dispositions.
8. **File to wiki** — `entities/mnemosyne-memory-optimization.md` +
   `projects/mnemosyne-memory-optimization.md` (isolated worktree off origin/master).
9. **Commit + push** to `ether-btc/mnemosyne-memory-optimization`; verify with `git ls-remote`.
10. **Save progress** — `mnemosyne_remember` + `mnemosyne_task_progress` + canonical slot.

## Progress Checkpoints

After each step, the named artifact exists and is committed. If interrupted, resume from
the last artifact.

## Constraints

- Evidence-gated: no claim of improvement without a measurement; no fabricated output.
- Ponytail: do not build a workflow engine for a problem that a 20-line script solves;
  closing a phase negatively with evidence is a first-class outcome.
- Hard gates respected: no live-service mutation, no secret exposure. GitHub push is
  authorized ("ALL github work is your job"); commits/pushes to the project repo are fine.
- English only. Save progress regularly.
