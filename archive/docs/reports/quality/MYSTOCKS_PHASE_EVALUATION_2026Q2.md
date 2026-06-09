# MyStocks 阶段性评估与优化报告

> 评估日期：2026-04-25
> 报告类型：2026Q2 阶段性评估 / 优化任务收敛
> 评估方式：zread 文档复核 + 仓库静态核验 + 外部意见逐条判定
> 本次未执行项：未启动服务、未跑 E2E、未做性能压测；以下“验证”均为文档/源码/配置级核验，不冒充运行时实测

---

## 1. 结论摘要

MyStocks 当前不是“推倒重来型”项目，主问题也不是基础架构缺失，而是以下四类收口不够彻底：

1. 实时链路存在多套实现和预留接口，但主推送路径、真实数据源接入、事件总线到前端的闭环还不够统一。
2. 领域分层设计在 `src/domain` / `src/application` / `src/infrastructure` 内已经建立，但 `web/backend/app/services/`、`app/main.py` 与 `app/app_factory.py` 仍体现出一定架构漂移。
3. 数据质量能力已经“有检查器”，但尚未形成以写入前校验、回补、对齐、治理闭环为核心的统一模块。
4. 交易与风险相关能力更接近“可演进骨架”而非“生产级实盘闭环”，需要把安全、幂等、审计和运行时策略前置为显式治理任务。

一句话判断：项目的骨架、治理和可观测性基础明显强于“从零到一”阶段，但要从“可开发、可演示、可扩展”迈向“可靠、可收口、可持续演进”，重点在统一实时主链路、收敛分层真相源、补强交易安全与数据治理。

---

## 2. 本次考查了哪些文档

### 2.1 治理与规则文档

- `architecture/STANDARDS.md`
- `openspec/AGENTS.md`
- `AGENTS.md`
- `docs/FUNCTION_TREE.md`
- `governance/function-tree/catalog.yaml`
- `governance/function-tree/schema.json`

### 2.2 zread 文档（重点阅读）

- `.zread/wiki/versions/2026-04-25-113808/5-xi-tong-jia-gou-yu-ling-yu-bian-jie-hua-fen.md`
- `.zread/wiki/versions/2026-04-25-113808/8-gong-neng-shu-qu-dong-de-ye-wu-neng-li-guan-li.md`
- `.zread/wiki/versions/2026-04-25-113808/14-fastapi-hou-duan-ying-yong-jia-gou-yu-qi-dong-liu-cheng.md`
- `.zread/wiki/versions/2026-04-25-113808/16-hou-duan-fu-wu-ceng-shu-ju-fu-wu-ce-lue-fu-wu-yu-jian-kong-fu-wu.md`
- `.zread/wiki/versions/2026-04-25-113808/18-shuang-shu-ju-ku-jia-gou-tdengine-shi-xu-cun-chu-yu-postgresql-guan-xi-cun-chu.md`
- `.zread/wiki/versions/2026-04-25-113808/21-ce-lue-guan-li-yu-hui-ce-yin-qing.md`
- `.zread/wiki/versions/2026-04-25-113808/23-jian-kong-gao-jing-yu-shu-ju-zhi-liang-bao-zhang.md`
- `.zread/wiki/versions/2026-04-25-113808/24-gao-ji-fen-xi-ji-qi-xue-xi-ce-lue-yu-gpu-jia-su.md`
- `.zread/wiki/versions/2026-04-25-113808/25-fen-ceng-ce-shi-ce-lue-yu-zhi-liang-men-jin.md`
- `.zread/wiki/versions/2026-04-25-113808/26-an-quan-ren-zheng-jwt-yu-owasp-fang-hu.md`
- `.zread/wiki/versions/2026-04-25-113808/27-bu-shu-yun-wei-pm2-docker-yu-jian-kong-zhan.md`

### 2.3 源码与配置核验文件

- `src/domain/shared/event_bus.py`
- `src/infrastructure/messaging/local_event_bus.py`
- `src/infrastructure/messaging/redis_event_bus.py`
- `src/application/bootstrap.py`
- `src/infrastructure/market_data/adapter.py`
- `src/core/data_quality_validator.py`
- `src/monitoring/data_quality_monitor.py`
- `web/backend/app/main.py`
- `web/backend/app/core/security.py`
- `web/backend/app/core/rate_limit.py`
- `web/backend/app/api/websocket.py`
- `web/backend/app/api/realtime_market.py`
- `web/backend/app/core/socketio_manager.py`
- `web/backend/app/services/streaming/stream_manager.py`
- `src/adapters/tdx_realtime_manager.py`
- `src/application/trading/order_mgmt_service.py`
- `src/trading/live_trading_engine.py`
- `src/infrastructure/logging/audit_system.py`

