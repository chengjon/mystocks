# Final Change Classification

## Purpose

This document classifies the current worktree changes produced during the data source / database / cache /
runtime audit so the branch can be reviewed or committed in coherent batches.

This is not a deployment note. It is a review and batching aid.

## Classification Summary

### A. Runtime Compatibility Fixes

Files:

- `web/backend/app/core/config.py`
- `src/utils/mongo_runtime_config.py`
- `.env.example`
- `config/.env.example`

Intent:

- restore missing Mongo compatibility fields/helpers required by governance tests
- align Celery default Redis URLs with role-aware Redis DB config
- align root/config env templates with actual runtime expectations

Verification:

- `pytest tests/unit/core/test_web_backend_runtime_settings.py tests/unit/core/test_runtime_config_governance.py -q -o addopts=''`
- observed result during execution: `15 passed`

Risk:

- low-to-medium behavior risk
- bounded by targeted tests already executed

Suggested commit boundary:

- can be committed together as one runtime-config batch

## B. PM2 Configuration Convergence

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

Intent:

- remove hard-coded old worktree paths
- converge active/test/production PM2 configs on current worktree-relative roots
- converge default frontend/backend ports to `3020/8020`

Verification:

- `node -c config/pm2/ecosystem.config.js`
- `node -c config/pm2/ecosystem.production.config.js`
- `node -c config/pm2/pm2.config.js`
- `node -c` sweep across active enhanced/playwright configs

Risk:

- medium operational risk
- syntax verified, but runtime PM2 start was not executed in this session

Suggested commit boundary:

- can be committed as a separate PM2/config batch

## C. Monitoring Stack Config And Docs Convergence

Files:

- `config/monitoring-stack/config/prometheus.yml`
- `config/monitoring-stack/config/alertmanager.yml`
- `config/monitoring-stack/README.md`
- `config/monitoring-stack/DEPLOYMENT.md`
- `config/monitoring-stack/MONITORING_STATUS.md`
- `config/monitoring-stack/MONITORING_VERIFICATION_COMPLETE_REPORT.md`

Intent:

- converge host scrape targets and webhook examples from `8000` to `8020`
- remove old `monitoring-stack` absolute path references
- keep active monitoring docs aligned to current runtime port policy

Verification:

- YAML parse via `yaml.safe_load`
- text scans showing no residual:
  - `localhost:8000`
  - `host.docker.internal:8000`
  - `/opt/claude/mystocks_spec/monitoring-stack`

Risk:

- low
- config/doc only

Suggested commit boundary:

- can be committed as one monitoring-docs batch

## D. Active Deployment/Operations Documentation Convergence

Files:

- `docs/deployment/README.md`
- `docs/operations/deployment-guide.md`
- `web/README.md`

Intent:

- replace stale `3000/8000` and auto-range wording with fixed `3020/8020` runtime policy
- align commands, URLs, and troubleshooting examples

Verification:

- text scan confirmed no remaining:
  - `localhost:3000`
  - `3000-3010`
  - `8000-8010`
  - `固定端口 3000`
  - `固定端口 8000`

Risk:

- low
- documentation only

Suggested commit boundary:

- can be committed with monitoring-docs or as a separate docs batch

## E. Low-Risk Redundant Cleanup Already Executed

Deleted files:

- `src/adapters/akshare_adapter.py.backup_1767777516`
- `src/adapters/financial_adapter.py.backup_1767777515`
- `src/core/config_driven_table_manager.py.backup_20251108`
- `src/core/data_source_manager_v2.py.backup_1767777516`

Intent:

- remove timestamped backup duplicates with canonical replacements already present

Verification:

- existence checks confirmed all deleted paths are gone

Risk:

- low
- selected specifically because they were backup duplicates with no active-source references

Suggested commit boundary:

- can be committed as one cleanup batch

## F. Example/Compatibility Path Cleanup

Files:

- deleted: `src/storage/database/execute_example_mysql_only.py`
- added: `src/storage/database/execute_example_postgresql_only.py`

Intent:

- remove misleading `mysql_only` naming for a PostgreSQL-only example

Verification:

- old path absent, new path present
- old name no longer appears in active-source references

Risk:

- low

Suggested commit boundary:

- can be committed with cleanup batch or as example hygiene batch

## G. Compatibility Isolation / Archival Execution

Files:

- deleted/moved:
  - `src/adapters/legacy_adapter.py`
- added/moved:
  - `archive/code-compatibility/examples/legacy_adapter.py`
  - `src/adapters/akshare/compat/__init__.py`
  - `src/adapters/akshare/compat/legacy_market_data.py`
- modified:
  - `src/adapters/akshare/legacy_market_data.py`
  - `src/adapters/akshare/__init__.py`
  - `scripts/dev/examples/real_project_application/real_project_application_methods/part1.py`

Intent:

- archive non-runtime legacy demo adapter
- isolate AkShare legacy sync helpers under `compat/`
- keep a thin compatibility shim at the old path

Verification:

- file existence checks
- `py_compile` on touched Python files
- active-source reference scan

Risk:

- medium
- compatibility-sensitive, but mitigated by keeping the shim and package export layer

Suggested commit boundary:

- should be reviewed as its own compatibility-isolation batch

## H. Compatibility Config Relocation

Files:

- deleted/moved:
  - `config/sina_finance_only.yaml`
  - `config/data_sources/sina_finance.yaml`
  - `config/datasource.yaml.example`
- added/moved:
  - `config/compatibility/sina_finance/main.yaml`
  - `config/compatibility/sina_finance/sina_finance.yaml`
  - `config/templates/datasource-registry.yaml.example`
- modified:
  - `scripts/quick_health_check.sh`
  - `scripts/tests/legacy/test_sina_integration_final.py`

Intent:

- physically isolate compatibility-only Sina Finance config
- move standalone datasource registry example into templates

Verification:

- file existence checks
- `DataSourcesLoader` load test against new Sina Finance location
- `py_compile scripts/tests/legacy/test_sina_integration_final.py`

Risk:

- medium
- script/test consumer sensitive, but minimal known consumers were updated and loader test passed

Suggested commit boundary:

- should be reviewed as its own compatibility-config batch

## I. Audit Trail / Reporting

Files:

- `TASK-REPORT.md`
- `reports/governance/2026-03-13-compatibility-retention-archival-plan.md`
- `reports/governance/2026-03-13-final-change-classification.md`

Intent:

- preserve evidence, reasoning, risk notes, and execution log

Risk:

- none operationally

Suggested commit boundary:

- include in every relevant batch, or commit last as audit trail

## Suggested Batch Order

1. Runtime compatibility fixes
2. PM2 convergence
3. Monitoring and deployment docs convergence
4. Redundant backup cleanup + example rename
5. Compatibility isolation execution
6. Compatibility config relocation
7. Reporting / audit trail finalization

## Notes

- If the branch is committed in one shot, this classification still provides review structure.
- If the branch is split, the highest-risk separable batches are:
  - PM2 convergence
  - compatibility isolation
  - compatibility config relocation
