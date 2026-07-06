# main 数据架构实证审计 — B4.014 重建的前提修正

> **日期**：2026-06-30（初版）／2026-06-30（同日二次修订，v2）
> **触发**：B4.014 重建（M1k/M1n/M1m/Wave 0）启动前的方向核对
> **结论**：B4.014 handoff 文档关于"main 架构"的描述存在多处事实错误，重建前提必须修正
> **状态**：审计文档，下次会话的战略决策输入

> ⚠️ **v2 修订说明（2026-06-30 同日）**
>
> 初版（v1）有重大事实错误：误判 `MarketDataServiceV2` 接 OpenStock。
> v2 基于 `git show origin/main:<file>` 直接读源码的实证，推翻 v1 的关键判断：
> - **main 上 OpenStock 接入代码为零**（V2 实际用东方财富 adapter，不是 OpenStock）
> - **`/market_v2/*` 路由不存在**（v1 误判）
> - **GitNexus 提示的 `get_openstock_market_client`、`_fetch_openstock_sync`、`_build_openstock_client` 都是幻觉符号**（main 源码里 grep 不到）
>
> 战略部分从 S1/S2/S3 重构为 S5（适配"OpenStock 优先 + 多源保留"的真实方向）。

> ⚠️ **v3 修订说明（2026-07-01）**
>
> 经 CodeWhale 审核（`docs/architecture/DEEPENING_CANDIDATES_2026-07-01.md`）后补充 P0 维度：
> - **OpenStock 服务可用性核查**：服务在线但 `/health` 端点 404（详见 §5.4）
> - **`IDataSource` 接口适配分析**：与 `OpenStockClient` 接口完全异构，需完整适配层（详见 §5.5）
> - **`httpx` 依赖声明核查**：**已声明**（`requirements.txt:53 httpx==0.27.0`）——审核意见 §3.2 此项判断本身有误
> - **S5 风险等级从"低"修正为"中"**，工作量估算 10-20h（2-3 工作日）
> - **§1.2 残留 v1 措辞已修正**（"OpenStock 唯一消费者" → "OpenStock 优先 + 多源保留"）

---

## 一、被证伪的前提

### 1.1 错误命题清单

| 错误命题 | 来源 | 实证结果 |
|---|---|---|
| "main 的 #485 DI 重构删除了 `openstock_client.py`" | `.continue-here.md`、handoff §1.3 | ❌ 假。`openstock_client.py` **从未在 origin/main 上存在过**（`git log --follow` 无历史，`--diff-filter=D` 无记录） |
| "main 用 `MarketDataService` 替代了 `OpenStockClient`" | handoff §1.3、§4.2 | ❌ 假。main 的 `MarketDataServiceV2` 用的是 eastmoney_adapter，**不是 OpenStock**（见 §2.1）。main 上**从未有过**任何 OpenStock 接入代码 |
| "B4.014 的 4 commits 跳过是因为 #485 删了文件" | handoff §1.3 | ❌ 假。真实原因：4 commits 引用的是 B4.014 工作分支自身的 `openstock_client.py`，从未提交到 main，与 main 现有的 `data_source_factory` + V2（eastmoney）体系不兼容 |
| "需要在 `MarketDataService` 架构下重新实现" | handoff §4.2 | ⚠️ 表述不准。main 上同时存在 V1（`market_data_service/`，用 akshare_extension）和 V2（`market_data_service_v2.py`，**用 eastmoney 不是 OpenStock**）两套服务，且 factory 多源骨架独立。不能笼统说"MarketDataService 架构" |

### 1.2 错误的连锁影响

这些错误命题导致**重建方向判断偏差**：
- 以为要做"在 V2 架构下重新实现 B4.014 的 4 commits"
- 实际真问题：**main 的数据架构本身未对齐"OpenStock 优先 + 多源保留"原则**（v2 用户方向更正），factory 多源骨架符合方向但缺 OpenStock adapter，重建前必须先决策 OpenStock 接入路径（见 §3 S5）

---

## 二、main 数据架构实证现状（v2 修订）

### 2.1 main 上 OpenStock 接入代码 = 零

**这是 v1 审计文档最大的事实错误，必须先纠正**。

