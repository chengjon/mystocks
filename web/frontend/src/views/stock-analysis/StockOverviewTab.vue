<template>
  <ArtDecoCard v-show="activeTab === 'overview'" class="monolithic-overview-card" variant="bordered">
    <template #header>
      <ArtDecoHeader title="PROJECT OVERVIEW" class="overview-header">
        <template #actions>
          <ArtDecoBadge type="success">MIGRATED</ArtDecoBadge>
        </template>
      </ArtDecoHeader>
    </template>

    <div class="content-section">
      <h3 class="artdeco-sub-header">INTRODUCTION</h3>
      <p class="artdeco-body-text">Stock-Analysis is a Chinese A-share stock screening and backtesting system based on Tongdaxin data. It leverages Tongdaxin's powerful local data advantages combined with Python flexibility to provide efficient stock screening strategies and complete backtesting framework.</p>

      <h3 class="artdeco-sub-header" style="margin-top: var(--artdeco-spacing-8);">CORE FEATURES</h3>
      <div class="artdeco-grid-4 features-grid">
        <ArtDecoCard hoverable title="TONGDAXIN DATA PARSING" class="feature-item">
          <ul class="artdeco-list">
            <li>Parse Tongdaxin .day/.lc1/.lc5 binary files</li>
            <li>Support daily, minute, 5-minute data</li>
            <li>Auto-identify stock codes and markets</li>
            <li>Efficient data caching mechanism</li>
            <li>Historical and real-time data support</li>
          </ul>
        </ArtDecoCard>

        <ArtDecoCard hoverable title="STOCK SCREENING STRATEGIES" class="feature-item">
          <ul class="artdeco-list">
            <li>Technical Indicator Screening (MA, MACD, RSI, KDJ)</li>
            <li>Pattern Recognition (Breakthrough, Golden Cross, Bottom)</li>
            <li>Volume-Price Analysis (Volume, Volume Ratio)</li>
            <li>Fundamental Screening (PE, PB, Net Profit)</li>
            <li>Custom Combined Conditions</li>
          </ul>
        </ArtDecoCard>

        <ArtDecoCard hoverable title="BACKTESTING" class="feature-item">
          <ul class="artdeco-list">
            <li>Integrated rqalpha backtesting engine</li>
            <li>Multi-strategy parallel backtesting</li>
            <li>Complete trading records and analysis</li>
            <li>Capital curve and drawdown analysis</li>
            <li>Sharpe ratio and performance metrics</li>
          </ul>
        </ArtDecoCard>

        <ArtDecoCard hoverable title="REAL-TIME & AFTER-HOURS" class="feature-item">
          <ul class="artdeco-list">
            <li>Intraday real-time data updates</li>
            <li>After-hours automatic screening</li>
            <li>Email/WeChat notification push</li>
            <li>Custom screening time</li>
            <li>Historical screening results save</li>
          </ul>
        </ArtDecoCard>
      </div>

      <h3 class="artdeco-sub-header" style="margin-top: var(--artdeco-spacing-8);">TECHNICAL ARCHITECTURE</h3>
      <div class="architecture-details">
        <el-descriptions :column="2" border class="descriptions artdeco-descriptions">
          <el-descriptions-item label="DATA SOURCE">Tongdaxin Local Data (.day/.lc1/.lc5)</el-descriptions-item>
          <el-descriptions-item label="DATA PARSING">struct Binary Parsing</el-descriptions-item>
          <el-descriptions-item label="STRATEGY LANGUAGE">Python 3.x</el-descriptions-item>
          <el-descriptions-item label="BACKTEST ENGINE">rqalpha</el-descriptions-item>
          <el-descriptions-item label="TECHNICAL INDICATORS">TA-Lib</el-descriptions-item>
          <el-descriptions-item label="DATA STORAGE">SQLite / PostgreSQL</el-descriptions-item>
        </el-descriptions>
      </div>

      <h3 class="artdeco-sub-header" style="margin-top: var(--artdeco-spacing-8);">REPOSITORY</h3>
      <p class="artdeco-body-text">This project is a functional demonstration. The complete source code is available in the <code>stock-analysis/</code> directory.</p>

      <ArtDecoAlert
        type="success"
        message=""
        style="margin-top: var(--artdeco-spacing-6);"
        :dismissible="false"
        class="advantage-alert"
      >
        <template #title>
          <div class="alert-title">💡 项目优势</div>
        </template>
        <ul class="artdeco-list advantage-list">
          <li><strong>数据本地化</strong>: 使用通达信本地数据,无需网络,速度快</li>
          <li><strong>数据全面性</strong>: 覆盖所有 A 股历史数据,包括分钟级</li>
          <li><strong>策略灵活性</strong>: 支持复杂的自定义筛选条件</li>
          <li><strong>回测可靠性</strong>: 基于真实历史数据,避免未来函数</li>
          <li><strong>实时性</strong>: 支持盘中实时监控和筛选</li>
        </ul>
      </ArtDecoAlert>
    </div>
  </ArtDecoCard>
