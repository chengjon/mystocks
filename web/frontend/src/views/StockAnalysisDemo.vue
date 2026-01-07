<template>
  <div class="stock-analysis-demo">

    <PageHeader
      title="STOCK ANALYSIS DEMO"
      subtitle="A-SHARE STOCK SCREENING | BACKTESTING | TECHNICAL ANALYSIS"
    />

    <div class="function-nav">
      <el-button
        v-for="tab in tabs"
        :key="tab.key"
        :type="activeTab === tab.key ? 'primary' : 'default'"
        @click="activeTab = tab.key"
      >
        {{ tab.icon }} {{ tab.label }}
      </el-button>
    </div>

    <el-card v-show="activeTab === 'overview'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>PROJECT OVERVIEW</span>
          <el-tag type="success">MIGRATED</el-tag>
        </div>
      </template>

      <div class="content-section">
        <h3>INTRODUCTION</h3>
        <p>Stock-Analysis is a Chinese A-share stock screening and backtesting system based on Tongdaxin data. It leverages Tongdaxin's powerful local data advantages combined with Python flexibility to provide efficient stock screening strategies and complete backtesting framework.</p>

        <h3 style="margin-top: 30px;">CORE FEATURES</h3>
        <div class="features-grid">
          <el-card :hoverable="true">
            <h4>TONGDAXIN DATA PARSING</h4>
            <ul>
              <li>Parse Tongdaxin .day/.lc1/.lc5 binary files</li>
              <li>Support daily, minute, 5-minute data</li>
              <li>Auto-identify stock codes and markets</li>
              <li>Efficient data caching mechanism</li>
              <li>Historical and real-time data support</li>
            </ul>
          </el-card>

          <el-card :hoverable="true">
            <h4>STOCK SCREENING STRATEGIES</h4>
            <ul>
              <li>Technical Indicator Screening (MA, MACD, RSI, KDJ)</li>
              <li>Pattern Recognition (Breakthrough, Golden Cross, Bottom)</li>
              <li>Volume-Price Analysis (Volume, Volume Ratio)</li>
              <li>Fundamental Screening (PE, PB, Net Profit)</li>
              <li>Custom Combined Conditions</li>
            </ul>
          </el-card>

          <el-card :hoverable="true">
            <h4>BACKTESTING</h4>
            <ul>
              <li>Integrated rqalpha backtesting engine</li>
              <li>Multi-strategy parallel backtesting</li>
              <li>Complete trading records and analysis</li>
              <li>Capital curve and drawdown analysis</li>
              <li>Sharpe ratio and performance metrics</li>
            </ul>
          </el-card>

          <el-card :hoverable="true">
            <h4>REAL-TIME & AFTER-HOURS</h4>
            <ul>
              <li>Intraday real-time data updates</li>
              <li>After-hours automatic screening</li>
              <li>Email/WeChat notification push</li>
              <li>Custom screening time</li>
              <li>Historical screening results save</li>
            </ul>
          </el-card>
        </div>

        <h3 style="margin-top: 30px;">TECHNICAL ARCHITECTURE</h3>
        <el-descriptions :column="2" border style="margin-top: 15px;" class="descriptions">
          <el-descriptions-item label="DATA SOURCE">Tongdaxin Local Data (.day/.lc1/.lc5)</el-descriptions-item>
          <el-descriptions-item label="DATA PARSING">struct Binary Parsing</el-descriptions-item>
          <el-descriptions-item label="STRATEGY LANGUAGE">Python 3.x</el-descriptions-item>
          <el-descriptions-item label="BACKTEST ENGINE">rqalpha</el-descriptions-item>
          <el-descriptions-item label="TECHNICAL INDICATORS">TA-Lib</el-descriptions-item>
          <el-descriptions-item label="DATA STORAGE">SQLite / PostgreSQL</el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 30px;">REPOSITORY</h3>
        <p>This project is a functional demonstration. The complete source code is available in the <code>stock-analysis/</code> directory.</p>

        <el-alert
          type="success"
          style="margin-top: 20px;"
          :closable="false"
        >
          <template #title>
            <div style="font-weight: bold;">💡 项目优势</div>
          </template>
          <ul style="margin-top: 10px;">
            <li><strong>数据本地化</strong>: 使用通达信本地数据,无需网络,速度快</li>
            <li><strong>数据全面性</strong>: 覆盖所有 A 股历史数据,包括分钟级</li>
            <li><strong>策略灵活性</strong>: 支持复杂的自定义筛选条件</li>
            <li><strong>回测可靠性</strong>: 基于真实历史数据,避免未来函数</li>
            <li><strong>实时性</strong>: 支持盘中实时监控和筛选</li>
          </ul>
        </el-alert>
      </div>
    </el-card>

    <!-- 2. 数据解析 -->
    <el-card v-show="activeTab === 'data'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>📂 通达信数据解析</span>
          <el-tag type="success">已集成</el-tag>
        </div>
      </template>

      <div class="content-section">
        <h3>📁 通达信数据文件格式</h3>
        <p>通达信将股票数据存储为二进制文件,不同周期对应不同的文件扩展名:</p>

        <el-table :data="fileFormatData" stripe style="margin-top: 15px;">
          <el-table-column prop="type" label="数据类型" width="120" />
          <el-table-column prop="extension" label="文件扩展名" width="120" />
          <el-table-column prop="recordSize" label="记录大小" width="120" />
          <el-table-column prop="description" label="说明" />
        </el-table>

        <h3 style="margin-top: 30px;">🔢 日线数据结构 (.day 文件)</h3>
        <p>每条日K线记录占用 32 字节,结构如下:</p>

        <el-table :data="dayStructureData" stripe style="margin-top: 15px;">
          <el-table-column prop="offset" label="偏移量" width="100" />
          <el-table-column prop="size" label="字节数" width="100" />
          <el-table-column prop="type" label="数据类型" width="120" />
          <el-table-column prop="field" label="字段名" width="120" />
          <el-table-column prop="description" label="说明" />
        </el-table>

        <h3 style="margin-top: 30px;">💻 数据解析代码示例</h3>
        <el-tabs type="border-card" style="margin-top: 20px;">
          <el-tab-pane label="日线数据解析" name="daily">
            <textarea readonly class="code-block" v-text="dayParserCode"></textarea>
          </el-tab-pane>

          <el-tab-pane label="分钟线数据解析" name="minute">
            <textarea readonly class="code-block">

