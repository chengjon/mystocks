# Credential Rotation And Publish Checklist

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、任务方案或执行矩阵，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值和时间线如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


Date: 2026-03-17

## Rotate First

1. Provider API keys
   Files previously affected:
   `./config/opencode_optimized_zeabur.json`
   `./.config/opencode-opimized.json`
   `./.config/opencode/model/fucai.api_key`
   `./.config/opencode/model/model-catalog.json`

2. Web reader bearer token
   Files previously affected:
   `./.config/oh-my-opencode.noco.json.bak.20260215`
   `./.config/oh-my-opencode.noco.json.bak.20260228-codex`
   `./.config/opencode.json.bak.20260228-codex`

3. PostgreSQL password
   Previously leaked value was embedded in DSN form and plain password form.
   Rotate the actual database user password, then update all real runtime env stores outside git.

4. Any service or docs derived from the same credentials
   Check CI secrets, PM2 env files, Docker `.env` files, deployment platform variables, and personal shell profiles.

## Before History Rewrite

1. Commit the current sanitized working tree you want to preserve.
2. Confirm `.config` local provider files are no longer tracked by Git.
3. Confirm `git grep` in the committed branch tip does not find the real leaked literals.
4. Export the old leaked values only in your current shell for the rewrite script.

## Rewrite Command

```bash
export OLD_PROVIDER_API_KEY='...'
export OLD_FUCAI_API_KEY='...'
export OLD_MODEL_CATALOG_API_KEY='...'
export OLD_WEB_READER_TOKEN='...'
export OLD_JWT_TOKEN='...'
export OLD_POSTGRES_PASSWORD='...'
export OLD_INTERNAL_HOST='...'

./scripts/maintenance/public-history/rewrite_public_history.sh /path/to/repo /tmp/mystocks_spec-public-sanitized.git
```

## Before Force Push

1. Inspect `/tmp/mystocks_spec-public-sanitized.git` commit log.
2. Re-run literal checks against the rewritten mirror.
3. Check that removed files are absent from rewritten history:
   `.archive/sensitive-backups/_.env.backup.20251124_232409`
   `.claude-trace/log-2025-11-06-11-23-22.jsonl`
   `.config/opencode-opimized.json`
   `archive/legacy-root-archived/services/a-stock-risk-management/.parcel-cache/*`

## After Force Push

1. Ask collaborators to discard old clones and re-clone.
2. Invalidate CI caches and build artifacts.
3. Revoke old provider sessions/tokens if the vendors support it.
4. Watch GitHub code search and secret scanning results until the new baseline settles.
