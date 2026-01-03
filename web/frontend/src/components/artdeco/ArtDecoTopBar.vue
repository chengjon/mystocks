<template>
  <header class="artdeco-topbar">
    <!-- Decorative left corner -->
    <div class="artdeco-corner-tl"></div>

    <div class="artdeco-topbar-left">
      <div class="artdeco-breadcrumb">
        <span class="artdeco-breadcrumb-title">{{ breadcrumbTitle }}</span>
        <span class="artdeco-breadcrumb-separator">/</span>
        <span class="artdeco-breadcrumb-subtitle">{{ breadcrumbSubtitle }}</span>
      </div>
    </div>

    <div class="artdeco-topbar-center" v-if="showSearch">
      <div class="artdeco-search-box">
        <input
          type="text"
          class="artdeco-search-input"
          :placeholder="searchPlaceholder"
          v-model="searchQuery"
          @keyup.enter="handleSearch"
        >
        <div class="artdeco-search-icon">🔍</div>
      </div>
    </div>

    <div class="artdeco-topbar-actions">
      <div class="artdeco-status">
        <span class="artdeco-status-dot online"></span>
        <span class="artdeco-status-text">{{ statusText }}</span>
      </div>
    </div>

    <!-- Decorative right corner -->
    <div class="artdeco-corner-tr"></div>
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

const breadcrumbTitle = computed(() => {
  const title = route.meta.title as string || '页面'
  return title
})

const breadcrumbSubtitle = computed(() => {
  const name = route.name as string || 'unknown'
  const nameMap: Record<string, string> = {
    'artdeco-dashboard': 'DASHBOARD',
    'artdeco-market-center': 'MARKET CENTER',
    'artdeco-stock-screener': 'STOCK SCREENER',
    'artdeco-data-analysis': 'DATA ANALYSIS',
    'artdeco-strategy-lab': 'STRATEGY LAB',
    'artdeco-backtest-arena': 'BACKTEST ARENA',
    'artdeco-trade-station': 'TRADE STATION',
    'artdeco-risk-center': 'RISK CENTER',
    'artdeco-system-settings': 'SYSTEM SETTINGS'
  }
  return nameMap[name] || name.toUpperCase()
})

const breadcrumbText = computed(() => {
  return `${breadcrumbTitle.value} / ${breadcrumbSubtitle.value}`
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
  height: 72px; /* Increased from 60px */
  background: var(--artdeco-bg-header); /* Obsidian Black */
  border-bottom: 2px solid var(--artdeco-gold-dim); /* Thicker border */
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--artdeco-space-xl);
  position: sticky;
  top: 0;
  z-index: var(--artdeco-z-sticky);
  position: relative;
}

.artdeco-topbar-left {
  flex: 1;
}

/* Breadcrumb with Art Deco styling */
.artdeco-breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--artdeco-space-sm);
  font-family: var(--artdeco-font-display);
  font-size: 0.875rem;
  letter-spacing: var(--artdeco-tracking-tight);
}

.artdeco-breadcrumb-title {
  color: var(--artdeco-text-dim); /* Pewter - Muted */
  font-weight: 500;
  text-transform: uppercase;
}

.artdeco-breadcrumb-separator {
  color: var(--artdeco-gold-primary);
  opacity: 0.5;
  font-weight: 700;
}

.artdeco-breadcrumb-subtitle {
  color: var(--artdeco-gold-primary);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-display); /* Wide tracking */
}

/* Search Box - Underlined Elegance */
.artdeco-topbar-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.artdeco-search-box {
  position: relative;
  width: 100%;
  max-width: 500px;
}

.artdeco-search-input {
  width: 100%;
  padding: 12px 48px 12px 16px; /* Space for icon */
  font-family: var(--artdeco-font-body); /* Josefin Sans */
  font-size: 0.875rem;
  color: var(--artdeco-text-primary); /* Champagne Cream */
  background: transparent; /* Underlined style - no background box */
  border: none;
  border-bottom: 2px solid var(--artdeco-gold-dim);
  transition: all var(--artdeco-transition-slow);
  letter-spacing: var(--artdeco-tracking-body);
}

.artdeco-search-input::placeholder {
  color: var(--artdeco-text-dim);
  opacity: 0.7;
}

.artdeco-search-input:focus {
  outline: none;
  border-bottom-color: var(--artdeco-gold-primary);
  border-bottom-width: 3px; /* Thicker on focus */
}

.artdeco-search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--artdeco-gold-primary);
  font-size: 1rem;
  opacity: 0.7;
  transition: opacity var(--artdeco-transition-slow);
  pointer-events: none;
}

.artdeco-search-input:focus + .artdeco-search-icon {
  opacity: 1;
}

/* Status Badge */
.artdeco-topbar-actions {
  display: flex;
  align-items: center;
  gap: var(--artdeco-space-md);
}

.artdeco-status {
  display: flex;
  align-items: center;
  gap: var(--artdeco-space-sm);
  padding: 8px 16px; /* Increased padding */
  font-size: 0.75rem;
  font-family: var(--artdeco-font-mono);
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-gold-dim);
  border-radius: var(--artdeco-radius-none);
  transition: all var(--artdeco-transition-slow);
  position: relative;
}

.artdeco-status::before {
  content: '';
  position: absolute;
  top: 4px;
  left: 4px;
  right: 4px;
  bottom: 4px;
  border: 1px solid var(--artdeco-gold-primary);
  opacity: 0.3;
  pointer-events: none;
}

.artdeco-status:hover {
  border-color: var(--artdeco-gold-primary);
  box-shadow: var(--artdeco-glow-subtle);
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

/* Corner Ornaments */
.artdeco-corner-tl,
.artdeco-corner-tr {
  position: absolute;
  width: 16px;
  height: 16px;
  pointer-events: none;
}

.artdeco-corner-tl {
  top: 0;
  left: var(--artdeco-space-xl);
  border-top: 2px solid var(--artdeco-gold-primary);
  border-left: 2px solid var(--artdeco-gold-primary);
  opacity: 0.4;
}

.artdeco-corner-tr {
  top: 0;
  right: var(--artdeco-space-xl);
  border-top: 2px solid var(--artdeco-gold-primary);
  border-right: 2px solid var(--artdeco-gold-primary);
  opacity: 0.4;
}

/* Responsive Design */
@media (max-width: 768px) {
  .artdeco-topbar {
    height: 64px;
    padding: 0 var(--artdeco-space-md);
  }

  .artdeco-search-box {
    max-width: 200px;
  }

  .artdeco-breadcrumb {
    font-size: 0.75rem;
  }

  .artdeco-breadcrumb-separator,
  .artdeco-breadcrumb-subtitle {
    display: none; /* Hide subtitle on mobile */
  }
}
</style>
