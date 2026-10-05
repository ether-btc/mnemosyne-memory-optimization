# Post-Restart Verification — LLM Extraction Activation

**Context:** `~/.config/hermes-gateway.env` was edited on 2026-10-05 to enable
Mnemosyne LLM-based fact extraction via the Hermes host aux client (free model).
The change takes effect on the next `hermes-gateway` restart. **Nothing else is
required before the restart** — the WIP hygiene (`wip_hygiene.py`) and all scripts
are already live and need no restart.

## Restart

```bash
systemctl --user restart hermes-gateway.service
```

(No `daemon-reload` needed — only the `EnvironmentFile` contents changed, not the unit.)

## 1. Confirm the env reached the process

```bash
tr '\0' '\n' < /proc/$(systemctl --user show hermes-gateway.service -p MainPID --value)/environ \
  | grep -E 'MNEMOSYNE_(LLM_ENABLED|HOST_LLM_ENABLED|HOST_LLM_MODEL)'
```
Expect: `MNEMOSYNE_LLM_ENABLED=true`, `MNEMOSYNE_HOST_LLM_ENABLED=true`,
`MNEMOSYNE_HOST_LLM_MODEL=stepfun/step-3.7-flash:free`.

## 2. Confirm extraction actually runs (functional)

Write one durable memory, then check the derived tables grow:

```bash
# In a Hermes session: mnemosyne_remember(content="The staging server runs on port 9443.")
# Then:
sqlite3 -readonly ~/.hermes/mnemosyne/data/mnemosyne.db \
  "SELECT COUNT(*) FROM annotations WHERE kind='fact' AND created_at > datetime('now','-5 minutes');
   SELECT COUNT(*) FROM facts WHERE created_at > datetime('now','-5 minutes');"
```
Non-zero counts after a remember = extraction is live. Before the fix these stayed flat.

## 3. Check the extraction diagnostics (why-is-it-empty)

```bash
python3 - <<'PY'
import sys; sys.path.insert(0,'/home/hermes-pi/mnemosyne')
from mnemosyne.extraction import get_extraction_stats
print(get_extraction_stats())
PY
```
Look for `host` successes. A `host` failure with `reason=...` names the cause directly.

## Rollback (if extraction misbehaves or cost appears)

```bash
cp ~/.config/hermes-gateway.env.bak-prehostllm-20261005 ~/.config/hermes-gateway.env
systemctl --user restart hermes-gateway.service
```
This restores the exact pre-change file (rules-based AAAK only).

## Notes / residual risk

- **Cost:** the host model is a `:free` tier. If it is retired or rate-limited, the
  host path returns None and extraction degrades to empty (the pre-fix behavior) —
  it does **not** fall through to a paid remote (decision A3). Monitor via step 3.
- **Prerequisite:** both `MNEMOSYNE_LLM_ENABLED` and `MNEMOSYNE_HOST_LLM_ENABLED`
  must be true (`local_llm._try_host_llm` gates on both). `MNEMOSYNE_FORCE_LOCAL=1`
  does **not** block the host path.
- **`~/.config/systemd/user/hermes-mnemosyne.env` is orphaned** — no unit references
  it. Editing it has no effect. The live file is `~/.config/hermes-gateway.env`
  (loaded by `hermes-gateway.service.d/override.conf`).
- **Pre-existing debris** (memoria_facts/consolidated_facts/etc.) is unaffected by
  this change — it only fixes *future* extraction. Pruning/rebuilding the debris is
  a separate, later action.