import struct
import pandas as pd
from datetime import datetime, timedelta

def parse_tdx_minute_file(file_path):
    """
    解析通达信分钟线数据文件 (.lc1)

    Returns:
        pd.DataFrame: 包含 OHLCV 数据的 DataFrame
    """
    data = []

    with open(file_path, 'rb') as f:
        while True:
            record = f.read(32)
            if len(record) != 32:
                break

            fields = struct.unpack('<HHIIIIfII', record)

            date = fields[0]  # 天数(从1900/1/1开始)
            minute = fields[1]  # 分钟(0-1439)
            open_price = fields[2] &#47; 100.0
            high_price = fields[3] &#47; 100.0
            low_price = fields[4] &#47; 100.0
            close_price = fields[5] / 100.0
            amount = fields[6]
            volume = fields[7]

            # 计算实际日期时间
            base_date = datetime(1900, 1, 1)
            actual_date = base_date + timedelta(days=date)
            hour = minute // 60
            min = minute % 60
            dt = actual_date.replace(hour=hour, minute=min)

            data.append({
                'datetime': dt,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume,
                'amount': amount
            })

    df = pd.DataFrame(data)
    df.set_index('datetime', inplace=True)
    return df</textarea>
          </el-tab-pane>

          <el-tab-pane label="批量读取" name="batch">
            <textarea readonly class="code-block">

import os
from pathlib import Path

def load_all_stocks_data(tdx_path, market='sh'):
    """
    批量加载指定市场的所有股票数据

    Args:
        tdx_path: 通达信数据目录
        market: 市场代码 ('sh' 或 'sz')

    Returns:
        dict: {股票代码: DataFrame}
    """
    data_dir = Path(tdx_path) / 'vipdoc' / market / 'lday'
    stocks_data = {}

    for file_path in data_dir.glob(f'{market}*.day'):
        # 提取股票代码
        code = file_path.stem[2:]  # 去掉 'sh' 或 'sz' 前缀

        try:
            df = parse_tdx_day_file(str(file_path))
            stocks_data[code] = df
            print(f"已加载 {market}{code}: {len(df)} 条记录")
        except Exception as e:
            print(f"加载 {file_path} 失败: {e}")

    return stocks_data

# 使用示例
tdx_path = 'D:/tdx'
sh_stocks = load_all_stocks_data(tdx_path, 'sh')
sz_stocks = load_all_stocks_data(tdx_path, 'sz')

