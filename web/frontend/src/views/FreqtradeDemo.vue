<template>
  <div class="freqtrade-demo">

    <div class="page-header">
      <h1 class="page-title">FREQTRADE DEMO</h1>
      <p class="page-subtitle">CRYPTO TRADING BOT | BACKTESTING | STRATEGY OPTIMIZATION</p>
    </div>

    <div class="function-nav">
      <el-button
        v-for="(tab, _idx) in tabs"
        :key="tab.key"
        type="activeTab === tab.key ? 'solid' : 'outline'"
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
        <p>Freqtrade is a free open source crypto trading bot written in Python, designed for the cryptocurrency market. It features a highly customizable strategy engine, complete backtesting framework and advanced machine learning support.</p>

        <h3 style="margin-top: 30px;">CORE FEATURES</h3>
        <div class="features-grid">
          <el-card :hoverable="true">
            <h4>TRADING</h4>
            <ul>
              <li>Multiple Exchanges (Binance, OKX, Bybit, Kraken)</li>
              <li>Custom Trading Strategies (Technical Indicators)</li>
              <li>Order Types (Limit, Market, Stop Loss)</li>
              <li>Position Management & Risk Control</li>
              <li>Real-time Market Monitoring</li>
            </ul>
          </el-card>

          <el-card :hoverable="true">
            <h4>BACKTESTING</h4>
            <ul>
              <li>Historical Data Backtesting</li>
              <li>Performance Metrics (Sharpe, Sortino, Calmar)</li>
              <li>Trade Logging & Visualization</li>
              <li>Multi-market & Multi-pair Support</li>
              <li>HTML Report Generation</li>
            </ul>
          </el-card>

          <el-card :hoverable="true">
            <h4>OPTIMIZATION</h4>
            <ul>
              <li>Hyperopt Parameter Optimization</li>
              <li>Machine Learning Strategies (scikit-learn)</li>
              <li>FreqAI Framework (Reinforcement Learning)</li>
              <li>Parameter Space Search</li>
              <li>GPU Acceleration Support</li>
            </ul>
          </el-card>

          <el-card :hoverable="true">
            <h4>MANAGEMENT</h4>
            <ul>
              <li>Web UI Management</li>
              <li>Telegram Bot Control</li>
              <li>REST API Interface</li>
              <li>Real-time Log Viewing</li>
              <li>Performance Monitoring</li>
            </ul>
          </el-card>
        </div>

        <h3 style="margin-top: 30px;">SUPPORTED EXCHANGES</h3>
        <div class="exchange-list">
          <el-tag v-for="exchange in exchanges" :key="exchange" type="info">
            {{ exchange }}
          </el-tag>
        </div>

        <h3 style="margin-top: 30px;">OFFICIAL RESOURCES</h3>
        <ul style="margin-top: 10px; line-height: 1.8;">
          <li>Website: <el-link href="https://www.freqtrade.io" target="_blank" type="primary">https://www.freqtrade.io</el-link></li>
          <li>Docs: <el-link href="https://www.freqtrade.io/en/stable/" target="_blank" type="primary">https://www.freqtrade.io/en/stable/</el-link></li>
          <li>GitHub: <el-link href="https://github.com/freqtrade/freqtrade" target="_blank" type="primary">https://github.com/freqtrade/freqtrade</el-link></li>
          <li>Discord Community</li>
        </ul>
      </div>
    </el-card>

    <!-- 2. 策略开发 -->
    <el-card v-show="activeTab === 'strategy'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>📝 策略开发</span>
          <el-tag type="warning">文档</el-tag>
        </div>
      </template>

      <div class="content-section">
        <h3>🎯 策略结构</h3>
        <p>Freqtrade 策略基于 IStrategy 接口,主要包含以下核心方法:</p>

        <el-tabs type="border-card" style="margin-top: 20px;">
          <el-tab-pane label="基础策略示例">
            <pre v-pre class="code-block">from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class SampleStrategy(IStrategy):
    # 策略参数
    minimal_roi = {
        "0": 0.10,   # 10% ROI
        "30": 0.05,  # 30分钟后5% ROI
        "60": 0.01   # 60分钟后1% ROI
    }

    stoploss = -0.10  # 止损 10%

    timeframe = '5m'  # 5分钟K线

    # 买入信号
    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] < 30) &  # RSI 超卖
                (dataframe['close'] < dataframe['bb_lowerband'])  # 价格低于布林带下轨
            ),
            'buy'] = 1
        return dataframe

    # 卖出信号
    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] > 70) |  # RSI 超买
                (dataframe['close'] > dataframe['bb_upperband'])  # 价格高于布林带上轨
            ),
            'sell'] = 1
        return dataframe

    # 指标计算
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # 布林带
        bollinger = ta.BBANDS(dataframe, timeperiod=20)
        dataframe['bb_upperband'] = bollinger['upperband']
        dataframe['bb_lowerband'] = bollinger['lowerband']

        return dataframe</pre>
          </el-tab-pane>

          <el-tab-pane label="机器学习策略">
            <pre v-pre class="code-block">from freqtrade.strategy import IStrategy
