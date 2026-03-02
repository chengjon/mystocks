# OpenCode Model Catalog (Managed)

This directory is the single source of truth for model binding and order.
Only `model-catalog.json` needs manual edits for model changes.

## Files

- `model-catalog.json`: ordered model list (OpenCode free + external endpoint non-Gemini)
- `model-stack.env`: env-style mirror of defaults and ordered model sets
- `main.model`: default main model reference
- `small.model`: default lightweight model reference
- `fucai.base_url`: external endpoint base URL
- `fucai.api_key`: external endpoint API key
- `omo.*.model`: model mapping for each oh-my-opencode agent

## Apply changes

1. Edit `model-catalog.json`.
2. Run:

```bash
python3 /opt/claude/mystocks_spec/scripts/opencode/sync_opencode_model_catalog.py
```

3. (Optional) Sync OMC team-member model routing from the same catalog:

```bash
python3 /opt/claude/mystocks_spec/scripts/opencode/sync_omc_model_catalog.py
```

If you also want to update user-level OMC config (`~/.config/claude-omc/config.jsonc`) in one shot:

```bash
python3 /opt/claude/mystocks_spec/scripts/opencode/sync_omc_model_catalog.py --write-user-config
```

This command updates:

- `/opt/claude/mystocks_spec/opencode.json` (project-level OpenCode config)
- `/opt/claude/mystocks_spec/.config/oh-my-opencode.noco.json` (oh-my-opencode config)
- all `*.model` ref files in this directory
- `model-stack.env`
- `.claude/omc.jsonc` (project OMC config)
- `omc-model-stack.env` + `omc.*.model` (OMC model references)

## Notes

- Project-level `opencode.json` has higher precedence than global config when running in this repo.
- External endpoint model list excludes any model whose ID contains `gemini`.
- Provider groups are standardized as `fucai`, `fucai-gpt`, `fucai-claude`, `fucai-mini`.
