# MyStocks量化分析功能整合方案

## 📋 执行摘要

本文档分析了`temp/analysis`目录下5个文件描述的量化分析功能，并提出将这些功能整合到现有MyStocks系统的本地化方案。

**分析文件**：
- README.md - 项目总览
- data_capture.md - 数据抓取模块
- data_analysis.md - 数据分析模块（选股+回测）
- data_visualization.md - 数据可视化模块
- complete_example.md - 完整使用示例

---

## 🎯 功能梳理要点

### 1️⃣ 数据抓取模块（Data Capture）

**核心功能**：
- 从通达信本地数据文件读取股票数据（避免网络爬虫不稳定性）
- 二进制格式转换（`.day` → CSV/pickle）
- 前复权处理
- 财务数据和股本变迁数据读取

**关键组件**：
```
readTDX_lday.py    # 日线数据读取和处理
readTDX_cw.py      # 财务数据读取
```

**特点**：
- ✅ 本地化数据处理，不依赖网络
- ✅ 支持增量更新和全量重建
- ✅ 多进程并行处理
- ✅ pickle格式优化读取性能

**技术依赖**：
- struct（二进制解析）
- pandas（数据处理）
- 通达信数据格式规范

---

### 2️⃣ 数据分析模块（Strategy & Backtest）

**核心功能**：
- 自定义选股策略执行
- 策略信号生成和保存
- 基于RQAlpha的回测分析

**关键组件**：
```
xuangu.py         # 选股策略执行器
celue_save.py     # 策略信号保存
huice.py          # RQAlpha回测引擎
celue.py          # 策略模板（用户自定义）
CeLue模板.py      # 策略开发模板
```

**策略执行流程**：
```
1. 策略1（快速筛选） → 初步筛选股票池
2. 策略2（深度分析） → 生成买入信号
3. 卖策略 → 生成卖出信号
4. 信号汇总 → celue汇总.csv
5. RQAlpha回测 → 生成报告和收益曲线
```

**特点**：
- ✅ 支持盘中选股和盘后选股
- ✅ 多进程并行提高效率
- ✅ 剔除ST股、科创板等特定股票
- ✅ 策略模板化，易于扩展
- ✅ 完整的回测框架（RQAlpha）

**技术依赖**：
- pandas, numpy（数据处理）
- talib（技术指标计算）
- RQAlpha（回测框架）
- tqdm（进度显示）
- rich（终端美化）

---

### 3️⃣ 数据可视化模块（Visualization）

**核心功能**：
- K线图绘制
- 策略买卖点标记
- 持仓区域可视化（盈亏颜色区分）
- 回测收益曲线图

**关键组件**：
```
plot.py           # K线图+买卖点可视化（PyECharts）
huice.py          # 回测收益曲线（RQAlpha内置）
```

**可视化元素**：
- **K线**：OHLC数据
- **买卖点标记**：策略信号位置
- **持仓区域**：红色（盈利）/绿色（亏损）
- **趋势线**：辅助分析线
- **数据缩放**：支持时间范围选择
- **交互式图表**：HTML格式，浏览器查看

**特点**：
- ✅ 基于PyECharts，交互性强
- ✅ 视觉化盈亏分析
- ✅ 支持自定义股票查看
- ✅ 生成静态HTML文件

**技术依赖**：
- pyecharts（图表库）
- RQAlpha（回测可视化）

---

## 🏗️ 现有MyStocks架构分析

### 架构核心特点

**1. 5层数据分类系统**
```
Market Data（时序数据）   → TDengine
Reference Data（参考数据） → MySQL
Derived Data（衍生数据）   → PostgreSQL+TimescaleDB
Transaction Data（交易）   → Redis(hot) + PostgreSQL(cold)
Meta Data（元数据）        → MySQL
```

**2. 适配器模式数据源**
```
已有适配器：
- akshare_adapter.py
- tdx_adapter.py
- baostock_adapter.py
- financial_adapter.py
- tushare_adapter.py
等...
```

