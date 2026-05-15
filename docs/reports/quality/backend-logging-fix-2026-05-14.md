# MyStocks 日志体系整改分析

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **来源**: `docs/reports/quality/backend-audit-2026-05-14.md` §二.2 深化
> **红线基准**: `architecture/STANDARDS.md` §一.4「严禁使用 `print`，必须统一使用 `from app.core.logger import logger`」
> **审计日期**: 2026-05-14
> **执行校准**: 2026-05-15

---

## 〇、2026-05-15 执行记录

### 已完成

| # | 动作 | 结果 |
|---|------|------|
| 1 | 创建 `app/core/logger.py` 统一门面 | ✅ 委托到 `app.core.logging.structured.StructuredLogger`（loguru） |
| 2 | 修复 `app/core/logging/__init__.py` tracing 可选导入 | ✅ 解决 opentelemetry ImportError |
| 3 | 消除 `print()` 违规 | ✅ **0 处残留**（原 115 处，跨 4 文件） |
| 4 | `from app.core.logger import logger` 可用 | ✅ 验证通过 |

### print() 清理明细

| 文件 | 原数量 | 处理方式 |
|------|--------|----------|
| `mock/coverage_report.py` | 36 | 全部替换为 `logger.info()` / `logger.error()` |
| `mock/simple_coverage_check.py` | 17 | 全部替换为 `logger.info()` / `logger.error()` |
| `mock/mock_data/factory.py` | 6 | `__main__` 测试块中替换为 `logger.info()` |
| `schemas/base_schemas.py` | 5 | `__main__` 测试块中替换为 `logging.getLogger()` |

> 注：`watchlist_service.py.bak2/bak3/before_schema_update` 中的 print() 随文件删除一并清除（共 51 处）。

---

## 一、当前状态（已更新）

### 1.1 `print()` 违规 ✅ 已清零

**已全部清理**。代码扫描确认 0 处 `print()` 残留。

### 1.2 Logger 生态现状

后端实际存在 **三套日志体系**（原审计仅识别两套）：

| 日志体系 | 使用文件数 | 实际底层 |
|----------|-----------|---------|
| `logging.getLogger(__name__)` (stdlib) | **165** | Python stdlib logging |
| `structlog.get_logger()` | **84** | structlog |
| `loguru` via `StructuredLogger` | 1 (core/logging/) | loguru |

统一入口已创建：`from app.core.logger import logger`（委托到 loguru StructuredLogger）。

| 日志体系 | 使用模块 | 典型用法 |
|----------|----------|----------|
| `logging` (stdlib) | `main.py`, `api/*.py`, `services/*.py`, `repositories/`, `db/` | `logger = logging.getLogger(__name__)` |
| `structlog` | `app_factory.py`, `core/*.py`(大部分), `gateway/`, `utils/risk_utils.py` | `logger = structlog.get_logger()` |

**分裂影响**：
- `logging` 使用 `%` 格式化：`logger.info("value: %s", val)`
- `structlog` 使用关键字参数：`logger.info("event", key=val)`
- 两套格式在日志输出中不一致，运维排查时需要适配两种模式
- `structlog` 自带结构化上下文绑定，`logging` 需要手动构建 `extra` 字典

### 1.3 `main.py` 日志初始化

`main.py` 仅配置了 `logging.basicConfig()`，未对 `structlog` 做统一配置：

```python
log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("app.main")
```

`structlog` 模块自行处理输出，未经统一配置，可能导致格式不一致。

---

## 二、整改方案

### 2.1 创建统一 Logger 模块

`architecture/STANDARDS.md` 当前要求统一入口为 `from app.core.logger import logger`。因此整改应优先创建或保留 `app/core/logger.py` 作为 canonical 导入面；如内部实现拆到 `app/core/logging/logger.py`，也必须由 `app/core/logger.py` 做薄 wrapper。

创建 `app/core/logger.py`：

```python
"""统一日志入口 — MyStocks canonical logger"""

import logging
import structlog
from app.core.config import settings

# --- 共享配置 ---
LOG_LEVEL = getattr(logging, settings.log_level.upper(), logging.INFO)

# --- structlog 配置 ---
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if settings.debug else structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# --- 标准 logging 配置（兼容层）---
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# --- 统一导出 ---
logger = structlog.get_logger("mystocks")


def get_logger(name: str = "mystocks"):
    """获取结构化 logger 实例"""
    return structlog.get_logger(name)
```

### 2.2 全模块替换方案