print(f"上海市场: {len(sh_stocks)} 只股票")
print(f"深圳市场: {len(sz_stocks)} 只股票")</textarea>
          </el-tab-pane>
        </el-tabs>

        <el-alert
          type="warning"
          title="⚠️ 注意事项"
          :closable="false"
          style="margin-top: 20px;"
        >
          <ul style="margin-top: 10px;">
            <li><strong>数据路径</strong>: 需要正确配置通达信数据目录路径</li>
            <li><strong>文件编码</strong>: 通达信数据为小端序 (little-endian)</li>
            <li><strong>价格处理</strong>: 价格数据需要除以 100 转换为实际价格</li>
            <li><strong>日期格式</strong>: 日期存储为整数,需要转换为 datetime 对象</li>
            <li><strong>数据完整性</strong>: 检查文件大小是否为 32 的整数倍</li>
          </ul>
        </el-alert>
      </div>
    </el-card>

    <!-- 3. 筛选策略 -->
    <el-card v-show="activeTab === 'strategy'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>🔍 股票筛选策略</span>
          <el-tag type="warning">文档</el-tag>
        </div>
      </template>

      <div class="content-section">
        <h3>📊 常用筛选策略</h3>
        <p>以下是一些经典的股票筛选策略示例:</p>

        <el-collapse accordion style="margin-top: 20px;">
          <el-collapse-item title="1️⃣ 均线多头排列" name="1">
            <div class="strategy-content">
              <h4>策略说明</h4>
              <p>寻找 MA5 > MA10 > MA20 > MA60 的股票,表示短期、中期、长期趋势向上</p>

              <h4 style="margin-top: 15px;">代码实现</h4>
              <textarea readonly class="code-block">
import talib as ta

def filter_ma_bullish(df):
    """均线多头排列筛选"""
    # 计算均线
    df['ma5'] = ta.SMA(df['close'], 5)
    df['ma10'] = ta.SMA(df['close'], 10)
    df['ma20'] = ta.SMA(df['close'], 20)
    df['ma60'] = ta.SMA(df['close'], 60)

    # 筛选条件
    condition = (
        (df['ma5'] > df['ma10']) &
        (df['ma10'] > df['ma20']) &
        (df['ma20'] > df['ma60'])
    )

    return df[condition]</textarea>
            </div>
          </el-collapse-item>

          <el-collapse-item title="2️⃣ MACD 金叉" name="2">
            <div class="strategy-content">
              <h4>策略说明</h4>
              <p>MACD 快线上穿慢线,且 MACD 柱状图由负转正,通常是买入信号</p>

              <h4 style="margin-top: 15px;">代码实现</h4>
              <textarea readonly class="code-block">
def filter_macd_golden_cross(df):
    """MACD 金叉筛选"""
    # 计算 MACD
    macd, signal, hist = ta.MACD(df['close'],
                                   fastperiod=12,
                                   slowperiod=26,
                                   signalperiod=9)

    df['macd'] = macd
    df['signal'] = signal
    df['hist'] = hist

    # 筛选条件: 今日金叉 且 昨日死叉
    condition = (
        (df['macd'] > df['signal']) &  # 今日快线在上
        (df['macd'].shift(1) <= df['signal'].shift(1)) &  # 昨日快线在下
        (df['hist'] > 0)  # 柱状图为正
    )

    return df[condition]</textarea>
            </div>
          </el-collapse-item>

          <el-collapse-item title="3️⃣ 放量突破" name="3">
            <div class="strategy-content">
              <h4>策略说明</h4>
              <p>价格突破前期高点,同时成交量放大,表示有资金介入</p>

              <h4 style="margin-top: 15px;">代码实现</h4>
              <textarea readonly class="code-block">
def filter_breakout_with_volume(df, lookback=20, vol_ratio=1.5):
    """放量突破筛选"""
    # 计算N日最高价
    df['high_n'] = df['high'].rolling(lookback).max().shift(1)

    # 计算N日平均成交量
    df['vol_ma'] = df['volume'].rolling(lookback).mean()

    # 筛选条件
    condition = (
        (df['close'] > df['high_n']) &  # 突破前期高点
        (df['volume'] > df['vol_ma'] * vol_ratio)  # 成交量放大
    )

    return df[condition]</textarea>
            </div>
          </el-collapse-item>

          <el-collapse-item title="4️⃣ RSI 超卖反弹" name="4">
            <div class="strategy-content">
              <h4>策略说明</h4>
              <p>RSI 指标从超卖区域回升,可能是反弹信号</p>

              <h4 style="margin-top: 15px;">代码实现</h4>
              <textarea readonly class="code-block">
