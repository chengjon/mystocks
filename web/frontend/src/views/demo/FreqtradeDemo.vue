<template>

    <div class="page-header">
      <h1 class="page-title">FREQTRADE</h1>
      <p class="page-subtitle">CRYPTO TRADING BOT | BACKTEST | ML | LIVE TRADING</p>
      <div class="decorative-line"></div>
    </div>

    <div class="function-nav tabs-nav">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="btn"
        @click="activeTab = tab.key"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        <span class="tab-label">{{ tab.label }}</span>
      </button>
    </div>

    <div class="card main-card" v-show="activeTab === 'overview'">
      <div class="card-header">
        <h3 class="card-title">📋 PROJECT OVERVIEW</h3>
        <span class="badge badge-success">MIGRATED</span>
      </div>

      <div class="content-section">
        <h3>🎯 FREQTRADE INTRODUCTION</h3>
        <p>Freqtrade is a free open-source cryptocurrency trading bot written in Python, designed for the crypto market. It features a highly customizable strategy engine, complete backtesting framework, and advanced machine learning support.</p>

        <h3 style="margin-top: 30px;">✨ CORE FEATURES</h3>
        <div class="features-grid" style="margin-top: 20px;">
          <div class="card feature-card">
            <h4>💹 TRADING FEATURES</h4>
            <ul>
              <li>Multiple exchange support (Binance, OKX, Bybit, Kraken, etc.)</li>
              <li>Custom trading strategies (technical indicators)</li>
              <li>Multiple order types (limit, market, stop-loss)</li>
              <li>Position management and risk control</li>
              <li>Real-time market monitoring and trading</li>
            </ul>
          </div>
          <div class="card feature-card">
            <h4>📊 BACKTEST & ANALYSIS</h4>
            <ul>
              <li>Historical data backtesting (any time range)</li>
              <li>Strategy performance metrics (Sharpe, Sortino, Calmar)</li>
              <li>Trading logs and chart visualization</li>
              <li>Multi-market and multi-pair backtesting</li>
              <li>HTML backtest report generation</li>
            </ul>
          </div>
          <div class="card feature-card">
            <h4>🤖 STRATEGY OPTIMIZATION</h4>
            <ul>
              <li>Hyperopt parameter optimization</li>
              <li>Machine learning strategies (scikit-learn)</li>
              <li>FreqAI framework (reinforcement learning)</li>
              <li>Parameter space search and cross-validation</li>
              <li>GPU-accelerated training support</li>
            </ul>
          </div>
          <div class="card feature-card">
            <h4>🎛️ MANAGEMENT & MONITORING</h4>
            <ul>
              <li>Web UI management interface</li>
              <li>Telegram bot control</li>
              <li>REST API endpoints</li>
              <li>Real-time log viewing</li>
              <li>Performance monitoring and alerts</li>
            </ul>
          </div>
        </div>

        <h3 style="margin-top: 30px;">🔗 SUPPORTED EXCHANGES</h3>
        <div class="exchange-list">
          <span class="badge badge-info" v-for="exchange in exchanges" :key="exchange">
            {{ exchange }}
          </span>
        </div>

          <div class="alert-title">📚 OFFICIAL RESOURCES</div>
          <ul style="margin-top: 10px; line-height: 1.8;">
            <li>Website: <a href="https://www.freqtrade.io" target="_blank" class="link">https://www.freqtrade.io</a></li>
            <li>Docs: <a href="https://www.freqtrade.io/en/stable/" target="_blank" class="link">https://www.freqtrade.io/en/stable/</a></li>
            <li>GitHub: <a href="https://github.com/freqtrade/freqtrade" target="_blank" class="link">https://github.com/freqtrade/freqtrade</a></li>
            <li>Discord Community: Active technical support and strategy discussions</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="card main-card" v-show="activeTab === 'strategy'">
      <div class="card-header">
        <h3 class="card-title">📝 STRATEGY DEVELOPMENT</h3>
        <span class="badge badge-warning">DOCUMENTATION</span>
      </div>

      <div class="content-section">
        <h3>🎯 STRATEGY STRUCTURE</h3>
        <p>Freqtrade strategies are based on the IStrategy interface and include the following core methods:</p>

        <div class="tabs">
          <div class="tabs-header">
            <button
              v-for="tab in strategyTabs"
              :key="tab.key"
              class="tab-btn"
              :class="{ active: strategyTab === tab.key }"
              @click="strategyTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>

          <div class="tab-content" v-show="strategyTab === 'basic'">
            <pre v-pre class="code-block">from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class SampleStrategy(IStrategy):
    # Strategy parameters
    minimal_roi = {
        "0": 0.10,   # 10% ROI
        "30": 0.05,  # 5% ROI after 30 minutes
        "60": 0.01   # 1% ROI after 60 minutes
    }

    stoploss = -0.10  # 10% stop loss

    timeframe = '5m'  # 5-minute K-line

    # Buy signal
    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] < 30) &  # RSI oversold
                (dataframe['close'] < dataframe['bb_lowerband'])  # Price below BB lower band
            ),
            'buy'] = 1
        return dataframe

    # Sell signal
    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] > 70) |  # RSI overbought
                (dataframe['close'] > dataframe['bb_upperband'])  # Price above BB upper band
            ),
            'sell'] = 1
        return dataframe

    # Indicator calculation
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # Bollinger Bands
        bollinger = ta.BBANDS(dataframe, timeperiod=20)
        dataframe['bb_upperband'] = bollinger['upperband']
        dataframe['bb_lowerband'] = bollinger['lowerband']

        return dataframe</pre>
          </div>

          <div class="tab-content" v-show="strategyTab === 'ml'">
            <pre v-pre class="code-block">from freqtrade.strategy import IStrategy