| v1 判断 | v2 实证 |
|---|---|
| `MarketDataServiceV2` 接 OpenStock | ❌ **错**。V2 顶部注释自述"使用东方财富直接API，不依赖akshare"，初始化 `self.em_adapter = get_eastmoney_adapter()`。源码：`git show origin/main:web/backend/app/services/market_data_service_v2.py:1-50` |
| `/market_v2/*` 路由走 V2 → OpenStock | ❌ **错**。main 上没有"OpenStock 直连"的路由。V2 提供的是 fund_flow / ETF / 龙虎榜 / 板块资金流 / 分红 / 大宗交易等领域服务，全部走 eastmoney_adapter。 |
| `get_openstock_market_client` 是 main 路由的接入点 | ❌ **错**。`git show origin/main:web/backend/app/api/market/market_data_request.py \| grep openstock` 空结果。**GitNexus 给的 5 个 OpenStock 符号全是幻觉**——可能是分支或 worktree 索引残留 |

### 2.2 main 上实际并存的两套数据架构

| 体系 | 文件位置 | 实际数据路径 |
|---|---|---|
| **A. `data_source_factory`** | `web/backend/app/services/data_source_factory/` | factory 按 source_name 分发：`market` → `MarketDataSourceAdapter`；`strategy`/`dashboard`/`watchlist` 等对应 adapter；通用类型按 `DataSourceMode` 选 Mock/Real/Hybrid。**完全不接 OpenStock** |
| **B. `MarketDataServiceV2`** | `web/backend/app/services/market_data_service_v2.py` | V2 → `eastmoney_adapter`。提供 fund_flow/ETF/龙虎榜等"领域级"数据服务。**完全不接 OpenStock** |

**注意**：`MarketDataService` V1（`market_data_service/` 包）在 v1 文档里被描述为"用 akshare_extension + tqlex_adapter"。v2 实证未深入核查 V1 内部——但这对战略决策不重要，因为 V1 本来就不接 OpenStock。

### 2.3 行情路由现状（`/quotes` 和 `/kline`）

| 路由 | 文件 | 真实数据路径 | OpenStock 接入？ |
|---|---|---|---|
| `/quotes` | `app/api/market/market_data_request.py` `/quotes` 端点 | `data_source_factory.get_data("market", "quotes", ...)` → `MarketDataSourceAdapter` | ❌ 未接入。factory 内部 Mock/Real/Hybrid，无 OpenStock |
| `/kline` | 同文件 `/kline` 端点 | `stock_search_service.get_a_stock_kline()` | ❌ 未接入。注释明说"数据源: AKShare stock_zh_a_hist()" |

### 2.4 用户方向（v2 修订）vs main 现状

**用户方向**（v2 更正，来自本会话）：
> "mystocks_spec 把 openstock 作为上游的数据源来消费，但并不是彼此唯一。本地也可连接别的数据服务商/接口。"

也就是说：**OpenStock 优先 + 多源可切换**，不是"OpenStock 唯一"。

**main 现状**：
- `data_source_factory` 的 Mock/Real/Hybrid **多源切换骨架是对的**，符合"多源可切换"
- 但 factory **完全没有 OpenStock adapter**——OpenStock 不是任何模式的 backend
- V2 的 eastmoney 接入、V1 的 akshare 接入都是"本地连接别的数据服务商"——这本身**符合用户方向**
- 唯一缺的是：**OpenStock 作为 primary backend 没有被接入 factory**

**结论（v2）**：main 的数据架构**骨架符合**用户方向（多源），缺的是 **OpenStock adapter 还没建**。B4.014 重建的核心工作是**把 B4.014 工作分支曾经实现的 `openstock_client.py` 重新建出来，并注册为 factory 的 primary backend**——不是"战略切割"。

---

## 三、B4.014 重建的真实问题域（v2 修订）

### 3.1 不是"战略切割"，是"补完 OpenStock 接入"

v1 误判为"main 已有 OpenStock 集成（V2），B4.014 是第三套冲突体系"。
v2 实证：**main 上 OpenStock 接入为零**。

