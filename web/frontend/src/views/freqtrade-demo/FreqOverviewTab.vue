<template>
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
</template>

<script setup lang="ts">
defineProps<{ 
  activeTab: string;
  exchanges: string[];
}>()
</script>