from freqai.base_model import BaseRegressionModel
import pandas as pd

class FreqAIStrategy(IStrategy):
    # FreqAI configuration
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # Define features
        dataframe['%-rsi'] = ta.RSI(dataframe)
        dataframe['%-mfi'] = ta.MFI(dataframe)
        dataframe['%-adx'] = ta.ADX(dataframe)

        # Define labels (prediction targets)
        dataframe['&-s_close'] = (
            dataframe['close']
            .shift(-5)  # Predict 5 K-lines ahead
            .rolling(5)
            .mean()
        )

        return dataframe

    def populate_buy_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # Use model predictions
        dataframe.loc[
            (dataframe['&-s_close'] > dataframe['close'] * 1.01),  # Predict 1% increase
            'buy'] = 1
        return dataframe</pre>
          </div>

          <div class="tab-content" v-show="strategyTab === 'indicators'">
            <div style="padding: 15px;">
              <h4>📊 SUPPORTED TECHNICAL INDICATORS</h4>
              <div class="indicators-grid" style="margin-top: 15px;">
                <div class="indicator-group">
                  <h5>TREND INDICATORS</h5>
                  <ul>
                    <li>SMA / EMA (Moving Average)</li>
                    <li>MACD</li>
                    <li>ADX (Trend Strength)</li>
                    <li>Parabolic SAR</li>
                  </ul>
                </div>
                <div class="indicator-group">
                  <h5>OSCILLATORS</h5>
                  <ul>
                    <li>RSI (Relative Strength)</li>
                    <li>Stochastic</li>
                    <li>CCI (Commodity Channel)</li>
                    <li>MFI (Money Flow)</li>
                  </ul>
                </div>
                <div class="indicator-group">
                  <h5>OTHER INDICATORS</h5>
                  <ul>
                    <li>Bollinger Bands</li>
                    <li>ATR (Volatility)</li>
                    <li>Volume</li>
                    <li>Fibonacci</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

          <div class="alert-title">⚠️ STRATEGY DEVELOPMENT NOTES</div>
          <ul style="margin-top: 10px;">
            <li><strong>Overfitting Risk</strong>: Avoid over-optimizing strategies on historical data</li>
            <li><strong>Slippage & Fees</strong>: Always consider trading costs in backtesting</li>
            <li><strong>Out-of-Sample Testing</strong>: Use unseen data for validation</li>
            <li><strong>Risk Management</strong>: Set reasonable stop-loss and position rules</li>
            <li><strong>Market Adaptability</strong>: Different markets may require parameter adjustments</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="card main-card" v-show="activeTab === 'backtest'">
      <div class="card-header">
        <h3 class="card-title">📈 BACKTEST ANALYSIS</h3>
        <span class="badge badge-warning">DOCUMENTATION</span>
      </div>

      <div class="content-section">
        <h3>🔍 BACKTEST PROCESS</h3>
        <p>Freqtrade provides powerful backtesting capabilities to test strategy performance on historical data:</p>

        <div class="steps">
          <div class="step-item">
            <div class="step-number">1</div>
            <div class="step-content">
              <div class="step-title">DOWNLOAD DATA</div>
              <div class="step-desc">freqtrade download-data</div>
            </div>
          </div>
          <div class="step-connector"></div>
          <div class="step-item">
            <div class="step-number">2</div>
            <div class="step-content">
              <div class="step-title">WRITE STRATEGY</div>
              <div class="step-desc">Implement IStrategy interface</div>
            </div>
          </div>
          <div class="step-connector"></div>
          <div class="step-item">
            <div class="step-number">3</div>
            <div class="step-content">
              <div class="step-title">RUN BACKTEST</div>
              <div class="step-desc">freqtrade backtesting</div>
            </div>
          </div>
          <div class="step-connector"></div>
          <div class="step-item">
            <div class="step-number">4</div>
            <div class="step-content">
              <div class="step-title">ANALYZE RESULTS</div>
              <div class="step-desc">View reports and charts</div>
            </div>
          </div>
        </div>

        <h3 style="margin-top: 30px;">⚙️ BACKTEST COMMAND EXAMPLES</h3>
        <div class="tabs">
          <div class="tabs-header">
            <button
              v-for="tab in backtestTabs"
              :key="tab.key"
              class="tab-btn"
              :class="{ active: backtestTab === tab.key }"
              @click="backtestTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>

          <div class="tab-content" v-show="backtestTab === 'basic'">
            <pre v-pre class="code-block"># Backtest single strategy
