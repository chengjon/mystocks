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
                />
                <div class="artdeco-search-icon">🔍</div>
            </div>
        </div>

        <div class="artdeco-topbar-actions">
            <div class="artdeco-status">
                <span class="artdeco-status-dot" :class="statusDotClass"></span>
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

    const props = withDefaults(
        defineProps<{
            showSearch?: boolean
            searchPlaceholder?: string
            statusText?: string
            statusType?: 'online' | 'warning' | 'offline'
        }>(),
        {
            showSearch: true,
            searchPlaceholder: '输入股票代码 / 名称快速搜索...',
            statusText: '数据源正常',
            statusType: 'online'
        }
    )

    const emit = defineEmits<{
        search: [query: string]
    }>()

    const searchQuery = ref('')

    const breadcrumbTitle = computed(() => {
        const title = (route.meta.title as string) || '页面'
        return title
    })

    const breadcrumbSubtitle = computed(() => {
        const name = (route.name as string) || 'unknown'
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

    const statusDotClass = computed(() => {
        return props.statusType
    })

    const handleSearch = () => {
        if (searchQuery.value.trim()) {
            emit('search', searchQuery.value)
        }
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens';

    .artdeco-topbar {
      height: calc(var(--artdeco-spacing-10) + var(--artdeco-spacing-5));
      background: var(--artdeco-bg-header);
      border-bottom: calc(var(--artdeco-spacing-1) / 2) solid var(--artdeco-gold-opacity-20);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 var(--artdeco-spacing-5);
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
      gap: var(--artdeco-spacing-2);
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-base);
      letter-spacing: var(--artdeco-tracking-wide);
    }

    .artdeco-breadcrumb-title {
      color: var(--artdeco-fg-muted);
      font-weight: 500;
      text-transform: uppercase;
    }

    .artdeco-breadcrumb-separator {
      color: var(--artdeco-accent-gold);
      opacity: 50%;
      font-weight: 700;
    }

    .artdeco-breadcrumb-subtitle {
      color: var(--artdeco-accent-gold);
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
    }

    /* Search Box - Underlined Elegance Style */
    .artdeco-topbar-center {
      flex: 1;
      display: flex;
      justify-content: center;
    }

    .artdeco-search-box {
      position: relative;
      width: 100%;
      max-width: calc(var(--artdeco-spacing-20) * 6 + var(--artdeco-spacing-5));
    }

    .artdeco-search-input {
      width: 100%;
      padding: var(--artdeco-spacing-2) var(--artdeco-spacing-5) var(--artdeco-spacing-2) 0;
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-base);
      color: var(--artdeco-fg-primary);
      background: transparent;
      border: none;
      border-bottom: calc(var(--artdeco-spacing-1) / 2) solid var(--artdeco-gold-opacity-20);
      border-radius: var(--artdeco-radius-none);
      transition: all var(--artdeco-transition-base);
      letter-spacing: var(--artdeco-tracking-normal);
    }

    .artdeco-search-input::placeholder {
      color: var(--artdeco-fg-muted);
      opacity: 70%;
    }

    .artdeco-search-input:focus {
      outline: none;
      border-bottom-color: var(--artdeco-accent-gold);
      border-bottom-width: calc(var(--artdeco-spacing-px) * 3);
      box-shadow: var(--artdeco-glow-subtle);
    }

    .artdeco-search-icon {
      position: absolute;
      right: var(--artdeco-spacing-2);
      top: 50%;
      transform: translateY(-50%);
      color: var(--artdeco-accent-gold);
      font-size: var(--artdeco-font-size-base);
      opacity: 70%;
      transition: opacity var(--artdeco-transition-base);
      pointer-events: none;
    }

    .artdeco-search-input:focus + .artdeco-search-icon {
      opacity: 100%;
    }

    /* Status Badge - Simplified */
    .artdeco-topbar-actions {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-3);
    }

    .artdeco-status {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-2);
      padding: calc(var(--artdeco-spacing-3) / 2) var(--artdeco-spacing-3);
      font-size: var(--artdeco-font-size-sm);
      font-family: var(--artdeco-font-mono);
      color: var(--artdeco-fg-secondary);
      background: transparent;
      border: 1px solid var(--artdeco-gold-opacity-20);
      border-radius: var(--artdeco-radius-none);
      transition: all var(--artdeco-transition-base);
    }

    .artdeco-status:hover {
      border-color: var(--artdeco-accent-gold);
      color: var(--artdeco-accent-gold);
      box-shadow: var(--artdeco-glow-subtle);
    }

    .artdeco-status-dot {
      width: calc(var(--artdeco-spacing-3) / 2);
      height: calc(var(--artdeco-spacing-3) / 2);
      border-radius: 50%;
      animation: artdeco-pulse 2s ease-in-out infinite;
    }

    .artdeco-status-dot.online {
      background: var(--artdeco-success);
      box-shadow: 0 0 calc(var(--artdeco-spacing-3) / 2) color-mix(in srgb, var(--artdeco-success) 60%, transparent);
    }

    .artdeco-status-dot.warning {
      background: var(--artdeco-warning);
      box-shadow: 0 0 calc(var(--artdeco-spacing-3) / 2) color-mix(in srgb, var(--artdeco-warning) 60%, transparent);
    }

    .artdeco-status-dot.offline {
      background: var(--artdeco-danger);
      box-shadow: 0 0 calc(var(--artdeco-spacing-3) / 2) color-mix(in srgb, var(--artdeco-danger) 60%, transparent);
    }

    @keyframes artdeco-pulse {
      0%, 100% {
        opacity: 100%;
      }
      50% {
        opacity: 50%;
      }
    }

    /* Corner Ornaments - Simplified */
    .artdeco-corner-tl,
    .artdeco-corner-tr {
      position: absolute;
      width: var(--artdeco-spacing-3);
      height: var(--artdeco-spacing-3);
      pointer-events: none;
    }

    .artdeco-corner-tl {
      top: 0;
      left: var(--artdeco-spacing-5);
      border-top: calc(var(--artdeco-spacing-1) / 2) solid var(--artdeco-accent-gold);
      border-left: calc(var(--artdeco-spacing-1) / 2) solid var(--artdeco-accent-gold);
      opacity: 30%;
    }

    .artdeco-corner-tr {
      top: 0;
      right: var(--artdeco-spacing-5);
      border-top: calc(var(--artdeco-spacing-1) / 2) solid var(--artdeco-accent-gold);
      border-right: calc(var(--artdeco-spacing-1) / 2) solid var(--artdeco-accent-gold);
      opacity: 30%;
    }

    // ============================================
    //   DESIGN NOTE - 设计说明
    //   本项目仅支持桌面端，不包含移动端响应式代码
    // ============================================
</style>
