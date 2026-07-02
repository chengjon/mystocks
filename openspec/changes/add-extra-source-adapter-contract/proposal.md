# Change: Add ExtraSourceAdapter Contract for Consumer-Side Auxiliary Data Sources

> **Scope**: `web/backend/app/services/` — new module for ExtraSource registration + routing
> **Parent context**: `externalize-data-source-provider-to-openstock` (B4.014 系列)。本提案契约接口独立于 B4.014,首轮落地场景为 B4.014 Wave 2/3
> **Architecture anchor**: `数据流分层规则.md`(Obsidian Hermes vault)— OpenStock 是数据网关,消费者可补充 OpenStock 未覆盖的空白品类

## Why

用户的顶层架构愿景(2026-07-02 grilling 会议)明确:

> "openstock 将作为其它项目(包括 mystocks_spec, quantix-rust 等)的数据源来发展...其他项目是 openstock 的消费者,但也可以接入另外的数据源(**最好是 openstock 未提供的,而不是已有的**)"

这条愿景在当前代码里**没有契约层落地**。具体症状:

1. **B4.014 Wave 2/3 的 8 个 akshare 直连方法** (`fund_flow.py:114-280`) 处于"OpenStock 没有 → 消费者直连 ak"的灰色地带。没有机制判断这些方法应该:
   - 进 OpenStock(提案新增 category)
   - 走消费者 extra source(本提案范围)
   - 还是临时过渡(`TEMP_OVERRIDE`)

2. **`HybridDataSource` 的 fallback 语义只能 Real→Mock**(`data_source_mode.py:404-466`),无法表达"OpenStock 没有 → 用 extra source"。所有"OpenStock 未覆盖"的需求都只能绕过 factory 直接 `import akshare`,反向侵蚀 OpenStock 边界。

3. **跨仓 provider-level fallback 不存在**。OpenStock 当前只有硬编码单点 fallback(eltdx→akshare for KLINES,见 `adapter_registry`),其余 70 类别均单 provider。消费者侧如果尝试给 OpenStock 已有 category 兜底,会重新引入 Round 2 已拒绝的"消费者侧容灾"反模式。

## What Changes

### 三层契约(grilling 收口结论)

**Layer 1 — ExtraSourceAdapter 接口与静态注册校验**(本提案核心)

新增模块 `web/backend/app/services/extra_source/`,定义:

```python
@dataclass(frozen=True)
class ExtraSourceMeta:
    name: str                          # adapter 标识(日志/监控/expires_on 追责)
    category: str                      # 必须不在 OpenStock 静态 70 category 内
    expires_on: Optional[str]          # ISO date,仅 TEMP_OVERRIDE 必填

@dataclass(frozen=True)
class ExtraSourceResult:
    data: Any                          # 字段化但暂不类型化(对齐 OpenStockFetchResult)
    provider_used: str

class ExtraSourceAdapter(Protocol):
    def get_meta(self) -> ExtraSourceMeta: ...
    def fetch(self, params: dict) -> ExtraSourceResult: ...

def register_extra_source(adapter: ExtraSourceAdapter) -> None: ...
    # 启动期执行:
    # 1. 与 OpenStock 静态 70 category 比对,重叠则启动 fail
    # 2. 校验 expires_on(TEMP_OVERRIDE 必填,常规 None)
```

**Layer 2 — 标准 category 容灾**(完全不属于本提案,完全收敛于 OpenStock 内部)

OpenStock 现状:硬编码单点 fallback(eltdx→akshare for KLINES),其余 70 类别单 provider。

**本提案完全不涉及 Layer 2**。阶段二(标准 category 内部多 provider 容灾调度)需要 OpenStock 仓先落地通用 `register_fallback(category, primary, secondary)` 框架(暂称 `OPENSTOCK-PROVIDER-FALLBACK-FRAMEWORK`),目前无该提案/issue/计划。阶段二待该框架落地后**另开提案承载**,不进本文档。

**Layer 3 — 故障处理分工边界**(规范文档)

| 故障层级 | 处置方 | 消费者侧行为 |
|---|---|---|
| OpenStock 单 provider 故障 | OpenStock 内部(目前无通用框架,等于该 category 不可用) | 收到 `DATA_GATEWAY_UNAVAILABLE` 错误,业务告警 |
| OpenStock 全 provider 离线 | OpenStock 统一返回错误 | 同上 |
| OpenStock 永久无覆盖的 category | ExtraSourceAdapter 提供 | 通过 `register_extra_source` 静态注册 |

### TEMP_OVERRIDE 临时过渡机制

