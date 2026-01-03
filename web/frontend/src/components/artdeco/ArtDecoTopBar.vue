<template>
  <header class="artdeco-topbar">
    <div class="artdeco-breadcrumb">{{ breadcrumbText }}</div>

    <div class="artdeco-search-box" v-if="showSearch">
      <input
        type="text"
        class="artdeco-search-input"
        :placeholder="searchPlaceholder"
        v-model="searchQuery"
        @keyup.enter="handleSearch"
      >
    </div>

    <div class="artdeco-topbar-actions">
      <div class="artdeco-status">
        <span class="artdeco-status-dot online"></span>
        <span>{{ statusText }}</span>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const props = withDefaults(defineProps<{
  showSearch?: boolean
  searchPlaceholder?: string
  statusText?: string
}>(), {
  showSearch: true,
  searchPlaceholder: '输入股票代码 / 名称快速搜索...',
  statusText: '数据源正常'
})

const searchQuery = ref('')

const breadcrumbText = computed(() => {
  const title = route.meta.title as string || '页面'
  const name = route.name as string || 'unknown'
  const nameMap: Record<string, string> = {
    'artdeco-dashboard': '主控仪表盘 / DASHBOARD',
    'artdeco-market-center': '市场行情中心 / MARKET CENTER',
    'artdeco-stock-screener': '智能选股池 / STOCK SCREENER',
    'artdeco-data-analysis': '数据分析 / DATA ANALYSIS',
    'artdeco-strategy-lab': '策略实验室 / STRATEGY LAB',
    'artdeco-backtest-arena': '回测竞技场 / BACKTEST ARENA',
    'artdeco-trade-station': '交易工作站 / TRADE STATION',
    'artdeco-risk-center': '风控中心 / RISK CENTER',
    'artdeco-system-settings': '系统设置 / SYSTEM SETTINGS'
  }
  return nameMap[name] || `${title} / ${name.toUpperCase()}`
})

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    // 触发搜索事件
    console.log('搜索:', searchQuery.value)
  }
}
</script>

<style scoped>
@import '@/styles/artdeco/artdeco-theme.css';

.artdeco-topbar {
  height: 60px;
  background: var(--artdeco-bg-header);
  border-bottom: 1px solid var(--artdeco-gold-dim);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--artdeco-space-lg);
  position: sticky;
  top: 0;
  z-index: var(--artdeco-z-sticky);
}

.artdeco-breadcrumb {
  font-family: var(--artdeco-font-display);
  font-size: 0.875rem;
  color: var(--artdeco-gold-primary);
  letter-spacing: 1px;
}

.artdeco-search-box {
  position: relative;
  width: 400px;
}

.artdeco-search-input {
  width: 100%;
  padding: 8px 40px 8px 16px;
  font-family: var(--artdeco-font-body);
  font-size: 0.875rem;
  color: var(--artdeco-silver-text);
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-gold-dim);
  border-radius: var(--artdeco-radius-none);
}

.artdeco-search-input:focus {
  outline: none;
  border-color: var(--artdeco-gold-primary);
  box-shadow: var(--artdeco-glow-subtle);
}

.artdeco-topbar-actions {
  display: flex;
  align-items: center;
  gap: var(--artdeco-space-md);
}

.artdeco-status {
  display: flex;
  align-items: center;
  gap: var(--artdeco-space-sm);
  padding: 6px 12px;
  font-size: 0.75rem;
  font-family: var(--artdeco-font-mono);
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-gold-dim);
  border-radius: var(--artdeco-radius-none);
}

.artdeco-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: artdeco-pulse 2s ease-in-out infinite;
}

.artdeco-status-dot.online {
  background: var(--artdeco-success);
  box-shadow: 0 0 8px rgba(39, 174, 96, 0.6);
}

@keyframes artdeco-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@media (max-width: 768px) {
  .artdeco-search-box {
    width: 200px;
  }
}
</style>
