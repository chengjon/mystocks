<template>
    <ArtDecoCard v-show="activeTab === 'strategy'" class="monolithic-strategy-card" variant="bordered">
      <template #header>
        <ArtDecoHeader 
          title="股票筛选策略" 
          subtitle="STOCK SCREENING STRATEGIES" 
          showStatus 
          statusText="文档" 
        />
      </template>

      <div class="content-section">
        <section class="strategy-intro">
          <ArtDecoHeader title="常用筛选策略" subtitle="COMMON SCREENING STRATEGIES" />
          <p class="description">以下是一些经典的股票筛选策略示例, 旨在为量化分析提供参考思路:</p>
        </section>

        <div class="artdeco-grid-4 strategy-grid">
          <!-- 1. Bullish Alignment -->
          <ArtDecoCard class="strategy-item-card" :hoverable="true">
            <template #header>
              <h3 class="strategy-name">1️⃣ 均线多头排列</h3>
            </template>
            <div class="strategy-info">
              <p class="strategy-desc">寻找 MA5 > MA10 > MA20 > MA60 的股票, 表示短期、中期、长期趋势向上</p>
              <textarea readonly class="mini-code-block">
import talib as ta
def filter_ma_bullish(df):
    df['ma5'] = ta.SMA(df['close'], 5)
    df['ma10'] = ta.SMA(df['close'], 10)
    df['ma20'] = ta.SMA(df['close'], 20)
    df['ma60'] = ta.SMA(df['close'], 60)
    condition = (df['ma5'] > df['ma10']) & (df['ma10'] > df['ma20']) & (df['ma20'] > df['ma60'])
    return df[condition]</textarea>
            </div>
          </ArtDecoCard>

          <!-- 2. MACD Golden Cross -->
          <ArtDecoCard class="strategy-item-card" :hoverable="true">
            <template #header>
              <h3 class="strategy-name">2️⃣ MACD 金叉</h3>
            </template>
            <div class="strategy-info">
              <p class="strategy-desc">MACD 快线上穿慢线, 且 MACD 柱状图由负转正, 通常是买入信号</p>
              <textarea readonly class="mini-code-block">
def filter_macd_golden_cross(df):
    macd, signal, hist = ta.MACD(df['close'], 12, 26, 9)
    df['macd'], df['signal'], df['hist'] = macd, signal, hist
    condition = (df['macd'] > df['signal']) & (df['macd'].shift(1) <= df['signal'].shift(1)) & (df['hist'] > 0)
    return df[condition]</textarea>
            </div>
          </ArtDecoCard>

          <!-- 3. Volume Breakout -->
          <ArtDecoCard class="strategy-item-card" :hoverable="true">
            <template #header>
              <h3 class="strategy-name">3️⃣ 放量突破</h3>
            </template>
            <div class="strategy-info">
              <p class="strategy-desc">价格突破前期高点, 同时成交量放大, 表示有资金介入</p>
              <textarea readonly class="mini-code-block">
def filter_breakout_with_volume(df, lookback=20, vol_ratio=1.5):
    df['high_n'] = df['high'].rolling(lookback).max().shift(1)
    df['vol_ma'] = df['volume'].rolling(lookback).mean()
    condition = (df['close'] > df['high_n']) & (df['volume'] > df['vol_ma'] * vol_ratio)
    return df[condition]</textarea>
            </div>
          </ArtDecoCard>

          <!-- 4. RSI Oversold -->
          <ArtDecoCard class="strategy-item-card" :hoverable="true">
            <template #header>
              <h3 class="strategy-name">4️⃣ RSI 超卖反弹</h3>
            </template>
            <div class="strategy-info">
              <p class="strategy-desc">RSI 指标从超卖区域回升, 可能是反弹信号</p>
              <textarea readonly class="mini-code-block">