**3. Web架构（FastAPI + Vue）**
```
后端API：
- /api/data       # 数据查询
- /api/market     # 市场数据
- /api/indicators # 技术指标（161个TA-Lib指标）
- /api/tdx        # 通达信接口
- /api/wencai     # 问财接口
等...

策略模块：
- strategies/strategy_base.py  # 策略基类
- StrategyRegistry             # 策略注册表
```

**4. 已有服务**
```
- indicator_calculator  # 161个TA-Lib指标计算
- data_service         # OHLCV数据加载
- monitoring           # 完整监控体系
```

---

## 🔗 架构对接分析

### 对接点1：数据抓取层
```
现状：
✅ 已有tdx_adapter.py（通达信在线接口）
❌ 缺少本地数据文件读取

整合方案：
新增 → adapters/tdx_local_adapter.py
     ├─ readTDX_lday() - 日线数据读取
     ├─ readTDX_cw() - 财务数据读取
     └─ day2csv() - 二进制格式转换
```

### 对接点2：策略执行层
```
现状：
✅ 已有StrategyBase基类
✅ 已有StrategyRegistry注册表
❌ 缺少完整的选股和回测框架

整合方案：
扩展 → strategies/
     ├─ stock_screening.py  # 选股策略执行
     ├─ signal_generator.py # 信号生成器
     └─ backtest_engine.py  # 回测引擎（RQAlpha集成）
```

### 对接点3：API接口层
```
现状：
✅ 已有 /api/indicators（技术指标）
❌ 缺少策略和回测接口

整合方案：
新增 → api/
     ├─ strategy.py  # 策略管理API
     │   ├─ POST /api/strategy/execute     # 执行选股
     │   ├─ POST /api/strategy/backtest    # 执行回测
     │   ├─ GET  /api/strategy/signals     # 获取信号
     │   └─ GET  /api/strategy/list        # 策略列表
     └─ visualization.py  # 可视化API
         ├─ GET  /api/viz/kline/{symbol}   # K线图数据
         └─ GET  /api/viz/backtest/{id}    # 回测结果
```

### 对接点4：前端可视化层
```
现状：
✅ Vue3前端框架
✅ ECharts图表库
❌ 缺少策略信号可视化组件

整合方案：
新增 → web/frontend/src/components/
     ├─ strategy/
     │   ├─ StrategyExecutor.vue   # 策略执行器
     │   ├─ BacktestViewer.vue     # 回测查看器
     │   └─ SignalList.vue         # 信号列表
     └─ charts/
         ├─ KLineChart.vue         # K线图（含买卖点）
         └─ BacktestChart.vue      # 回测收益曲线
```

---

## 💡 本地化整合建议

### 建议1：数据层整合 ⭐⭐⭐⭐⭐

**问题分析**：
- 原项目依赖通达信本地文件，需要手动运行readTDX_lday.py
- MyStocks已有完整的数据管理系统和多数据源适配器

**整合方案**：
```python
# adapters/tdx_local_adapter.py
class TDXLocalAdapter(IDataSource):
    """
    通达信本地数据适配器
    复用现有适配器接口，读取本地通达信数据文件
    """

    def __init__(self, tdx_path: str):
        self.tdx_path = tdx_path

    def fetch_daily_data(self, symbol: str, start_date: str, end_date: str):
        """读取日线数据（从.day文件）"""
        day_file = self._get_day_file_path(symbol)
        df = self._parse_day_file(day_file)
        df = self._apply_qfq(df, symbol)  # 前复权
        return df

    def fetch_financial_data(self, symbol: str):
        """读取财务数据（从通达信专业财务文件）"""
        cw_file = self._get_cw_file_path(symbol)
        return self._parse_cw_file(cw_file)
```

**配置整合**：
```yaml
# table_config.yaml 新增配置
data_sources:
  tdx_local:
    enabled: true
    tdx_path: "/path/to/tdx"
    auto_update: true
    update_schedule: "16:00"  # 每日收盘后自动更新
```

**优势**：
✅ 复用现有适配器接口
✅ 自动化数据更新（定时任务）
✅ 无需手动运行脚本
✅ 数据统一存储到TDengine/PostgreSQL