freqtrade backtesting \
  --strategy SampleStrategy \
  --timerange 20210101-20211231 \
  --timeframe 5m

# Backtest multiple pairs
freqtrade backtesting \
  --strategy SampleStrategy \
  --pairs BTC/USDT ETH/USDT BNB/USDT \
  --timerange 20210101-20211231

# Enable verbose logging
freqtrade backtesting \
  --strategy SampleStrategy \
  --timerange 20210101-20211231 \
  --verbose</pre>
          </div>

          <div class="tab-content" v-show="backtestTab === 'hyperopt'">
            <pre v-pre class="code-block"># Hyperopt parameter optimization
freqtrade hyperopt \
  --hyperopt-loss SharpeHyperOptLoss \
  --strategy SampleStrategy \
  --timerange 20210101-20211231 \
  --epochs 500

# Optimize buy parameters only
freqtrade hyperopt \
  --spaces buy \
  --strategy SampleStrategy \
  --timerange 20210101-20211231

# Parallel optimization (multi-core CPU)
freqtrade hyperopt \
  --strategy SampleStrategy \
  --timerange 20210101-20211231 \
  --jobs 4</pre>
          </div>

          <div class="tab-content" v-show="backtestTab === 'report'">
            <pre v-pre class="code-block"># Generate HTML backtest report
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