真实问题：**B4.014 工作分支的 `openstock_client.py` 是这个项目唯一的 OpenStock 消费代码**，但它被 PR #489 排除了（理由：基于"main 已重构"的错误前提）。重建工作的核心是**把 OpenStock adapter 建出来，让 factory 能调度它**。

### 3.2 战略选择（v2 重构）

| 战略 | 描述 | 工作量 | 风险 | 与用户方向契合度 |
|---|---|---|---|---|
| **S5（推荐）新建 OpenStockDataSourceAdapter，注册为 factory primary backend** | (a) 重新引入 `openstock_client.py`；(b) 新建 `OpenStockDataSourceAdapter` 实现 `IDataSource` 接口；(c) factory 配置：`market` 类型默认走 OpenStock，失败 fallback 到 `MarketDataSourceAdapter`（akshare/eastmoney）；(d) `/kline` 从直连 akshare 改为走 factory | **中（11-21h，2-3 工作日，详见 §5.7）** | **中**（factory 多源骨架不动，但适配层非平凡、健康端点未确认、测试覆盖未核查，详见 §5.5/§5.7） | ✅ 完全契合。OpenStock 优先 + 多源 fallback |
| ~~S1 废弃 factory + V1~~ | 删除多源能力 | — | — | ❌ 与"本地可连其他数据源"冲突 |
| ~~S2 factory 内部强制 OpenStock~~ | 消灭 Mock/Real/Hybrid | — | — | ❌ 同上 |
| ~~S3 双轨并存~~ | 不主动迁移 | — | — | ❌ main 上根本没有 OpenStock 轨可"并存" |
| ~~S4 V2 作为 factory primary backend~~ | 基于 v1 误判 | — | — | ❌ V2 用的是 eastmoney，不是 OpenStock |

### 3.3 B4.014 跳过的 4 commits 在 S5 下的命运

| Commit | S5 下的工作 |
|---|---|
| **M1k 路由接入** | 重新实现：把 B4.014 的 `openstock_client.py` 重引入；新建 `OpenStockDataSourceAdapter` 注册到 factory；`/quotes` 已经走 factory，只需让 factory 默认走 OpenStock adapter；`/kline` 需要从直连 akshare 改为走 factory |
| **M1m 合约桥接** | 必做。前后端 K 线响应格式契约对齐（与 S5 战略无关，独立做） |
| **M1n Playbook + lint** | 必做，但**重新定义**：不是"forbidden_imports 禁止非 OpenStock"，而是"非 OpenStock adapter 必须在 factory 注册并标记为 fallback"。Playbook 描述 primary/fallback 语义 |
| **Wave 0 FundFlowMixin** | 必做。FundFlow 域接入 OpenStock（独立于行情域，可并行） |

---

## 四、handoff 文档需修正的错误（v2 修订）

### 4.1 已识别错误（v2 表）

`docs/reports/worklogs/claude-auto/b4-014-handoff-2026-06-30.md` 中以下表述需修正：

| 位置 | 原表述 | v2 修正 |
|---|---|---|
| 顶部警告 | "main 的 #485 DI 重构删除了 `openstock_client.py`" | "B4.014 工作分支自身的 `openstock_client.py` 从未提交到 main；main 上 OpenStock 接入代码为零（既无 client 也无路由）" |
| §1.3 跳过根因 | "main 的 #485 DI 重构用 `MarketDataService` 替代了 `OpenStockClient`，删除了 `openstock_client.py`" | "main 上**从未**有过 `openstock_client.py` 或任何 OpenStock 接入代码。跳过的真实根因：B4.014 的 OpenStock 接入代码完全未提交到 main，PR #489 排除了它们，理由基于错误前提" |
| §4.2 重建方法 | "理解 main 上 `MarketDataService` 如何替代 `OpenStockClient`" | "main 的 `MarketDataServiceV2` 用的是 eastmoney_adapter，不是 OpenStock。重建工作是**新建 OpenStock adapter 注册到 factory**（见 v2 审计 S5），不是'适配 V2'" |
| §5 关键引用 | 补充本 v2 审计文档链接 | 新增 |

### 4.2 修订时机

handoff 已 revert（commit `f00aff3a2`），原文件在主仓库工作区为未跟踪状态。**修订应在 S5 战略确认后**与本审计一起更新。在战略未确认前，handoff 里的错误表述暂保留，但本 v2 审计已明确指出每处错误，避免下次会话重复踩坑。