---

### 建议2：策略层重构 ⭐⭐⭐⭐⭐

**问题分析**：
- 原项目策略硬编码在celue.py，不够模块化
- MyStocks已有StrategyBase基类框架

**整合方案**：
```python
# strategies/stock_screening_strategy.py
from app.strategies.strategy_base import StrategyBase, StrategyCategory

class StockScreeningStrategy(StrategyBase):
    """
    选股策略（对标原xuangu.py）
    """

    def __init__(self):
        super().__init__(
            strategy_id="stock_screening_v1",
            name="多因子选股策略",
            description="基于技术指标和财务数据的多因子选股",
            category=StrategyCategory.TREND_FOLLOWING
        )

    def execute(self, symbol: str, start_date: str, end_date: str, parameters: dict):
        """
        执行选股策略
        """
        # 1. 加载OHLCV数据（复用data_service）
        data_service = get_data_service()
        df = data_service.load_stock_data(symbol, start_date, end_date)

        # 2. 计算技术指标（复用indicator_calculator）
        calculator = get_indicator_calculator()
        df = calculator.calculate_indicators(df, ['MA', 'MACD', 'RSI'])

        # 3. 策略逻辑
        signals = self._apply_strategy_logic(df, parameters)

        return signals

    def _apply_strategy_logic(self, df, params):
        """
        策略逻辑实现
        (将原celue.py中的策略1、策略2逻辑移植到这里)
        """
        # 策略1：初步筛选
        filter1 = self._strategy_filter_1(df, params)

        # 策略2：买入信号
        buy_signals = self._strategy_buy(df, params)

        # 卖出策略
        sell_signals = self._strategy_sell(df, params)

        return pd.DataFrame({
            'date': df['date'],
            'signal': buy_signals - sell_signals,  # 1=买, -1=卖, 0=持有
            'price': df['close'],
            'reason': self._generate_reason(df, buy_signals, sell_signals)
        })
```

**优势**：
✅ 模块化设计，易于扩展
✅ 复用现有161个TA-Lib指标
✅ 策略可注册、可管理
✅ 支持参数化配置

---

### 建议3：回测引擎集成 ⭐⭐⭐⭐

**问题分析**：
- 原项目使用RQAlpha，是Python生态成熟的回测框架
- MyStocks尚无回测模块

**整合方案**：
```python
# services/backtest_service.py
from rqalpha import run_func
from rqalpha.api import *

class BacktestService:
    """
    回测服务（集成RQAlpha）
    """

    def run_backtest(self, strategy_id: str, signals_df: pd.DataFrame, config: dict):
        """
        执行回测

        Args:
            strategy_id: 策略ID
            signals_df: 信号DataFrame（celue汇总.csv格式）
            config: 回测配置
        """

        # RQAlpha配置
        rq_config = {
            "base": {
                "start_date": config['start_date'],
                "end_date": config['end_date'],
                "accounts": {"stock": config['initial_capital']},
                "frequency": "1d",
                "matching_type": "current_bar"
            },
            "mod": {
                "sys_analyser": {
                    "enabled": True,
                    "benchmark": "000300.XSHG",
                    "plot_save_file": f"backtest_results/{strategy_id}.png"
                }
            }
        }

        # 执行回测
        result = run_func(
            init=self._init_strategy(signals_df),
            handle_bar=self._handle_bar(signals_df),
            config=rq_config
        )

        # 保存回测结果到PostgreSQL（Derived Data）
        self._save_backtest_result(strategy_id, result)

        return result

    def _init_strategy(self, signals_df):
        """初始化策略（对标原huice.py的init函数）"""
        def init(context):
            context.signals = signals_df
            # ... 其他初始化逻辑
        return init

    def _handle_bar(self, signals_df):
        """处理每日行情（对标原huice.py的handle_bar函数）"""
        def handle_bar(context, bar_dict):
            # 根据signals_df生成交易
            today_signals = context.signals[context.signals['date'] == context.now]
            for _, signal in today_signals.iterrows():
                if signal['celue_buy']:
                    order_target_value(signal['code'], context.target_value)
                elif signal['celue_sell']:
                    order_target_value(signal['code'], 0)
        return handle_bar
```

