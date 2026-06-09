# EastMoney Enhanced Lifecycle DI Pilot Evidence

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- generated_at: 2026-05-18T17:43:44.970Z
- git_head: 62f1c102a18b
- scope: GH #78 single pilot only.

## Implementation Evidence

- Added `get_eastmoney_enhanced_adapter_dependency(request)` for FastAPI `Depends()` usage.
- Added `install_eastmoney_enhanced_adapter(app, adapter=None)` to install the instance on `app.state`.
- Added `close_eastmoney_enhanced_adapter(app)` and `EastMoneyEnhancedAdapter.close()` for teardown.
- Wired install/close into `web/backend/app/app_factory.py` lifespan. Canonical `web/backend/app/main.py` wiring is deferred because production Python guardrails block staged edits while `main.py` exceeds the 700-line threshold.
- Retained `get_eastmoney_enhanced_adapter()` compatibility getter.

## Verification Evidence

- RED: `pytest -o addopts= web/backend/tests/test_eastmoney_enhanced_lifecycle_di.py -q --no-cov` initially failed on missing provider/helper imports.
- RED: `pytest -o addopts= web/backend/tests/test_eastmoney_enhanced_lifecycle_di.py::test_eastmoney_enhanced_adapter_close_closes_underlying_session -q --no-cov` failed with missing `close()`.
- GREEN: `pytest -o addopts= web/backend/tests/test_eastmoney_enhanced_lifecycle_di.py -q --no-cov` -> 5 passed.
- Style: `ruff check web/backend/app/main.py web/backend/app/app_factory.py web/backend/app/adapters/eastmoney_enhanced.py web/backend/tests/test_eastmoney_enhanced_lifecycle_di.py` -> All checks passed.
- Syntax: `python -m py_compile web/backend/app/main.py web/backend/app/app_factory.py web/backend/app/adapters/eastmoney_enhanced.py web/backend/tests/test_eastmoney_enhanced_lifecycle_di.py` -> no output.
- Import smoke: adapter-only smoke with `PYTHONPATH=web/backend:.` -> `adapter-import-smoke-ok`.

## Non-Gate Observations

- `web/backend/tests/test_post_rewrite_backend_import_stability.py` still has existing unrelated failures in broad app import/optional dependency recovery paths; it is not caused by this pilot and was not used as the pilot gate.