---

## 五、本审计的实证证据链（v2 修订）

### 5.1 v1 已验证命题（仍然成立）

| 命题 | 验证命令 | 结果 |
|---|---|---|
| `openstock_client.py` 在 main 不存在 | `git ls-tree -r origin/main --name-only \| grep openstock_client` | 空 |
| `openstock_client.py` 在 main 从未被提交 | `git log origin/main --follow -- **/openstock_client.py` | 空 |
| `openstock_client.py` 在 B4.014 历史里曾存在 | `git log --all --diff-filter=A --name-only -- "**/openstock_client.py"` | `web/backend/app/services/openstock_client.py` |
| #485 PR 范围窄 | `gh pr view 485 --json body` | 5 文件，仅 strategy.py |
| factory 是 Mock/Real/Hybrid | 读 `data_source_factory.py:1-3` | 注释自标"Week 1 Day 1 支持 Mock/Real/Hybrid" |
| `/quotes` 走 factory | `market_data_request.py` `/quotes` 端点 | `from app.services.data_source_factory import get_data_source_factory` |
| `/kline` 走 akshare | `market_data_request.py` `/kline` 端点注释 | "数据源: AKShare stock_zh_a_hist()" |

### 5.2 v2 新增验证命题（推翻 v1 关键判断）

| v1 命题 | v2 验证命令 | v2 结果 |
|---|---|---|
| ~~V2 接 OpenStock~~ | `git show origin/main:web/backend/app/services/market_data_service_v2.py \| head -50` | ❌ V2 自述"使用东方财富直接API，不依赖akshare"；初始化 `self.em_adapter = get_eastmoney_adapter()` |
| ~~main 路由有 `get_openstock_market_client`~~ | `git show origin/main:web/backend/app/api/market/market_data_request.py \| grep -in openstock` | ❌ 空（main 上整个文件不出现 "openstock" 字样） |
| ~~V2 有 `_fetch_openstock_sync`、`_build_openstock_client` 方法~~ | `git show origin/main:web/backend/app/services/market_data_service_v2.py \| grep -in openstock` | ❌ 空（V2 整个文件不出现 "openstock" 字样） |
| ~~main 有 `/market_v2/*` 路由接 V2 OpenStock~~ | `git show origin/main:web/backend/app/api/market/market_data_request.py` | ❌ V2 服务确实被某些路由使用，但**接入的是 fund_flow / ETF / 龙虎榜**等 eastmoney 数据，**不是行情** |
| main 上 OpenStock 接入总量 | `git show origin/main:web/backend/app/api/market/market_data_request.py \| grep -ic openstock; git show origin/main:web/backend/app/services/market_data_service_v2.py \| grep -ic openstock` | **0**（main 上这两个核心文件 OpenStock 接入为零） |

### 5.3 GitNexus 幻觉符号警告

GitNexus 在本会话内**两次**提示以下不存在的符号：
- `get_openstock_market_client` (market_data_request.py)
- `_fetch_openstock_sync` (market_data_service_v2.py)
- `_fetch_openstock_records` (market_data_service_v2.py)
- `_build_openstock_client` (market_data_service_v2.py)
- `_mock_openstock_quotes_client` (test_market_api.py)

**这些符号在 `origin/main` 上不存在**。GitNexus 索引的可能是：
- (a) 某个 worktree 的本地未提交状态
- (b) 某个分支（如 `feat/b4-014-fundflow-mixin-openspec-proposal`）的历史
- (c) 旧版本索引未刷新

**结论**：本会话已多次验证 GitNexus 在 main 数据架构相关查询上不可信，下次会话涉及 main 架构判断时应**优先使用 `git show origin/main:<file>` 直接读源码**，不能轻信 GitNexus 的符号提示。

### 5.4 OpenStock 服务可用性核查（v3 新增 P0）

**核查命令**：`curl -sS -m 5 -w "HTTP %{http_code} | time %{time_total}s" http://192.168.123.104:8040/health`