**API接口**：
```python
# api/strategy.py
@router.post("/backtest")
async def run_backtest(request: BacktestRequest):
    """
    执行策略回测

    Request:
        strategy_id: str
        start_date: str
        end_date: str
        initial_capital: float
        signals: List[Signal]  # 策略信号

    Response:
        backtest_id: str
        total_returns: float
        annualized_returns: float
        max_drawdown: float
        sharpe_ratio: float
        result_plot_url: str  # 收益曲线图URL
    """
    service = get_backtest_service()
    result = await service.run_backtest(
        strategy_id=request.strategy_id,
        signals_df=pd.DataFrame(request.signals),
        config={
            'start_date': request.start_date,
            'end_date': request.end_date,
            'initial_capital': request.initial_capital
        }
    )

    return BacktestResponse(
        backtest_id=result['id'],
        total_returns=result['summary']['total_returns'],
        annualized_returns=result['summary']['annualized_returns'],
        max_drawdown=result['summary']['max_drawdown'],
        sharpe_ratio=result['summary']['sharpe_ratio'],
        result_plot_url=f"/api/backtest/plot/{result['id']}"
    )
```

**优势**：
✅ 复用RQAlpha成熟框架
✅ 支持多种回测模式
✅ 自动生成性能指标
✅ 结果持久化存储

---

### 建议4：可视化组件开发 ⭐⭐⭐⭐

**问题分析**：
- 原项目使用PyECharts生成静态HTML
- MyStocks已有ECharts前端集成

**整合方案**：
```vue
<!-- web/frontend/src/components/charts/KLineWithSignals.vue -->
<template>
  <div class="kline-chart">
    <v-chart :option="chartOption" :autoresize="true" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CandlestickChart, LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, DataZoomComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { getKLineData, getStrategySignals } from '@/api/visualization'

// 注册ECharts组件
use([CandlestickChart, LineChart, GridComponent, TooltipComponent, DataZoomComponent, CanvasRenderer])

const props = defineProps({
  symbol: String,
  startDate: String,
  endDate: String,
  strategyId: String
})

const klineData = ref([])
const signals = ref([])

const chartOption = computed(() => ({
  title: { text: `${props.symbol} K线图与策略信号` },
  grid: { left: '3%', right: '1%', bottom: '10%' },
  xAxis: { type: 'category', data: klineData.value.map(d => d.date) },
  yAxis: { type: 'value', scale: true },
  dataZoom: [
    { type: 'inside', start: 0, end: 100 },
    { type: 'slider', start: 0, end: 100 }
  ],
  series: [
    // K线图
    {
      type: 'candlestick',
      data: klineData.value.map(d => [d.open, d.close, d.low, d.high]),
      itemStyle: {
        color: '#ef232a',
        color0: '#14b143',
        borderColor: '#ef232a',
        borderColor0: '#14b143'
      },
      // 买卖点标记区域（对标原plot.py的markareadata）
      markArea: {
        silent: true,
        data: generateMarkAreas(),
        itemStyle: { opacity: 0.5 }
      }
    }
  ],
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' }
  }
}))

function generateMarkAreas() {
  // 将原plot.py的markareadata逻辑移植到这里
  const areas = []
  let buyIndex = null

  signals.value.forEach((signal, idx) => {
    if (signal.type === 'buy' && buyIndex === null) {
      buyIndex = idx
    } else if (signal.type === 'sell' && buyIndex !== null) {
      const buyPrice = klineData.value[buyIndex].close
      const sellPrice = klineData.value[idx].close
      const isProfitable = sellPrice > buyPrice

      areas.push([
        { xAxis: buyIndex },
        {
          xAxis: idx,
          itemStyle: { color: isProfitable ? '#ef232a' : '#14b143' }
        }
      ])
      buyIndex = null
    }
  })

  return areas
}

onMounted(async () => {
  // 加载K线数据和策略信号
  klineData.value = await getKLineData(props.symbol, props.startDate, props.endDate)
  signals.value = await getStrategySignals(props.strategyId, props.symbol)
})
</script>
```