# Generate profit chart
freqtrade plot-profit \
  --strategy SampleStrategy \
  --timerange 20210101-20211231</pre>
          </div>
        </div>

        <h3 style="margin-top: 30px;">📊 BACKTEST PERFORMANCE METRICS</h3>
        <table class="table" style="margin-top: 15px;">
          <thead>
            <tr>
              <th>METRIC</th>
              <th>DESCRIPTION</th>
              <th>TARGET</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="metric in metricsData" :key="metric.metric">
              <td class="metric-name">{{ metric.metric }}</td>
              <td>{{ metric.description }}</td>
              <td class="metric-target">{{ metric.target }}</td>
            </tr>
          </tbody>
        </table>

          <div class="alert-title">💡 BACKTEST RESULTS INTERPRETATION</div>
          <ul style="margin-top: 10px;">
            <li><strong>Total Return</strong>: Strategy's total return during backtest period</li>
            <li><strong>Win Rate</strong>: Profitable trades / Total trades, ≥ 50% is good</li>
            <li><strong>Profit Factor</strong>: Avg profit / Avg loss, ≥ 1.5 is good</li>
            <li><strong>Max Drawdown</strong>: Peak to valley decline, smaller is better</li>
            <li><strong>Sharpe Ratio</strong>: Risk-adjusted return, ≥ 1.0 is good</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="card main-card" v-show="activeTab === 'config'">
      <div class="card-header">
        <h3 class="card-title">⚙️ CONFIGURATION</h3>
        <span class="badge badge-warning">DOCUMENTATION</span>
      </div>

      <div class="content-section">
        <h3>📝 CONFIG FILE STRUCTURE</h3>
        <p>Freqtrade uses JSON format configuration files (config.json):</p>

        <div class="tabs">
          <div class="tabs-header">
            <button
              v-for="tab in configTabs"
              :key="tab.key"
              class="tab-btn"
              :class="{ active: configTab === tab.key }"
              @click="configTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>

          <div class="tab-content" v-show="configTab === 'basic'">
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
          </div>

          <div class="tab-content" v-show="configTab === 'strategy'">
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
          </div>

          <div class="tab-content" v-show="configTab === 'telegram'">
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
          </div>

          <div class="tab-content" v-show="configTab === 'api'">
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
          </div>
        </div>

        <h3 style="margin-top: 30px;">🔑 KEY CONFIGURATION PARAMETERS</h3>
        <table class="table" style="margin-top: 15px;">
          <thead>
            <tr>
              <th>PARAMETER</th>
              <th>DESCRIPTION</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="param-name">max_open_trades</td>
              <td>Maximum concurrent trades, controls risk diversification</td>
            </tr>
            <tr>
              <td class="param-name">stake_amount</td>
              <td>Trade amount per transaction ("unlimited" for auto-calculation)</td>
            </tr>
            <tr>
              <td class="param-name">dry_run</td>
              <td>Simulation mode (true=simulated, false=live trading)</td>
            </tr>
            <tr>
              <td class="param-name">timeframe</td>
              <td>K-line period (1m, 5m, 15m, 1h, 4h, 1d, etc.)</td>
            </tr>
            <tr>
              <td class="param-name">stoploss</td>
              <td>Stop-loss percentage (negative value, e.g., -0.10 = -10%)</td>
            </tr>
            <tr>
              <td class="param-name">trailing_stop</td>
              <td>Trailing stop-loss, automatically adjusts stop point with price increase</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="card main-card" v-show="activeTab === 'webui'">
      <div class="card-header">
        <h3 class="card-title">🖥️ WEB UI MANAGEMENT</h3>
        <span class="badge badge-info">PLANNED</span>
      </div>

      <div class="content-section">
        <h3>🎨 FREQUI FEATURES</h3>
        <p>FreqUI is the official Freqtrade web management interface, providing intuitive visual management:</p>

        <div class="features-grid" style="margin-top: 20px;">
          <div class="card feature-card">
            <h4>📊 REAL-TIME MONITORING</h4>
            <ul>
              <li>View positions and orders in real-time</li>
              <li>Check strategy running status</li>
              <li>Monitor account balance changes</li>
              <li>View trading history</li>
              <li>Real-time log output</li>
            </ul>
          </div>
          <div class="card feature-card">
            <h4>🎛️ TRADING CONTROL</h4>
            <ul>
              <li>Start/stop trading bot</li>
              <li>Force buy/sell</li>
              <li>Modify configuration parameters</li>
              <li>Emergency stop all trades</li>
              <li>Switch strategies</li>
            </ul>
          </div>
        </div>

        <h3 style="margin-top: 30px;">🚀 STARTING WEB UI</h3>
        <pre v-pre class="code-block"># Start Freqtrade with API enabled
freqtrade trade --config config.json --strategy SampleStrategy

