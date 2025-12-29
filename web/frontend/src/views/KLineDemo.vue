<template>
  <div class="kline-demo-page">
    <div class="page-header">
      <h1 class="page-title">K线图表演示</h1>
      <p class="page-subtitle">Phase 3 - Art Deco 风格 K线图表组件</p>
    </div>

    <div class="chart-wrapper">
      <ProKLineChart
        initial-symbol="000001.SZ"
        initial-interval="1d"
      />
    </div>

    <div class="feature-list">
      <div class="feature-item">
        <div class="feature-icon">📊</div>
        <div class="feature-content">
          <h3>Art Deco 风格</h3>
          <p>深色主题 + 金色点缀，专业的金融终端美学</p>
        </div>
      </div>
      <div class="feature-item">
        <div class="feature-icon">📈</div>
        <div class="feature-content">
          <h3>多周期切换</h3>
          <p>支持 1分/5分/15分/1小时/日/周/月 周期</p>
        </div>
      </div>
      <div class="feature-item">
        <div class="feature-icon">🔄</div>
        <div class="feature-content">
          <h3>复权模式</h3>
          <p>支持前复权/后复权/不复权 切换</p>
        </div>
      </div>
      <div class="feature-item">
        <div class="feature-icon">📉</div>
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

<style scoped>
.kline-demo-page {
  padding: 24px;
  min-height: 100vh;
  background: #0A0A0A;
}

.page-header {
  margin-bottom: 24px;
  text-align: center;
}

.page-title {
  font-family: 'Marcellus', serif;
  font-size: 32px;
  color: #D4AF37;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-family: 'Josefin Sans', sans-serif;
  font-size: 14px;
  color: #888888;
  margin: 0;
}

.chart-wrapper {
  height: 600px;
  border: 1px solid rgba(212, 175, 55, 0.3);
  background: #141414;
  margin-bottom: 32px;
}

.feature-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: #141414;
  border: 1px solid rgba(212, 175, 55, 0.2);
}

.feature-icon {
  font-size: 24px;
}

.feature-content h3 {
  font-family: 'Marcellus', serif;
  font-size: 16px;
  color: #D4AF37;
  margin: 0 0 4px 0;
}

.feature-content p {
  font-family: 'Josefin Sans', sans-serif;
  font-size: 13px;
  color: #888888;
  margin: 0;
}
</style>
