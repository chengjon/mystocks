## Context

> **设计方案说明**:
> 本文件用于记录某项变更的设计思路、结构拆分、实现取舍或技术路径，属于方案设计层材料。
> 它不是共享规则正文，也不直接代表当前仓库已落地状态；落地判断应结合 `architecture/STANDARDS.md`、对应 proposal/tasks、审批结果与实际代码验证。

MyStocks项目当前已实现基础的akshare数据源支持，但akshare库提供了极为丰富的数据接口。根据akshare官方文档，包含了股票市场总貌、个股信息、资金流向、预测分析、板块行业、行情新闻等20多个重要数据类别。

当前系统仅支持融资融券、龙虎榜和股指期货等少数功能，缺失大量关键数据源：
- 市场总貌数据：交易所统计、地区交易排名等
- 个股深度信息：主营业务、千股千评、新闻等
- 资金流向数据：沪深港通、筹码分布、大单统计等
- 预测分析数据：盈利预测、技术指标等
- 板块行业数据：概念板块、行业板块、热度排名等
- 行情新闻数据：涨停板、盘口异动、财经精选等

## Goals / Non-Goals
### Goals
- 在akshare适配器中实现20+个新数据接口
- 提供完整的股票市场数据生态
- 支持量化分析和策略开发的完整数据需求
- 保持与现有系统架构的一致性
- 在 MyStocks 侧只接入“本地已存在的 AkShare 同名函数”，并补充可重复执行的可用性 / repo-truth 门禁
- 记录 `435bc8f00` 已落地的 gate baseline，并在不污染当前 repo-truth 的前提下定义后续 retained candidate 的提升条件

### Non-Goals
- 不实现akshare库不支持的功能
- 不修改现有的数据存储架构
- 不影响现有接口的稳定性和性能
- 不使用名称相近的 AkShare 函数、第三方非同源接口或历史旁路能力替代缺失同名函数
- 不把复杂扩展或深度数据能力转移到 MyStocks；这类实现继续收敛到 `akquant` 仓库
- 不把 advisory `help_candidates` 直接计为已实现运行时能力
- 不在当前批次批准 `stock_news_main_em -> stock_news_main_cx`
- 不为已退役的 `stock_weak_pool_em` 保留虚假的 runtime 空壳

## Decisions

### 0. MyStocks / AkQuant Boundary
**Decision**: MyStocks 只做本地同名函数接入与闭环审计，复杂扩展统一留在 `akquant`
- 原因：避免双仓库职责交叉、替代实现蔓延与 repo-truth 失真
- 落地：
  - 缺失同名函数时保持 gap，不伪造完成
  - 新增 `run_akshare_market_gates.py` 作为统一 wrapper，输出 availability / repo-truth / summary 三份报告
  - 门禁只做校验与审计，不自动生成 adapter / route / registry / OpenSpec 代码

### 0.1 Official Rename Mapping Candidate Scope
**Decision**: 仅允许评估“本地 `akshare` 包内的官方同源改名候选”，不接受自研推导、第三方替代或 provider 漂移
- 接受评估的候选：
  - `stock_dt_pool_em` -> `stock_zt_pool_dtgc_em`
  - `stock_strong_pool_em` -> `stock_zt_pool_strong_em`
  - `stock_new_em` -> `stock_zt_pool_sub_new_em`
- 已考虑但不映射到当前 OpenSpec 条目的邻接官方函数：
  - `stock_zt_pool_previous_em`
    - 说明：昨日涨停股池，当前 change 第 6 节没有对应任务项
  - `stock_zt_pool_zbgc_em`
    - 说明：炸板股池，当前 change 第 6 节没有对应任务项
- 明确排除：
  - `stock_news_main_em` -> `stock_news_main_cx`
    - 排除原因：候选 provider 从 `em` 漂移到财新，不再是同源替换
  - `stock_weak_pool_em`
    - 排除原因：当前本地 `akshare` 未检出明确候选，且业务已决定不再承接该能力
  - `stock_new_em` -> `stock_zh_a_new_em`
    - 排除原因：语义更接近“新股”而非 OpenSpec 第 6.9 项要求的“次新股池”
- 接受标准：
  - 候选函数必须在当前本地 `akshare` 包内可调用
  - 候选函数必须保持同一官方来源或更窄的同源页面族
  - 候选函数的业务语义必须直接匹配 OpenSpec 条目，不允许二次推导
  - 参数差异只能是薄兼容映射，不允许引入新的派生逻辑
  - 在单独获批前，这些候选只能作为方案材料和审计线索，不能直接计为已实现

### 0.2 Current Gate Truth
**Decision**: 当前实现真相以 `435bc8f00` 的 same-name gate baseline 为起点，但已扩展为“native + approved mapping + retired”三类受控状态
- 含义：
  - 本地同名 AkShare 函数继续计为 `native`
  - 已批准的官方改名映射计为 `mapped`
  - 业务明确下线且无保留价值的条目标记为 `retired`
  - `help_candidates` 仍只作为人工评估线索输出
- 影响：
  - `stock_dt_pool_em`、`stock_strong_pool_em`、`stock_new_em` 已是 `mapped` 完成项
  - `stock_weak_pool_em` 已转为 `retired / removed with reason`
  - `stock_news_main_em` 继续保持 excluded

