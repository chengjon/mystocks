# Design — ExtraSourceAdapter Contract

> 本文档记录 C3 阶段一的技术决策。所有结论来自 2026-07-02 七轮 grilling 压测。

## 1. 决策时间线

| 轮次 | 关键决策 | 否决项 |
|---|---|---|
| R1 | 静态注册期硬校验 + 运行时不做 fallback | 动态约束(违反顶层"OpenStock 是统一网关") |
| R2 | fallback 完全收敛 OpenStock 内部(D 方案) | A(单点故障)/B(同名覆盖)/C(override 开关) |
| R3 | C3 拆两阶段;阶段二完整阻塞于 OpenStock 通用 fallback 框架 | 跨仓改动 / 消费者侧兜底 |
| R4 | TEMP_OVERRIDE 强制 expires_on + CI 阻断;跨仓 follow-up 双仓 issue 互链 | 单仓 issue / 第三方看板 |
| R5 | 阶段一独立成完整提案 | 阶段二混入本提案 backlog |
| R6 | 接口:`ExtraSourceMeta` + `fetch()` + `register_extra_source()` | 字段缺失(name) |
| R7 | fetch 返回 `ExtraSourceResult`(字段化,无 typed schema) | Dict[str, Any] / 强类型 schema |

## 2. 三层契约详解

### Layer 1 — ExtraSource 注册与校验(本提案范围)

**校验时机**:启动 lifespan(同步,无网络调用)

**校验规则**:
1. 加载 OpenStock 静态 70 category 清单(来源:`DATA_CAPABILITY_SCOPE.md`,以代码常量形式固化于 `extra_source/registry.py`)
2. 对每个 `register_extra_source(adapter)` 调用:
   - `adapter.get_meta().category` 必须不在静态清单内
   - 若 `expires_on is None`:常规 ExtraSource,通过
   - 若 `expires_on is not None`:TEMP_OVERRIDE,通过;CI 流水线单独校验过期
   - 若 `category` 在静态清单内:抛 `ExtraSourceCategoryConflictError`,启动 fail
3. 同名 `name` 注册拒绝(每个 adapter 必须唯一标识)

**OpenStock 静态清单维护**:
- 当前从 `DATA_CAPABILITY_SCOPE.md` 手动同步(2026-07-02 快照,70 项)
- 未来 OpenStock 落地通用 fallback 框架后(Layer 2 解锁),可改用 OpenStock 启动期发布的 `/sources/categories` 静态 endpoint(目前不存在)
- 同步责任:B4.014 follow-up,非本提案阻塞

### Layer 2 — OpenStock 内部容灾(本提案完全排除)

**当前状态**(2026-07-02 核查):
- OpenStock `adapter_registry` 内仅 1 个硬编码 fallback:`KLINES` 主 eltdx → 备 akshare
- 其余 70 类别(包括所有 FundFlow 相关)均为单 provider
- 无通用 `register_fallback(category, primary, secondary)` API
- 无配置驱动 fallback 触发

**为何排除**:
- 跨仓改动违反治理边界(mystocks_spec 提案不应夹带 OpenStock 仓代码改动)
- OpenStock 落地通用 fallback 框架前,任何"标准 category 容灾"都是空中楼阁
- 消费者侧做 fallback(Round 2 B/C 方案)直接违反 Round 2 D 决策

**Layer 2 落地后影响**:
- Layer 1 完全不变
- Layer 3 错误模型不变(消费者永远只看 OpenStock 统一错误)
- 新增能力:OpenStock 单 provider 故障时不再返回 `DATA_GATEWAY_UNAVAILABLE`,自动切备源

### Layer 3 — 故障处理分工

**消费者侧永远不做**:
- 检测 OpenStock provider 是否健康
- 在 OpenStock 故障时切换到 extra source 做同名 category 兜底
- 实现 OpenStock 已有 category 的"备份版本"

**消费者侧只做**:
- 调用 OpenStock 标准品类接口
- 调用 ExtraSource(只针对 OpenStock 永久无覆盖的 category)
- 收到 `DATA_GATEWAY_UNAVAILABLE` 错误时业务告警,不自动 fallback

## 3. TEMP_OVERRIDE 治理细则

### 字段语义

```python
@dataclass(frozen=True)
class ExtraSourceMeta:
    name: str                     # 全局唯一,kebab-case
    category: str                 # 全局唯一,UPPER_SNAKE_CASE
    expires_on: Optional[str]     # ISO date "YYYY-MM-DD"
                                 # None = 常规 ExtraSource
                                 # not None = TEMP_OVERRIDE,必填日期
```