**结果**：
- HTTP 404，响应 7ms，22 bytes（`{"detail":"Not Found"}`）
- **服务在线**（TCP 连接成功、FastAPI/Uvicorn 应答），但 `/health` 端点不存在
- 实际健康端点未确认——可能路径为 `/api/health`、`/healthz`、`/` 或需查 OpenStock 服务文档

**对 S5 的影响**：
- 服务在线是好消息——OpenStock 作为 primary backend 物理可达
- 但 `/health` 端点缺失意味着 `OpenStockDataSourceAdapter.health_check()` 实现需先调研正确端点
- **S5 拍板前剩余前置**：找到 OpenStock 真实健康端点（建议读 OpenStock 项目的 API 文档或源码）

### 5.5 `IDataSource` 接口适配分析（v3 新增 P0）

**`IDataSource` 接口契约**（`web/backend/app/services/data_source_interface.py`）：
```python
class IDataSource(ABC):
    def __init__(self, config: Dict[str, Any]): ...
    @abstractmethod
    async def get_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]
    @abstractmethod
    async def health_check(self) -> HealthStatus
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]
```

**`OpenStockClient` 实际 API**（来自 B4.014 历史 commit）：
- `fetch(data_category, *, params, request_id) -> OpenStockFetchResult`（通用分类查询）
- `fetch_bars(*, symbol, period, count, request_id) -> OpenStockFetchResult`（专用方法）
- 返回值是 `OpenStockFetchResult` 数据类（不是 `Dict`）

**适配差距**：

| 维度 | factory 期望 | OpenStockClient 提供 | 适配工作 |
|---|---|---|---|
| 入口签名 | `get_data(endpoint, params)` 单一入口 | `fetch(category)` + 多个专用方法 | 需 endpoint→method 路由表（"quotes" → `fetch("REALTIME_QUOTES")`、`"kline"` → `fetch_bars(...)`） |
| 返回类型 | `Dict[str, Any]` | `OpenStockFetchResult` 数据类 | 需 unpack 数据类 → dict（包括 `data`、`source`、`latency_ms` 等字段） |
| 健康检查 | `health_check() -> HealthStatus` | 无内置健康检查 | 需新建：调 `/health`（端点需先找到，见 §5.4）或执行一次轻量 fetch 作为活性探针 |
| 性能指标 | `get_metrics() -> Dict` | 无内置指标采集 | 需在 adapter 层包装：累计请求数、错误率、平均延迟 |
| 配置 | `Dict[str, Any]`（JSON config） | `OpenStockClientConfig` frozen dataclass | 需在 adapter 内做 dict→dataclass 转换 |

**结论**：适配工作量**非平凡**，CodeWhale 估算 4-8h 合理（含路由表 + 参数映射 + 错误转换 + 健康检查 + 指标采集）。

**对 S5 风险等级的影响**：v2 评级"低"过于乐观，v3 修正为**"中"**——主要风险来自 (a) `health_check` 端点未确认、(b) endpoint 路由表需要逐个验证 OpenStock 支持的 category、(c) 测试覆盖现状未核查。

### 5.6 `httpx` 依赖声明核查（v3 新增 P0）

**核查命令**：`grep -nE "^httpx" web/backend/requirements.txt`

**结果**：`web/backend/requirements.txt:53: httpx==0.27.0`

**结论**：
- ✅ **httpx 已在 main 的 requirements.txt 声明**（v0.27.0，版本固定）
- 同时被多个现有 service 使用（`windows_bridge_adapter.py`、`byapi_adapter.py`、`kronos_client.py` 等）
- **审核意见 §3.2 表格中"未声明"判断为误**——该项无需整改

**对 S5 的影响**：无。依赖已就绪，`openstock_client.py` 直接 import httpx 可用。

### 5.7 S5 工作量与风险综合重估（v3 新增）

综合 §5.4-5.6 核查结果：

| 子任务 | 工作量 | 备注 |
|---|---|---|
| (a) 重新引入 `openstock_client.py` | 0.5h | cherry-pick 即可，代码质量良好 |
| (b) 调研 OpenStock 真实健康端点 | 0.5-1h | 需读 OpenStock 项目文档 |
| (c) 新建 `OpenStockDataSourceAdapter` | 4-8h | §5.5 适配差距全清单 |
| (d) factory 配置注册 primary | 1-2h | JSON config + 优先级策略 |
| (e) `/kline` 路由迁移 + 前端合约桥接 | 2-4h | 含 M1m 工作 |
| (f) 测试（单元 + 集成 + 回归） | 3-6h | 需先核查现有测试覆盖 |
| **总计** | **11-21h** | 约 **2-3 工作日** |