# Start FreqUI in another terminal (requires separate installation)
# Or visit: http://localhost:8080 (if api_server configured)</pre>

          <div class="alert-title">💡 WEB UI ACCESS</div>
          <p style="margin-top: 10px;">Default access: <code>http://127.0.0.1:8080</code></p>
          <p>Default credentials: Configured in config.json api_server section</p>
          <p style="margin-top: 10px;">
            <a href="https://github.com/freqtrade/frequi" target="_blank" class="link">
              FreqUI GitHub Repository
            </a>
          </p>
        </div>

        <h3 style="margin-top: 30px;">🔌 REST API ENDPOINTS</h3>
        <table class="table" style="margin-top: 15px;">
          <thead>
            <tr>
              <th>METHOD</th>
              <th>ENDPOINT</th>
              <th>DESCRIPTION</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="endpoint in apiEndpoints" :key="endpoint.endpoint">
              <td class="method-badge">{{ endpoint.method }}</td>
              <td class="endpoint-path">{{ endpoint.endpoint }}</td>
              <td>{{ endpoint.description }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="card main-card" v-show="activeTab === 'status'">
      <div class="card-header">
        <h3 class="card-title">✅ INTEGRATION STATUS</h3>
      </div>

      <div class="content-section">
        <h3>📦 INTEGRATED FEATURES</h3>
        <table class="table" style="margin-top: 15px;">
          <thead>
            <tr>
              <th>FEATURE</th>
              <th>STATUS</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Project Documentation</td>
              <td><span class="badge badge-success">✅ COMPLETED</span></td>
            </tr>
            <tr>
              <td>Strategy Examples</td>
              <td><span class="badge badge-success">✅ COLLECTED</span></td>
            </tr>
            <tr>
              <td>Configuration Templates</td>
              <td><span class="badge badge-success">✅ DOCUMENTED</span></td>
            </tr>
            <tr>
              <td>Backend API</td>
              <td><span class="badge badge-warning">⏳ PENDING</span></td>
            </tr>
            <tr>
              <td>Data Interface</td>
              <td><span class="badge badge-warning">⏳ PENDING</span></td>
            </tr>
            <tr>
              <td>Web UI Integration</td>
              <td><span class="badge badge-info">📅 PLANNED</span></td>
            </tr>
          </tbody>
        </table>

        <h3 style="margin-top: 30px;">🎯 FUTURE INTEGRATION PLAN</h3>
        <div class="timeline" style="margin-top: 20px;">
          <div class="timeline-item">
            <div class="timeline-marker">1</div>
            <div class="timeline-content">
              <div class="timeline-title">PHASE 1: DATA INTERFACE</div>
              <div class="timeline-desc">Integrate Freqtrade data download and storage into MyStocks data management system</div>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-marker">2</div>
            <div class="timeline-content">
              <div class="timeline-title">PHASE 2: STRATEGY MANAGEMENT</div>
              <div class="timeline-desc">Implement strategy creation, editing and management in web interface</div>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-marker">3</div>
            <div class="timeline-content">
              <div class="timeline-title">PHASE 3: BACKTEST SYSTEM</div>
              <div class="timeline-desc">Integrate Freqtrade backtesting engine, run backtests and view results in web</div>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-marker">4</div>
            <div class="timeline-content">
              <div class="timeline-title">PHASE 4: LIVE TRADING</div>
              <div class="timeline-desc">Support starting and monitoring live trading bots in web interface</div>
            </div>
          </div>
        </div>

          <div class="alert-title">⚠️ IMPORTANT DISCLAIMER</div>
          <ul style="margin-top: 10px;">
            <li><strong>Risk Warning</strong>: Cryptocurrency trading has high risks, ensure you understand risks before use</li>
            <li><strong>Paper Trading</strong>: Recommend testing strategies fully in simulation mode first</li>
            <li><strong>Fund Management</strong>: Only invest funds you can afford to lose</li>
            <li><strong>Continuous Monitoring</strong>: Live trading requires continuous monitoring of bot status</li>
            <li><strong>Legal Compliance</strong>: Ensure cryptocurrency trading is allowed in your region</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeTab = ref('overview')
const strategyTab = ref('basic')
const backtestTab = ref('basic')
const configTab = ref('basic')

const tabs = [
  { key: 'overview', label: 'Overview', icon: '📋' },
  { key: 'strategy', label: 'Strategy', icon: '📝' },
  { key: 'backtest', label: 'Backtest', icon: '📈' },
  { key: 'config', label: 'Config', icon: '⚙️' },
  { key: 'webui', label: 'Web UI', icon: '🖥️' },
  { key: 'status', label: 'Status', icon: '✅' }
]

const strategyTabs = [
  { key: 'basic', label: 'Basic Strategy' },
  { key: 'ml', label: 'Machine Learning' },
  { key: 'indicators', label: 'Indicators' }
]

const backtestTabs = [
  { key: 'basic', label: 'Basic Backtest' },
  { key: 'hyperopt', label: 'Hyperopt' },
  { key: 'report', label: 'Generate Report' }
]

const configTabs = [
  { key: 'basic', label: 'Basic' },
  { key: 'strategy', label: 'Strategy' },
  { key: 'telegram', label: 'Telegram' },
  { key: 'api', label: 'API' }
]

const exchanges = [
  'Binance', 'OKX', 'Bybit', 'Kraken', 'Bitfinex',
  'Huobi', 'Gate.io', 'KuCoin', 'Coinbase Pro', 'Bitstamp'
]

const metricsData = [
  { metric: 'Total Profit', description: 'Total return rate', target: '> 0%' },
  { metric: 'Win Rate', description: 'Profitable trades ratio', target: '≥ 50%' },
  { metric: 'Profit Factor', description: 'Total profit / Total loss', target: '≥ 1.5' },
  { metric: 'Max Drawdown', description: 'Maximum drawdown', target: '< 30%' },
  { metric: 'Sharpe Ratio', description: 'Risk-adjusted return', target: '≥ 1.0' },
  { metric: 'Sortino Ratio', description: 'Downside risk-adjusted return', target: '≥ 1.5' },
  { metric: 'Calmar Ratio', description: 'Return / Max drawdown', target: '≥ 3.0' },
  { metric: 'Total Trades', description: 'Total number of trades', target: '≥ 100' }
]

const apiEndpoints = [
  { method: 'GET', endpoint: '/api/v1/balance', description: 'Get account balance' },
  { method: 'GET', endpoint: '/api/v1/status', description: 'Get bot status' },
  { method: 'GET', endpoint: '/api/v1/trades', description: 'Get trade history' },
  { method: 'GET', endpoint: '/api/v1/performance', description: 'Get performance metrics' },
  { method: 'POST', endpoint: '/api/v1/start', description: 'Start trading' },
  { method: 'POST', endpoint: '/api/v1/stop', description: 'Stop trading' },
  { method: 'POST', endpoint: '/api/v1/forcebuy', description: 'Force buy' },
  { method: 'POST', endpoint: '/api/v1/forcesell', description: 'Force sell' },
  { method: 'GET', endpoint: '/api/v1/logs', description: 'Get logs' }
]
</script>

<style scoped lang="scss">

.freqtrade-demo {
  min-height: 100vh;
  padding: var(--spacing-6);
  background: var(--bg-primary);
  position: relative;
}

  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.04;
  background-image:
    repeating-linear-gradient(45deg, var(--accent-gold) 0px, var(--accent-gold) 1px, transparent 1px, transparent 10px),
    repeating-linear-gradient(-45deg, var(--accent-gold) 0px, var(--accent-gold) 1px, transparent 1px, transparent 10px);
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

  .decorative-line {
    width: 200px;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
    margin: var(--spacing-5) auto 0;
    position: relative;

    &::after {
      content: '';
      position: absolute;
      bottom: -8px;
      left: 50%;
      transform: translateX(-50%);
      width: 60px;
      height: 1px;
      background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.5), transparent);
    }
  }
}