def filter_rsi_oversold(df, period=14, oversold=30):
    """RSI 超卖反弹筛选"""
    # 计算 RSI
    df['rsi'] = ta.RSI(df['close'], timeperiod=period)

    # 筛选条件: 昨日超卖,今日回升
    condition = (
        (df['rsi'].shift(1) < oversold) &  # 昨日超卖
        (df['rsi'] > oversold) &  # 今日脱离超卖
        (df['rsi'] > df['rsi'].shift(1))  # RSI 上升
    )

    return df[condition]</textarea>
            </div>
          </el-collapse-item>

          <el-collapse-item title="5️⃣ 底部放量" name="5">
            <div class="strategy-content">
              <h4>策略说明</h4>
              <p>股价处于低位,成交量突然放大,可能是主力建仓信号</p>

              <h4 style="margin-top: 15px;">代码实现</h4>
              <textarea readonly class="code-block">
def filter_bottom_volume(df, lookback=60):
    """底部放量筛选"""
    # 计算60日最低价和当前价格相对位置
    df['low_60'] = df['low'].rolling(lookback).min()
    df['price_position'] = (df['close'] - df['low_60']) / (df['high'].rolling(lookback).max() - df['low_60'])

    # 计算成交量比率
    df['vol_ma5'] = df['volume'].rolling(5).mean()
    df['vol_ma20'] = df['volume'].rolling(20).mean()
    df['vol_ratio'] = df['vol_ma5'] / df['vol_ma20']

    # 筛选条件
    condition = (
        (df['price_position'] < 0.3) &  # 价格在底部30%区域
        (df['vol_ratio'] > 1.5)  # 5日均量 > 20日均量的1.5倍
    )

    return df[condition]</textarea>
            </div>
          </el-collapse-item>
        </el-collapse>

        <h3 style="margin-top: 30px;">🎯 组合筛选示例</h3>
        <textarea readonly class="code-block">
def comprehensive_filter(stock_code):
    """
    综合筛选策略:
    1. 均线多头排列
    2. MACD 金叉
    3. RSI 不超买 (< 70)
    4. 成交量放大
    """
    df = load_stock_data(stock_code)

    # 计算所有指标
    df['ma5'] = ta.SMA(df['close'], 5)
    df['ma10'] = ta.SMA(df['close'], 10)
    df['ma20'] = ta.SMA(df['close'], 20)

    macd, signal, _ = ta.MACD(df['close'])
    df['macd'] = macd
    df['signal'] = signal

    df['rsi'] = ta.RSI(df['close'], 14)
    df['vol_ma'] = df['volume'].rolling(20).mean()

    # 组合筛选条件
    condition = (
        (df['ma5'] > df['ma10']) &
        (df['ma10'] > df['ma20']) &
        (df['macd'] > df['signal']) &
        (df['rsi'] < 70) &
        (df['volume'] > df['vol_ma'] * 1.2)
    )

    # 获取最新一天的筛选结果
    latest = df[condition].iloc[-1] if condition.any() else None

    return latest

# 批量筛选
results = []
for code in all_stock_codes:
    result = comprehensive_filter(code)
    if result is not None:
        results.append({
            'code': code,
            'close': result['close'],
            'rsi': result['rsi'],
            'volume_ratio': result['volume'] / result['vol_ma']
        })

# 输出结果
print(f"共筛选出 {len(results)} 只股票")
for r in results[:10]:  # 显示前10只
    print(f"{r['code']}: 收盘价={r['close']:.2f}, RSI={r['rsi']:.2f}")</textarea>
      </div>
    </el-card>

    <!-- 4. 回测系统 -->
    <el-card v-show="activeTab === 'backtest'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>📈 回测系统</span>
          <el-tag type="warning">文档</el-tag>
        </div>
      </template>

      <div class="content-section">
        <h3>🔧 回测框架: RQAlpha</h3>
        <p>Stock-Analysis 集成了 RQAlpha 回测框架,提供专业的策略回测能力:</p>

        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="12">
            <el-card shadow="hover">
              <h4>✨ RQAlpha 特性</h4>
              <ul>
                <li>事件驱动回测引擎</li>
                <li>支持多种订单类型</li>
                <li>完整的交易成本模拟</li>
                <li>丰富的性能指标分析</li>
                <li>可视化回测报告</li>
              </ul>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover">
              <h4>📊 支持的策略类型</h4>
              <ul>
                <li>日频策略</li>
                <li>分钟频策略</li>
                <li>事件驱动策略</li>
                <li>多品种策略</li>
                <li>期货/期权策略</li>
              </ul>
            </el-card>
          </el-col>
        </el-row>

        <h3 style="margin-top: 30px;">💻 回测代码示例</h3>
        <el-tabs type="border-card" style="margin-top: 20px;">
          <el-tab-pane label="简单策略" name="simple">
            <textarea readonly class="code-block">
