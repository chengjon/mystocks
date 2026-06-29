# OpenStock 单业务域迁移操作手册 (V1.0)

> **文档定位**: 本文件是 [`architecture/standards/openstock-consumer-boundary-sot.md`](../../../architecture/standards/openstock-consumer-boundary-sot.md) §九 要求的"迁移操作手册"。Phase 1.1（FundFlow 域）首次产出，后续 Phase 1.2 ~ 1.6 业务域迁移严格按本手册执行。
>
> **生效条件**: 自 2026-06-29 V1.0 起生效。手册本身的更新必须随对应域迁移 PR 同步提交。

---

## 零、本手册要解决的问题

每个业务域从"直接 `import akshare`"切换到"`OpenStockClient.fetch()`"看似简单，但历史上每次尝试都因为以下问题失败或半途而废：

1. **白名单扩展未配套测试** → 客户端在运行时炸出 `OpenStockUnsupportedCategory`
2. **响应字段形态漂移** → 切换后前端页面字段缺失或类型错位
3. **OpenStock 中台类别缺失** → 部分 endpoint 无法迁移，但没有显式登记，下次会话再次踩坑
4. **路由路径在前端 PR 中被混合修改** → review 难度爆炸、回滚成本高
5. **CI 没有强制门禁** → 迁移后业务代码再次出现 `import akshare`

本手册用一组**强制步骤 + 自检清单 + 拆分阈值**消除上述问题。

---

## 一、单域迁移标准步骤

每个 Phase 1.x 域迁移 PR 必须按下列顺序执行：

### Step 1 — 端点盘点与 OpenStock 类别映射

- 列出该域所有 endpoint（路径、HTTP 方法、原 akshare 调用方法）
- 对每个 endpoint 检查 OpenStock 中台是否有对应 `data_category`（参考 [`/opt/claude/openstock/docs/DATA_CAPABILITY_SCOPE.md`](../../../../openstock/docs/DATA_CAPABILITY_SCOPE.md)）
- 将结果填入本文件 §三 的"未迁移接口 & 中台能力需求清单"

### Step 2 — 白名单扩展

- 修改 [`web/backend/app/services/openstock_client.py`](../../../web/backend/app/services/openstock_client.py) 的 `DEFAULT_SUPPORTED_CATEGORIES`
- 每个新增类别必须以**行内注释**形式标注对应 endpoint 路径，例如：
  ```python
  "NORTHBOUND_FLOW",     # /api/akshare/market/fund-flow/hsgt-summary
  ```

### Step 3 — 单元解析测试

- 路径: `tests/services/openstock_client/test_<category>_parsing.py`（小写）
- 必须覆盖: 正常返回 / 空 data 列表 / 必要字段缺失 / 可选字段 null / 字段类型转换
- 测试桩必须基于 OpenStock 真实响应字段（参考 live curl probe 或 OpenStack `API_REFERENCE.md`）

### Step 4 — API 端到端测试

- 路径: `tests/api/test_<domain>_openstock.py`
- 必须覆盖: 至少一个对外 HTTP endpoint 的全链路测试（mock OpenStock 响应 → 走完整路由 → 验证响应形态）+ OpenStock 不可用时的降级行为

### Step 5 — 业务代码切换

- 修改对应 API 文件（例如 `web/backend/app/api/akshare_market/fund_flow.py`）
- **仅切换内部实现**，路由路径、请求参数、响应中文键名保持不变
- 对该 PR 无法覆盖的 endpoint（OpenStock 中台类别缺失），加标准化 TODO：
  ```python
  # TODO(B4.014-Phase1.x-gap): 待 OpenStock 新增 <类别名> 类别方可迁移
  # 缺失能力: <一句话描述>
  # 详细登记见 docs/guides/openstock-migration/DOMAIN_MIGRATION_PLAYBOOK.md §三
  ```

### Step 6 — 浏览器端到端验证

- 启动 backend + frontend，在浏览器打开对应页面
- 验证清单（参考 §四）
- 在 PR 描述中贴截图证明页面正常渲染（含 OpenStock 正常响应场景）

### Step 7 — CI lint 与 Playbook 更新