**风险等级**：**中**
- 主要不确定性：(b) 健康端点、(c) endpoint 路由表对 OpenStock category 的覆盖、(f) 现有测试覆盖
- 可控性：factory 多源骨架不变，失败可 fallback 到 akshare/eastmoney

**S5 拍板的剩余前置条件**（按优先级）：
1. 找到 OpenStock 真实健康端点（§5.4）
2. 核查 origin/main 现有测试覆盖（`pytest --collect-only -k "kline or quotes or factory"`）
3. 前端 K 线组件期望 schema 调研（§3.3 M1m 范围）

---

## 六、下次会话动作建议（v2 修订）

### 优先级 1：S5 战略确认

输入：本审计 §3.2 的 S5。
输出：用户确认 S5 路径（或提出调整）。
约束：决策必须符合用户"OpenStock 优先 + 多源保留"方向。

### 优先级 2：修正 handoff 文档错误

按 §4.1 表格修订，但**先**完成优先级 1（战略决定后 handoff 才有正确的方向描述）。

### 优先级 3：B4.014 4 commits 在 S5 下的重建

按 §3.3 表格执行：
- M1k：重新引入 `openstock_client.py` → 新建 `OpenStockDataSourceAdapter` → factory 注册为 primary
- M1m：前后端 K 线合约桥接（独立做）
- M1n：Playbook 重新定义为 "primary/fallback 语义"（不是禁止非 OpenStock）
- Wave 0：FundFlowMixin（独立做）

### 优先级 4：main 环境依赖修复（独立 PR）

与本审计无关，独立 PR。pin numpy<2, scipy<1.14, 补 pytest 插件。

### 优先级 5：dirty worktree rescue（独立议题）

按 `docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE.md` 走，与本审计无关。

### 优先级 6：GitNexus 索引刷新（低优先）

GitNexus 索引与 origin/main 不一致（§5.3）。下次会话开始时执行 `gitnexus analyze` 刷新，避免再次出现幻觉符号。**注意**：刷新前先确认索引的是哪个 ref，避免在错误的 base 上重建索引。

---

## 七、关键引用（v2 修订）

| 资源 | 路径 |
|---|---|
| 本审计 v2 | `docs/reports/worklogs/claude-auto/main-data-architecture-audit-2026-06-30.md` |
| 原 handoff（含错误，已 revert） | `docs/reports/worklogs/claude-auto/b4-014-handoff-2026-06-30.md` |
| PR #489 | https://github.com/chengjon/mystocks/pull/489 |
| PR #485（被误判为删文件） | https://github.com/chengjon/mystocks/pull/485 |
| Worktree | `/opt/claude/mystocks_spec/.claude/worktrees/b4-014-milestone`（HEAD `f00aff3a2`） |
| OpenStock 消费者边界 | `architecture/STANDARDS.md` §1.5 |
| 本项目设计方向（v2 更正） | 用户本会话更正："OpenStock 优先上游，但不是唯一，本地可连其他数据服务商" |

---

## 八、本会话工作总结（v2 修订）

### v1 会话（初版审计）
1. ✅ 修正了 3 次事实前提（openstock_client.py 真相、#485 真实范围、factory 真实架构）
2. ⚠️ 误判 V2 接 OpenStock（GitNexus 幻觉符号所致）
3. ⚠️ 误判 `/market_v2/*` 路由存在
4. ✅ 把"B4.014 重建"从"技术适配"重构为"架构战略"

### v2 会话（本次修订）
1. ✅ 推翻 v1 的 V2/OpenStock 误判（用 `git show origin/main:<file>` 直接读源码）
2. ✅ 确认 main 上 OpenStock 接入为零
3. ✅ 识别 GitNexus 在 main 数据架构查询上的幻觉符号问题
4. ✅ 用户更正方向：从"OpenStock 唯一"改为"OpenStock 优先 + 多源保留"
5. ✅ 战略从 S1/S2/S3 重构为 S5（新建 OpenStockDataSourceAdapter，注册为 factory primary backend）
6. ⏸️ M1k/M1m 实施暂停——S5 战略确认前不动手