from rqalpha.api import *

def init(context):
    """策略初始化"""
    context.stock = "000001.XSHE"
    context.ma_short = 5
    context.ma_long = 20

def before_trading(context):
    """盘前处理"""
    pass

def handle_bar(context, bar_dict):
    """每个bar的处理逻辑"""
    # 获取历史数据
    prices = history_bars(context.stock, context.ma_long + 1, '1d', 'close')

    # 计算均线
    ma_short = prices[-context.ma_short:].mean()
    ma_long = prices[-context.ma_long:].mean()

    # 当前持仓
    position = context.portfolio.positions[context.stock]

    # 交易逻辑
    if ma_short > ma_long and position.quantity == 0:
        # 金叉买入
        order_target_percent(context.stock, 0.95)
        logger.info(f"买入信号: MA{context.ma_short} > MA{context.ma_long}")
    elif ma_short < ma_long and position.quantity > 0:
        # 死叉卖出
        order_target_percent(context.stock, 0)
        logger.info(f"卖出信号: MA{context.ma_short} < MA{context.ma_long}")</textarea>
          </el-tab-pane>

          <el-tab-pane label="多股票策略" name="multi">
            <textarea readonly class="code-block">
from rqalpha.api import *

def init(context):
    """初始化股票池"""
    context.stocks = [
        "000001.XSHE",  # 平安银行
        "600000.XSHG",  # 浦发银行
        "600036.XSHG",  # 招商银行
        "601398.XSHG"   # 工商银行
    ]
    context.holding_days = {}

def handle_bar(context, bar_dict):
    """多股票轮动策略"""
    # 计算每只股票的动量
    momentums = {}
    for stock in context.stocks:
        try:
            prices = history_bars(stock, 20, '1d', 'close')
            momentum = (prices[-1] - prices[0]) / prices[0]
            momentums[stock] = momentum
        except:
            continue

    # 按动量排序
    sorted_stocks = sorted(momentums.items(), key=lambda x: x[1], reverse=True)

    # 持有前2名
    target_stocks = [s[0] for s in sorted_stocks[:2]]

    # 调仓
    current_positions = list(context.portfolio.positions.keys())

    # 卖出不在目标池的股票
    for stock in current_positions:
        if stock not in target_stocks:
            order_target_percent(stock, 0)
            logger.info(f"卖出 {stock}")

    # 买入目标股票
    target_weight = 0.45  # 每只股票45%仓位
    for stock in target_stocks:
        order_target_percent(stock, target_weight)
        logger.info(f"买入 {stock}, 目标仓位 {target_weight*100}%")</textarea>
          </el-tab-pane>

          <el-tab-pane label="运行回测" name="run">
            <textarea readonly class="code-block">
# 运行回测的命令
rqalpha run \
    -f strategy.py \
    -s 2020-01-01 \
    -e 2021-12-31 \
    --stock-starting-cash 100000 \
    --frequency 1d \
    --benchmark 000300.XSHG \
    --output-file results.pkl \
    --plot

# 或者使用 Python API
from rqalpha import run

config = {
    "base": {
        "start_date": "2020-01-01",
        "end_date": "2021-12-31",
        "frequency": "1d",
        "accounts": {
            "stock": 100000
        }
    },
    "mod": {
        "sys_analyser": {
            "enabled": True,
            "plot": True,
            "output_file": "results.pkl"
        }
    }
}

result = run(config=config, strategy_file="strategy.py")
print(f"总收益率: {result['summary']['total_returns']:.2%}")
print(f"夏普比率: {result['summary']['sharpe']:.2f}")
print(f"最大回撤: {result['summary']['max_drawdown']:.2%}")</textarea>
          </el-tab-pane>
        </el-tabs>

        <h3 style="margin-top: 30px;">📊 回测结果指标</h3>
        <el-table :data="backtestMetrics" stripe style="margin-top: 15px;">
          <el-table-column prop="metric" label="指标" width="200" />
          <el-table-column prop="description" label="说明" />
        </el-table>
      </div>
    </el-card>

    <!-- 5. 实时监控 -->
    <el-card v-show="activeTab === 'realtime'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>⏰ 实时监控</span>
          <el-tag type="info">计划集成</el-tag>
        </div>
      </template>

      <div class="content-section">
        <h3>📡 实时数据更新</h3>
        <p>Stock-Analysis 支持盘中实时数据监控和筛选:</p>

        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="12">
            <el-card shadow="hover">
              <h4>🔄 实时更新机制</h4>
              <ul>
                <li>定时读取通达信实时数据</li>
                <li>支持分钟级数据更新</li>
                <li>自动检测新增数据</li>
                <li>增量式数据处理</li>
                <li>低延迟数据推送</li>
              </ul>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover">
              <h4>📢 通知推送</h4>
              <ul>
                <li>邮件通知</li>
                <li>微信通知 (Server酱)</li>
                <li>钉钉通知</li>
                <li>自定义 Webhook</li>
                <li>本地弹窗提醒</li>
              </ul>
            </el-card>
          </el-col>
        </el-row>

        <h3 style="margin-top: 30px;">💻 实时监控代码</h3>
        <textarea readonly class="code-block">