---

## 3. 本次验证了哪些功能或事实

| 验证项 | 结论 | 备注 |
|---|---|---|
| 领域事件总线是否存在 | 已验证存在 | `IEventBus` + `LocalEventBus` + `RedisEventBus` 均有实现 |
| 事件总线是否接入应用编排 | 已验证存在 | `src/application/bootstrap.py` 中有 `OrderFilledEvent -> Portfolio` 订阅 |
| 防腐层是否完全缺失 | 否 | `DataSourceV2Adapter` 明确以 ACL 方式适配 `IMarketDataRepository` |
| WebSocket / Socket.IO 是否完全不存在 | 否 | `web/backend/app/api/websocket.py`、`realtime_market.py`、`socketio_manager.py` 均存在 |
| 实时推送是否已经形成唯一主链路 | 否 | 通道多、主链路不唯一，且部分流管理与数据源仍偏预留/模拟 |
| 数据质量模块是否完全缺失 | 否 | `DataQualityValidator` + `DataQualityMonitor` 已存在 |
| 数据质量治理是否闭环 | 否 | 仍缺写入前治理、回补、时间对齐、统一归口 |
| 双数据库路由是否存在 | 是 | zread 与源码均支持 TDengine + PostgreSQL 分层路由 |
| Redis / 缓存层是否缺失 | 否 | Redis 已用于缓存、事件、黑名单、锁等能力 |
| 安全基线是否完全缺失 | 否 | JWT / CSRF / RBAC / 审计组件均有实现 |
| 安全是否已足够覆盖交易场景 | 否 | 交易二次确认、幂等、交易专属红线仍不足 |
| 监控栈是否缺失 | 否 | Prometheus / Grafana / Loki / Tempo 均有配置与文档 |
| 可观测性是否已经强绑定业务主链路 | 部分 | 基础设施完整，但交易/实时主链路视角仍需加强 |
| 后端应用是否只有一套规范入口 | 否 | `app/main.py` 与 `app/app_factory.py` 并行存在 |
| 回测/实时交易是否同一成熟执行引擎 | 否 | 回测成熟度高于实时交易；实时交易入口存在试验/占位特征 |

---

## 4. 对收集意见的吸收、拒绝与理由

### 4.1 架构分层类意见

| 意见 | 结论 | 理由 |
|---|---|---|
| API 层与核心业务层职责模糊 | 部分采纳 | `src/application` 的 DDD 分层设计是存在的，但 `web/backend/app/services/` 与两套应用入口说明架构漂移客观存在，值得治理 |
| 缺少反腐层（ACL） | 拒绝“完全缺失”说法 | `DataSourceV2Adapter` 已明确承担适配职责；但“领域语义是否彻底脱源”仍值得做二次审计 |

**判定**：这组意见里，真正要做的不是“从零补 DDD”，而是“收敛现有 DDD 与 Web 层并行实现”。

### 4.2 数据架构类意见

| 意见 | 结论 | 理由 |
|---|---|---|
| TDengine 与 PostgreSQL 边界应更清晰 | 采纳 | 路由机制存在，但跨库计算路径和冷热分层策略仍值得复核 |
| 应简化为单库 | 暂不采纳 | 当前仓库对双库路由已有明显投入，且未见足够性能数据支持直接收缩为单库 |
| 缺少统一数据质量管理模块 | 采纳 | 现有 validator/monitor 更像“检查组件”，还不是统一治理模块 |

### 4.3 实时性与性能类意见

| 意见 | 结论 | 理由 |
|---|---|---|
| 缺少事件驱动架构 | 拒绝“完全缺失”说法 | 事件总线已经存在 |
| 缺少实时推送链路 | 部分采纳 | WebSocket/Socket.IO 已存在，但主链路不唯一、数据源闭环不够清晰，这一问题成立 |
| GPU 定位不清晰 | 采纳 | GPU 能力广泛存在，但“哪些场景进入生产主链路、哪些仅实验/离线”缺统一口径 |

### 4.4 治理与安全类意见

