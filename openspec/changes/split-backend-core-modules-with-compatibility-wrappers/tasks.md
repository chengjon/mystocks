> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## 1. Pre-Implementation Evidence

- [x] 1.1 Confirm orchestration artifact: `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md`.
- [x] 1.2 Generate current Core file tree.
- [x] 1.3 Generate import reference counts for high-risk Core paths.
- [x] 1.4 Classify candidate modules by import compatibility strategy.
- [x] 1.5 Identify test monkeypatch paths and runtime startup dependencies.
- [x] 1.6 Identify lifecycle-owned Core modules that must coordinate with E before movement.

## 2. Design Decisions

- [x] 2.1 Define canonical target package per Core domain.
- [x] 2.2 Define wrapper strategy for renamed modules.
- [x] 2.3 Confirm `app.core.logger` remains canonical.
- [x] 2.4 Define wrapper retirement criteria.
- [x] 2.5 Define rollback per batch.
- [x] 2.6 Define import compatibility matrix output path and owner.

## 3. Implementation Batches

- [ ] 3.1 Move low-risk pure helpers first.
- [ ] 3.2 Introduce same-name packages with `__init__.py` re-exports.
- [ ] 3.3 Move renamed modules with old-path wrapper modules.
- [ ] 3.4 Avoid broad database/security/socketio/logger moves until import smoke, monkeypatch evidence, and E lifecycle coordination are ready.

## 4. Verification

- [ ] 4.1 Run import smoke for old and new Core paths, including `PYTHONPATH=web/backend python -c "from app.core.logger import logger; import app.core.database; import app.core.cache_manager; import app.core.security; import app.core.socketio_manager"`.
- [ ] 4.2 Run targeted tests for moved modules.
- [ ] 4.3 Run PM2 backend startup smoke with `./scripts/run_pm2_integration_workflow.sh` or a named equivalent approved by the implementation issue.
- [ ] 4.4 Run `/api/health/services`, `/health/ready`, and `/api/health/ready` smoke after runtime-affecting moves.
- [ ] 4.5 Confirm no unintended route or OpenAPI drift.

## 5. Closure

- [ ] 5.1 Update docs with canonical Core paths and retained wrappers.
- [ ] 5.2 Record wrapper retirement candidates.
- [ ] 5.3 Defer deletion until references are clear and rollback is proven.