适用于"OpenStock 已规划但暂未开发"的标准品类(例如 B4.014 Wave 2 的 `MARKET_BIG_DEAL`)。约束:

- `expires_on` ISO date 字段必填
- 无明确 OpenStock 排期时上限 90 天
- CI 过期阻断(具体实施细节由 tasks.md 定义)

### Wave 2/3 归属判定附录(本提案提供,作为后续各域迁移判定模板)

| akshare 函数 | OpenStock category 状态 | 归属 |
|---|---|---|
| `stock_em_bigdeal` | 标准规划(`MARKET_BIG_DEAL`)但未开发 | TEMP_OVERRIDE ExtraSource + 双仓 issue |
| `stock_hsgt_*` 南向/明细 6 个 | OpenStock 无规划 | 常规 ExtraSource |
| 现有 `NORTHBOUND_FLOW/HOLDING` | OpenStock 标准品类(已注册) | 禁止 ExtraSource 同名 |

具体 8 个方法的归属清单详见 `design.md` 附录。

## Impact

**新增**:
- `web/backend/app/services/extra_source/__init__.py`
- `web/backend/app/services/extra_source/contract.py`(接口定义)
- `web/backend/app/services/extra_source/registry.py`(注册入口 + 静态校验)
- `openspec/specs/.../extra-source-adapter/spec.md`(delta spec)

**修改**:
- `web/backend/app/services/data_source_factory/data_source_mode.py`(`HybridDataSource` 路由层感知 ExtraSource registry)
- 启动 lifespan 注入 ExtraSource 注册步骤

**不修改**:
- OpenStock 仓任何代码(跨仓改动违反治理边界)
- B4.014 Wave 1 已完成的 FundFlowMixin 部分
- 当前 `src/data_sources/factory.py`(旧 factory)—— 待 C2 提案独立处置

**阻塞依赖**(本提案不阻塞,但需要并行开 issue):
- OpenStock 仓 issue:`MARKET_BIG_DEAL` category 注册需求(Wave 2/3 follow-up)
- OpenStock 仓 issue:通用 fallback 框架(本提案 Layer 2 阻塞前置,但 Layer 2 不在本提案范围)

**双仓 issue completion gate**:本提案合并后 48h 内,需在 mystocks_spec 仓和 OpenStock 仓各开立对应 issue,两 issue 正文互相链接,且把 issue URL 填回 `tasks.md` Phase 4。Phase 4 完成标志 = 两个 issue URL 已填入 tasks.md。

## Non-Goals

- **不实现 OpenStock 内部 fallback 框架**。该框架属 OpenStock 仓治理边界,本提案仅在文档层引用。
- **不重命名或重构现有 `src/data_sources/factory.py`**。两 factory 收口是 C2 提案范围。
- **不强制 ExtraSource 实现 typed schema**。fetch 返回 `ExtraSourceResult.data: Any`,与 OpenStock `OpenStockFetchResult.data: Any` 对齐。typed schema 是 C7 提案范围(观察期 ≥ 1 月)。
- **不修改 B4.014 Wave 1 已落地代码**。Wave 1 走 endpoint-layer 直连 OpenStock 的模式,与 ExtraSource 契约并存,不强制对齐。
- **不实现 CI 过期阻断的具体流水线脚本**。tasks.md 列出该任务为 follow-up,不阻塞本提案合并。

## Risks

| 风险 | 缓解 |
|---|---|
| ExtraSource registry 在启动 lifespan 失败导致服务无法启动 | 静态校验只校验 `category` 集合,不调用网络;启动开销 < 10ms |
| Wave 2/3 归属判定主观性强 | 附录给出规则(已规划 vs 无规划),双仓 issue 双向链接保留可追溯性 |
| TEMP_OVERRIDE 沦为永久技术债 | expires_on 强制 + CI 过期阻断(实施细节见 tasks.md) |
| Layer 2 阻塞于 OpenStock 框架,长期无进展 | 本提案 Layer 1 独立可落地,不依赖 Layer 2;Layer 2 落地后另开提案 |

## References

- `数据流分层规则.md`(Obsidian Hermes vault)— 顶层架构契约
- `/opt/claude/openstock/docs/DATA_CAPABILITY_SCOPE.md` — 70 静态 category 清单来源
- `/opt/claude/openstock/docs/CONNECTION_GUIDE.md` — fallback 注册机制现状
- `openspec/changes/migrate-akshare-fundflow-mixin-to-openstock/` — B4.014 提案,本提案为其 Wave 2/3 提供判定模板
- 2026-07-02 grilling 记录(本会话归档于 `/root/.claude/_docs/` 下)— 七轮压测过程
