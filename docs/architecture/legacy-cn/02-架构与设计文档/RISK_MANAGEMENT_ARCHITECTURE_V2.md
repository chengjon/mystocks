# 轻量级高性能风险管理系统架构方案 (LHP-RMS)

**版本**: v2.0
**日期**: 2026-01-10
**状态**: 待审核
**适用场景**: 个人/小型量化投资机构 (MyStocks Project)

---

## 1. 设计理念

针对个人及小型机构"资源有限、追求实效"的特点，本方案摒弃传统金融机构繁冗的合规报告功能，聚焦于**资本保全**与**执行效率**。充分利用现有的 `Data Source Ecosystem` (50+数据源) 和 GPU 算力，构建一个**实时、自动、可操作**的风控闭环。

**核心原则**:
1.  **数据驱动 (Data-Driven)**: 直接复用 `MyStocksUnifiedManager` 和 `TDengine` 中的实时清洗数据。
2.  **算力赋能 (GPU-Accelerated)**: 利用 GPU 处理矩阵运算（相关性、VaR），释放 CPU 用于策略逻辑。
3.  **交易阻断 (Execution-Gated)**: 风控不是事后报告，而是事前拦截（Pre-trade）和事中干预（Real-time）。

---

## 2. 系统架构图

```mermaid
graph TD
    subgraph Data Layer [数据层 - 已就绪]
        RT[TDengine: 实时行情]
        Ref[PostgreSQL: 持仓/历史]
        DS[数据源生态: AkShare/TDX]
    end

    subgraph Risk Engine [核心风控引擎 src/governance/risk_management]
        direction TB
        L1[资产卫士 Asset Guardian] -->|单标的检查| Signal
        L2[组合平衡器 Portfolio Balancer] -->|系统性风险| Signal
        L3[交易哨兵 Execution Sentinel] -->|订单拦截| OrderSystem
        
        Calc[计算核心]
        Calc --> CPU_Calc[CPU: 基础指标]
        Calc --> GPU_Calc[GPU: 矩阵/模拟]
    end

    subgraph Application [应用层]
        API[FastAPI: /api/v1/risk]
        Dash[前端: 风险仪表盘]
        Alert[通知中心: 邮件/微信]
    end

    RT --> Risk Engine
    Ref --> Risk Engine
    Risk Engine --> API
    Risk Engine --> Alert
```

---

## 3. 四大核心功能模块 (功能范围)

### 3.1 资产卫士 (Asset Guardian) - P0 级
*专注单只股票的"体检"，防止持有"有毒"资产。*

| 功能点 | 风险逻辑 | 数据源 (已就绪) | 实现方式 |
| :--- | :--- | :--- | :--- |
| **实时波动监控** | 价格发生异常闪崩或拉升 | `REALTIME_QUOTES` (TDX) | 实时计算 1分钟/5分钟 收益率标准差，超过阈值(如3σ)告警。 |
| **流动性枯竭预警** | 成交量过低，导致无法平仓 | `TICK_DATA`, `DAILY_KLINE` | 监控 `换手率 < 0.5%` 或 `量比 < 0.3`。 |
| **趋势破位保护** | 价格跌破关键支撑位 | `DAILY_KLINE` | 检查 `Price < MA(60)` 或 `Price < 20日低点`。 |
| **盘口异常检测** | 跌停板大单封死预兆 | `ORDER_BOOK_DEPTH` | 监控 `买一量` 急剧减少或 `卖一量` 异常堆积。 |

### 3.2 组合平衡器 (Portfolio Balancer) - P1 级
*专注投资组合的"健康度"，防止鸡蛋放在同一个篮子里。*

| 功能点 | 风险逻辑 | 数据源 (已就绪) | 实现方式 |
| :--- | :--- | :--- | :--- |
| **集中度控制** | 单股或单行业持仓过重 | `REALTIME_POSITIONS` | 限制 `单股仓位 < 20%`，`行业仓位 < 40%`。 |
| **相关性矩阵 (GPU)** | 持仓股票同涨同跌风险 | `DAILY_KLINE` (全持仓) | **GPU (CuPy)** 计算 N只股票的 Correlation Matrix，热力图展示。 |
| **组合 VaR (GPU)** | 极端情况下的最大预期亏损 | `DAILY_KLINE` | **GPU** 加速的历史模拟法 (Historical Simulation)，置信度 95%。 |
| **杠杆/保证金监控** | 融资融券爆仓风险 | `REALTIME_ACCOUNT` | 实时监控 `维持担保比例 < 140%` 立即告警。 |

### 3.3 交易哨兵 (Execution Sentinel) - P0 级
*专注交易环节的"安检"，防止因操作失误或市场环境恶劣导致的亏损。*