.function-nav {
  display: flex;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-6);
  flex-wrap: wrap;
  position: relative;
  z-index: 1;
}

.main-card {
  position: relative;
  z-index: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-5);
  padding-bottom: var(--spacing-4);
  border-bottom: 1px solid rgba(212, 175, 55, 0.3);

  .card-title {
    font-family: var(--font-display);
    font-size: var(--font-size-h4);
    color: var(--fg-primary);
    margin: 0;
  }
}

.content-section {
  padding: var(--spacing-2) 0;
  line-height: 1.8;

  h3 {
    font-family: var(--font-display);
    font-size: var(--font-size-h5);
    color: var(--accent-gold);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    margin-bottom: var(--spacing-4);
  }

  h4 {
    font-family: var(--font-display);
    font-size: var(--font-size-body);
    color: var(--fg-primary);
    margin-bottom: var(--spacing-3);
  }

  h5 {
    font-family: var(--font-display);
    font-size: var(--font-size-small);
    color: var(--fg-muted);
    margin-bottom: var(--spacing-2);
  }

  p {
    color: var(--fg-secondary);
    margin: var(--spacing-3) 0;
  }

  ul {
    padding-left: var(--spacing-6);
    margin: var(--spacing-3) 0;

    li {
      margin: var(--spacing-2) 0;
      color: var(--fg-secondary);
    }
  }
}

  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-4);
}