### v2 未完成
- handoff 文档错误未修订（待 S5 战略确认后一起更新）
- S5 战略未拍板（等用户确认）
- M1k/M1m 实施未启动

---

## 九、S5 三项前置核查与正式拍板（v5 新增，2026-07-01）

### 9.1 三项前置核查结果

**前置 1：OpenStock 服务真实健康端点**

原审计 §5.4 用 `/health` 探测得到 404，结论"未知"。v5 通过 `/openapi.json` 拉到完整路由清单并直接探测：

| 端点 | 结果 |
|---|---|
| `/health/live` | ✅ HTTP 200, 9.9ms, `{"service":"openstock","status":"alive"}` |
| `/health/ready` | ⚠️ 5s 超时（端点存在但响应慢，可能做实际依赖检查） |
| `/docs` | ✅ HTTP 200, 8ms（FastAPI 文档） |
| `/sources` | ✅ HTTP 200，返回 30+ category × 多 source 的完整能力清单 |
| `/data/bars` `/data/batch` `/data/fetch` `/data/snapshot` | ✅ OpenAPI 已定义（`/data/fetch` 是核心，对 `data_category` 路由） |

**结论**：**OpenStock 服务在线可用**。`/health/live` 是正确的 liveness 端点（之前 `/health` 404 是路由名错认）。`/health/ready` 超时需在 S5 实施时单独诊断，但不阻塞 primary backend 启用——可以做"liveness 通就上，ready 失败降级到 fallback"的策略。

---

**前置 2：main 测试覆盖基线**

`pytest --collect-only -q -k "quotes or kline or factory"` 收集到 **1521 tests**，5 errors（全是 `markers` 配置问题：`ai_assisted`、`fault_injection` 未注册，非 B4.014 引入）。

**关键测试资产**（在 B4.014 分支上，origin/main 没有）：

| 测试文件 | 覆盖范围 |
|---|---|
| `tests/test_openstock_client.py` | 10 个 coroutine 测试：`fetch` 数据保留 runtime metadata、`fetch_bars` payload 形态、5 个 category contract（FUND_FLOW/SECTOR_FUND_FLOW/DRAGON_TIGER/BLOCK_TRADE/ETF_SPOT）、provider_unavailable 错误映射、unsupported_category 映射、invalid payload 拒绝 |
| `tests/test_data_adapter_regression.py` | data adapter 回归（stocks_basic/daily/dashboard/technical/strategy/watchlist） |
| `tests/test_data_api_regression.py` | API 层回归（含 `test_get_kline`） |

**结论**：B4.014 已经为 OpenStockClient 建立了完整测试样板，S5 的适配层可直接复用。**测试回归风险从 §5.7 的"中"下调为"低"**。

---

**前置 3：前端 K-line schema 兼容性**

**前端期望**（`web/frontend/src/views/market/marketKlineData.ts`）：

```typescript
interface KLineRow {
  datetime: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}
```

`extractKlineRows(payload)` 已实现 envelope 容错（`Array | {data: [...]} | {candles: [...]}` 都能解析），但**只识别英文 OHLCV + datetime 字段名**，不做字段名翻译。

**OpenStock `/data/bars` for KLINES** 字段（从 `/sources` 拉到的 `provider_capabilities`）：

```
symbol, time, open, high, low, close, volume, amount, period, anchor_date
```

**akshare `stock_zh_a_hist`** 返回（`web/backend/app/services/adapters_split/akshare_adapter.py:82-84`）：

```python
df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=..., end_date=...)
# 中文列名 DataFrame：日期/开盘/收盘/最高/最低/成交量/成交额/振幅/涨跌幅/涨跌额/换手率
```

**字段映射差距**：