import time
import schedule
from datetime import datetime

def realtime_monitor():
    """实时监控主函数"""
    print(f"{datetime.now()} - 开始筛选...")

    # 加载所有股票数据
    all_stocks = load_all_stocks()

    # 执行筛选
    matched_stocks = []
    for code, df in all_stocks.items():
        if check_strategy(df):
            matched_stocks.append(code)

    if matched_stocks:
        print(f"发现 {len(matched_stocks)} 只股票符合条件:")
        for code in matched_stocks:
            print(f"  {code}")

        # 发送通知
        send_notification(matched_stocks)

def check_strategy(df):
    """检查策略条件"""
    latest = df.iloc[-1]

    # 示例: MACD金叉 + RSI不超买
    condition = (
        latest['macd'] > latest['signal'] and
        latest['macd_prev'] <= latest['signal_prev'] and
        latest['rsi'] < 70
    )

    return condition

def send_notification(stocks):
    """发送通知"""
    message = f"发现{len(stocks)}只股票符合条件:\n"
    message += "\n".join(stocks)

    # 发送邮件
    send_email("股票筛选提醒", message)

    # 发送微信 (Server酱)
    send_wechat(message)

# 设置定时任务
schedule.every(5).minutes.do(realtime_monitor)  # 每5分钟执行一次

# 只在交易时间运行
def run_scheduler():
    while True:
        now = datetime.now()
        # 交易日的 9:30-11:30 和 13:00-15:00
        if now.weekday() < 5:  # 周一到周五
            if (9 <= now.hour < 12) or (13 <= now.hour < 15):
                schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    print("开始实时监控...")
    run_scheduler()</textarea>

        <h3 style="margin-top: 30px;">📅 盘后自动筛选</h3>
        <textarea readonly class="code-block">
def after_market_screen():
    """盘后自动筛选"""
    print(f"{datetime.now()} - 开始盘后筛选...")

    # 更新所有股票数据
    update_all_stocks()

    # 执行多个策略筛选
    strategies = {
        '均线多头': filter_ma_bullish,
        'MACD金叉': filter_macd_golden_cross,
        '放量突破': filter_breakout_with_volume,
        'RSI超卖': filter_rsi_oversold
    }

    report = []
    for name, strategy in strategies.items():
        matched = []
        for code in all_stock_codes:
            df = load_stock_data(code)
            if strategy(df):
                matched.append(code)

        report.append({
            'strategy': name,
            'count': len(matched),
            'stocks': matched[:10]  # 只保留前10只
        })

    # 生成HTML报告
    generate_html_report(report)

    # 发送邮件
    send_email_report(report)