- 同 PR 内交付 `scripts/linting/forbidden_imports.py` 的对应规则
- 同 PR 内更新本文件 §三 的对应域"未迁移接口清单"

---

## 二、迁移自检核对清单

每个域迁移 PR 描述必须包含以下清单，全部勾选才能提交 review：

- [ ] **白名单扩展**: `DEFAULT_SUPPORTED_CATEGORIES` 新增类别均带行内注释
- [ ] **单元解析测试**: `tests/services/openstock_client/test_<category>_parsing.py` 全部通过
- [ ] **API e2e 测试**: `tests/api/test_<domain>_openstock.py` 全部通过
- [ ] **响应字段对齐**: 切换前后调用同一 endpoint，响应中文键名集合一致
- [ ] **错误码对齐**: OpenStock 不可用时返回的 `UnifiedResponse.error.code` 与原 akshare 错误码一致或显式登记差异
- [ ] **性能对比**: 单 endpoint p50 延迟对比 ≤ 1.5x 原值（mock 数据测试 + 浏览器手测）
- [ ] **路由路径**: 路由路径未变化（Phase 1.x），或显式登记为 Phase 3 路由统一 PR
- [ ] **未迁移接口 TODO**: 所有无法切换的 endpoint 加 `# TODO(B4.014-Phase1.x-gap)` 注释
- [ ] **§三 清单同步**: 本文件 §三 的对应域清单已更新
- [ ] **CI lint**: `scripts/linting/forbidden_imports.py` 通过
- [ ] **浏览器 e2e 截图**: PR 描述包含 OpenStock 正常响应截图

---

## 三、未迁移接口 & 中台能力需求清单

> **用途**: OpenStock 中台尚未提供对应 `data_category` 的 endpoint，统一在此登记。每个条目需要: 端点路径 / 原 akshare 方法 / 缺失 OpenStock 类别 / 业务场景 / 优先级。
>
> **维护规则**: 域迁移 PR 必须同步更新本清单；禁止以"以后再说"为由省略登记。

### 3.1 FundFlow 域（Phase 1.1，截至 2026-06-29）

| 端点路径 | 原 akshare 方法 | 缺失 OpenStock 类别 | 业务场景 | 优先级 |
|---|---|---|---|---|
| `/api/akshare/market/fund-flow/hsgt-detail` | `stock_hsgt_fund_flow_details_em` | `NORTHBOUND_FLOW_DETAIL` | 北向资金明细（每日个股层面净买入） | P2 |
| `/api/akshare/market/fund-flow/north-daily` | `stock_hsgt_hist_em` (北向) | `NORTHBOUND_DAILY_HISTORY` | 北向资金每日历史汇总 | P2 |
| `/api/akshare/market/fund-flow/south-daily` | `stock_hsgt_hist_em` (南向) | `SOUTHBOUND_DAILY_HISTORY` | 南向资金每日历史汇总 | P2 |
| `/api/akshare/market/fund-flow/south-stock/{symbol}` | `stock_hsgt_south_acc_flow_in_em` | `SOUTHBOUND_HOLDING` | 单标的南向持股明细 | P2 |
| `/api/akshare/market/fund-flow/hsgt-holdings/{symbol}` | `stock_hsgt_individual_em` | `HSGT_INDIVIDUAL_HOLDING` | 沪深港通个股持股汇总 | P3 |
| `/api/akshare/market/fund-flow/big-deal` | `stock_lhb_*` / 大单接口 | `MARKET_BIG_DEAL_RANK` | 全市场大单成交排名（异动） | P3 |

**说明**:
- Phase 1.1 该域共 8 个 endpoint，2 个已完成迁移（`hsgt-summary`、`north-stock/{symbol}`），6 个待 OpenStock 中台补类别
- P2 优先级: 业务有真实使用计划（前端 FundFlow 页面后续扩展时需要）
- P3 优先级: 业务当前无活跃消费者，但 OpenStock 补齐后可解锁未来场景
- OpenStock 中台侧能力扩展需走 OpenSpec 提案，参考 [`openstock/openspec/`](../../../../openstock/openspec/)