def filter_rsi_oversold(df, period=14, oversold=30):
    df['rsi'] = ta.RSI(df['close'], timeperiod=period)
    condition = (df['rsi'].shift(1) < oversold) & (df['rsi'] > oversold) & (df['rsi'] > df['rsi'].shift(1))
    return df[condition]</textarea>
            </div>
          </ArtDecoCard>

          <!-- 5. Bottom Volume (Expanded to grid) -->
          <ArtDecoCard class="strategy-item-card" :hoverable="true">
            <template #header>
              <h3 class="strategy-name">5️⃣ 底部放量</h3>
            </template>
            <div class="strategy-info">
              <p class="strategy-desc">股价处于低位, 成交量突然放大, 可能是主力建仓信号</p>
              <textarea readonly class="mini-code-block">
def filter_bottom_volume(df, lookback=60):
    df['low_60'] = df['low'].rolling(lookback).min()
    df['price_pos'] = (df['close'] - df['low_60']) / (df['high'].rolling(lookback).max() - df['low_60'])
    df['vol_ratio'] = df['volume'].rolling(5).mean() / df['volume'].rolling(20).mean()
    condition = (df['price_pos'] < 0.3) & (df['vol_ratio'] > 1.5)
    return df[condition]</textarea>
            </div>
          </ArtDecoCard>
        </div>

        <section class="composite-strategy" style="margin-top: var(--artdeco-spacing-8);">
          <ArtDecoHeader title="组合筛选示例" subtitle="COMPOSITE SCREENING EXAMPLE" />
          <textarea readonly class="code-block" style="margin-top: var(--artdeco-spacing-4);">
def comprehensive_filter(stock_code):
    """
    综合筛选策略:
    1. 均线多头排列
    2. MACD 金叉
    3. RSI 不超买 (< 70)
    4. 成交量放大
    """
    df = load_stock_data(stock_code)
    # ... 计算逻辑 ...
    condition = (
        (df['ma5'] > df['ma10']) &
        (df['ma10'] > df['ma20']) &
        (df['macd'] > df['signal']) &
        (df['rsi'] < 70) &
        (df['volume'] > df['vol_ma'] * 1.2)
    )
    return df[condition].iloc[-1] if condition.any() else None</textarea>
        </section>
      </div>
    </ArtDecoCard>
</template>

<script setup lang="ts">
import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
import ArtDecoHeader from '@/components/artdeco/core/ArtDecoHeader.vue'

defineProps<{
  activeTab: string
}>()
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';
@import '@/styles/artdeco-grid';

.monolithic-strategy-card {
  border-color: var(--artdeco-border-default); // 30% transparency by token
}

.content-section {
  padding: var(--artdeco-spacing-4);
}

.description {
  margin-bottom: var(--artdeco-spacing-6);
  color: var(--artdeco-fg-muted);
  font-family: var(--font-body);
}

.strategy-grid {
  margin-top: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-8);
}

.strategy-item-card {
  @include artdeco-stepped-corners($size: 12px);

  display: flex;
  flex-direction: column;
  height: 100%;
  background: #141414;
  border: 1px solid var(--artdeco-border-default);

  &:hover {
    border-color: var(--artdeco-gold-primary);
  }
}

.strategy-name {
  margin: 0;
  color: var(--artdeco-gold-primary);
  font-family: Marcellus, serif;
  font-size: var(--artdeco-text-lg);
  letter-spacing: normal;
  text-transform: none; // Reset uppercase from global h3
}

.strategy-info {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-3);
  height: 100%;
}

.strategy-desc {
  flex-grow: 1;
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-family: 'Josefin Sans', sans-serif;
  font-size: var(--artdeco-text-sm);
  line-height: 1.5;
}

.mini-code-block {
  width: 100%;
  height: 120px;
  padding: var(--artdeco-spacing-2);
  outline: none;
  background-color: #050505;
  color: var(--artdeco-gold-dim);
  border: 1px solid rgb(212 175 55 / 10%);
  font-family: var(--font-mono);
  font-size: 11px;
  line-height: 1.3;
  resize: none;
}

.code-block {
  width: 100%;
  height: 400px;
  background-color: #050505;
  color: #D4AF37;
  border: 1px solid var(--artdeco-border-default);
  padding: var(--artdeco-spacing-4);
  font-family: var(--font-mono);
  font-size: var(--artdeco-text-sm);
  line-height: 1.5;
  resize: vertical;
  outline: none;
}
</style>