from freqai.base_model import BaseRegressionModel
import pandas as pd

class FreqAIStrategy(IStrategy):
    # FreqAI 配置
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # 定义特征
        dataframe['%-rsi'] = ta.RSI(dataframe)
        dataframe['%-mfi'] = ta.MFI(dataframe)
        dataframe['%-adx'] = ta.ADX(dataframe)

        # 定义标签 (预测目标)
        dataframe['&-s_close'] = (
            dataframe['close']
            .shift(-5)  # 预测5根K线后的价格
            .rolling(5)
            .mean()
        )

        return dataframe

    def populate_buy_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # 使用模型预测
        dataframe.loc[
            (dataframe['&-s_close'] > dataframe['close'] * 1.01),  # 预测上涨1%
            'buy'] = 1
        return dataframe</pre>
          </el-tab-pane>

          <el-tab-pane label="常用技术指标">
            <div style="padding: 15px;">
              <h4>TECHNICAL INDICATORS</h4>
              <div class="indicators-grid">
                <div class="indicator-category">
                  <h5>TREND</h5>
                  <ul>
                    <li>SMA / EMA</li>
                    <li>MACD</li>
                    <li>ADX</li>
                    <li>Parabolic SAR</li>
                  </ul>
                </div>
                <div class="indicator-category">
                  <h5>OSCILLATOR</h5>
                  <ul>
                    <li>RSI</li>
                    <li>Stochastic</li>
                    <li>CCI</li>
                    <li>MFI</li>
                  </ul>
                </div>
                <div class="indicator-category">
                  <h5>OTHER</h5>
                  <ul>
                    <li>Bollinger Bands</li>
                    <li>ATR</li>
                    <li>Volume</li>
                    <li>Fibonacci</li>
                  </ul>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>

        <el-alert
          type="warning"
          title="⚠️ 策略开发注意事项"
          :closable="false"
          style="margin-top: 20px;"
        >
          <ul style="margin-top: 10px;">
            <li><strong>过拟合风险</strong>: 避免策略过度优化历史数据,导致实盘表现不佳</li>
            <li><strong>滑点和手续费</strong>: 回测时务必考虑交易成本</li>
            <li><strong>样本外测试</strong>: 使用未参与优化的数据进行验证</li>
            <li><strong>风险管理</strong>: 设置合理的止损和仓位管理规则</li>
            <li><strong>市场适应性</strong>: 不同市场环境可能需要调整策略参数</li>
          </ul>
        </el-alert>
      </div>
    </el-card>

    <!-- 3. 回测分析 -->
    <el-card v-show="activeTab === 'backtest'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>📈 回测分析</span>
          <el-tag type="warning">文档</el-tag>
        </div>
      </template>

      <div class="content-section">
        <h3>🔍 回测流程</h3>
        <p>Freqtrade 提供强大的回测功能,可以在历史数据上测试策略表现:</p>

        <el-steps :active="3" align-center style="margin: 30px 0;">
          <el-step title="下载数据" description="freqtrade download-data" />
          <el-step title="编写策略" description="实现 IStrategy 接口" />
          <el-step title="运行回测" description="freqtrade backtesting" />
          <el-step title="分析结果" description="查看报告和图表" />
        </el-steps>

        <h3 style="margin-top: 30px;">⚙️ 回测命令示例</h3>
        <el-tabs type="border-card" style="margin-top: 20px;">
          <el-tab-pane label="基础回测">
            <pre v-pre class="code-block"># 回测单个策略
freqtrade backtesting \
  --strategy SampleStrategy \
  --timerange 20210101-20211231 \
  --timeframe 5m

