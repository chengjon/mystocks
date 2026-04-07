# Split Commit Playbook

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## Current Blocker

`git commit` cannot run inside the current sandbox because the worktree Git metadata lives outside the writable root:

```text
fatal: Unable to create '.../index.lock': Read-only file system
```

The working tree changes are ready, but commits must be created in an environment that can write the worktree
gitdir metadata.

## Current Staging State

Already staged:

- `.env.example`
- `config/.env.example`
- `web/backend/app/core/config.py`
- `src/utils/mongo_runtime_config.py`

Recommended first commit message:

```bash
git commit -m "fix: align runtime config compatibility defaults"
```

## Suggested Commit Sequence

### Commit 1: Runtime compatibility defaults

Files:

- `.env.example`
- `config/.env.example`
- `web/backend/app/core/config.py`
- `src/utils/mongo_runtime_config.py`

If you need to rebuild staging from scratch:

```bash
git restore --staged .
git add .env.example config/.env.example web/backend/app/core/config.py src/utils/mongo_runtime_config.py
git commit -m "fix: align runtime config compatibility defaults"
```

### Commit 2: PM2 path and port convergence

Files:

- `config/pm2/ecosystem.config.js`
- `config/pm2/ecosystem.production.config.js`
- `config/pm2/pm2.config.js`
- `config/pm2/ecosystem.enhanced.config.js`
- `config/pm2/ecosystem.playwright.config.js`
- `config/pm2/ecosystem.playwright.p0.config.js`
- `config/pm2/ecosystem.playwright.p1.config.js`
- `config/pm2/ecosystem.playwright.p1.fixed.config.js`
- `config/pm2/ecosystem.playwright.p2.config.js`

```bash
git restore --staged .
git add config/pm2/ecosystem.config.js \
  config/pm2/ecosystem.production.config.js \
  config/pm2/pm2.config.js \
  config/pm2/ecosystem.enhanced.config.js \
  config/pm2/ecosystem.playwright.config.js \
  config/pm2/ecosystem.playwright.p0.config.js \
  config/pm2/ecosystem.playwright.p1.config.js \
  config/pm2/ecosystem.playwright.p1.fixed.config.js \
  config/pm2/ecosystem.playwright.p2.config.js
git commit -m "refactor: decouple pm2 configs from fixed worktree paths"
```

### Commit 3: Monitoring and active deployment docs convergence

Files:

- `config/monitoring-stack/DEPLOYMENT.md`
- `config/monitoring-stack/MONITORING_STATUS.md`
- `config/monitoring-stack/MONITORING_VERIFICATION_COMPLETE_REPORT.md`
- `config/monitoring-stack/README.md`
- `config/monitoring-stack/config/alertmanager.yml`
- `config/monitoring-stack/config/prometheus.yml`
- `docs/deployment/README.md`
- `docs/operations/deployment-guide.md`
- `web/README.md`

```bash
git restore --staged .
git add config/monitoring-stack/DEPLOYMENT.md \
  config/monitoring-stack/MONITORING_STATUS.md \
  config/monitoring-stack/MONITORING_VERIFICATION_COMPLETE_REPORT.md \
  config/monitoring-stack/README.md \
  config/monitoring-stack/config/alertmanager.yml \
  config/monitoring-stack/config/prometheus.yml \
  docs/deployment/README.md \
  docs/operations/deployment-guide.md \
  web/README.md
git commit -m "docs: converge monitoring and deployment port references"
```

### Commit 4: Redundant backup cleanup and example rename

Files:

- deleted:
  - `src/adapters/akshare_adapter.py.backup_1767777516`
  - `src/adapters/financial_adapter.py.backup_1767777515`
  - `src/core/config_driven_table_manager.py.backup_20251108`
  - `src/core/data_source_manager_v2.py.backup_1767777516`
  - `src/storage/database/execute_example_mysql_only.py`
- added:
  - `src/storage/database/execute_example_postgresql_only.py`

```bash
git restore --staged .
git add -A src/adapters/akshare_adapter.py.backup_1767777516 \
  src/adapters/financial_adapter.py.backup_1767777515 \
  src/core/config_driven_table_manager.py.backup_20251108 \
  src/core/data_source_manager_v2.py.backup_1767777516 \
  src/storage/database/execute_example_mysql_only.py \
  src/storage/database/execute_example_postgresql_only.py
git commit -m "chore: remove redundant backups and rename postgres example"
```

### Commit 5: Compatibility isolation and config relocation

Files:

- `archive/code-compatibility/examples/legacy_adapter.py`
- `scripts/dev/examples/real_project_application/real_project_application_methods/part1.py`
- `scripts/quick_health_check.sh`
- `scripts/tests/legacy/test_sina_integration_final.py`
- `src/adapters/akshare/__init__.py`
- `src/adapters/akshare/legacy_market_data.py`
- `src/adapters/akshare/compat/__init__.py`
- `src/adapters/akshare/compat/legacy_market_data.py`
- deleted:
  - `src/adapters/legacy_adapter.py`
  - `config/sina_finance_only.yaml`
  - `config/data_sources/sina_finance.yaml`
  - `config/datasource.yaml.example`
- added:
  - `config/compatibility/sina_finance/main.yaml`
  - `config/compatibility/sina_finance/sina_finance.yaml`
  - `config/templates/datasource-registry.yaml.example`

```bash
git restore --staged .
git add -A archive/code-compatibility/examples/legacy_adapter.py \
  scripts/dev/examples/real_project_application/real_project_application_methods/part1.py \
  scripts/quick_health_check.sh \
  scripts/tests/legacy/test_sina_integration_final.py \
  src/adapters/akshare/__init__.py \
  src/adapters/akshare/legacy_market_data.py \
  src/adapters/akshare/compat/__init__.py \
  src/adapters/akshare/compat/legacy_market_data.py \
  src/adapters/legacy_adapter.py \
  config/sina_finance_only.yaml \
  config/data_sources/sina_finance.yaml \
  config/datasource.yaml.example \
  config/compatibility/sina_finance/main.yaml \
  config/compatibility/sina_finance/sina_finance.yaml \
  config/templates/datasource-registry.yaml.example
git commit -m "refactor: isolate compatibility assets into archive and compat paths"
```

### Commit 6: Audit trail

Files:

- `TASK-REPORT.md`
- `reports/governance/2026-03-13-compatibility-retention-archival-plan.md`
- `reports/governance/2026-03-13-final-change-classification.md`
- `reports/governance/2026-03-13-split-commit-playbook.md`

```bash
git restore --staged .
git add TASK-REPORT.md \
  reports/governance/2026-03-13-compatibility-retention-archival-plan.md \
  reports/governance/2026-03-13-final-change-classification.md \
  reports/governance/2026-03-13-split-commit-playbook.md
git commit -m "docs: record audit trail and commit classification"
```

## Final Check

After the last commit:

```bash
git status --short
git log --oneline -n 6
```