**API支持**：
```python
# api/visualization.py
@router.get("/kline/{symbol}")
async def get_kline_data(
    symbol: str,
    start_date: str,
    end_date: str
):
    """
    获取K线数据
    """
    data_service = get_data_service()
    df = data_service.load_stock_data(symbol, start_date, end_date)

    return {
        "symbol": symbol,
        "data": df.to_dict(orient='records')
    }

@router.get("/signals/{strategy_id}/{symbol}")
async def get_strategy_signals(
    strategy_id: str,
    symbol: str
):
    """
    获取策略信号（买卖点）
    """
    # 从PostgreSQL读取策略信号（Derived Data）
    signals = await db.query(
        """
        SELECT date, signal_type, price, reason
        FROM strategy_signals
        WHERE strategy_id = %s AND symbol = %s
        ORDER BY date
        """,
        (strategy_id, symbol)
    )

    return {
        "strategy_id": strategy_id,
        "symbol": symbol,
        "signals": signals
    }
```

**优势**：
✅ 前后端分离，更现代化
✅ 实时交互，体验更好
✅ 复用ECharts组件库
✅ 支持多图表联动

---

### 建议5：自动化任务调度 ⭐⭐⭐

**问题分析**：
- 原项目需要手动运行多个脚本
- MyStocks已有后台任务系统

**整合方案**：
```python
# tasks/strategy_tasks.py
from celery import shared_task
from app.services.tdx_local_service import TDXLocalService
from app.services.strategy_service import StrategyService
from app.services.backtest_service import BacktestService

@shared_task
def daily_data_update():
    """
    每日数据更新任务（对标readTDX_lday.py）
    16:00自动执行
    """
    service = TDXLocalService()
    service.update_daily_data()  # 读取通达信数据
    service.save_to_database()   # 保存到TDengine

@shared_task
def daily_stock_screening():
    """
    每日选股任务（对标xuangu.py）
    16:30自动执行
    """
    strategy_service = StrategyService()
    results = strategy_service.execute_screening(
        strategy_id="stock_screening_v1",
        mode="daily"
    )
    # 保存选股结果
    strategy_service.save_screening_results(results)

@shared_task
def generate_strategy_signals():
    """
    生成策略信号任务（对标celue_save.py）
    17:00自动执行
    """
    strategy_service = StrategyService()
    strategy_service.generate_historical_signals()

@shared_task
def run_backtest_task(strategy_id: str, config: dict):
    """
    后台回测任务（对标huice.py）
    """
    backtest_service = BacktestService()
    result = backtest_service.run_backtest(strategy_id, config)
    # 通知用户回测完成
    send_notification(result)
```

**调度配置**：
```python
# celery配置
CELERY_BEAT_SCHEDULE = {
    'daily-data-update': {
        'task': 'tasks.strategy_tasks.daily_data_update',
        'schedule': crontab(hour=16, minute=0),  # 每日16:00
    },
    'daily-stock-screening': {
        'task': 'tasks.strategy_tasks.daily_stock_screening',
        'schedule': crontab(hour=16, minute=30),  # 每日16:30
    },
    'generate-signals': {
        'task': 'tasks.strategy_tasks.generate_strategy_signals',
        'schedule': crontab(hour=17, minute=0),  # 每日17:00
    },
}
```

**优势**：
✅ 全自动化执行
✅ 无需手动干预
✅ 任务状态监控
✅ 失败自动重试

---

## 🚀 实施路线图

### 阶段1：基础整合（1-2周）⭐⭐⭐⭐⭐

**目标**：建立数据层和策略层基础框架

**任务清单**：
1. ✅ 创建`adapters/tdx_local_adapter.py`
   - 实现日线数据读取
   - 实现财务数据读取
   - 实现前复权处理