# 回测多个币对
freqtrade backtesting \
  --strategy SampleStrategy \
  --pairs BTC/USDT ETH/USDT BNB/USDT \
  --timerange 20210101-20211231

# 启用详细日志
freqtrade backtesting \
  --strategy SampleStrategy \
  --timerange 20210101-20211231 \
  --verbose</pre>
          </el-tab-pane>

          <el-tab-pane label="超参数优化">
            <pre v-pre class="code-block"># Hyperopt 参数优化
freqtrade hyperopt \
  --hyperopt-loss SharpeHyperOptLoss \
  --strategy SampleStrategy \
  --timerange 20210101-20211231 \
  --epochs 500

# 只优化买入参数
freqtrade hyperopt \
  --spaces buy \
  --strategy SampleStrategy \
  --timerange 20210101-20211231

# 并行优化 (使用多核CPU)
freqtrade hyperopt \
  --strategy SampleStrategy \
  --timerange 20210101-20211231 \
  --jobs 4</pre>
          </el-tab-pane>

          <el-tab-pane label="生成报告">
            <pre v-pre class="code-block"># 生成 HTML 回测报告
freqtrade backtesting \
  --strategy SampleStrategy \
  --timerange 20210101-20211231 \
  --export trades \
  --export-filename backtest_results.json

freqtrade plot-dataframe \
  --strategy SampleStrategy \
  --timerange 20210101-20211231 \
  --indicators1 sma ema \
  --indicators2 rsi