| 意见 | 结论 | 理由 |
|---|---|---|
| 功能树完成度指标不够严格 | 采纳 | `docs/FUNCTION_TREE.md` 自身已声明完成度是阶段性快照，`schema.json` 也未定义量化完成标准 |
| `STANDARDS.md` 缺少安全红线 | 部分采纳 | 通用安全能力不少，但交易域安全红线未提升为治理入口约束 |

### 4.5 运维与可观测性类意见

| 意见 | 结论 | 理由 |
|---|---|---|
| 监控栈集成度需要加强 | 部分采纳 | 监控栈本身并不缺，但业务主链路视角和落地面板可再强化 |
| 缺少蓝绿/灰度发布方案 | 拒绝作为当前主优先级 | 以当前“本地化/单体”为主的项目定位，优先级低于优雅关闭、状态持久化和运行时恢复 |

---

## 5. 对“潜在风险与薄弱点”的判定

### 5.1 采纳或部分采纳的风险

| 风险意见 | 结论 | 理由 |
|---|---|---|
| 交易执行层是最大短板 | 采纳 | `OrderManagementService` 未体现幂等键/重复提交防护；`live_trading_engine.py` 体现出试验性/未完全收口特征 |
| 性能优化口径不清晰 | 部分采纳 | Redis、WebSocket、GPU 都存在，但缺少统一的实时性能基线与关键链路压测结论 |
| 安全与合规仍有缺口 | 部分采纳 | 通用安全能力较好，但交易域特有的二次确认、幂等、专属审计约束不足 |
| 可观测性与业务绑定不足 | 部分采纳 | 可观测性底座较完整，但交易/策略/实时行情的业务视图仍不够聚焦 |

### 5.2 拒绝或下调的风险

| 风险意见 | 结论 | 理由 |
|---|---|---|
| 当前使用 COM/HID 模拟交易是已确认事实 | 暂不采纳 | 本次未找到足够源码证据直接证明这一实现路径，不能写成已验证事实 |
| 无 Redis / 无缓存层 | 拒绝 | Redis 明确存在并已用于多类场景 |
| 无 RBAC / 无审计日志 | 拒绝 | 代码中已存在 RBAC 与审计实现 |
| 无高可用设计必须立即补集群/failover | 下调优先级 | 对当前单体/本地化定位而言，优先级低于优雅关闭、恢复能力和单实例可靠性 |

---

## 6. 当前最关键的真实问题

以下不是外部意见里的“猜测”，而是本次复核后认为最值得进入优化任务池的事实问题：

### 6.1 架构真相源并未完全收敛

- `web/backend/app/main.py` 与 `web/backend/app/app_factory.py` 并行存在。
- `src/application` 已承担应用层职责，但 `web/backend/app/services/` 仍有较多服务逻辑。
- zread 对分层的叙述总体成立，但仓库运行态入口与代码组织仍有现实漂移。

### 6.2 实时链路“有实现”但“不唯一”

- 后端存在 WebSocket 路由、Socket.IO 管理器、流管理器、实时行情 API。
- 但 `StreamManager`、`TdxRealtimeManager` 等模块仍可见模拟/占位式实现。
- 因此问题不是“没有实时能力”，而是“实时能力未统一为唯一、可信、可治理的主链路”。

### 6.3 数据质量能力分散

- `src/core/data_quality_validator.py`
- `src/monitoring/data_quality_monitor.py`
- `src/data_governance/quality.py`

以上说明质量能力有积累，但归口与职责边界仍分散，缺少“进入系统前”“进入系统后”“修复/回补”三阶段统一设计。

### 6.4 交易安全缺口比通用安全缺口更严重

- JWT / CSRF / 黑名单 / 基础 RBAC 都是存在的。
- 但交易二次确认、订单幂等、重复提交防护、交易专属审计、风控前置约束没有形成统一治理红线。

### 6.5 功能树完成度目前更像“说明文字”，不是“门禁指标”

- `docs/FUNCTION_TREE.md` 已明确声明完成度是阶段性快照。
- `governance/function-tree/schema.json` 不包含量化完成标准字段。
- 因此“85% / 70% / 50%”更适合作为管理观察值，不应直接视为当前硬指标。

---

## 7. 建议纳入待优化任务池的方向

### P0

1. **统一实时主链路**
   - 明确唯一推荐通道：`WebSocket events`、`realtime_market`、`Socket.IO` 三者至少选定一条主链路
   - 打通“真实行情源 -> 事件/流处理 -> 前端订阅 -> 监控指标”的闭环
   - 清理或降级标注模拟/预留实现