2. ✅ 扩展`strategies/`模块
   - 创建`stock_screening_strategy.py`
   - 移植原celue.py策略逻辑
   - 注册到StrategyRegistry

3. ✅ 数据库schema扩展
   - 新增`strategy_signals`表（PostgreSQL - Derived Data）
   - 新增`backtest_results`表（PostgreSQL - Derived Data）

**交付物**：
- 可通过API查询通达信本地数据
- 可执行基础选股策略
- 策略信号持久化存储

---

### 阶段2：回测引擎集成（2-3周）⭐⭐⭐⭐

**目标**：集成RQAlpha回测框架

**任务清单**：
1. ✅ 创建`services/backtest_service.py`
   - 集成RQAlpha
   - 实现回测逻辑
   - 结果解析和存储

2. ✅ 创建回测API
   - `POST /api/strategy/backtest`
   - `GET /api/backtest/result/{id}`
   - `GET /api/backtest/plot/{id}`

3. ✅ 性能指标计算
   - 收益率、夏普比率
   - 最大回撤
   - 胜率、盈亏比

**交付物**：
- 完整的回测API
- 回测结果持久化
- 性能指标报告

---

### 阶段3：可视化开发（2-3周）⭐⭐⭐⭐

**目标**：开发前端可视化组件

**任务清单**：
1. ✅ 创建K线图组件
   - `KLineWithSignals.vue`
   - 买卖点标记
   - 持仓区域可视化

2. ✅ 创建回测结果查看器
   - `BacktestViewer.vue`
   - 收益曲线图
   - 性能指标仪表盘

3. ✅ 创建策略管理界面
   - `StrategyExecutor.vue`
   - 参数配置
   - 执行控制

**交付物**：
- 完整的前端可视化界面
- 交互式图表
- 策略管理功能

---

### 阶段4：自动化和优化（1-2周）⭐⭐⭐

**目标**：实现自动化任务调度和性能优化

**任务清单**：
1. ✅ 创建定时任务
   - 每日数据更新
   - 自动选股
   - 信号生成

2. ✅ 性能优化
   - 多进程并行处理
   - 数据缓存策略
   - 查询优化

3. ✅ 监控集成
   - 任务执行监控
   - 性能指标监控
   - 异常告警

**交付物**：
- 全自动化工作流
- 性能优化报告
- 监控告警系统

---

### 阶段5：测试和文档（1周）⭐⭐⭐

**目标**：全面测试和完善文档

**任务清单**：
1. ✅ 单元测试
   - 策略逻辑测试
   - API接口测试
   - 回测准确性测试

2. ✅ 集成测试
   - 端到端流程测试
   - 性能压力测试

3. ✅ 文档编写
   - API文档
   - 用户手册
   - 开发者指南

**交付物**：
- 完整的测试覆盖
- 全面的文档
- 上线就绪

---

## 📊 架构对比总结

### 原项目架构
```
通达信本地数据
    ↓
readTDX_lday.py（手动运行）
    ↓
CSV/pickle文件
    ↓
xuangu.py（手动运行）
    ↓
celue_save.py（手动运行）
    ↓
celue汇总.csv
    ↓
huice.py（手动运行）
    ↓
rq_result.png + plot.html
```

**特点**：
- ✅ 简单直接
- ✅ 本地化处理
- ❌ 手动执行，缺少自动化
- ❌ 文件存储，不易管理
- ❌ 缺少Web界面

---

### 整合后架构
```
通达信本地数据
    ↓
TDXLocalAdapter（自动更新，16:00定时任务）
    ↓
MyStocks数据库（TDengine/PostgreSQL/MySQL）
    ↓
StockScreeningStrategy（自动执行，16:30定时任务）
    ↓
StrategySignals表（PostgreSQL - Derived Data）
    ↓
BacktestService（RQAlpha集成）
    ↓
BacktestResults表（PostgreSQL - Derived Data）
    ↓
Web前端（Vue3 + ECharts）
    ├─ K线图组件（实时交互）
    ├─ 回测结果查看器
    └─ 策略管理界面
```