.feature-card {
  background: rgba(212, 175, 55, 0.03);
  border: 1px solid rgba(212, 175, 55, 0.2);
  padding: var(--spacing-5);
  border-radius: 0;

  h4 {
    font-family: var(--font-display);
    color: var(--accent-gold);
    margin-bottom: var(--spacing-4);
  }

  ul {
    margin: 0;

    li {
      font-size: var(--font-size-small);
    }
  }
}

.exchange-list {
  margin-top: var(--spacing-4);
  padding: var(--spacing-5);
  background: rgba(212, 175, 55, 0.03);
  border: 1px solid rgba(212, 175, 55, 0.2);
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2);
}

.tabs {
  margin-top: var(--spacing-5);
  border: 1px solid rgba(212, 175, 55, 0.3);
  background: rgba(212, 175, 55, 0.02);
}

.tabs-header {
  display: flex;
  border-bottom: 1px solid rgba(212, 175, 55, 0.3);
  background: rgba(212, 175, 55, 0.05);
}

.tab-btn {
  padding: var(--spacing-3) var(--spacing-5);
  background: transparent;
  border: none;
  border-right: 1px solid rgba(212, 175, 55, 0.2);
  color: var(--fg-muted);
  font-family: var(--font-display);
  font-size: var(--font-size-small);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  cursor: pointer;
  transition: all var(--transition-base);

  &:hover {
    color: var(--accent-gold);
    background: rgba(212, 175, 55, 0.05);
  }

  &.active {
    color: var(--bg-primary);
    background: var(--accent-gold);
  }
}

.tab-content {
  padding: var(--spacing-5);
}

  display: flex;
  align-items: center;
  justify-content: center;
  margin: var(--spacing-8) 0;
  flex-wrap: wrap;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.step-number {
  width: 48px;
  height: 48px;
  border: 2px solid var(--accent-gold);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: var(--font-size-h5);
  color: var(--accent-gold);
  margin-bottom: var(--spacing-3);
  background: transparent;
}

.step-content {
  max-width: 140px;
}

.step-title {
  font-family: var(--font-display);
  font-size: var(--font-size-small);
  color: var(--fg-primary);
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: var(--spacing-1);
}

.step-desc {
  font-family: var(--font-body);
  font-size: var(--font-size-xs);
  color: var(--fg-muted);
}

.step-connector {
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, var(--accent-gold), transparent);
  margin: 0 var(--spacing-4);
  margin-bottom: 40px;
}

  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-5);
}

.indicator-group {
  h5 {
    color: var(--accent-gold);
    border-bottom: 1px solid rgba(212, 175, 55, 0.3);
    padding-bottom: var(--spacing-2);
    margin-bottom: var(--spacing-3);
  }

  ul {
    margin: 0;
    padding-left: var(--spacing-5);

    li {
      font-size: var(--font-size-small);
    }
  }
}

