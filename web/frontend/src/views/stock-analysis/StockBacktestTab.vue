<template>
  <div v-show="activeTab === 'backtest'" class="backtest-tab-container">
    <ArtDecoHeader title="BACKTEST ENGINE">
      <template #actions>
        <el-tag type="warning" effect="dark" class="artdeco-tag">RQALPHA</el-tag>
      </template>
    </ArtDecoHeader>

    <div class="content-section" :style="{ padding: 'var(--artdeco-spacing-6)' }">
      <h3 class="section-title">🔧 BACKTEST FRAMEWORK: RQALPHA</h3>
      <p class="description">Stock-Analysis integrates RQAlpha for professional strategy backtesting:</p>

      <div class="artdeco-grid-2" style="margin-top: var(--artdeco-spacing-6);">
        <ArtDecoCard title="✨ RQAlpha Features" variant="bordered">
          <ul class="feature-list">
            <li>Event-driven engine</li>
            <li>Multiple order types</li>
            <li>Transaction cost simulation</li>
            <li>Performance analytics</li>
            <li>Visual reports</li>
          </ul>
        </ArtDecoCard>

        <ArtDecoCard title="📊 Supported Strategies" variant="bordered">
          <ul class="feature-list">
            <li>Daily frequency</li>
            <li>Minute frequency</li>
            <li>Event-driven</li>
            <li>Multi-symbol</li>
            <li>Future/Options</li>
          </ul>
        </ArtDecoCard>
      </div>

      <h3 class="section-title" style="margin-top: var(--artdeco-spacing-8);">💻 CODE EXAMPLES</h3>
      <el-tabs type="border-card" class="artdeco-tabs" style="margin-top: var(--artdeco-spacing-4);">
        <el-tab-pane label="SIMPLE STRATEGY" name="simple">
          <textarea readonly class="code-block">
from rqalpha.api import *

def init(context):
    """Strategy Initialization"""
    context.stock = "000001.XSHE"
    context.ma_short = 5
    context.ma_long = 20

def handle_bar(context, bar_dict):
    """Bar Handler"""
    prices = history_bars(context.stock, context.ma_long + 1, '1d', 'close')
    ma_short = prices[-context.ma_short:].mean()
    ma_long = prices[-context.ma_long:].mean()
    position = context.portfolio.positions[context.stock]

    if ma_short > ma_long and position.quantity == 0:
        order_target_percent(context.stock, 0.95)
    elif ma_short < ma_long and position.quantity > 0:
        order_target_percent(context.stock, 0)</textarea>
        </el-tab-pane>

        <el-tab-pane label="MULTI-STOCK" name="multi">
          <textarea readonly class="code-block">
from rqalpha.api import *

def init(context):
    context.stocks = ["000001.XSHE", "600000.XSHG", "600036.XSHG"]

def handle_bar(context, bar_dict):
    # Rotation logic here
    pass</textarea>
        </el-tab-pane>

        <el-tab-pane label="RUNNING" name="run">
          <textarea readonly class="code-block">
# CLI command
rqalpha run \
    -f strategy.py \
    -s 2020-01-01 \
    -e 2021-12-31 \
    --stock-starting-cash 100000 \
    --frequency 1d</textarea>
        </el-tab-pane>
      </el-tabs>

      <h3 class="section-title" style="margin-top: var(--artdeco-spacing-8);">📊 PERFORMANCE METRICS</h3>
      <ArtDecoCard class="metrics-summary-card" variant="bordered">
        <el-table :data="backtestMetrics" stripe class="artdeco-table">
          <el-table-column prop="metric" label="METRIC" width="200" />
          <el-table-column prop="description" label="DESCRIPTION" />
        </el-table>
      </ArtDecoCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import ArtDecoHeader from '@/components/artdeco/core/ArtDecoHeader.vue'
import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'

interface BacktestMetricItem {
  metric: string
  description: string
}

defineProps<{
  activeTab: string
  backtestMetrics: BacktestMetricItem[]
}>()
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.backtest-tab-container {
  background: var(--artdeco-bg-base);
  min-height: 100%;
}

.section-title {
  font-family: var(--font-display);
  color: var(--artdeco-gold-primary);
  letter-spacing: var(--artdeco-tracking-wider);
  text-transform: uppercase;
}

.description {
  color: var(--artdeco-fg-muted);
  margin-top: var(--artdeco-spacing-2);
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
  li {
    color: var(--artdeco-fg-primary);
    padding: var(--artdeco-spacing-1) 0;
    &::before {
      content: '⚡';
      margin-right: var(--artdeco-spacing-2);
      color: var(--artdeco-gold-primary);
    }
  }
}

.code-block {
  width: 100%;
  height: 200px;
  background: #1e1e1e;
  color: #d4d4d4;
  font-family: var(--font-mono);
  padding: var(--artdeco-spacing-4);
  border: none;
  resize: none;
}

.metrics-summary-card {
  margin-top: var(--artdeco-spacing-4);
  @include artdeco-stepped-corners(16px);
  border: 2px solid var(--artdeco-border-default) !important;
}

.artdeco-tabs {
  background: transparent !important;
  border: 1px solid var(--artdeco-border-default) !important;
}
</style>