### expires_on 取值规则

| OpenStock 排期状态 | expires_on 上限 |
|---|---|
| 有明确版本/迭代计划 | 计划上线日期 + 1 迭代缓冲 |
| 有规划无排期 | 90 天硬上限 |
| 无规划但消费者提了 OpenStock issue | 90 天(issue 关闭后转有排期或下架) |
| 无规划无 issue | 拒绝 TEMP_OVERRIDE,改为常规 ExtraSource |

### CI 过期阻断(实施细节)

- 流水线步骤:扫描所有 `register_extra_source` 调用 → 提取 expires_on → 与当前日期比对
- 过期处理:CI fail,阻断合并
- 提前 7 天告警:CI warn(不阻断),通知 owner
- 延期规则:tasks.md 列出,本提案不锁定具体延期机制(实施时决定)
- 到期后行为(CI 阻断 = 强制决策点):
  - 若 OpenStock 已覆盖该 category → 删除 TEMP_OVERRIDE,迁移到 OpenStockClient
  - 若 OpenStock 仍未覆盖 → 人工重评估,二选一:(a) 转为常规 ExtraSource(`expires_on=None`,需证明 OpenStock 永久无规划);(b) 延期(重设 `expires_on`,需审批,延期次数记入 issue 追溯)
  - 禁止"到期静默续期"——CI 阻断必须触发上面某条决策,避免 TEMP_OVERRIDE 沦为永久技术债

## 4. Wave 2/3 归属判定附录(B4.014 应用)

### 判定规则

| 信号 | 归属 |
|---|---|
| 在 `DATA_CAPABILITY_SCOPE.md` 静态清单内 | 禁止 ExtraSource,只能走 OpenStock(如 OpenStock 当前无 provider,等 OpenStock 落地) |
| OpenStock roadmap 已规划,暂未开发 | TEMP_OVERRIDE ExtraSource |
| OpenStock 无规划,且无类似业务需求 | 常规 ExtraSource |
| OpenStock 无规划,但属大众需求 | 提案进 OpenStock,本提案不直接归属 |

### B4.014 Wave 2/3 八方法逐项归属

| akshare 函数 | OpenStock category | 归属 |
|---|---|---|
| `stock_em_bigdeal` | `MARKET_BIG_DEAL`(规划中) | TEMP_OVERRIDE |
| `stock_hsgt_fund_flow_detail_em` | 无规划 | 常规 ExtraSource |
| `stock_hsgt_south_net_flow_in_em` | 无规划(南向) | 常规 ExtraSource |
| `stock_hsgt_south_acc_flow_in_em` | 无规划(南向) | 常规 ExtraSource |
| `stock_hsgt_north_net_flow_in_em` | `NORTHBOUND_FLOW`(已注册) | 禁止 ExtraSource,迁移走 OpenStock |
| `stock_hsgt_north_acc_flow_in_em` | `NORTHBOUND_FLOW`(已注册) | 禁止 ExtraSource,迁移走 OpenStock |
| `stock_hsgt_hold_stock_em` | `NORTHBOUND_HOLDING`(已注册) | 禁止 ExtraSource,迁移走 OpenStock |
| `stock_fund_flow_big_deal` | 同 `stock_em_bigdeal` | TEMP_OVERRIDE |

### 双仓 follow-up 跟踪

每个 `TEMP_OVERRIDE` 必须双仓开 issue:
- mystocks_spec 仓:标 `cross-repo-dependency` + `temp-override-backlog`,链 OpenStock issue
- OpenStock 仓:对应 category 注册需求 issue,链回 mystocks_spec issue

状态联动:
- OpenStock issue 关闭(category 已上线)→ mystocks_spec CI 提醒删除 TEMP_OVERRIDE
- mystocks_spec 删除 TEMP_OVERRIDE 前,OpenStock issue 不得关闭

## 5. 接口签名定稿

