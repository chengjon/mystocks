<template>
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

        <el-tabs type="border-card" class="strategy-tabs-offset">
          <el-tab-pane name="basic-strategy" label="基础策略示例">
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

          <el-tab-pane name="ml-strategy" label="机器学习策略">
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

          <el-tab-pane name="common-indicators" label="常用技术指标">
            <div class="strategy-indicators-panel">
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
          class="strategy-warning-alert"
        >
          <ul class="strategy-warning-list">
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
</template>

<script setup lang="ts">
defineProps<{ activeTab: string }>()
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.strategy-tabs-offset,
.strategy-warning-alert {
  margin-top: var(--artdeco-spacing-5);
}

.strategy-indicators-panel {
  padding: calc(var(--artdeco-spacing-5) - var(--artdeco-spacing-px) * 5);
}

.strategy-warning-list {
  margin-top: calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) * 2);
}
</style>