**特点**：
- ✅ **全自动化**：定时任务自动执行
- ✅ **数据库存储**：统一管理，易于查询
- ✅ **Web界面**：现代化UI，实时交互
- ✅ **模块化设计**：易于扩展和维护
- ✅ **完整监控**：任务状态、性能指标
- ✅ **多用户支持**：权限管理、数据隔离

---

## 🎯 关键决策点

### 决策1：是否保留原项目脚本？

**建议**：**部分保留**

**保留**（作为独立工具）：
- `readTDX_lday.py` - 可作为手动数据导入工具
- `plot.py` - 可作为快速本地可视化工具

**废弃**（完全整合）：
- `xuangu.py` → 整合到StrategyService
- `celue_save.py` → 整合到SignalGenerator
- `huice.py` → 整合到BacktestService

---

### 决策2：RQAlpha还是自研回测引擎？

**建议**：**优先使用RQAlpha**

**理由**：
- ✅ 成熟稳定，Python生态标准
- ✅ 文档完善，社区活跃
- ✅ 功能全面（多种回测模式、风控、滑点等）
- ✅ 节省开发时间

**未来扩展**：
- 可考虑增加轻量级自研引擎（特定场景）
- 支持多引擎切换

---

### 决策3：策略信号存储在哪个数据库？

**建议**：**PostgreSQL（Derived Data）**

**理由**：
- ✅ 策略信号属于衍生数据
- ✅ 需要复杂查询和关联分析
- ✅ TimescaleDB扩展支持时序查询
- ✅ 符合5层数据分类原则

---

### 决策4：前端使用PyECharts还是ECharts？

**建议**：**ECharts（Vue集成）**

**理由**：
- ✅ 前后端分离，更灵活
- ✅ 实时交互性更好
- ✅ 与现有前端技术栈一致
- ✅ 支持动态更新和多图表联动

---

## 📝 配置文件示例

### 新增配置：tdx_local.yaml
```yaml
# 通达信本地数据配置
tdx_local:
  enabled: true
  tdx_path: "/path/to/tdx"

  # 数据更新配置
  auto_update:
    enabled: true
    schedule: "16:00"  # 每日16:00自动更新

  # 数据路径
  paths:
    vipdoc_sh: "${tdx_path}/vipdoc/sh/lday"
    vipdoc_sz: "${tdx_path}/vipdoc/sz/lday"
    finance: "${tdx_path}/T0002/hq_cache/finance"

  # 前复权配置
  qfq:
    enabled: true
    factor_source: "local"  # local / online

  # 性能优化
  performance:
    use_multiprocessing: true
    num_workers: 8
    use_pickle_cache: true
```

### 新增配置：strategy.yaml
```yaml
# 策略配置
strategies:
  stock_screening_v1:
    enabled: true
    name: "多因子选股策略"
    category: "trend_following"

    # 执行配置
    execution:
      auto_run: true
      schedule: "16:30"  # 每日16:30自动执行
      mode: "daily"  # daily / intraday

    # 筛选条件
    filters:
      exclude_st: true
      exclude_kcb: true  # 科创板
      exclude_industries: ["银行", "保险"]
      min_price: 9.0
      min_market_cap: 1000000000  # 10亿

    # 策略参数
    parameters:
      ma_period: 5
      rsi_period: 14
      volume_threshold: 30000000

  # 可以定义更多策略
  stock_screening_v2:
    enabled: false
    # ...
```

### 新增配置：backtest.yaml
```yaml
# 回测配置
backtest:
  engine: "rqalpha"  # rqalpha / backtrader / custom

  # RQAlpha配置
  rqalpha:
    data_bundle_path: "/data/rqalpha/bundle"
    frequency: "1d"  # 1d / 1m
    matching_type: "current_bar"  # current_bar / next_bar
    benchmark: "000300.XSHG"  # 沪深300

  # 默认回测参数
  defaults:
    initial_capital: 1000000  # 初始资金100万
    commission_rate: 0.0003  # 佣金万3
    slippage: 0.0  # 滑点

  # 结果存储
  results:
    save_plot: true
    plot_format: "png"
    save_trades: true
    save_daily_positions: true
```