| 替换目标 | 旧代码 | 新代码 |
|----------|--------|--------|
| Core 模块 | `logger = structlog.get_logger()` | `from app.core.logger import get_logger` + `logger = get_logger(__name__)` |
| API 模块 | `logger = logging.getLogger(__name__)` | `from app.core.logger import get_logger` + `logger = get_logger(__name__)` |
| Services | `logger = logging.getLogger(__name__)` | `from app.core.logger import get_logger` + `logger = get_logger(__name__)` |
| Repositories | `logger = logging.getLogger(__name__)` | `from app.core.logger import get_logger` + `logger = get_logger(__name__)` |
| main.py | `logging.getLogger("app.main")` | `from app.core.logger import get_logger` + `logger = get_logger("app.main")` |

### 2.3 日志调用适配

由于统一为 `structlog`，调用方式需从 `%` 格式化改为关键字参数：

```python
# 旧 (logging)
logger.info("Processing %s: %d items", symbol, count)
logger.error("Failed: %s", error)

# 新 (structlog — 统一后)
logger.info("Processing", symbol=symbol, count=count)
logger.error("Failed", error=str(error))
```

**兼容策略**：`structlog` 的 `PositionalArgumentsFormatter` 处理器支持 `%` 格式化作为过渡期兼容。可在 Phase 1 保留 `%` 格式，Phase 2 逐步迁移为结构化参数。

---

## 三、实施路线

### Phase 1: print() 清零与 logger facade 复核（已完成，门禁保留）

| 动作 | 说明 |
|------|------|
| 复核 `app/core/logger.py` | 当前已存在，作为 `STANDARDS.md` 要求的统一 facade |
| 复核 `mock/coverage_report.py` | 当前已无 `print()`，保留 `logger.info()` / `logger.error()` |
| 复核 `mock/simple_coverage_check.py` | 当前已无 `print()`，保留 `logger.info()` / `logger.error()` |
| 复核 `web/backend/app` | 2026-05-15 扫描结果为 0 处 `print()` |

**验收**: `grep -rn "print(" web/backend/app/ --include="*.py" | grep -v __pycache__` 返回 0 结果。

### Phase 2: 统一 Core 层（1 天）

Core 层已有大量 `structlog` 使用，替换剩下的 `logging.getLogger` 调用：

```bash
# 扫描仍使用 logging 的 core 文件
grep -rl "logging.getLogger" web/backend/app/core/ --include="*.py"
```

逐文件替换为 `from app.core.logger import get_logger`，并保留模块名：

```python
logger = get_logger(__name__)
```

### Phase 3: 统一 API + Services 层（2 天）

这是最大批量，API 和 Services 文件几乎全部使用 `logging.getLogger(__name__)`。

**策略**：通过脚本批量替换 import 行，逐文件验证。

```bash
# 查找所有需要替换的文件
grep -rl "logging.getLogger" web/backend/app/api/ web/backend/app/services/ \
  --include="*.py" | grep -v __pycache__
```

**替换模板**：
```
旧:
import logging
...
logger = logging.getLogger(__name__)

新:
from app.core.logger import get_logger
...
logger = get_logger(__name__)
```

### Phase 4: 迁移 % 格式化为结构化参数（可选，长期）

当所有模块统一 logger 后，逐步将 `%` 格式化调用迁移为 `structlog` 关键字参数风格。

---

## 四、影响范围

| 层 | 受影响文件数（估计） | 风险 |
|----|---------------------|------|
| mock/ | 2 | 无（工具脚本） |
| core/ | ~5（仍有 logging 的） | 低（import 替换） |
| api/ | ~40 | 中（批量替换，需验证） |
| services/ | ~30 | 中（同上） |
| repositories/ | ~10 | 低 |
| gateway/ | ~5 | 低（已用 structlog） |
| 其他 (db/, utils/, tasks/) | ~10 | 低 |

---

## 五、验收标准

| 检查项 | 命令 | 通过标准 |
|--------|------|----------|
| 零 `print()` | `grep -r "print(" web/backend/app/ --include="*.py" \| grep -v __pycache__` | 0 结果 |
| 统一 logger 导入 | `grep -r "logging.getLogger" web/backend/app/ --include="*.py" \| grep -v __pycache__` | 仅 `core/logger.py` 或其内部实现模块使用 |
| PM2 日志可读性 | `pm2 logs mystocks-backend --lines 20` | 时间戳 + 级别 + 结构化字段完整 |
| 服务正常运行 | `curl http://localhost:8020/api/health/services` | 返回 healthy |

---

*前置文档: `docs/reports/quality/backend-audit-2026-05-14.md` §二.2*
