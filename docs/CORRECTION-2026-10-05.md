# CORRECTION — 2026-10-05: the "LLM extraction off" root cause was WRONG

**What I claimed (in `docs/PHASE-DISPOSITIONS.md` and the wiki page):** the `memoria_*`
debris exists because `MNEMOSYNE_LLM_ENABLED=false` since 2026-08-07 disabled LLM
extraction, leaving only rules-based AAAK.

**That is FALSE.** Post-restart verification proved it, and I am correcting the record
rather than editing around it.

## The actual mechanism (verified by source + execution)

There are **two independent extractors** writing to **disjoint stores**:

| Path | Code | Trigger | Writes to | LLM? |
|------|------|---------|-----------|------|
| Regex / "MEMORIA" | `BeamMemory.extract_and_store_facts()` (beam.py:7590) | **unconditional on every `remember()`** | `memoria_facts`, `memoria_instructions`, `memoria_preferences`, `memoria_kg`, `memoria_timelines` | **No** — "Uses regex patterns matching the BEAM benchmark oracles" |
| LLM | `_extract_and_store_facts()` (beam.py:2782) → `extract_facts_safe()` | only when `remember(extract=True)` (default **False**) | `annotations` (kind=fact) + `facts` table | Yes |

The regex extractor is explicitly labeled **"always-on, zero-LLM-cost"** in the code
(beam.py:5648, 5751) and runs regardless of `MNEMOSYNE_LLM_ENABLED`.

**Execution proof:** two probe writes made *after* the restart (when `MNEMOSYNE_LLM_ENABLED=true`)
grew `memoria_facts` **9,880 → 9,895**, with exactly the debris pattern
(`sequence|second|…`, `date|iso_date|2026-10-05`). The flag had no effect on that table.

## Consequences

1. **The (a) config change does NOT fix the debris.** `memoria_*` is rules-extraction
   output and will keep accumulating identically whether or not the LLM flag is set. The
   debris is a property of the always-on regex extractor, not of the LLM setting.
2. **The (a) change is not reliably delivering the LLM path either.** The `extract=True`
   path calls the host aux backend, which timed out at 15–30 s against the `nous` endpoint
   in probes, so `extract_facts_safe()` returned `[]` and 0 facts were written. `extract=True`
   is also off by default, so nothing in the normal write path even attempts it.
3. **The original 2026-08-07 wiki note was about a different thing** (LLM summarization /
   consolidation via a broken local URL). It was true then and is unrelated to the
   `memoria_*` debris.

## What is actually true

- The `memoria_*` tables are populated by a **rules/regex extractor with no config toggle**.
  To stop the debris you must **gate or disable `extract_and_store_facts()`** (a code change,
  not a config setting) or accept it as the intended always-on design.
- The LLM (`extract=True`) path writes to `facts`/`annotations` and is **not** the source of
  any `memoria_*` row.

## Status of the (a) change

Left in place (harmless — the host path returns `None` on timeout and degrades gracefully;
`extract=True` defaults off, so normal writes are unaffected). It is **not** doing the job
it was made for. Options for the operator:

- **To actually fix the debris:** patch/disable the regex extractor (upstream change).
- **To make LLM extraction usable:** the sync write path cannot afford a cloud call per
  write; use a fast local model for the aux `compression` slot, or make extraction async.
- **To revert (a):** `cp ~/.config/hermes-gateway.env.bak-prehostllm-20261005 ~/.config/hermes-gateway.env && systemctl --user restart hermes-gateway.service`.

## Lesson

I attributed a data-quality defect to the most visible configuration flag instead of
tracing which code actually writes the table. **Trace the writer before naming the cause** —
`grep` the table name to the `INSERT`, and read the enclosing function's docstring, before
attributing the data to a setting.