### 0.3 Historical Candidate Promotion Order
**Decision**: 已完成的候选提升微批按 `dt -> strong -> new` 顺序执行
- 排序依据：
  - `dt` 与现有板池类归一化管线最接近，且“跌停股池”语义最收敛，复用成本最低
  - `strong` 仍属同一家族，但比 `dt` 多出 `入选理由`、`是否新高`、`量比` 等扩展字段
  - `new` 引入 `转手率`、`开板日期`、`上市日期` 等次新语义字段，字段解释和前端消费差异最大
- 结果：
  - 三个 retained candidate 已按该顺序全部落地
  - 当前第 6 节不再保留待提升 candidate；只剩 `stock_news_main_em` excluded

### 0.4 `stock_weak_pool_em` Retirement Rule
**Decision**: `stock_weak_pool_em` 在当前 change 中正式改写为 retired / removed with reason
- 原因：
  - 本地 AkShare 1.18.60 未提供同名函数
  - 当前未检出可接受的官方同源候选
  - 业务侧已明确决定不再承接该能力
- 落地要求：
  - OpenSpec 任务项改写为已下线能力
  - repo-truth 行状态改为 `已下线/上游移除`
  - gate 输出 `resolution_status=retired`
  - registry / adapter / route / focused tests 均不得保留 runtime 工件
- 若未来业务重新需要该能力，应作为新的 capability re-entry 微批重新提案，而不是直接恢复当前 retired 项

### 0.5 Upstream Re-rename Contingency
**Decision**: 如果 AkShare 后续版本再次改名，系统应显式失败并重新评估，而不是静默兜底
- gate 应重新把目标标记为 `missing` 或 `missing with advisory candidate`
- `PREFERRED_HELP_CANDIDATES` 如需支持多版本候选，应升级为有序候选列表，并记录适用的 AkShare 版本窗口
- runtime adapter 不应对未批准的新上游名做静默 fallback
- 任何再改名修复都必须重新经过 candidate evaluation

### 1. 适配器架构设计
**Decision**: 采用模块化扩展现有akshare适配器结构
- 原因：现有akshare适配器已采用动态混入模式，易于扩展
- 替代方案：创建新的独立适配器（过于复杂，难以维护）

### 2. 数据分类策略
**Decision**: 按照项目5层数据分类体系进行接口分类
- `MARKET_DATA`: 市场总貌、实时行情、资金流向
- `REFERENCE_DATA`: 个股信息、板块成分、行业分类
- `DERIVED_DATA`: 技术指标、盈利预测、筹码分布
- `TRANSACTION_DATA`: 涨停板、盘口异动等交易数据
- `METADATA`: 财经新闻、热度数据等

### 3. API设计模式
**Decision**: 统一使用现有的API契约和响应格式
- 路径模式：`/api/akshare/market/{module}/{action}`
- 当前模块拆分：`sse`、`szse`、`stock_info`、`fund_flow`、`boards`、`analysis`
- 响应格式：标准UnifiedResponse格式
- 认证方式：JWT token认证
- 参数验证：Pydantic模型验证

### 4. 缓存策略
**Decision**: 基于数据更新频率实现差异化缓存
- 高频数据（实时行情）：缓存5分钟
- 中频数据（每日更新）：缓存1小时
- 低频数据（每周/月度）：缓存1天
- 静态数据（基本信息）：缓存1周

### 5. 批量处理策略
**Decision**: 实现智能批量处理，支持多股票同时查询
- 单次请求最多支持50只股票
- 自动分批处理，避免API限制
- 并发处理提升性能

## Risks / Trade-offs

### 性能风险
**风险**: 新增20+个接口可能影响系统整体性能
**缓解措施**:
- 实现严格的缓存策略
- 添加性能监控和告警
- 支持按需加载接口

### 数据质量风险
**风险**: akshare数据源质量参差不齐
**缓解措施**:
- 实现数据质量验证
- 提供数据源切换机制
- 添加数据完整性检查

### 维护复杂性风险
**风险**: 大量接口增加维护复杂度
**缓解措施**:
- 模块化代码组织
- 统一的错误处理机制
- 完善的测试覆盖

## Migration Plan

### Phase 1: 基础架构准备 (Week 1)
1. 分析所有新接口的需求和参数
2. 更新akshare适配器架构
3. 准备数据源配置模板

### Phase 2: 核心接口实现 (Week 2-3)
1. 按优先级实现高频使用的接口
2. 添加对应的数据源配置
3. 创建API端点

### Phase 3: 测试和优化 (Week 4)
1. 编写完整的测试套件
2. 性能测试和优化
3. 文档更新

### Phase 4: 生产部署 (Week 5)
1. 灰度发布新接口
2. 监控系统稳定性
3. 用户反馈收集

### Rollback Plan
如果出现严重问题，可以：
1. 通过配置禁用新接口
2. 回滚到上一版本
3. 逐步启用经过验证的接口

## Open Questions

### 1. API限流处理
akshare是否有API调用频率限制？需要实现什么样的限流策略？

### 2. 数据一致性保证
不同接口返回的数据格式如何保证一致性？是否需要额外的标准化处理？

### 3. 缓存失效策略
如何处理市场开闭市时间对缓存策略的影响？

### 4. 错误处理机制
遇到网络异常或数据源不可用时，应该如何降级处理？

### 5. 监控指标设计
需要监控哪些关键指标来确保系统稳定性？