# 生成利润图表
freqtrade plot-profit \
  --strategy SampleStrategy \
  --timerange 20210101-20211231</pre>
          </el-tab-pane>
        </el-tabs>

        <h3 style="margin-top: 30px;">📊 回测性能指标</h3>
        <el-table :data="metricsData" stripe style="margin-top: 15px;">
          <el-table-column prop="metric" label="指标" width="200" />
          <el-table-column prop="description" label="说明" />
          <el-table-column prop="target" label="目标值" width="150" />
        </el-table>

        <el-alert
          type="info"
          title="💡 回测结果解读"
          :closable="false"
          style="margin-top: 20px;"
        >
          <ul style="margin-top: 10px;">
            <li><strong>总收益率</strong>: 策略在回测期间的总收益,需考虑复利效应</li>
            <li><strong>胜率</strong>: 盈利交易占总交易的比例,≥ 50% 较好</li>
            <li><strong>盈亏比</strong>: 平均盈利 / 平均亏损,≥ 1.5 较好</li>
            <li><strong>最大回撤</strong>: 从峰值到谷底的最大跌幅,越小越好</li>
            <li><strong>夏普比率</strong>: 风险调整后收益,≥ 1.0 较好</li>
          </ul>
        </el-alert>
      </div>
    </el-card>

    <!-- 4. 配置说明 -->
    <el-card v-show="activeTab === 'config'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>⚙️ 配置说明</span>
          <el-tag type="warning">文档</el-tag>
        </div>
      </template>

      <div class="content-section">
        <h3>📝 配置文件结构</h3>
        <p>Freqtrade 使用 JSON 格式配置文件 (config.json):</p>

        <el-tabs type="border-card" style="margin-top: 20px;">
          <el-tab-pane label="基础配置">
            <pre v-pre class="code-block">{
  "max_open_trades": 3,
  "stake_currency": "USDT",
  "stake_amount": "unlimited",
  "tradable_balance_ratio": 0.99,

  "dry_run": true,
  "dry_run_wallet": 1000,

  "timeframe": "5m",

  "exchange": {
    "name": "binance",
    "key": "your-api-key",
    "secret": "your-api-secret",
    "ccxt_config": {},
    "ccxt_async_config": {},
    "pair_whitelist": [
      "BTC/USDT",
      "ETH/USDT",
      "BNB/USDT"
    ],
    "pair_blacklist": []
  }
}</pre>
          </el-tab-pane>

          <el-tab-pane label="策略配置">
            <pre v-pre class="code-block">{
  "strategy": "SampleStrategy",
  "strategy_path": "user_data/strategies/",

  "minimal_roi": {
    "0": 0.10,
    "30": 0.05,
    "60": 0.01
  },

  "stoploss": -0.10,
  "trailing_stop": true,
  "trailing_stop_positive": 0.01,
  "trailing_stop_positive_offset": 0.02,
  "trailing_only_offset_is_reached": true,

  "unfilledtimeout": {
    "buy": 10,
    "sell": 10,
    "unit": "minutes"
  }
}</pre>
          </el-tab-pane>

          <el-tab-pane label="Telegram 机器人">
            <pre v-pre class="code-block">{
  "telegram": {
    "enabled": true,
    "token": "your-telegram-bot-token",
    "chat_id": "your-telegram-chat-id",
    "notification_settings": {
      "status": "on",
      "warning": "on",
      "startup": "on",
      "buy": "on",
      "sell": "on",
      "buy_cancel": "on",
      "sell_cancel": "on"
    }
  }
}</pre>
          </el-tab-pane>

          <el-tab-pane label="API 配置">
            <pre v-pre class="code-block">{
  "api_server": {
    "enabled": true,
    "listen_ip_address": "127.0.0.1",
    "listen_port": 8080,
    "verbosity": "error",
    "enable_openapi": true,
    "jwt_secret_key": "your-jwt-secret-key",
    "CORS_origins": [],
    "username": "admin",
    "password": "your-password"
  }
}</pre>
          </el-tab-pane>
        </el-tabs>

        <h3 style="margin-top: 30px;">🔑 关键配置参数说明</h3>
        <el-descriptions :column="1" border style="margin-top: 15px;">
          <el-descriptions-item label="max_open_trades">
            最大同时持仓数量,控制风险分散
          </el-descriptions-item>
          <el-descriptions-item label="stake_amount">
            每笔交易金额 ("unlimited" 表示自动计算)
          </el-descriptions-item>
          <el-descriptions-item label="dry_run">
            模拟交易模式 (true=模拟, false=实盘)
          </el-descriptions-item>
          <el-descriptions-item label="timeframe">
            K线周期 (1m, 5m, 15m, 1h, 4h, 1d 等)
          </el-descriptions-item>
          <el-descriptions-item label="stoploss">
            止损百分比 (负值,如 -0.10 表示 -10%)
          </el-descriptions-item>
          <el-descriptions-item label="trailing_stop">
            移动止损,跟随价格上涨自动调整止损点
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>

    <!-- 5. Web UI -->
    <el-card v-show="activeTab === 'webui'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>🖥️ Web UI 管理界面</span>
          <el-tag type="info">计划集成</el-tag>
        </div>
      </template>

      <div class="content-section">
        <h3>🎨 FreqUI 功能</h3>
        <p>FreqUI 是 Freqtrade 的官方 Web 管理界面,提供直观的可视化管理功能:</p>

        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="12">
            <el-card shadow="hover">
              <h4>📊 实时监控</h4>
              <ul>
                <li>实时查看持仓和订单</li>
                <li>查看策略运行状态</li>
                <li>监控账户余额变化</li>
                <li>查看交易历史记录</li>
                <li>实时日志输出</li>
              </ul>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover">
              <h4>🎛️ 交易控制</h4>
              <ul>
                <li>启动/停止交易机器人</li>
                <li>强制买入/卖出</li>
                <li>修改配置参数</li>
                <li>紧急停止所有交易</li>
                <li>切换策略</li>
              </ul>
            </el-card>
          </el-col>
        </el-row>

        <h3 style="margin-top: 30px;">🚀 启动 Web UI</h3>
        <pre v-pre class="code-block"># 启动 Freqtrade 并开启 API
freqtrade trade --config config.json --strategy SampleStrategy