---

## 🔧 技术栈对比

| 组件 | 原项目 | MyStocks现有 | 整合后 |
|------|--------|--------------|--------|
| **数据源** | 通达信本地文件 | Akshare/Tushare/TDX在线 | 通达信本地+在线数据源 |
| **数据存储** | CSV/pickle文件 | TDengine/PostgreSQL/MySQL | 统一数据库存储 |
| **策略框架** | 硬编码celue.py | StrategyBase基类 | 注册式策略系统 |
| **回测引擎** | RQAlpha | 无 | RQAlpha集成 |
| **技术指标** | talib | 161个TA-Lib指标 | 复用现有指标 |
| **可视化** | PyECharts静态HTML | ECharts（前端） | Vue3+ECharts交互式 |
| **任务调度** | 手动运行脚本 | Celery后台任务 | 全自动定时任务 |
| **API接口** | 无 | FastAPI RESTful | 完整策略/回测API |
| **前端界面** | 无 | Vue3 | 策略管理+可视化界面 |
| **监控** | 无 | 完整监控体系 | 策略执行监控 |

---

## ⚠️ 风险和注意事项

### 1. 数据一致性风险
**问题**：通达信本地数据与在线数据源可能存在差异

**解决方案**：
- 实施数据质量检查（DataQualityMonitor）
- 提供数据源切换功能
- 记录数据来源标识

---

### 2. 回测准确性风险
**问题**：回测结果可能与实盘存在偏差

**解决方案**：
- 设置合理的滑点和手续费
- 考虑停牌、涨跌停限制
- 提供实盘对比功能

---

### 3. 性能风险
**问题**：大规模选股和回测可能耗时较长

**解决方案**：
- 多进程并行处理
- 数据预加载和缓存
- 异步任务执行
- 进度监控和中断机制

---

### 4. 依赖风险
**问题**：RQAlpha等第三方库可能存在版本兼容问题

**解决方案**：
- 锁定依赖版本
- 定期更新和测试
- 提供降级方案

---

## 📚 参考资源

### 原项目相关
- 通达信数据格式文档
- RQAlpha官方文档: https://github.com/ricequant/rqalpha
- PyECharts文档: https://pyecharts.org/

### MyStocks相关
- FastAPI文档: https://fastapi.tiangolo.com/
- Vue3文档: https://vuejs.org/
- ECharts文档: https://echarts.apache.org/
- Celery文档: https://docs.celeryq.dev/

### 量化相关
- TA-Lib指标库: https://mrjbq7.github.io/ta-lib/
- Pandas文档: https://pandas.pydata.org/
- NumPy文档: https://numpy.org/

---

## ✅ 总结

本整合方案将原项目的**数据抓取、策略执行、回测分析、可视化**四大核心功能，**无缝整合**到MyStocks现有架构中，实现：

1. **数据层整合** - 通过TDXLocalAdapter统一数据源
2. **策略层重构** - 模块化策略系统，复用StrategyBase
3. **回测引擎集成** - RQAlpha框架集成
4. **可视化现代化** - Vue3+ECharts交互式界面
5. **自动化增强** - Celery定时任务全自动执行
6. **数据库存储** - 符合5层数据分类原则

**核心优势**：
- ✅ 保留原项目优点（本地化、RQAlpha、技术指标）
- ✅ 提升用户体验（Web界面、自动化、实时交互）
- ✅ 符合现代架构（前后端分离、微服务、监控）
- ✅ 易于扩展维护（模块化、注册式、配置驱动）

**建议实施顺序**：
1. **阶段1**（基础整合）→ 2-3周
2. **阶段2**（回测引擎）→ 2-3周
3. **阶段3**（可视化）→ 2-3周
4. **阶段4**（自动化）→ 1-2周
5. **阶段5**（测试文档）→ 1周

**总时间预估**：8-12周（2-3个月）

---

**文档生成时间**：2025-10-18
**文档版本**：v1.0
**下一步行动**：使用SpecKit工具生成详细实施计划