2. **交易域安全契约先行**
   - 交易执行层尚未完成开发，当前加固应聚焦于**接口级安全契约**而非实现级加固
   - 先在 `STANDARDS.md` 中定义交易域安全红线：幂等键、防重复提交、二次确认、审计必记字段、最小权限
   - 待交易适配器实现后再做运行时加固，避免对未稳定接口做过度约束

### P1

3. **收敛应用层边界**
   - 统一 `app/main.py` 与 `app/app_factory.py` 的真相源
   - 审计 `web/backend/app/services/` 与 `src/application/` 的职责重叠
   - 固化“API 只编排、领域逻辑不回流到 Web 层”的迁移准则

4. **建立统一数据质量模块**
   - 以 ingestion gate 为中心组织：完整性、准确性、重复、时间对齐、回补
   - 将 validator / monitor / governance 口径收敛成一套能力模型

5. **实现交易适配器（miniQMT 优先）**
   - 采用适配器模式，与现有数据源适配器（AKShare/TDX/EFinance）保持一致
   - 路径：`src/domain/trading/` 定义交易聚合根与订单接口，`src/infrastructure/trading/` 实现具体适配器
   - **miniQMT 适配器**（P1 优先实现）：通过 miniQMT 接口对接实盘交易
   - **TDX 适配器**（预留接口桩）：通过个人 TDX 开发接口实现，当前仅定义接口不做实现
   - 实现前提：P0 交易域安全契约已在 STANDARDS.md 中定义、domain trading 接口已稳定

6. **量化功能树完成度口径**
   - 为“完成度”补充可量化依据：测试通过率、契约覆盖、E2E、文档、运行门禁
   - 完成度改为“有依据的状态字段”，而不是纯主观百分比

### P2

7. **双数据库策略复核**
   - 用真实回测/查询链路做压测
   - 判断哪些衍生指标应前推、缓存或连续聚合
   - 先做证据化评估，再决定是否讨论单库收缩

8. **观测性与业务链路绑定**
   - 为实时行情、策略执行、订单处理、风控决策补齐业务级指标、日志字段和追踪 span
   - 不仅监控“服务活着”，还要监控“关键业务链路是否正常”

### P3

9. **GPU 场景分层**
   - 明确哪些是离线回测/训练
   - 哪些是可进入准实时计算
   - 哪些仍保持实验性

---

## 7a. 交易执行层方向决策

### 背景

当前交易执行层（`OrderManagementService`、`live_trading_engine.py`）尚未完成开发，属于"可演进骨架"阶段。在骨架未稳定前对实现做运行时加固会导致约束与未定型接口纠缠，后续改造成本高。

### 决策

采用**适配器模式**实现交易执行，与现有数据源适配器体系保持一致：

| 适配器 | 优先级 | 状态 | 对接方式 |
|--------|--------|------|----------|
| miniQMT | P1（优先实现） | 待开发 | 通过 miniQMT 接口对接实盘交易 |
| TDX | 预留 | 仅接口桩 | 通过个人 TDX 开发接口实现 |

### 目标架构

```
src/domain/trading/           # 交易聚合根 + 订单/持仓接口（与具体券商无关）
src/infrastructure/trading/
  ├── miniqmt_adapter.py      # P1 — 首个实现
  └── tdx_adapter.py          # 预留接口桩
```

### 实施前提

1. P0 阶段先在 `STANDARDS.md` 中定义交易域安全红线（幂等、二次确认、审计字段、最小权限）
2. `src/domain/trading/` 接口稳定后再启动 miniQMT 适配器实现
3. TDX 适配器仅保留接口定义，不做实现

### 与评估报告的关联

此决策直接影响报告中以下条目的优先级调整：
- P0 原第 2 项"交易安全加固"调整为"交易域安全契约先行"——聚焦接口级契约而非实现级加固
- P1 新增第 5 项"实现交易适配器"——明确 miniQMT 优先、TDX 预留的实施路径

---

## 8. 本次明确拒绝写入任务池的事项

以下意见本次不建议直接进入优化主清单：

1. **“立即改成蓝绿/灰度发布”**
   - 当前收益不如先做单实例可靠性、优雅关闭、状态恢复。

2. **“直接改单库”**
   - 缺少压测证据，贸然收缩会把现有双库投入全部重置。

3. **“从零引入事件驱动架构”**
   - 已有事件总线与实时通道，真正问题是收敛与闭环，不是从零搭骨架。

4. **“已确认 COM/HID 模拟交易”**
   - 缺少足够证据，不能以未核实结论驱动任务优先级。

