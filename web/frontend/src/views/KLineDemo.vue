<template>
  <div class="kline-demo-page">
    <div class="page-header">
      <h1 class="page-title">K线图表演示</h1>
      <p class="page-subtitle">K-LINE CHART DEMO | ART DECO STYLE</p>
      <div class="decorative-line"></div>
    </div>

    <div class="card chart-card">
      <div class="chart-wrapper">
        <ProKLineChart
          initial-symbol="000001.SZ"
          initial-interval="1d"
        />
      </div>
    </div>

    <div class="feature-grid">
      <div class="card feature-card">
        <div class="feature-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="3" y1="9" x2="21" y2="9"></line>
            <line x1="9" y1="21" x2="9" y2="9"></line>
          </svg>
        </div>
        <div class="feature-content">
          <h3>Art Deco 风格</h3>
          <p>深色主题 + 金色点缀，专业的金融终端美学</p>
        </div>
      </div>

      <div class="card feature-card">
        <div class="feature-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
            <polyline points="22,12 18,12 15,21 9,3 6,12 2,12"></polyline>
          </svg>
        </div>
        <div class="feature-content">
          <h3>多周期切换</h3>
          <p>支持 1分/5分/15分/1小时/日/周/月 周期</p>
        </div>
      </div>

      <div class="card feature-card">
        <div class="feature-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
          </svg>
        </div>
        <div class="feature-content">
          <h3>复权模式</h3>
          <p>支持前复权/后复权/不复权 切换</p>
        </div>
      </div>

      <div class="card feature-card">
        <div class="feature-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
            <line x1="12" y1="20" x2="12" y2="10"></line>
            <line x1="18" y1="20" x2="18" y2="4"></line>
            <line x1="6" y1="20" x2="6" y2="16"></line>
          </svg>
        </div>
        <div class="feature-content">
          <h3>涨跌停显示</h3>
          <p>实时计算并显示涨跌停价格线</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ProKLineChart from '@/components/Charts/ProKLineChart.vue';
</script>

<style scoped lang="scss">

.kline-demo-page {
  padding: 20px;
  min-height: 100vh;
  background: var(--bg-primary);
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 30px 0;
  position: relative;

  .page-title {
    font-family: var(--font-display);
    font-size: 32px;
    font-weight: 700;
    color: var(--gold-primary);
    text-transform: uppercase;
    letter-spacing: 4px;
    margin: 0 0 8px 0;
  }

  .page-subtitle {
    font-family: var(--font-body);
    font-size: 12px;
    color: var(--gold-muted);
    letter-spacing: 6px;
    text-transform: uppercase;
    margin: 0;
  }

  .decorative-line {
    width: 200px;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold-primary), transparent);
    margin: 20px auto 0;

    &::before {
      content: '';
      position: absolute;
      bottom: -6px;
      left: 50%;
      transform: translateX(-50%);
      width: 60px;
      height: 1px;
      background: linear-gradient(90deg, transparent, var(--gold-muted), transparent);
    }
  }
}

.card {
  background: var(--bg-secondary);
  border: 1px solid var(--gold-dim);
  position: relative;
  border-radius: 0;

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 16px;
    height: 16px;
    border: 2px solid var(--gold-primary);
  }

  &::before {
    top: 12px;
    left: 12px;
    border-right: none;
    border-bottom: none;
  }

  &::after {
    bottom: 12px;
    right: 12px;
    border-left: none;
    border-top: none;
  }

  &:hover {
    border-color: var(--gold-primary);
    box-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
  }
}

.chart-card {
  margin-bottom: 30px;

  .chart-wrapper {
    height: 600px;
    background: var(--bg-primary);
    padding: 20px;
  }
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.feature-card {
  padding: 24px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-4px);
  }

  .feature-icon {
    width: 56px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(212, 175, 55, 0.1);
    border: 1px solid var(--gold-dim);
    flex-shrink: 0;
  }

  .feature-content {
    flex: 1;

    h3 {
      font-family: var(--font-display);
      font-size: 16px;
      color: var(--gold-primary);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin: 0 0 8px 0;
      font-weight: 600;
    }

    p {
      font-family: var(--font-body);
      font-size: 13px;
      color: var(--text-muted);
      line-height: 1.6;
      margin: 0;
    }
  }
}

@media (max-width: 768px) {
  .kline-demo-page {
    padding: 10px;
  }

  .page-header {
    padding: 20px 0;

    .page-title {
      font-size: 24px;
      letter-spacing: 2px;
    }

    .page-subtitle {
      font-size: 10px;
      letter-spacing: 3px;
    }
  }

  .chart-card .chart-wrapper {
    height: 400px;
    padding: 10px;
  }

  .feature-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .feature-card {
    padding: 16px;

    .feature-icon {
      width: 48px;
      height: 48px;
    }
  }
}
</style>