| 功能点 | 风险逻辑 | 数据源 | 实现方式 |
| :--- | :--- | :--- | :--- |
| **事前风控 (Pre-trade)** | 下单前检查是否违规 | `STRATEGY_PARAMS` | 拦截器模式：`validate_order(order)`。若超仓位或被禁交易，直接拒绝。 |
| **滑点控制** | 市场买卖价差过大 | `ORDER_BOOK_DEPTH` | 若 `(Ask1 - Bid1) / Bid1 > 1%`，暂停市价单，改用限价单。 |
| **动态止损 (Trailing)** | 盈利回撤保护 | `REALTIME_QUOTES` | 记录持仓最高价 `High_Watermark`，若回撤 `> ATR(14)*2` 触发市价平仓。 |

### 3.4 市场雷达 (Market Radar) - P2 级
*专注宏观环境的"天气预报"，决定是否空仓或减仓。*

| 功能点 | 风险逻辑 | 数据源 | 实现方式 |
| :--- | :--- | :--- | :--- |
| **市场宽度 (Breadth)** | 市场整体赚钱效应 | `MARKET_BREADTH` (衍生) | 计算全市场 `上涨家数 / 下跌家数` 比例。 |
| **聪明钱流向** | 北向/主力资金大幅流出 | `FUND_FLOW` (AkShare) | 监控 `主力净流出 > 100亿` 或 `北向大幅流出`。 |

---

## 4. 技术实施方案

### 4.1 目录结构规划
将风控逻辑从 API 层剥离，下沉至核心领域层。

```text
src/
├── governance/
│   └── risk_management/         # 新增：核心风控模块
│       ├── __init__.py
│       ├── asset_guard.py       # 个股风险逻辑 (Asset Guardian)
│       ├── portfolio_risk.py    # 组合风险逻辑 (Portfolio Balancer)
│       ├── execution_guard.py   # 交易拦截逻辑 (Execution Sentinel)
│       ├── alerts.py            # 告警聚合与分发
│       └── calculators/         # 计算引擎
│           ├── cpu_calc.py      # Pandas 实现 (基础指标)
│           └── gpu_calc.py      # CuPy/PyTorch 实现 (矩阵/模拟)
```

### 4.2 关键技术栈
*   **计算**: Python 3.12, Pandas, NumPy, **CuPy (GPU加速)**
*   **存储**: TDengine (实时流计算窗口), PostgreSQL (配置/历史)
*   **API**: FastAPI (异步非阻塞)
*   **通信**: 内存队列 (In-Process) 或 Redis Pub/Sub (用于触发交易系统)

### 4.3 实施路线图 (Roadmap)

**阶段一：生存基石 (MVP) - 预计 2周**
*   **目标**: 替换 `api/risk_management.py` 中的 Mock 数据，接入真实数据源。
*   **任务**:
    1.  建立 `src/governance/risk_management` 目录结构。
    2.  实现 `Asset Guardian`：接入 `MyStocksUnifiedManager` 获取真实行情，计算波动率和均线风险。
    3.  实现 `Execution Sentinel`：基础的 Pre-trade 检查接口。
    4.  输出：可用的 `/api/v1/risk/check` 接口，供交易系统调用。

**阶段二：组合优化 (GPU) - 预计 2周**
*   **目标**: 启用 GPU 算力，上线组合级风控。
*   **任务**:
    1.  实现 `src/gpu/risk_engine.py` (或 `calculators/gpu_calc.py`)。
    2.  开发相关性矩阵和 VaR 计算逻辑。
    3.  前端 `RiskDashboard` 对接真实组合风险数据。

**阶段三：全自动化 - 预计 2周**
*   **目标**: 完善告警与自动处置。
*   **任务**:
    1.  集成 `NotificationManager` 实现多渠道告警。
    2.  实现动态止损的自动触发逻辑（需谨慎测试）。
    3.  上线市场雷达功能。

---

## 5. 数据源映射表 (已验证)

| 风险模块 | 核心指标 | 数据源 API (参考) |
| :--- | :--- | :--- |
| **个股** | 实时价格/成交量 | `akshare.stock_zh_a_spot_em`, `tdx.get_security_quotes` |
| **个股** | 历史K线 (波动率) | `akshare.stock_zh_a_hist`, `efinance.stock.get_quote_history` |
| **组合** | 持仓信息 | `trade.position` (内部数据库) |
| **组合** | 财务/基本面 | `akshare.stock_financial_abstract`, `efinance.stock.get_base_info` |
| **市场** | 资金流向 | `akshare.stock_individual_fund_flow`, `efinance.stock.get_money_flow` |
| **市场** | 龙虎榜/大宗 | `akshare.stock_lhb_detail_em` |

---

**总结**:
本方案不追求大而全，而是追求**快而准**。通过复用现有的数据生态，我们能以极低的成本快速构建起一套保护本金的"防盗门"。下一步建议优先落地 **阶段一 (MVP)**，确保所有风险计算不再基于 Mock 数据。