# 每个交易日下午3点15分执行
schedule.every().day.at("15:15").do(after_market_screen)</textarea>
      </div>
    </el-card>

    <!-- 6. 集成状态 -->
    <el-card v-show="activeTab === 'status'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>✅ 集成状态</span>
        </div>
      </template>

      <div class="content-section">
        <h3>📦 已集成功能</h3>
        <el-descriptions :column="1" border style="margin-top: 15px;">
          <el-descriptions-item label="通达信数据解析">
            <el-tag type="success">✅ 已集成到 tdx_parser_service</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="技术指标计算">
            <el-tag type="success">✅ 已集成到 feature_engineering</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="筛选策略文档">
            <el-tag type="success">✅ 已整理</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="回测框架">
            <el-tag type="info">⏳ 待集成</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="实时监控">
            <el-tag type="info">⏳ 计划中</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Web UI">
            <el-tag type="info">⏳ 计划中</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 30px;">🎯 后续集成计划</h3>
        <el-timeline style="margin-top: 20px;">
          <el-timeline-item timestamp="Phase 1" placement="top">
            <el-card>
              <h4>策略库管理</h4>
              <p>在 Web 界面中管理和执行各种筛选策略</p>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="Phase 2" placement="top">
            <el-card>
              <h4>回测系统集成</h4>
              <p>集成 RQAlpha 回测引擎,在线运行回测</p>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="Phase 3" placement="top">
            <el-card>
              <h4>实时监控</h4>
              <p>实现盘中实时监控和推送通知功能</p>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="Phase 4" placement="top">
            <el-card>
              <h4>策略优化</h4>
              <p>支持策略参数优化和性能对比分析</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>

        <el-alert
          type="info"
          title="💡 数据源说明"
          :closable="false"
          style="margin-top: 20px;"
        >
          <p style="margin-top: 10px;">Stock-Analysis 使用通达信本地数据,优势在于:</p>
          <ul style="margin-top: 10px;">
            <li>数据完整: 覆盖所有A股从上市到最新的历史数据</li>
            <li>访问快速: 本地文件读取,无需网络请求</li>
            <li>数据可靠: 通达信是专业的行情软件,数据质量有保障</li>
            <li>成本低廉: 无需购买数据接口,免费使用</li>
          </ul>
          <p style="margin-top: 10px;">需要配置通达信数据目录路径,通常为: <code>D:/tdx/vipdoc</code></p>
        </el-alert>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { PageHeader } from '@/components/shared'

interface TabItem {
  key: string
  label: string
  icon: string
}

interface FileFormatItem {
  type: string
  extension: string
  recordSize: string
  description: string
}

interface DayStructureItem {
  offset: string
  size: string
  type: string
  field: string
  description: string
}

interface BacktestMetricItem {
  metric: string
  description: string
}

const activeTab = ref<string>('overview')

const tabs: TabItem[] = [
  { key: 'overview', label: '项目概览', icon: '📋' },
  { key: 'data', label: '数据解析', icon: '📂' },
  { key: 'strategy', label: '筛选策略', icon: '🔍' },
  { key: 'backtest', label: '回测系统', icon: '📈' },
  { key: 'realtime', label: '实时监控', icon: '⏰' },
  { key: 'status', label: '集成状态', icon: '✅' }
]

// Code examples as string constants to avoid Vue template parsing issues
const dayParserCode = `import struct
import pandas as pd
from datetime import datetime

def parse_tdx_day_file(file_path):
    """
    解析通达信日线数据文件 (.day)

    Returns:
        pd.DataFrame: 包含 OHLCV 据的 DataFrame
    """
    data = []

    with open(file_path, 'rb') as f:
        while True:
            # 读取32字节
            record = f.read(32)
            if len(record) != 32:
                break

            # 解析数据 (小端序)
            fields = struct.unpack('<IIIIIfII', record)

            date = fields[0]  # YYYYMMDD 格式
            open_price = fields[1] / 100.0
            high_price = fields[2] / 100.0
            low_price = fields[3] / 100.0
            close_price = fields[4] / 100.0
            amount = fields[5]  # 成交额
            volume = fields[6]  # 成交量

            # 转换日期格式
            date_str = str(date)
            date_obj = datetime.strptime(date_str, '%Y%m%d')

            data.append({
                'date': date_obj,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume,
                'amount': amount
            })

    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    return df

# 使用示例
df = parse_tdx_day_file('D:/tdx/vipdoc/sh/lday/sh600000.day')
print(df.head())
print(f"总共 {len(df)} 条记录")`

const fileFormatData: FileFormatItem[] = [
  { type: '日线', extension: '.day', recordSize: '32字节', description: '每条记录包含日期、OHLC、成交量和成交额' },
  { type: '分钟线', extension: '.lc1', recordSize: '32字节', description: '1分钟K线数据' },
  { type: '5分钟线', extension: '.lc5', recordSize: '32字节', description: '5分钟K线数据' },
  { type: '财务数据', extension: '.gbbq', recordSize: '变长', description: '股本变迁、除权除息数据' }
]

const dayStructureData: DayStructureItem[] = [
  { offset: '0-3', size: '4', type: 'uint32', field: 'date', description: '日期 (YYYYMMDD 格式)' },
  { offset: '4-7', size: '4', type: 'uint32', field: 'open', description: '开盘价 (需除以100)' },
  { offset: '8-11', size: '4', type: 'uint32', field: 'high', description: '最高价 (需除以100)' },
  { offset: '12-15', size: '4', type: 'uint32', field: 'low', description: '最低价 (需除以100)' },
  { offset: '16-19', size: '4', type: 'uint32', field: 'close', description: '收盘价 (需除以100)' },
  { offset: '20-23', size: '4', type: 'float', field: 'amount', description: '成交额 (元)' },
  { offset: '24-27', size: '4', type: 'uint32', field: 'volume', description: '成交量 (手)' },
  { offset: '28-31', size: '4', type: 'uint32', field: 'reserved', description: '保留字段' }
]