### 3.2 ~ 3.6 其他域

待 Phase 1.2 ~ 1.6 启动时由对应 PR 填充。模板：

```markdown
### 3.x <Domain> 域（Phase 1.x，截至 YYYY-MM-DD）

| 端点路径 | 原 akshare 方法 | 缺失 OpenStock 类别 | 业务场景 | 优先级 |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |
```

---

## 四、浏览器端到端验证清单

每个域迁移 PR 在浏览器验证环节必须完成以下检查（以 FundFlow 域 `/data/fund-flow` 页面为例）：

### 4.1 通用清单（所有域）

- [ ] 页面打开不报白屏（控制台无 5xx、无 JS runtime error）
- [ ] 主数据列表渲染正常，至少有 1 行真实数据
- [ ] 字段值与 OpenStock 实际响应一致（手工比对 1~2 个字段）
- [ ] RequestId 在 UI 显式展示（参考 STANDARDS.md 二.1 "TRACE_ID 显化"）
- [ ] 主动降级测试: 临时关闭 OpenStock 服务（或修改 `OPENSTOCK_BASE_URL` 为不可达地址），刷新页面 → 前端展示降级提示而非白屏

### 4.2 FundFlow 域专属清单

- [ ] `/data/fund-flow` 北向资金汇总区域（沪股通 / 深股通）显示当日净买入、持股余额、上涨/下跌家数
- [ ] 单标的北向持股明细查询（输入 `sh600519` 等代码）返回持股数、持股市值、占比
- [ ] 字段映射对照: 浏览器显示的"净买入金额"等于 OpenStock 响应中 `net_buy_amount` 字段
- [ ] OpenStock 不可用时，FundFlow 页面显示空数据状态或降级提示，**不**报 500 错误

---

## 五、PR 拆分阈值

### 5.1 必须拆分的信号

出现以下任一情况，PR 必须拆为多个独立 PR：

- 单域 endpoint 数 ≥ 12（FundFlow 域 8 个 → 单 PR；Boards 域 16 个 → 拆 2 PR）
- 新增 `DEFAULT_SUPPORTED_CATEGORIES` 类别 ≥ 6
- PR diff 总 LOC ≥ 1500（含测试 + 业务代码）
- 触及 ≥ 2 个独立业务页面

### 5.2 拆分原则

- **垂直拆分优先**: 按 endpoint 分组，每个 PR 完成一组（白名单 + 测试 + 业务切换 + 浏览器验收）完整闭环
- **禁止水平拆分**: 不允许"PR1 全部白名单 + PR2 全部测试 + PR3 全部业务切换"——这会让每个中间 PR 都违反 SOT §五.2"白名单扩展必须同 PR 配套测试"
- **路由路径 PR 独立**: Phase 3 路径切换必须独立 PR，不与 Phase 1.x 业务切换混合（见 SOT §七）

### 5.3 单 PR 最小完成单元

任何 Phase 1.x PR 必须是**端到端闭环**：

```
白名单 +2 类别
  → 单元测试 ×2 通过
    → 业务代码切换 2 个 endpoint
      → API e2e 测试通过
        → 浏览器验收截图
          → Playbook §三 同步更新
```

不允许跳过任何环节，也不允许"先合入 PR1 完成前 3 步，下个 PR 补 API e2e 与浏览器验收"。

---

## 六、本手册未覆盖的事项

- OpenStock 中台类别扩展流程（参考 [`openstock/openspec/AGENTS.md`](../../../../openstock/openspec/AGENTS.md)）
- TDengine 缓存策略细节（参考 SOT §四）
- CI lint 脚本具体实现（参考 [`scripts/linting/forbidden_imports.py`](../../../scripts/linting/forbidden_imports.py)）
- Phase 2 后台/数据服务迁移（参考 SOT §三）

---

## 修订历史

- **2026-06-29 V1.0（初始）**: Phase 1.1 FundFlow 域首次产出。包含标准步骤、自检清单、FundFlow 域未迁移接口清单（6 条）、浏览器验证清单、PR 拆分阈值。基于 SOT §九要求与用户授权方案。