# 在另一个终端启动 FreqUI (需要单独安装)
# 或者访问: http://localhost:8080 (如果配置了 api_server)</pre>

        <el-alert
          type="info"
          title="💡 Web UI 访问"
          :closable="false"
          style="margin-top: 20px;"
        >
          <p style="margin-top: 10px;">默认访问地址: <code>http://127.0.0.1:8080</code></p>
          <p>默认账号: 在 config.json 的 api_server 部分配置</p>
          <p style="margin-top: 10px;">
            <el-link href="https://github.com/freqtrade/frequi" target="_blank" type="primary">
              FreqUI GitHub 仓库
            </el-link>
          </p>
        </el-alert>

        <h3 style="margin-top: 30px;">🔌 REST API 端点</h3>
        <el-table :data="apiEndpoints" stripe style="margin-top: 15px;">
          <el-table-column prop="method" label="方法" width="100" />
          <el-table-column prop="endpoint" label="端点" width="250" />
          <el-table-column prop="description" label="说明" />
        </el-table>
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
          <el-descriptions-item label="项目文档">
            <el-tag type="success">✅ 已整理</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="策略示例">
            <el-tag type="success">✅ 已收集</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="配置模板">
            <el-tag type="success">✅ 已文档化</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="后端 API">
            <el-tag type="info">⏳ 待开发</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="数据接口">
            <el-tag type="info">⏳ 待开发</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Web UI 集成">
            <el-tag type="info">⏳ 计划中</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 30px;">🎯 后续集成计划</h3>
        <el-timeline style="margin-top: 20px;">
          <el-timeline-item timestamp="Phase 1" placement="top">
            <el-card>
              <h4>数据接口集成</h4>
              <p>整合 Freqtrade 的数据下载和存储功能到 MyStocks 数据管理系统</p>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="Phase 2" placement="top">
            <el-card>
              <h4>策略管理</h4>
              <p>在 Web 界面中实现策略的创建、编辑和管理功能</p>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="Phase 3" placement="top">
            <el-card>
              <h4>回测系统</h4>
              <p>集成 Freqtrade 回测引擎,在 Web 界面中运行回测并查看结果</p>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="Phase 4" placement="top">
            <el-card>
              <h4>实盘交易</h4>
              <p>支持在 Web 界面中启动和监控实盘交易机器人</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>

        <el-alert
          type="warning"
          title="⚠️ 重要提醒"
          :closable="false"
          style="margin-top: 20px;"
        >
          <ul style="margin-top: 10px;">
            <li><strong>风险警示</strong>: 加密货币交易存在高风险,请务必充分了解风险后再使用</li>
            <li><strong>模拟交易</strong>: 建议先在模拟模式下充分测试策略</li>
            <li><strong>资金管理</strong>: 只投入您能承受损失的资金</li>
            <li><strong>持续监控</strong>: 实盘交易时需要持续监控机器人运行状态</li>
            <li><strong>法律合规</strong>: 确保您所在地区允许加密货币交易</li>
          </ul>
        </el-alert>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeTab = ref('overview')

const tabs = [
  { key: 'overview', label: '项目概览', icon: '📋' },
  { key: 'strategy', label: '策略开发', icon: '📝' },
  { key: 'backtest', label: '回测分析', icon: '📈' },
  { key: 'config', label: '配置说明', icon: '⚙️' },
  { key: 'webui', label: 'Web UI', icon: '🖥️' },
  { key: 'status', label: '集成状态', icon: '✅' }
]

const exchanges = [
  'Binance', 'OKX', 'Bybit', 'Kraken', 'Bitfinex',
  'Huobi', 'Gate.io', 'KuCoin', 'Coinbase Pro', 'Bitstamp'
]

const metricsData = [
  { metric: 'Total Profit', description: '总收益率', target: '> 0%' },
  { metric: 'Win Rate', description: '胜率(盈利交易占比)', target: '≥ 50%' },
  { metric: 'Profit Factor', description: '盈亏比(总盈利/总亏损)', target: '≥ 1.5' },
  { metric: 'Max Drawdown', description: '最大回撤', target: '< 30%' },
  { metric: 'Sharpe Ratio', description: '夏普比率(风险调整收益)', target: '≥ 1.0' },
  { metric: 'Sortino Ratio', description: '索提诺比率(下行风险调整收益)', target: '≥ 1.5' },
  { metric: 'Calmar Ratio', description: '卡玛比率(收益/最大回撤)', target: '≥ 3.0' },
  { metric: 'Total Trades', description: '总交易次数', target: '≥ 100' }
]

const apiEndpoints = [
  { method: 'GET', endpoint: '/api/v1/balance', description: '获取账户余额' },
  { method: 'GET', endpoint: '/api/v1/status', description: '获取机器人状态' },
  { method: 'GET', endpoint: '/api/v1/trades', description: '获取交易历史' },
  { method: 'GET', endpoint: '/api/v1/performance', description: '获取性能指标' },
  { method: 'POST', endpoint: '/api/v1/start', description: '启动交易' },
  { method: 'POST', endpoint: '/api/v1/stop', description: '停止交易' },
  { method: 'POST', endpoint: '/api/v1/forcebuy', description: '强制买入' },
  { method: 'POST', endpoint: '/api/v1/forcesell', description: '强制卖出' },
  { method: 'GET', endpoint: '/api/v1/logs', description: '获取日志' }
]
</script>

<style scoped>
@import "./styles/FreqtradeDemo.css";
</style>
