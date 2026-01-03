<template>
  <nav class="artdeco-sidebar">
    <div class="artdeco-sidebar-header">
      <!-- Decorative corner ornaments -->
      <div class="artdeco-corner-tl"></div>
      <div class="artdeco-corner-tr"></div>

      <router-link to="/artdeco/dashboard" class="artdeco-logo">
        <span class="artdeco-logo-text">MYSTOCKS</span>
      </router-link>

      <!-- Decorative divider line -->
      <div class="artdeco-header-divider"></div>
    </div>

    <div class="artdeco-nav">
      <div class="artdeco-nav-section">
        <div class="artdeco-nav-section-title">市场数据</div>
        <router-link to="/artdeco/dashboard" class="artdeco-nav-item" active-class="active">
          <span class="artdeco-nav-icon">Ⅰ</span>
          <span class="artdeco-nav-text">主控仪表盘</span>
        </router-link>
        <router-link to="/artdeco/market-center" class="artdeco-nav-item" active-class="active">
          <span class="artdeco-nav-icon">Ⅱ</span>
          <span class="artdeco-nav-text">市场行情中心</span>
        </router-link>
        <router-link to="/artdeco/stock-screener" class="artdeco-nav-item" active-class="active">
          <span class="artdeco-nav-icon">Ⅲ</span>
          <span class="artdeco-nav-text">智能选股池</span>
        </router-link>
      </div>

      <div class="artdeco-nav-section">
        <div class="artdeco-nav-section-title">分析工具</div>
        <router-link to="/artdeco/data-analysis" class="artdeco-nav-item" active-class="active">
          <span class="artdeco-nav-icon">Ⅳ</span>
          <span class="artdeco-nav-text">数据分析</span>
        </router-link>
        <router-link to="/artdeco/strategy-lab" class="artdeco-nav-item" active-class="active">
          <span class="artdeco-nav-icon">Ⅴ</span>
          <span class="artdeco-nav-text">策略实验室</span>
        </router-link>
        <router-link to="/artdeco/backtest-arena" class="artdeco-nav-item" active-class="active">
          <span class="artdeco-nav-icon">Ⅵ</span>
          <span class="artdeco-nav-text">回测竞技场</span>
        </router-link>
      </div>

      <div class="artdeco-nav-section">
        <div class="artdeco-nav-section-title">交易管理</div>
        <router-link to="/artdeco/trade-station" class="artdeco-nav-item" active-class="active">
          <span class="artdeco-nav-icon">Ⅶ</span>
          <span class="artdeco-nav-text">交易工作站</span>
        </router-link>
        <router-link to="/artdeco/risk-center" class="artdeco-nav-item" active-class="active">
          <span class="artdeco-nav-icon">Ⅷ</span>
          <span class="artdeco-nav-text">风控中心</span>
        </router-link>
      </div>

      <div class="artdeco-nav-section">
        <div class="artdeco-nav-section-title">系统</div>
        <router-link to="/artdeco/system-settings" class="artdeco-nav-item" active-class="active">
          <span class="artdeco-nav-icon">Ⅸ</span>
          <span class="artdeco-nav-text">系统设置</span>
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
  width: 260px; /* Increased from 240px */
  background: var(--artdeco-bg-header); /* Obsidian Black */
  border-right: 2px solid var(--artdeco-gold-dim); /* Thicker border */
  position: fixed;
  height: 100vh;
  overflow-y: auto;
  z-index: var(--artdeco-z-fixed);
  transition: transform var(--artdeco-transition-slow); /* Theatrical 500ms */
}

.artdeco-sidebar-header {
  padding: var(--artdeco-space-xl) var(--artdeco-space-lg);
  border-bottom: 2px solid var(--artdeco-gold-dim);
  text-align: center;
  position: relative;
}

.artdeco-logo {
  display: inline-block;
  text-decoration: none;
  position: relative;
  z-index: 1;
}

.artdeco-logo-text {
  font-family: var(--artdeco-font-display); /* Marcellus/Italiana */
  font-size: 1.75rem; /* Increased from 1.5rem */
  font-weight: 700;
  color: var(--artdeco-gold-primary);
  letter-spacing: 6px; /* Wide tracking - Art Deco style */
  text-transform: uppercase;
  display: block;
  transition: all var(--artdeco-transition-slow);
}

.artdeco-logo:hover .artdeco-logo-text {
  color: var(--artdeco-gold-hover);
  text-shadow: var(--artdeco-glow-subtle);
}

/* Decorative divider line under logo */
.artdeco-header-divider {
  height: 1px;
  background: linear-gradient(
    to right,
    transparent,
    var(--artdeco-gold-primary) 50%,
    transparent
  );
  margin: var(--artdeco-space-md) auto 0;
  opacity: 0.5;
}

.artdeco-nav {
  padding: var(--artdeco-space-lg);
}

.artdeco-nav-section {
  margin-bottom: var(--artdeco-space-xl); /* Increased spacing */
}

.artdeco-nav-section-title {
  font-family: var(--artdeco-font-display);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--artdeco-text-dim); /* Pewter */
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-display); /* 0.2em - Wide tracking */
  padding: var(--artdeco-space-sm) var(--artdeco-space-md);
  margin-bottom: var(--artdeco-space-md);
  border-bottom: 1px solid var(--artdeco-gold-dim);
  position: relative;
}

.artdeco-nav-item {
  display: flex;
  align-items: center;
  gap: var(--artdeco-space-md);
  padding: 14px var(--artdeco-space-md); /* Increased padding */
  color: var(--artdeco-text-dim);
  text-decoration: none;
  border-left: 3px solid transparent;
  transition: all var(--artdeco-transition-slow); /* Theatrical timing */
  font-size: 0.875rem;
  position: relative;
  margin-bottom: var(--artdeco-space-xs);
}

.artdeco-nav-icon {
  font-family: var(--artdeco-font-display);
  font-size: 1.125rem; /* Larger roman numerals */
  font-weight: 700;
  color: var(--artdeco-gold-primary);
  min-width: 24px;
  text-align: center;
  transition: all var(--artdeco-transition-slow);
}

.artdeco-nav-text {
  flex: 1;
  font-family: var(--artdeco-font-body); /* Josefin Sans */
  font-weight: 500;
  letter-spacing: var(--artdeco-tracking-body);
  transition: all var(--artdeco-transition-slow);
}

/* Hover State - Theatrical */
.artdeco-nav-item:hover {
  background: var(--artdeco-bg-hover);
  color: var(--artdeco-text-primary); /* Champagne Cream */
  border-left-color: var(--artdeco-gold-primary);
  padding-left: calc(var(--artdeco-space-md) + 4px); /* Subtle shift */
}

.artdeco-nav-item:hover .artdeco-nav-icon {
  color: var(--artdeco-gold-hover);
  transform: scale(1.1); /* Slight scale increase */
}

/* Active State */
.artdeco-nav-item.active {
  background: var(--artdeco-gold-dim);
  border-left-color: var(--artdeco-gold-primary);
  color: var(--artdeco-gold-primary);
  box-shadow: var(--artdeco-glow-subtle);
}

.artdeco-nav-item.active .artdeco-nav-icon {
  color: var(--artdeco-gold-primary);
  text-shadow: var(--artdeco-glow-subtle);
}

/* Responsive Design */
@media (max-width: 768px) {
  .artdeco-sidebar {
    transform: translateX(-100%);
  }

  .artdeco-sidebar.mobile-open {
    transform: translateX(0);
  }
}
</style>
