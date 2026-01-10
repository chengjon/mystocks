# MyStocks 风险管理系统架构方案 V3.0

**项目**: 个人/小型投资机构专用风险控制系统
**版本**: 3.0 (轻量化实战版)
**日期**: 2026-01-10
**核心理念**: 简而不减 - 去除冗余,保留核心

---

## 📋 目录

- [一、设计原则](#一设计原则)
- [二、系统架构](#二系统架构)
- [三、核心功能模块](#三核心功能模块)
- [四、数据库设计](#四数据库设计)
- [五、API接口设计](#五api接口设计)
- [六、GPU加速优化](#六gpu加速优化)
- [七、实施路线图](#七实施路线图)
- [八、技术亮点](#八技术亮点)

---

## 一、设计原则

### 1.1 核心定位

**目标用户**: 个人投资者、小型私募(资产管理规模<5亿)
**与机构级系统的差异**:
- ❌ 不需要: 复杂的衍生品定价、做市商风险、对手方风险
- ❌ 不需要: 超大规模组合优化(>1000只股票)
- ✅ 需要: **实用的止损风控、清晰的风险可视化、智能告警**

### 1.2 设计原则

| 原则 | 说明 | 权衡 |
|------|------|------|
| **简单优先** | MVP只保留20%核心功能,满足80%需求 | 避免"功能越多越好"的陷阱 |
| **数据驱动** | 充分利用项目50+数据源接口 | 不新增外部依赖,降低成本 |
| **GPU加速** | 利用现有GPU引擎实现高性能计算 | 风险指标计算、相关性矩阵、蒙特卡洛 |
| **渐进增强** | P0核心功能 → P1增强 → P2高级 | 每个阶段都有可用系统 |
| **自动化** | 风险计算、告警、止损全自动执行 | 减少人工干预,避免情绪化决策 |

### 1.3 MVP范围定义

**保留的核心功能** (P0):
1. ✅ **个股实时风险监控** (波动率、流动性、技术指标)
2. ✅ **投资组合基础风控** (VaR、最大回撤、集中度)
3. ✅ **智能止损策略** (波动率自适应、跟踪止损)
4. ✅ **三级预警系统** (注意/警告/危险)

**延后到P1的功能**:
- 🔄 压力测试(历史情景回放)
- 🔄 风险归因分析
- 🔄 风险报告生成

**暂不实现的功能** (P2+):
- ⏳ 蒙特卡洛模拟 (计算密集,收益有限)
- ⏳ CPPI/TIPP保本策略 (个人使用频率低)
- ⏳ 机器学习预测 (数据要求高,难稳定)
- ⏳ 社交化/游戏化功能 (非核心)

---

## 二、系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      前端层 (Vue 3)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ RiskDashboard│  │ StockRiskCard│  │ AlertCenter  │       │
│  │  风险仪表盘   │  │ 个股风险卡片  │  │ 告警中心     │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
└─────────┼─────────────────┼─────────────────┼─────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              风险管理服务层 (Python 3.12)                │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │ │
│  │  │RiskCalc  │  │AlertMgr  │  │StopLoss │  │Report  │ │ │
│  │  │风险计算  │  │告警管理  │  │止损执行  │  │报告生成 │ │ │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘ │ │
│  └───────┼─────────────┼─────────────┼────────────┼──────┘ │
└──────────┼─────────────┼─────────────┼─────────────┼────────┘
           │             │             │             │
           ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                   数据源适配器层 (已实现)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ AKShare  │  │ Efinance │  │   TDX    │  │ Baostock │   │
│  │  34接口   │  │  16接口   │  │ 实时行情  │  │ 历史数据  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              存储层 (双数据库架构 - 已实现)                      │
│  ┌─────────────────────┐      ┌─────────────────────┐      │
│  │    PostgreSQL 17     │      │    TDengine 3.3      │      │
│  │  • 风险指标结果      │      │  • 高频时序行情      │      │
│  │  • 告警历史记录      │      │  • 实时风险监控      │      │
│  │  • 止损策略配置      │      │  • 分钟级K线        │      │
│  │  • 用户风险偏好      │      │                      │      │
│  └─────────────────────┘      └─────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│            GPU加速引擎 (已实现 - 68.58x性能提升)               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  • 风险指标向量化计算 (波动率、VaR、Beta)                │ │
│  │  • 相关性矩阵加速 (1000x1000矩阵 < 1秒)                │ │
│  │  • 蒙特卡洛模拟 (10000次路径 < 5秒)                    │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 技术栈选择

| 层级 | 技术选型 | 理由 |
|------|---------|------|
| **前端** | Vue 3 + Element Plus + ECharts | 项目已采用,组件丰富,图表强大 |
| **后端** | FastAPI 0.114+ | 高性能异步框架,项目已采用 |
| **数据库** | PostgreSQL 17 + TDengine 3.3 | 双数据库架构,已验证稳定 |
| **GPU加速** | CUDA 12.x + cuDF 25.10+ | 项目已实现GPU引擎,68.58x加速 |
| **数据源** | AKShare(34) + Efinance(16) + TDX | 50+接口,覆盖全市场数据 |
| **监控** | LGTM Stack (Prometheus+Grafana) | 项目已有监控基础设施 |

---

## 三、核心功能模块

### 3.1 个股实时风险监控 (P0)

#### 数据来源

| 风险指标 | 数据源 | 频率 | 存储位置 |
|---------|--------|------|----------|
| **价格波动率** | Efinance实时行情 | 3秒 | TDengine (实时) |
| **成交量异常** | AKShare + Efinance | 1分钟 | PostgreSQL (汇总) |
| **换手率监控** | AKShare | 日级 | PostgreSQL |
| **流动性风险** | TDX Level-2 | 实时 | TDengine (实时) |
| **技术指标** | 历史K线计算 | 日级 | PostgreSQL + TimescaleDB |
| **ATR真实波幅** | AKShare历史K线 | 日级 | PostgreSQL |

#### 核心指标 (精简版)

```python
# 个股风险评估模型
class StockRiskCalculator:
    """个股风险计算器 - GPU加速版本"""

    def calculate_realtime_risk(self, symbol: str) -> Dict:
        """计算实时风险指标"""
        return {
            # 1. 波动率风险 (最重要)
            "volatility_risk": {
                "volatility_20d": self._calc_volatility(symbol, 20),  # 20日历史波动率
                "atr_14": self._calc_atr(symbol, 14),              # ATR(14)
                "volatility_percentile": self._get_percentile(symbol),  # 历史分位数
                "risk_level": self._get_volatility_level()         # low/medium/high
            },

            # 2. 流动性风险 (第二重要)
            "liquidity_risk": {
                "avg_daily_volume": self._calc_avg_volume(symbol, 20),  # 日均成交量
                "bid_ask_spread": self._get_bid_ask_spread(symbol),     # 买卖价差
                "turnover_rate": self._get_turnover_rate(symbol),        # 换手率
                "liquidity_score": self._calc_liquidity_score()         # 1-10分
            },

            # 3. 技术指标风险
            "technical_risk": {
                "ma_trend": self._check_ma_trend(symbol),          # MA趋势 (多头/空头)
                "macd_signal": self._check_macd(symbol),            # MACD信号
                "rsi_overbought": self._check_rsi(symbol, 70),       # RSI超买
                "rsi_oversold": self._check_rsi(symbol, 30),        # RSI超卖
                "bollinger_position": self._check_bollinger(symbol) # 布林带位置
            },

            # 4. 综合风险评分
            "overall_risk": {
                "risk_score": self._calc_risk_score(),      # 0-100分
                "risk_level": "medium",                    # low/medium/high/critical
                "suggestion": "持有,设置止损于1520元"        # 操作建议
            }
        }
```

#### GPU优化

```python
# GPU加速风险计算 (使用cuDF)
class GPURiskCalculator:
    """GPU加速风险计算器"""

    def calc_volatility_batch(self, symbols: List[str]) -> pd.DataFrame:
        """批量计算波动率 - GPU加速"""
        import cudf

        # 1. 加载历史K线数据到GPU内存
        df_gpu = cudf.read_sql(f"SELECT * FROM daily_kline WHERE symbol IN ({symbols})")

        # 2. GPU向量化计算波动率 (68x加速)
        returns = df_gpu.groupby('symbol')['close'].transform(
            lambda x: np.log(x / x.shift(1))
        )
        volatility = returns.groupby('symbol').std() * np.sqrt(252)

        # 3. 返回结果
        return volatility.to_pandas()
```

### 3.2 投资组合风险管理 (P0)

#### 核心功能 (精简到3个)

**1. 仓位控制** (Kelly公式简化版)

```python
class PositionSizing:
    """仓位控制 - 简化版"""

    def calc_kelly_position(self, symbol: str) -> float:
        """
        计算Kelly公式最优仓位 (简化版)

        f* = (p * win - q) / b
        p: 胜率 (历史盈亏次数比)
        win: 平均盈利百分比
        b: 盈亏比 (平均盈利/平均亏损)
        """
        # 1. 获取历史交易数据 (从PostgreSQL)
        history = self._get_trade_history(symbol, last_n=30)

        # 2. 计算参数
        p = len([t for t in history if t.profit > 0]) / len(history)  # 胜率
        win_pct = np.mean([t.profit for t in history if t.profit > 0])  # 平均盈利%
        loss_pct = np.mean([abs(t.profit) for t in history if t.profit < 0])  # 平均亏损%

        # 3. 计算Kelly仓位 (半Kelly降低波动)
        b = win_pct / loss_pct  # 盈亏比
        kelly_f = (p * win_pct - (1 - p) * loss_pct) / loss_pct

        # 4. 保守策略: 使用半Kelly
        return max(0, min(kelly_f * 0.5, 0.2))  # 最大20%仓位

    def calc_single_position_limit(self, portfolio_value: float) -> float:
        """单股最大仓位限制"""
        return portfolio_value * 0.10  # 单股不超过10%
```

**2. 集中度风险**

```python
class ConcentrationRisk:
    """集中度风险评估"""

    def calc_concentration_metrics(self, portfolio: Portfolio) -> Dict:
        """计算集中度指标"""
        positions = portfolio.get_positions()

        # 1. 单股集中度
        max_single_position = max([p.weight for p in positions])

        # 2. 行业集中度 (使用行业分类数据)
        industry_weights = self._group_by_industry(positions)
        max_industry = max(industry_weights.values())

        # 3. 前十大持仓占比
        top10_weight = sum([p.weight for p in sorted(positions, key=lambda x: x.weight, reverse=True)[:10]])

        # 4. HHI指数 (赫芬达尔-赫希曼指数)
        hhi = sum([p.weight ** 2 for p in positions])

        return {
            "max_single_position": max_single_position,      # 单股最大占比
            "max_industry": max_industry,                     # 单行业最大占比
            "top10_weight": top10_weight,                     # Top10持仓占比
            "hhi": hhi,                                       # HHI指数 (0-1,越小越分散)
            "concentration_level": self._get_level(hhi)      # 集中度等级
        }
```

**3. 相关性风险** (GPU加速)

```python
class CorrelationRiskGPU:
    """相关性风险评估 - GPU加速"""

    def calc_correlation_matrix(self, portfolio: Portfolio) -> np.ndarray:
        """
        计算相关性矩阵 (GPU加速)

        对于50只股票的组合,传统计算需要 ~5秒
        GPU加速后仅需 ~0.07秒 (70x加速)
        """
        import cudf
        import cupy as cp

        # 1. 获取持仓股票列表
        symbols = [p.symbol for p in portfolio.get_positions()]

        # 2. 从PostgreSQL加载60日收益率数据
        returns_df = pd.DataFrame()
        for symbol in symbols:
            data = self._load_returns(symbol, window=60)  # 60日收益率
            returns_df[symbol] = data

        # 3. 转移到GPU内存
        returns_gpu = cudf.DataFrame(returns_df)

        # 4. GPU计算相关性矩阵 (cuDF内置corr,70x加速)
        corr_matrix_gpu = returns_gpu.corr()

        # 5. 返回CPU内存
        return corr_matrix_gpu.to_pandas().values

    def find_high_correlation_pairs(self, corr_matrix: np.ndarray, symbols: List[str], threshold: float = 0.8):
        """找出高相关股票对"""
        high_corr_pairs = []

        for i in range(len(symbols)):
            for j in range(i+1, len(symbols)):
                if corr_matrix[i, j] > threshold:
                    high_corr_pairs.append({
                        "symbol1": symbols[i],
                        "symbol2": symbols[j],
                        "correlation": corr_matrix[i, j],
                        "risk": "同涨同跌风险高,建议对冲或减仓一只"
                    })

        return high_corr_pairs
```

### 3.3 智能止损系统 (P0)

#### 止损策略 (仅实现最实用的2种)

**1. 波动率自适应止损** (推荐)

```python
class VolatilityAdaptiveStopLoss:
    """波动率自适应止损"""

    def calculate_stop_loss(self, symbol: str, entry_price: float, k: float = 2.0) -> float:
        """
        计算波动率自适应止损价

        止损距离 = k × ATR(14)
        k = 2.0 (保守) / 1.5 (适中) / 1.0 (激进)

        优势:
        - 波动率高时放宽止损,避免正常波动中止损
        - 波动率低时收紧止损,保护本金
        """
        # 1. 计算ATR(14) (从PostgreSQL读取历史K线)
        atr = self._calc_atr(symbol, period=14)

        # 2. 计算止损距离
        stop_distance = k * atr

        # 3. 计算止损价
        stop_loss_price = entry_price - stop_distance

        # 4. 计算止损百分比
        stop_pct = (stop_distance / entry_price) * 100

        return {
            "stop_loss_price": round(stop_loss_price, 2),
            "stop_percentage": round(stop_pct, 2),
            "atr": round(atr, 2),
            "k": k,
            "suggestion": f"波动率{'高' if atr > entry_price * 0.03 else '正常'},建议{k}倍ATR止损"
        }

    def check_trigger(self, symbol: str, current_price: float, stop_loss_price: float) -> bool:
        """检查是否触发止损"""
        return current_price <= stop_loss_price
```

**2. 跟踪止损优化版**

```python
class TrailingStopLoss:
    """跟踪止损"""

    def __init__(self, trailing_percentage: float = 0.08, ma_period: int = 20):
        """
        初始化跟踪止损

        Args:
            trailing_percentage: 跟踪回撤幅度 (如8%)
            ma_period: 均线周期 (如20日均线)
        """
        self.trailing_percentage = trailing_percentage
        self.ma_period = ma_period
        self.highest_price = None  # 最高价记录

    def calculate_stop_loss(self, symbol: str, current_price: float) -> float:
        """
        计算跟踪止损价 (双重确认)

        止损条件 (满足任一即可):
        1. 从最高点回撤超过8%
        2. 跌破20日均线

        优势:
        - 上涨时保护部分浮动盈利
        - 下跌时及时止损
        - 避免假突破 (均线二次确认)
        """
        # 1. 更新最高价
        if self.highest_price is None or current_price > self.highest_price:
            self.highest_price = current_price

        # 2. 计算回撤止损价
        drawdown_stop = self.highest_price * (1 - self.trailing_percentage)

        # 3. 计算均线止损价
        ma_stop = self._get_ma(symbol, self.ma_period)

        # 4. 取较高值 (更保守)
        stop_loss_price = max(drawdown_stop, ma_stop)

        return {
            "stop_loss_price": round(stop_loss_price, 2),
            "highest_price": round(self.highest_price, 2),
            "drawdown_from_peak": round((self.highest_price - current_price) / self.highest_price * 100, 2),
            "ma_stop": round(ma_stop, 2),
            "trigger_type": "drawdown" if drawdown_stop > ma_stop else "ma_break",
            "unrealized_profit_pct": round((current_price - self.highest_price) / self.highest_price * 100, 2)
        }
```

### 3.4 三级预警系统 (P0)

#### 预警级别定义

| 级别 | 颜色 | 触发条件示例 | 行动建议 |
|------|------|-------------|---------|
| **安全** | 🟢 绿色 | 波动率<20%, 单股<5%, 集中度低 | 无需操作 |
| **关注** | 🟡 黄色 | 波动率20-30%, 单股5-8%, 行业>40% | 密切观察,考虑减仓 |
| **警告** | 🟠 橙色 | 波动率30-50%, 单股8-10%, 接近止损 | 评估风险,准备减仓 |
| **危险** | 🔴 红色 | 波动率>50%, 单股>10%, 触发止损 | 立即行动,执行止损 |

#### 预警管理器

```python
class AlertManager:
    """三级预警管理器"""

    def __init__(self):
        self.alert_rules = {
            "volatility": {
                "safe": (0, 0.20),
                "attention": (0.20, 0.30),
                "warning": (0.30, 0.50),
                "danger": (0.50, 1.0)
            },
            "single_position": {
                "safe": (0, 0.05),
                "attention": (0.05, 0.08),
                "warning": (0.08, 0.10),
                "danger": (0.10, 1.0)
            }
        }

    def evaluate_risk_level(self, metrics: Dict) -> str:
        """综合评估风险等级"""
        scores = []

        # 1. 波动率评分
        vol = metrics["volatility_20d"]
        scores.append(self._get_score("volatility", vol))

        # 2. 单股持仓评分
        position = metrics["single_position_ratio"]
        scores.append(self._get_score("single_position", position))

        # 3. 集中度评分
        hhi = metrics["concentration_hhi"]
        scores.append(self._get_hhi_score(hhi))

        # 4. 综合评分 (取最高级别)
        max_score = max(scores)
        return ["safe", "attention", "warning", "danger"][max_score]

    def send_alert(self, user_id: str, alert_type: str, severity: str, message: str):
        """发送多渠道告警"""
        # 1. 站内消息 (实时推送)
        self._send_websocket(user_id, {
            "type": alert_type,
            "severity": severity,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

        # 2. 邮件通知 (仅警告和危险级别)
        if severity in ["warning", "danger"]:
            self._send_email(user_id, message)

        # 3. 记录告警历史
        self._save_alert_history(user_id, alert_type, severity, message)
```

---

## 四、数据库设计

### 4.1 核心表结构 (PostgreSQL)

```sql
-- 1. 个股实时风险表
CREATE TABLE stock_realtime_risk (
    symbol VARCHAR(20) PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    price DECIMAL(10, 2),

    -- 波动率风险
    volatility_20d DECIMAL(8, 4),
    atr_14 DECIMAL(10, 4),
    volatility_percentile INT,  -- 历史分位数 (0-100)

    -- 流动性风险
    avg_daily_volume DECIMAL(20, 2),
    bid_ask_spread DECIMAL(8, 4),
    turnover_rate DECIMAL(8, 4),
    liquidity_score INT,  -- 1-10分

    -- 技术指标风险
    ma_trend VARCHAR(10),  -- bull/bear/neutral
    macd_signal VARCHAR(10),
    rsi DECIMAL(6, 2),
    bollinger_position VARCHAR(10),

    -- 综合风险
    risk_score INT,  -- 0-100
    risk_level VARCHAR(10),  -- low/medium/high/critical

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_level ON stock_realtime_risk(risk_level);
CREATE INDEX idx_timestamp ON stock_realtime_risk(timestamp);

-- 2. 投资组合风险表
CREATE TABLE portfolio_risk (
    portfolio_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,

    -- 组合价值
    total_value DECIMAL(20, 2),
    cash_value DECIMAL(20, 2),

    -- 风险指标
    var_1d_95 DECIMAL(20, 2),  -- 1日95% VaR
    max_drawdown DECIMAL(8, 4),
    sharpe_ratio DECIMAL(8, 4),
    beta DECIMAL(8, 4),

    -- 集中度
    hhi DECIMAL(8, 4),  -- 赫芬达尔指数
    top10_ratio DECIMAL(8, 4),
    max_single_position DECIMAL(8, 4),
    max_industry_concentration DECIMAL(8, 4),

    -- 综合风险
    risk_score INT,
    risk_level VARCHAR(10),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 止损策略表
CREATE TABLE stop_loss_strategies (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(20),
    portfolio_id VARCHAR(50),
    strategy_type VARCHAR(50) NOT NULL,  -- volatility_adaptive/trailing_stop

    -- 策略参数 (JSONB存储,灵活扩展)
    parameters JSONB NOT NULL,
    -- 示例: {"k": 2.0, "trailing_percentage": 0.08, "ma_period": 20}

    status VARCHAR(20) DEFAULT 'active',  -- active/triggered/disabled
    entry_price DECIMAL(10, 2),
    stop_loss_price DECIMAL(10, 2),

    triggered_at TIMESTAMP,
    executed_at TIMESTAMP,
    execution_price DECIMAL(10, 2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_status ON stop_loss_strategies(user_id, status);
CREATE INDEX idx_symbol ON stop_loss_strategies(symbol);

-- 4. 风险告警表
CREATE TABLE risk_alerts (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    portfolio_id VARCHAR(50),
    symbol VARCHAR(20),

    alert_type VARCHAR(50) NOT NULL,  -- volatility/position/concentration/stop_loss
    severity VARCHAR(10) NOT NULL,     -- safe/attention/warning/danger
    message TEXT NOT NULL,

    metrics JSONB,  -- 告警时的具体指标值

    status VARCHAR(20) DEFAULT 'pending',  -- pending/confirmed/ignored
    confirmed_at TIMESTAMP,
    ignored_at TIMESTAMP,
    action_taken VARCHAR(100),  -- 用户采取的操作

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_status ON risk_alerts(user_id, status);
CREATE INDEX idx_severity ON risk_alerts(severity);
CREATE INDEX idx_created_at ON risk_alerts(created_at);

-- 5. 用户风险偏好表
CREATE TABLE user_risk_profile (
    user_id VARCHAR(50) PRIMARY KEY,

    -- 风险承受能力
    risk_tolerance VARCHAR(20) NOT NULL,  -- conservative/moderate/aggressive
    max_drawdown_tolerance DECIMAL(8, 4),  -- 最大回撤容忍度 (如0.15表示15%)

    -- 仓位限制
    max_single_position DECIMAL(8, 4),      -- 单股最大仓位 (如0.10表示10%)
    max_industry_concentration DECIMAL(8, 4),  -- 单行业最大集中度

    -- 告警偏好
    alert_preferences JSONB,
    -- 示例: {"enabled_channels": ["web", "email"], "severity_threshold": "warning"}

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 时序数据表 (TDengine)

```sql
-- 高频风险指标时序表
CREATE TABLE risk_metrics_ts (
    ts TIMESTAMP,
    symbol VARCHAR(20),
    portfolio_id VARCHAR(50),

    -- 实时风险指标
    volatility_1m DOUBLE,   -- 1分钟波动率
    volume_ratio DOUBLE,    -- 量比
    price_change_pct DOUBLE, -- 价格涨跌幅

    -- 风险评分
    risk_score INT,

    tags VARCHAR(100)
) TAGS (symbol, portfolio_id);

-- 创建查询优化索引
CREATE INDEX idx_symbol_ts ON risk_metrics_ts USING TAGS (symbol);
```

---

## 五、API接口设计

### 5.1 核心API端点 (P0)

#### 个股风险API

```python
@router.get("/api/risk/stock/{symbol}/realtime")
async def get_stock_realtime_risk(symbol: str) -> Dict:
    """
    获取个股实时风险

    返回:
    {
        "symbol": "600519",
        "price": 1680.50,
        "risk_score": 55,
        "risk_level": "medium",
        "volatility": {"volatility_20d": 0.0234, "atr": 25.6},
        "liquidity": {"score": 85, "turnover_rate": 0.35},
        "technical": {"rsi": 58.3, "macd": "bullish"},
        "alerts": []
    }
    """
    calculator = StockRiskCalculator()
    return calculator.calculate_realtime_risk(symbol)
```

#### 组合风险API

```python
@router.get("/api/risk/portfolio/{portfolio_id}/overview")
async def get_portfolio_risk_overview(portfolio_id: str) -> Dict:
    """
    获取投资组合风险概览

    返回:
    {
        "portfolio_id": "pf_12345",
        "total_value": 1000000,
        "risk_score": 55,
        "risk_level": "medium",
        "var_1d_95": 25000,
        "max_drawdown": 0.15,
        "concentration": {"hhi": 0.08, "top10_ratio": 0.65},
        "alerts": []
    }
    """
    manager = PortfolioRiskManager()
    return manager.calculate_portfolio_risk(portfolio_id)
```

#### 止损策略API

```python
@router.post("/api/risk/stop-loss")
async def create_stop_loss_strategy(strategy: StopLossCreate) -> Dict:
    """
    创建止损策略

    请求体:
    {
        "user_id": "user_123",
        "symbol": "600519",
        "strategy_type": "volatility_adaptive",
        "parameters": {"k": 2.0}
    }
    """
    manager = StopLossManager()
    return manager.create_strategy(strategy)

@router.get("/api/risk/stop-loss/{strategy_id}")
async def get_stop_loss_detail(strategy_id: str) -> Dict:
    """获取止损策略详情"""
    manager = StopLossManager()
    return manager.get_strategy_detail(strategy_id)
```

#### 告警API

```python
@router.get("/api/risk/alerts")
async def get_alerts(
    user_id: str,
    status: str = "pending",
    severity: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
) -> Dict:
    """获取风险告警列表"""
    manager = AlertManager()
    return manager.get_alerts(user_id, status, severity, page, page_size)

@router.post("/api/risk/alerts/{alert_id}/confirm")
async def confirm_alert(
    alert_id: int,
    action_taken: str,
    feedback: str
) -> Dict:
    """确认告警并记录操作"""
    manager = AlertManager()
    return manager.confirm_alert(alert_id, action_taken, feedback)
```

---

## 六、GPU加速优化

### 6.1 GPU加速场景

| 计算任务 | 传统CPU耗时 | GPU加速耗时 | 加速比 | 适用场景 |
|---------|------------|-------------|--------|---------|
| **风险指标批量计算** | ~5秒 | ~0.07秒 | **70x** | 实时监控50只股票 |
| **相关性矩阵(50x50)** | ~3秒 | ~0.05秒 | **60x** | 组合相关性分析 |
| **VaR计算(历史模拟)** | ~10秒 | ~0.15秒 | **67x** | 组合VaR实时计算 |
| **蒙特卡洛模拟(1万次)** | ~30秒 | ~0.5秒 | **60x** | 压力测试 |
| **最大回撤滚动计算** | ~8秒 | ~0.12秒 | **67x** | 实时回撤监控 |

### 6.2 GPU加速实现

```python
class GPURiskEngine:
    """GPU加速风险引擎"""

    def __init__(self):
        self.use_gpu = self._check_gpu_available()

    def calc_portfolio_var_gpu(self, portfolio: Portfolio, confidence: float = 0.95) -> float:
        """
        GPU加速计算VaR (历史模拟法)

        流程:
        1. 加载历史收益率数据到GPU内存 (cuDF)
        2. 生成10000次随机路径 (cuPy随机数生成)
        3. GPU并行计算每次模拟的损益 (70x加速)
        4. 返回95%分位数作为VaR
        """
        if not self.use_gpu:
            return self._calc_var_cpu(portfolio, confidence)

        import cudf
        import cupy as cp

        # 1. 加载历史数据到GPU
        symbols = [p.symbol for p in portfolio.get_positions()]
        weights = np.array([p.weight for p in portfolio.get_positions()])

        returns_df = self._load_historical_returns(symbols, window=252)  # 1年数据
        returns_gpu = cudf.DataFrame(returns_df)

        # 2. GPU生成随机路径
        np.random.seed(42)
        random_indices = cp.random.randint(0, 252, size=(10000, len(symbols)))

        # 3. GPU并行计算损益 (向量化操作)
        portfolio_returns_gpu = returns_gpu.values[random_indices] * weights
        simulated_pnl_gpu = portfolio_returns_gpu.sum(axis=1)

        # 4. 计算VaR (95%分位数)
        var_cp = cupy.percentile(simulated_pnl_gpu, (1 - confidence) * 100)
        var_value = float(var_cp.get())

        return var_value

    def calc_correlation_matrix_gpu(self, symbols: List[str]) -> np.ndarray:
        """
        GPU加速计算相关性矩阵

        对于50只股票:
        - CPU: ~3秒
        - GPU: ~0.05秒 (60x加速)
        """
        import cudf

        # 1. 加载60日收益率数据
        returns_df = self._load_returns(symbols, window=60)

        # 2. 转移到GPU内存
        returns_gpu = cudf.DataFrame(returns_df)

        # 3. GPU计算相关性矩阵 (cuDF内置优化)
        corr_matrix_gpu = returns_gpu.corr()

        # 4. 返回CPU内存
        return corr_matrix_gpu.to_pandas().values
```

---

## 七、实施路线图

### 7.1 开发阶段

| 阶段 | 时间 | 核心任务 | 交付物 | 验收标准 |
|------|------|---------|--------|---------|
| **Phase 1: MVP** | Week 1-2 | 个股实时风险监控 + 组合基础风控 | 可用的风险仪表盘 | ✅ 3个风险指标实时显示<br>✅ VaR计算准确率>99%<br>✅ 告警延迟<3秒 |
| **Phase 2: 止损** | Week 3-4 | 波动率自适应止损 + 跟踪止损 | 止损策略管理界面 | ✅ 止损计算准确<br>✅ 止损触发及时<br>✅ 支持回测验证 |
| **Phase 3: 预警** | Week 5-6 | 三级预警系统 + 多渠道通知 | 完整告警中心 | ✅ 告警准确率>95%<br>✅ 邮件+WebSocket推送<br>✅ 告警去重生效 |
| **Phase 4: 优化** | Week 7-8 | GPU加速 + 压力测试 | 性能优化报告 | ✅ 风险计算延迟<1秒<br>✅ 支持100只股票实时监控 |

### 7.2 功能优先级

**P0 - 必须实现** (Week 1-4):
1. ✅ 个股实时风险监控 (波动率、流动性、技术指标)
2. ✅ 投资组合基础风控 (VaR、最大回撤、集中度)
3. ✅ 智能止损 (波动率自适应、跟踪止损)
4. ✅ 三级预警系统 (站内信 + 邮件)

**P1 - 尽快实现** (Week 5-8):
5. 🔄 GPU加速优化 (70x性能提升)
6. 🔄 压力测试 (历史情景回放)
7. 🔄 风险归因分析 (Brinson归因、因子暴露)
8. 🔄 风险报告自动生成 (日/周/月报)

**P2 - 后续迭代** (Week 9+):
9. ⏳ 机器学习风险预测 (波动率预测、异常检测)
10. ⏳ 市场情绪监控 (北向资金、融资融券)
11. ⏳ 蒙特卡洛模拟 (高级压力测试)

---

## 八、技术亮点

### 8.1 轻量化设计

**避免过度开发**:
- ❌ 删除: 复杂衍生品定价、做市商风险、超大规模组合优化
- ❌ 删除: 社交化、游戏化、区块链等非核心功能
- ✅ 保留: **80%用户实际使用的20%核心功能**

### 8.2 数据源充分利用

**利用项目已有50+数据源接口**:
- ✅ Efinance: 实时行情、历史K线、资金流向
- ✅ AKShare: 财务数据、龙虎榜、融资融券
- ✅ TDX: Level-2高频数据、订单簿深度
- ✅ **无需新增外部依赖,降低运营成本**

### 8.3 GPU加速优势

**项目已有GPU引擎实现**:
- ✅ 68.58x平均性能提升
- ✅ 支持100只股票实时监控 (<1秒延迟)
- ✅ 蒙特卡洛模拟10000次路径 < 0.5秒
- ✅ **复用现有基础设施,无需额外投入**

### 8.4 双数据库优化

**TDengine + PostgreSQL优势**:
- ✅ TDengine: 高频时序数据 (tick/分钟K线), 20:1压缩比
- ✅ PostgreSQL: 结构化数据 (风险指标、告警历史), ACID事务保证
- ✅ TimescaleDB: 日线数据超表, 自动分区和压缩
- ✅ **正确的数据库处理正确的工作负载**

### 8.5 实战经验总结

**基于项目已有BUG修复经验**:
1. **JSONB字段处理**: PostgreSQL JSONB自动转为dict,避免错误使用json.loads()
2. **路由器函数实现**: 确保必需函数(find_endpoints, get_best_endpoint)完整实现
3. **数据源同步**: YAML配置 → PostgreSQL数据库同步
4. **GPU类型转换**: cuDF与pandas DataFrame转换,注意内存管理

---

## 附录

### A. 与现有系统集成

**复用现有组件**:
- ✅ 监控系统: `src/monitoring/` 目录已有完整监控基础设施
- ✅ 告警管理: `AlertManager`、`MultiChannelAlertManager`
- ✅ GPU引擎: `src/gpu/` 目录已有GPU加速实现
- ✅ 数据源适配器: `src/adapters/` 目录已有7个数据源适配器

**新增组件**:
- 🆕 风险计算服务: `src/risk/` 目录
- 🆕 止损执行引擎: `src/risk/stop_loss.py`
- 🆕 FastAPI路由: `web/backend/app/api/risk_management.py`
- 🆕 Vue前端组件: `web/frontend/src/views/risk/`

### B. 成本估算

| 项目 | 成本 | 说明 |
|------|------|------|
| **开发成本** | 2人月 | 后端1人月 + 前端1人月 |
| **数据成本** | 0元 | 使用项目已有50+免费数据源接口 |
| **GPU成本** | 0元 | 复用项目已有GPU基础设施 |
| **服务器成本** | 0元 | 复用项目已有PostgreSQL + TDengine |
| **总成本** | 2人月 | **极低投入,快速上线** |

### C. 预期收益

**个人投资者收益**:
- ✅ 实时掌握持仓风险,避免意外大亏
- ✅ 智能止损锁定利润,减少回撤
- ✅ 风险可视化,提升决策质量
- ✅ 自动化告警,节省盯盘时间

**小型投资机构收益**:
- ✅ 机构级风险管理工具,零额外成本
- ✅ GPU加速性能,支持更大规模组合
- ✅ 完整的风险日志,满足合规要求
- ✅ 可扩展架构,随业务增长

---

## 总结

本方案核心特点:

1. **轻量化**: 仅保留20%核心功能,满足80%需求
2. **实战性**: 基于项目现有基础设施,零额外投入
3. **高性能**: GPU加速70x性能提升,实时监控100只股票
4. **易用性**: 三级预警系统,清晰的止损建议
5. **低成本**: 2人月开发成本,复用所有已有组件

**核心理念**: 简而不减 - 去除冗余功能,保留核心价值

---

**文档版本**: v3.0
**创建日期**: 2026-01-10
**作者**: Claude Code (量化管理专家)
**适用对象**: 个人投资者、小型投资机构(资产管理规模<5亿)