---

## 9. 下一步建议执行顺序

建议按以下顺序推进下一阶段：

1. 先做一轮 **实时链路真相源审计**。
2. 同步在 STANDARDS.md 中定义 **交易域安全契约**（接口级，不依赖实现）。
3. 再做 **应用层/服务层收敛方案**。
4. 然后补 **统一数据质量治理设计**。
5. 待 domain trading 接口稳定后，启动 **miniQMT 适配器实现**（TDX 仅保留接口桩）。
6. 最后进入 **双库压测与 GPU 场景收口**。

---

## 10. 最终评语

这是一个已经有明显“架构意识”和“治理积累”的量化系统，问题不在有没有骨架，而在骨架之上叠加了较多并行路径、预留实现和阶段性快照。后续最该做的不是继续铺新能力，而是把实时、交易、安全、数据质量和分层真相源逐步收拢成一套更少分叉、更可验证的主系统。

---

## 11. Q2 Closure 执行结果回写

在本评估报告形成后，Q2 closure 已按单 CLI 顺序推进到 `Wave 4`，并完成了 A-E 主线中的治理收口批次。

### 11.1 已完成的 closure-wave 收口

#### Wave 1：后端组合与实时真相源收口

已完成内容：
- 将 `app.main:app` 锁定为当前 canonical runtime truth
- 将 FastAPI WebSocket 路由族锁定为当前 canonical public realtime transport
- 将 `app_factory.py` 明确降级为 compatibility-retained / test-scoped surface
- 将 Socket.IO 明确标记为 compatibility-retained / non-canonical

已形成的收口文档：
- `Q2_WAVE1_IMPLEMENTATION_PROGRESS_2026-04-26.md`
- `Q2_WAVE1_FOLLOWUP_DEBT_CAPTURE_2026-04-26.md`

当前仍未完成：
- connection-manager consolidation
- `app_factory.py` 长期去留
- realtime transport deeper unification

#### Wave 2：数据质量 ownership closure

已完成内容：
- canonical split 已明确：
  - validation: `src/core/data_quality_validator.py`
  - monitoring: `src/monitoring/data_quality_monitor.py`
  - governance/reporting: `src/data_governance/quality.py`
- compatibility-retained / operational delivery surfaces 已明确分类
- ingest gate、双库质量规则、cross-storage alignment 与 repair/backfill gap 已明确落成文档

已形成的收口文档：
- `Q2_WAVE2_IMPLEMENTATION_PROGRESS_2026-04-26.md`
- `Q2_WAVE2_OWNERSHIP_BOUNDARY_CAPTURE_2026-04-26.md`
- `Q2_WAVE2_INGEST_GATE_AND_STORAGE_RULES_2026-04-26.md`
- `Q2_WAVE2_REPAIR_BACKFILL_GAP_CAPTURE_2026-04-26.md`

当前仍未完成：
- validation 与 monitoring 的运行时副作用解耦
- repair/backfill owner 的真正实现
- unified ingest pipeline runtime enforcement

#### Wave 3：交易安全 blocking contract

已完成内容：
- canonical placement path 已锁定为：
  - `RealtimeStrategyExecutor`
  - `LiveTradingEngine`
  - `OrderManagementService.place_order()`
  - `OrderRepository`
- 所有 inspected execution-capable paths 均被保守分类为 `experimental`
- idempotency、pre-execution risk gate、confirmation policy、audit binding、residual gap 均已形成 contract/gap 文档

已形成的收口文档：
- `Q2_WAVE3_IMPLEMENTATION_PROGRESS_2026-04-26.md`
- `Q2_WAVE3_CANONICAL_PATH_AND_CLASSIFICATION_2026-04-26.md`
- `Q2_WAVE3_IDEMPOTENCY_AND_DEDUP_CONTRACT_2026-04-26.md`
- `Q2_WAVE3_RISK_GATE_AND_CONFIRMATION_POLICY_2026-04-26.md`
- `Q2_WAVE3_AUDIT_BINDING_AND_RETENTION_2026-04-26.md`
- `Q2_WAVE3_RESIDUAL_GAP_CAPTURE_2026-04-26.md`

当前仍未完成：
- DTO / service 层幂等 identity
- runtime pre-order blocking gate
- runtime confirmation / approved bypass
- decision-point durable audit binding
- verified external execution adapter closure

#### Wave 4：功能树证据硬化

