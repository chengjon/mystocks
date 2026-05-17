# ADR-0001: Core 目录按职责拆分子目录

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **Status**: Proposed
> **Date**: 2026-05-16
> **Decision makers**: Backend team

## Context

`app/core/` 当前包含 75 个 Python 文件、26,429 行代码，平铺在单一目录下。STANDARDS.md §三.1 要求"同一职责只允许一个主实现"，但 Core 目录的职责边界模糊，导致：

- 12 个缓存相关文件（部分在根级，部分在 `cache/` 子目录）
- 10 个数据库相关文件
- 6 个 SocketIO 文件
- 3 个异常处理文件（`exception_handler.py` + `exception_handlers.py` + `global_exception_handlers.py`）
- 3 个校验文件（`validation.py` + `validators.py` + `validation_messages.py`）
- 21 个未分类文件（`other` 类别占 6,429 行，是最大的一组）

## Decision

将 Core 按功能域拆分为子目录：

```
core/
├── config/           # config.py, secure_config.py, celery_app.py
├── database/         # database*.py, sync_db_manager.py, tdengine_*.py
├── cache/            # (已存在，合并根级 cache_*.py)
├── socketio/         # socketio_*.py, _socketio_manager_singleton.py
├── security/         # security.py, encryption.py, password_policy.py, casbin_*.py
├── sse/              # sse_*.py
├── exception/        # exception*.py, error_*.py, error_codes.py
├── validation/       # validation*.py, validators.py
├── logging/          # (已存在)
├── middleware/        # (已存在)
├── event/            # event_bus.py
├── responses.py      # 保留根级（被广泛导入）
└── readiness.py      # 保留根级（被广泛导入）
```

重复文件处理策略：
- `exception_handler.py` → canonical；`exception_handlers.py` + `global_exception_handlers.py` → 合并或删除
- `validation.py` → canonical；`validators.py` → 合并
- `cache_manager.py` + `cache_utils.py` → 合并到 `cache/` 子目录

## Consequences

**Positive**:
- 每个子域职责清晰，新文件有明确归属
- 消除重复实现（exception ×3, validation ×3, cache ×12）
- 与 STANDARDS.md §三.1 对齐

**Negative**:
- 大量 import 路径需要更新（影响面需通过 GitNexus impact 分析）
- 需要创建兼容 wrapper 或 re-export 避免一次性全量迁移
- 迁移过程必须按 OpenSpec 审批执行

**Migration strategy**: 按子域分批迁移，每批创建 `__init__.py` re-export 旧路径，保持向后兼容。