.table {
  width: 100%;
  border-collapse: collapse;

  th {
    background: rgba(212, 175, 55, 0.1);
    color: var(--accent-gold);
    font-family: var(--font-display);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    padding: var(--spacing-3) var(--spacing-4);
    border-bottom: 2px solid var(--accent-gold);
    text-align: left;
  }

  td {
    padding: var(--spacing-3) var(--spacing-4);
    border-bottom: 1px solid rgba(212, 175, 55, 0.2);
    color: var(--fg-secondary);
  }

  tr:hover td {
    background: rgba(212, 175, 55, 0.03);
  }

  .metric-name {
    font-family: var(--font-mono);
    color: var(--accent-gold);
  }

  .metric-target {
    font-family: var(--font-mono);
    color: var(--color-up);
  }

  .param-name {
    font-family: var(--font-mono);
    font-size: var(--font-size-small);
    color: var(--accent-gold);
  }

  .method-badge {
    font-family: var(--font-mono);
    font-size: var(--font-size-xs);
    color: var(--accent-gold);
    background: rgba(212, 175, 55, 0.1);
    padding: 4px 8px;
    text-align: center;
  }

  .endpoint-path {
    font-family: var(--font-mono);
    font-size: var(--font-size-small);
    color: var(--fg-primary);
  }
}

  border-left: 2px solid rgba(212, 175, 55, 0.3);
  padding-left: var(--spacing-6);
}

.timeline-item {
  position: relative;
  padding-bottom: var(--spacing-6);

  &:last-child {
    padding-bottom: 0;
  }
}

.timeline-marker {
  position: absolute;
  left: calc(var(--spacing-6) * -1 - 11px);
  top: 0;
  width: 24px;
  height: 24px;
  background: var(--accent-gold);
  color: var(--bg-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: var(--font-size-xs);
  font-weight: 600;
}

.timeline-title {
  font-family: var(--font-display);
  font-size: var(--font-size-body);
  color: var(--fg-primary);
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: var(--spacing-2);
}

.timeline-desc {
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  color: var(--fg-muted);
  line-height: 1.6;
}

  padding: var(--spacing-4);
  border: 1px solid;

  .alert-title {
    font-family: var(--font-display);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    margin-bottom: var(--spacing-2);
  }
}

  background: rgba(74, 144, 226, 0.1);
  border-color: rgba(74, 144, 226, 0.4);

  .alert-title {
    color: #4A90E2;
  }
}

  background: rgba(230, 126, 34, 0.1);
  border-color: rgba(230, 126, 34, 0.4);

  .alert-title {
    color: #E67E22;
  }
}

  color: var(--accent-gold);
  text-decoration: none;
  border-bottom: 1px solid var(--accent-gold);

  &:hover {
    color: var(--accent-gold-light);
  }
}

.code-block {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 0;
  padding: var(--spacing-4);
  font-family: 'SF Mono', 'Fira Code', 'Courier New', monospace;
  font-size: var(--font-size-small);
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre;
  color: var(--fg-primary);
}

  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3) var(--spacing-5);
  font-family: var(--font-display);
  font-size: var(--font-size-small);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  border: 2px solid var(--accent-gold);
  border-radius: 0;
  cursor: pointer;
  transition: all var(--transition-base);
}

  background: var(--accent-gold);
  color: var(--bg-primary);

  &:hover {
    background: var(--accent-gold-light);
    box-shadow: var(--glow-medium);
  }
}

  background: transparent;
  color: var(--accent-gold);

  &:hover {
    background: rgba(212, 175, 55, 0.1);
    box-shadow: var(--glow-subtle);
  }
}

.tab-icon {
  font-size: 14px;
}

.tab-label {
  font-size: var(--font-size-small);
}

.badge {
  display: inline-block;
  padding: 4px 12px;
  font-family: var(--font-display);
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  border-radius: 0;
}

.badge-success {
  background: rgba(39, 174, 96, 0.15);
  color: #27AE60;
  border: 1px solid #27AE60;
}

.badge-warning {
  background: rgba(230, 126, 34, 0.15);
  color: #E67E22;
  border: 1px solid #E67E22;
}

.badge-info {
  background: rgba(74, 144, 226, 0.15);
  color: #4A90E2;
  border: 1px solid #4A90E2;
}

@media (max-width: 768px) {
  .freqtrade-demo {
    padding: var(--spacing-4);
  }

    grid-template-columns: 1fr;
  }

    grid-template-columns: 1fr;
  }

    flex-direction: column;
    gap: var(--spacing-4);
  }

  .step-connector {
    width: 2px;
    height: 30px;
    background: linear-gradient(180deg, var(--accent-gold), transparent);
    margin: 0;
  }

  .function-nav {
    flex-direction: column;

      width: 100%;
    }
  }
}
</style>