已完成内容：
- `docs/FUNCTION_TREE.md` 已从“叙述性完成”收紧为“证据层解释”
- `✅ / 🚧 / 🧪` 的解释已绑定 implementation / verification / runtime / safety-governance evidence
- `05-投资组合与交易` 已明确按安全敏感域保守解读
- 完成度百分比已明确降级为 snapshot，除非后续补齐计算口径

已形成的收口文档：
- `Q2_WAVE4_IMPLEMENTATION_PROGRESS_2026-04-26.md`
- `Q2_WAVE4_STATUS_SEMANTICS_AND_EVIDENCE_LAYER_2026-04-26.md`
- `Q2_WAVE4_SAFETY_SENSITIVE_RULES_2026-04-26.md`
- `Q2_WAVE4_CLOSURE_EVIDENCE_BINDING_2026-04-26.md`
- `Q2_WAVE4_PERCENTAGE_SNAPSHOT_POLICY_2026-04-26.md`
- `Q2_WAVE4_HISTORICAL_REVIEW_DEBT_CAPTURE_2026-04-26.md`

当前仍未完成：
- 全量 historical node evidence backfill
- 自动化 evidence citation gate
- completion percentage formal calculation model

### 11.2 本次 closure 的性质

必须明确：

1. 本轮 closure 的主要成果是 **truth-locking / governance-hardening / interpretation-hardening**。
2. 本轮 closure **不是** 大规模 runtime refactor，也 **不是** 交易/实时链路 productionization。
3. 本轮 closure 已显著降低“文档把当前能力说得比事实更强”的风险，但没有消除所有运行时技术债。

---

## 12. 更新后的整体判断

结合 Wave 1 到 Wave 4 的已完成工作，当前项目状态可重新表述为：

1. **架构与治理底座比最初评估时更清晰**  
   真相源、ownership、safety class、function-tree status semantics 已有更明确口径。

2. **实时、数据质量、交易安全的“认知风险”已显著下降**  
   当前最重要的不是再讨论“有没有这项能力”，而是明确哪些是 canonical、哪些是 compatibility-retained、哪些仍只是 experimental。

3. **运行时硬化仍然是下一阶段主战场**  
   特别是交易幂等、预执行风控、审计绑定、数据质量解耦、实时链路进一步收口，这些都还没有在代码层闭合。

4. **功能树现在更接近“治理入口”而不是“乐观宣传页”**  
   这是重要进展，因为它会直接降低后续评审、OpenSpec、任务拆分时的状态漂移。

---

## 13. 更新后的下一步建议

在 Q2 closure A-E 完成后，下一轮不建议继续扩散文档，而应开始一批小而硬的 runtime-hardening 工作。

建议顺序如下：

1. **Trading Safety Runtime Batch 1**
   - 为 `CreateOrderRequest` / canonical placement path 增加 idempotency identity
   - 在 decision point 绑定 durable audit
   - 目标：先解决“重复意图不可追踪、决策不可重建”

2. **Trading Safety Runtime Batch 2**
   - 为 canonical placement path 增加 pre-order risk gate
   - 增加 confirmation / approved bypass enforcement
   - 目标：让 Wave 3 的 contract 从文档进入代码

3. **Data Quality Runtime Batch**
   - 优先解耦 `validation -> monitoring` 的隐藏副作用
   - 明确 ingest gate 调用点
   - 目标：让 Wave 2 的 ownership split 进入可演化实现

4. **Realtime Runtime Batch**
   - 继续收紧 `app.main` 与兼容入口的关系
   - 审计并收敛 connection-manager / transport surface
   - 目标：减少 Wave 1 follow-up debt

5. **Function Tree Evidence Follow-Up**
   - 只对安全敏感和争议最大的 historical nodes 做 selective evidence backfill
   - 不要一次性全量重审全树

---

## 14. 最终结论（更新版）

MyStocks 当前最有价值的进展，不是“又新增了多少能力”，而是 Q2 closure 已经把几个最容易失真的地方重新压回事实边界：

- 实时链路不再被混写成多套平行真相
- 数据质量不再被混写成单一模糊能力
- 交易执行不再被误读为接近 production-ready
- 功能树不再默认把 `✅` 解释为“已经生产可用”

因此，项目现在更接近一个**可治理、可继续演进的主系统**，而不是一个“能力很多但状态口径漂移”的集合体。

下一阶段最该做的，不是继续扩大评估范围，而是把已经写清楚的 contract 逐步下沉到运行时代码里。
