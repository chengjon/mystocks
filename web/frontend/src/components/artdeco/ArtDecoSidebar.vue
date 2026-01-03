<template>
  <nav class="artdeco-sidebar">
    <div class="artdeco-sidebar-header">
      <router-link to="/artdeco/dashboard" class="artdeco-logo">MYSTOCKS</router-link>
    </div>

    <div class="artdeco-nav">
      <div class="artdeco-nav-section">
        <div class="artdeco-nav-section-title">市场数据</div>
        <router-link to="/artdeco/dashboard" class="artdeco-nav-item" active-class="active">
          <span>Ⅰ</span>
          <span>主控仪表盘</span>
        </router-link>
        <router-link to="/artdeco/market-center" class="artdeco-nav-item" active-class="active">
          <span>Ⅱ</span>
          <span>市场行情中心</span>
        </router-link>
        <router-link to="/artdeco/stock-screener" class="artdeco-nav-item" active-class="active">
          <span>Ⅲ</span>
          <span>智能选股池</span>
        </router-link>
      </div>

      <div class="artdeco-nav-section">
        <div class="artdeco-nav-section-title">分析工具</div>
        <router-link to="/artdeco/data-analysis" class="artdeco-nav-item" active-class="active">
          <span>Ⅳ</span>
          <span>数据分析</span>
        </router-link>
        <router-link to="/artdeco/strategy-lab" class="artdeco-nav-item" active-class="active">
          <span>Ⅴ</span>
          <span>策略实验室</span>
        </router-link>
        <router-link to="/artdeco/backtest-arena" class="artdeco-nav-item" active-class="active">
          <span>Ⅵ</span>
          <span>回测竞技场</span>
        </router-link>
      </div>

      <div class="artdeco-nav-section">
        <div class="artdeco-nav-section-title">交易管理</div>
        <router-link to="/artdeco/trade-station" class="artdeco-nav-item" active-class="active">
          <span>Ⅵ</span>
          <span>交易工作站</span>
        </router-link>
        <router-link to="/artdeco/risk-center" class="artdeco-nav-item" active-class="active">
          <span>Ⅷ</span>
          <span>风控中心</span>
        </router-link>
      </div>

      <div class="artdeco-nav-section">
        <div class="artdeco-nav-section-title">系统</div>
        <router-link to="/artdeco/system-settings" class="artdeco-nav-item" active-class="active">
          <span>Ⅸ</span>
          <span>系统设置</span>
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
</script>

<style scoped>
@import '@/styles/artdeco/artdeco-theme.css';

.artdeco-sidebar {
  width: 240px;
  background: var(--artdeco-bg-header);
  border-right: 1px solid var(--artdeco-gold-dim);
  position: fixed;
  height: 100vh;
  overflow-y: auto;
  z-index: var(--artdeco-z-fixed);
  transition: transform var(--artdeco-transition-base);
}

.artdeco-sidebar-header {
  padding: var(--artdeco-space-lg);
  border-bottom: 1px solid var(--artdeco-gold-dim);
  text-align: center;
}

.artdeco-logo {
  font-family: var(--artdeco-font-display);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--artdeco-gold-primary);
  letter-spacing: 4px;
  text-decoration: none;
}

.artdeco-nav {
  padding: var(--artdeco-space-md);
}

.artdeco-nav-section {
  margin-bottom: var(--artdeco-space-lg);
}

.artdeco-nav-section-title {
  font-family: var(--artdeco-font-display);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--artdeco-silver-muted);
  text-transform: uppercase;
  letter-spacing: 2px;
  padding: var(--artdeco-space-sm) var(--artdeco-space-md);
  margin-bottom: var(--artdeco-space-sm);
}

.artdeco-nav-item {
  display: flex;
  align-items: center;
  gap: var(--artdeco-space-md);
  padding: 12px var(--artdeco-space-md);
  color: var(--artdeco-silver-dim);
  text-decoration: none;
  border-left: 3px solid transparent;
  transition: all var(--artdeco-transition-fast);
  font-size: 0.875rem;
}

.artdeco-nav-item:hover {
  background: var(--artdeco-bg-hover);
  color: var(--artdeco-silver-text);
}

.artdeco-nav-item.active {
  background: var(--artdeco-gold-dim);
  border-left-color: var(--artdeco-gold-primary);
  color: var(--artdeco-gold-primary);
}

@media (max-width: 768px) {
  .artdeco-sidebar {
    transform: translateX(-100%);
  }

  .artdeco-sidebar.mobile-open {
    transform: translateX(0);
  }
}
</style>