| 字段 | 前端期望 | OpenStock | akshare |
|---|---|---|---|
| 时间 | `datetime` | `time` ✅（需重命名） | `日期` ❌（需翻译+重命名） |
| 开 | `open` | `open` ✅ | `开盘` ❌ |
| 高 | `high` | `high` ✅ | `最高` ❌ |
| 低 | `low` | `low` ✅ | `最低` ❌ |
| 收 | `close` | `close` ✅ | `收盘` ❌ |
| 量 | `volume` | `volume` ✅ | `成交量` ❌ |

**结论**：
- OpenStock → 前端：只需做 `time → datetime` 一对字段重命名（适配层 5 行代码）
- akshare → 前端：需要完整中文列名翻译表（已在 `akshare_adapter.py` 中存在）
- **前端 `extractKlineRows` 已做 envelope 容错，无需改动**
- M1m 合约桥接的具体工作清单：**适配层做 `time → datetime` 字段重命名**，前端零改动

**前端 K-line 兼容性从 §5.7 的"中高"下调为"低"**。

---

### 9.2 S5 风险与工作量重估

| 维度 | v4 评级 | v5 重估 | 依据 |
|---|---|---|---|
| Adapter 复杂度 | 中 | **中**（不变） | endpoint→method 路由 + 字段重命名（time→datetime）+ 错误转换 |
| 测试回归风险 | 中 | **低** ↓ | B4.014 已有 `test_openstock_client.py` 完整测试样板 |
| OpenStock 服务可用性 | 未知 | **✅ 已确认在线** | `/health/live` 9.9ms |
| 前端 K-line 兼容性 | 中高 | **低** ↓ | 适配层做字段重命名，前端零改动 |
| `/health/ready` 超时 | — | **新风险：低** | 用 liveness + 业务 fallback 即可 |
| 工作量 | 11–21h | **8–16h** ↓ | 测试和前端工作量大头已被 B4.014 提前吸收 |

**综合风险等级：中→低**（可控）

---

### 9.3 S5 正式拍板

基于三项前置全部通过，2026-07-01 用户正式拍板 S5：

**S5 战略（最终版）**：
1. 重新引入 B4.014 的 `openstock_client.py`（已在分支上，cherry-pick 或独立提交）
2. 新建 `OpenStockDataSourceAdapter` 实现 `IDataSource` 接口（endpoint→method 路由 + 字段映射）
3. 注册为 factory primary backend，保持多源 fallback（akshare/eastmoney adapter 作 fallback）
4. `/quotes` 走 factory（已通），只需让 factory 默认走 OpenStock adapter
5. `/kline` 从直连 akshare 改为走 factory
6. 健康检查用 `/health/live`；业务层 fallback 触发条件：`/health/ready` 异常 或 fetch 失败率超阈值
7. 符合用户方向更正：**OpenStock 优先 + 多源保留**

### 9.4 v5 后的下一步（按依赖顺序）

| 步骤 | 内容 | 预估 |
|---|---|---|
| (a) | `openstock_client.py` 独立 commit（或随 M1k 一起） | 0.5h |
| (b) | `OpenStockDataSourceAdapter` 实现 + endpoint 路由表 + 字段映射 + 错误转换 | 3–5h |
| (c) | factory 配置：注册为 primary + fallback 策略 + 健康检查用 `/health/live` | 1–2h |
| (d) | `/kline` 路由改走 factory + 适配层 `time→datetime` 字段重命名 | 1–2h |
| (e) | 单测：复用 `test_openstock_client.py` 模式 + 新增 adapter 单测 | 2–4h |
| (f) | 集成测试 + 回归（`test_data_adapter_regression.py` / `test_data_api_regression.py`） | 1–3h |
| **合计** | | **8–16h** |

**M1k/M1m 重建 PR 范围**：(a)(b)(c)(d) 是 M1k 范围（行情路由接入），(e)(f) 是 M1m 范围（合约桥接验证）。M1n Playbook 重新定义：不是"禁止非 OpenStock"，而是"非 OpenStock adapter 必须在 factory 注册并标记为 fallback"。Wave 0 FundFlowMixin 独立。

### 9.5 v5 未完成（移至实施阶段）

- handoff 文档错误仍未修订（§4.1 表）——可与 M1k/M1m PR 一起修订
- `/health/ready` 超时根因诊断——S5 实施时查
- Wave 0 FundFlowMixin + Wave 2/3 FundFlow 6 方法迁移——独立推进