const backtestMetrics: BacktestMetricItem[] = [
  { metric: 'Total Returns', description: '总收益率' },
  { metric: 'Annual Returns', description: '年化收益率' },
  { metric: 'Max Drawdown', description: '最大回撤' },
  { metric: 'Sharpe Ratio', description: '夏普比率 (风险调整后收益)' },
  { metric: 'Sortino Ratio', description: '索提诺比率 (下行风险调整后收益)' },
  { metric: 'Win Rate', description: '胜率 (盈利交易占比)' },
  { metric: 'Profit Factor', description: '盈亏比 (总盈利/总亏损)' },
  { metric: 'Total Trades', description: '总交易次数' },
  { metric: 'Average Holding Days', description: '平均持仓天数' }
]
</script>

<style scoped>

.stock-analysis-demo {
  padding: var(--spacing-6);
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  position: relative;
  background: var(--bg-primary);
}

.background-pattern {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.04;
  background-image:
    repeating-linear-gradient(
      45deg,
      var(--accent-gold) 0px,
      var(--accent-gold) 1px,
      transparent 1px,
      transparent 10px
    ),
    repeating-linear-gradient(
      -45deg,
      var(--accent-gold) 0px,
      var(--accent-gold) 1px,
      transparent 1px,
      transparent 10px
    );
}

.page-header {
  text-align: center;
  margin-bottom: var(--spacing-8);
  position: relative;
  z-index: 1;

  .page-title {
    font-family: var(--font-display);
    font-size: var(--font-size-h2);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-widest);
    color: var(--accent-gold);
    margin: 0 0 var(--spacing-2) 0;
  }

  .page-subtitle {
    font-family: var(--font-body);
    font-size: var(--font-size-small);
    color: var(--fg-muted);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    margin: 0;
  }
}

.demo-grid {
  display: flex;
  gap: var(--spacing-3);
  margin-bottom: var(--spacing-6);
  flex-wrap: wrap;
  position: relative;
  z-index: 1;
}

.demo-card {
  margin-bottom: var(--spacing-6);
  position: relative;
  z-index: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-family: var(--font-display);
  font-size: var(--font-size-h4);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  color: var(--accent-gold);
}

.content-section {
  padding: var(--spacing-4) 0;
  line-height: 1.8;
}

.content-section h3 {
  font-family: var(--font-display);
  font-size: var(--font-size-h4);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  color: var(--accent-gold);
  margin-bottom: var(--spacing-4);
}

.content-section h4 {
  font-family: var(--font-display);
  font-size: var(--font-size-body);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  color: var(--fg-primary);
  margin-bottom: var(--spacing-3);
}

.content-section p {
  margin: var(--spacing-3) 0;
  color: var(--fg-primary);
}

.content-section ul {
  padding-left: var(--spacing-6);
  margin: var(--spacing-3) 0;
}

.content-section ul li {
  margin: var(--spacing-2) 0;
  color: var(--fg-primary);
}

.code-block {
  background: rgba(212, 175, 55, 0.05);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: var(--radius-none);
  padding: var(--spacing-4);
  font-family: 'Courier New', monospace;
  font-size: var(--font-size-small);
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre;
  color: var(--fg-primary);
}

.model-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-4);
  margin-top: var(--spacing-4);
}

.model-list ul {
  padding-left: var(--spacing-5);
  margin: var(--spacing-3) 0;
  list-style: disc;
}

.profiling-section :deep(.el-descriptions__label) {
  background: rgba(212, 175, 55, 0.1) !important;
  color: var(--fg-muted) !important;
  font-family: var(--font-display);
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
}

.profiling-section :deep(.el-descriptions__content) {
  background: transparent !important;
  color: var(--fg-primary) !important;
  font-family: var(--font-body);
}

.code-block {
  overflow-x: auto;
  white-space: pre;
  color: #303133;
}

textarea.code-block {
  width: 100%;
  min-height: 400px;
  resize: vertical;
  border: 1px solid #e4e7ed;
  outline: none;
}

.strategy-content {
  padding: 15px;
}

:deep(.el-card__body) {
  padding: 15px;
}

:deep(.el-collapse-item__content) {
  padding: 0;
}

:deep(.el-timeline-item__timestamp) {
  font-weight: bold;
  color: #409eff;
}
</style>