```python
# web/backend/app/services/extra_source/contract.py

from dataclasses import dataclass
from typing import Any, Optional, Protocol


@dataclass(frozen=True)
class ExtraSourceMeta:
    name: str
    category: str
    expires_on: Optional[str] = None


@dataclass(frozen=True)
class ExtraSourceResult:
    data: Any
    provider_used: str


class ExtraSourceAdapter(Protocol):
    def get_meta(self) -> ExtraSourceMeta: ...
    def fetch(self, params: dict[str, Any]) -> ExtraSourceResult: ...


class ExtraSourceCategoryConflictError(RuntimeError):
    """Raised when an ExtraSource adapter declares a category that
    overlaps with OpenStock's static 70-category inventory."""


class ExtraSourceNameConflictError(RuntimeError):
    """Raised when an ExtraSource adapter is registered with a `name`
    that is already present in the registry. Names MUST be globally
    unique so that logs, metrics, and CI attribution remain
    unambiguous."""


# web/backend/app/services/extra_source/registry.py

OPENSTOCK_STATIC_CATEGORIES: frozenset[str] = frozenset({
    # 70 items, source: DATA_CAPABILITY_SCOPE.md 2026-07-02 snapshot
    # ... (full list in module)
})
# Drift detection:
#   - 当前:每季度人工比对一次 DATA_CAPABILITY_SCOPE.md(责任人:B4.014 follow-up)
#   - 未来:OpenStock 落地 /sources/categories 静态 endpoint 后,改为启动期动态加载

def register_extra_source(adapter: ExtraSourceAdapter) -> None:
    meta = adapter.get_meta()
    if meta.category in OPENSTOCK_STATIC_CATEGORIES:
        raise ExtraSourceCategoryConflictError(
            f"ExtraSource '{meta.name}' declares category '{meta.category}' "
            f"which overlaps with OpenStock static inventory"
        )
    if meta.name in _registered:
        raise ExtraSourceNameConflictError(
            f"ExtraSource name '{meta.name}' is already registered "
            f"by another adapter"
        )
    _registered[meta.name] = adapter
```

## 6. 与现有架构的关系

| 现有组件 | 与 ExtraSource 关系 |
|---|---|
| `OpenStockClient` (`web/backend/app/services/openstock_client.py`) | 同级,均被 route handler 显式调用(handler 决定调哪个) |
| `ExtraSourceRouter` (`web/backend/app/services/extra_source/router.py`,本提案新增) | 接受 `category` + `params`,查 registry 命中则调 adapter,未命中返回 `UNSUPPORTED_CATEGORY`;adapter `fetch()` 异常包装为 `DATA_GATEWAY_UNAVAILABLE` 错误信封 |
| `HybridDataSource` (`web/backend/app/services/data_source_factory/data_source_mode.py`) | **不动**。endpoint-driven 抽象层(`get_data(endpoint, params)`),内部 Real→Mock 二元 fallback,与 category 无关。语义错位:把 category-driven 路由塞进 endpoint-driven 层会污染其抽象 |
| `src/data_sources/factory.py` (旧 factory, 514 行) | 不动,待 C2 提案处置 |
| `FundFlowMixin` (`src/adapters/akshare/market_adapter/fund_flow.py`) | Wave 2/3 落地后,8 方法可改用 ExtraSourceRouter 实现(独立 follow-up) |

### 路由层设计选择(2026-07-02 实施期修订)

初稿设想"`HybridDataSource` fallback 链扩展为 OpenStock → ExtraSource → Mock",实施期核查代码发现错位:

- `HybridDataSource.get_data(endpoint, params)` 是 endpoint-driven,不知道 category 概念
- `real_source` 是 generic HTTP wrapper,不感知 OpenStockClient vs ExtraSource 的差异
- 在 HybridDataSource 内注入 `extra_source_registry` 需要所有调用点改签名,污染 endpoint-driven 抽象

**正确路径**:ExtraSource 路由独立成 `ExtraSourceRouter`,与 `HybridDataSource` 并列存在。route handler 决定调用哪个:

```text
handler 收到请求
├─ category ∈ OPENSTOCK_STATIC_CATEGORIES  → OpenStockClient.fetch(category, ...)
├─ category ∈ ExtraSourceRouter.registered_categories() → router.fetch(category, params)
└─ else → UNSUPPORTED_CATEGORY 错误信封
```

`ExtraSourceRouter` 不依赖 HybridDataSource,避免污染现有 endpoint-driven 抽象。

## 7. 不在本提案范围的后续工作

| 后续提案 | 范围 |
|---|---|
| C1 — 客户端构造点收口 | `get_openstock_market_client` per-route rebuild 收敛到 lifespan singleton |
| C2 — 两个 DataSourceFactory 收口 | 旧 `src/data_sources/factory.py` 与新 `data_source_factory/` 二选一 |
| C7 — ExtraSource 类型化 | `ExtraSourceResult.data` 引入 typed schema(等 OpenStock `fields_typed` v3 在生产验证 1 月后) |
| Layer 2 — OpenStock 内部 fallback 框架 | 跨仓,本提案仅文档引用 |
| B4.014 Wave 2/3 落地 | 使用本提案提供的契约实现 8 个 akshare 方法的 ExtraSource 版本 |