</template>

<script setup lang="ts">
import { 
  ArtDecoCard, 
  ArtDecoHeader,
  ArtDecoBadge,
  ArtDecoAlert 
} from '@/components/artdeco'

defineProps<{
  activeTab: string
}>()
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';
@import '@/styles/artdeco-grid';

.monolithic-overview-card {
  margin-bottom: var(--artdeco-spacing-8);
}

.overview-header {
  :deep(.header-title) {
    font-family: Cinzel, serif;
  }
}

.artdeco-sub-header {
  font-family: Marcellus, serif;
  color: var(--artdeco-gold-primary);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wider);
  margin-bottom: var(--artdeco-spacing-4);
  border-left: 3px solid var(--artdeco-gold-primary);
  padding-left: var(--artdeco-spacing-3);
}

.artdeco-body-text {
  font-family: var(--font-body);
  color: var(--artdeco-fg-primary);
  line-height: var(--artdeco-leading-relaxed);
  font-size: var(--artdeco-text-base);
}

.features-grid {
  margin-top: var(--artdeco-spacing-4);
}

.feature-item {
  height: 100%;
  
  :deep(.artdeco-card__header h3) {
    font-size: var(--artdeco-text-sm);
    color: var(--artdeco-gold-light);
  }
}

.artdeco-list {
  list-style: none;
  padding-left: 0;
  margin: 0;

  li {
    position: relative;
    padding-left: var(--artdeco-spacing-5);
    margin-bottom: var(--artdeco-spacing-2);
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-sm);
    line-height: var(--artdeco-leading-normal);

    &::before {
      content: '◆';
      position: absolute;
      left: 0;
      color: var(--artdeco-gold-primary);
      font-size: 0.6rem;
      top: 0.2rem;
    }
  }
}

.artdeco-descriptions {
  background: var(--artdeco-bg-base);
  border-color: var(--artdeco-border-default) !important;
  
  :deep(.el-descriptions__label) {
    background: var(--artdeco-bg-elevated) !important;
    color: var(--artdeco-gold-primary) !important;
    font-family: var(--font-mono);
    text-transform: uppercase;
    font-size: var(--artdeco-text-xs);
  }

  :deep(.el-descriptions__content) {
    color: var(--artdeco-fg-primary);
    background: var(--artdeco-bg-base);
  }
}

.advantage-alert {
  background: rgb(212 175 55 / 5%) !important;
  border-color: var(--artdeco-border-default) !important;
  
  .alert-title {
    color: var(--artdeco-gold-primary);
    font-family: Marcellus, serif;
    font-weight: bold;
    margin-bottom: var(--artdeco-spacing-2);
  }
}

.advantage-list {
  li {
    color: var(--artdeco-fg-primary);
    
    strong {
      color: var(--artdeco-gold-light);
    }
  }
}
</style>
