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
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-topbar {
      height: 60px;
      background: var(--artdeco-bg-header);
      border-bottom: 2px solid rgba(212, 175, 55, 0.2);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 var(--artdeco-spacing-5);  // 40px
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
      gap: var(--artdeco-spacing-2);  // 16px
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
      letter-spacing: var(--artdeco-tracking-wide);  // 0.05em
    }

    .artdeco-breadcrumb-title {
      color: var(--artdeco-fg-muted);
      font-weight: 500;
      text-transform: uppercase;
    }

    .artdeco-breadcrumb-separator {
      color: var(--artdeco-accent-gold);
      opacity: 0.5;
      font-weight: 700;
    }

    .artdeco-breadcrumb-subtitle {
      color: var(--artdeco-accent-gold);
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);  // 0.05em
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
      max-width: 500px;
    }

    .artdeco-search-input {
      width: 100%;
      padding: 8px 40px 8px 0;
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
      color: var(--artdeco-fg-primary);
      background: transparent;
      border: none;
      border-bottom: 2px solid rgba(212, 175, 55, 0.2);
      border-radius: var(--artdeco-radius-none);
      transition: all var(--artdeco-transition-base);
      letter-spacing: var(--artdeco-tracking-normal);  // 0em
    }

    .artdeco-search-input::placeholder {
      color: var(--artdeco-fg-muted);
      opacity: 0.7;
    }

    .artdeco-search-input:focus {
      outline: none;
      border-bottom-color: var(--artdeco-accent-gold);
      border-bottom-width: 3px;
      box-shadow: var(--artdeco-glow-subtle);
    }

    .artdeco-search-icon {
      position: absolute;
      right: 8px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--artdeco-accent-gold);
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
      opacity: 0.7;
      transition: opacity var(--artdeco-transition-base);
      pointer-events: none;
    }

    .artdeco-search-input:focus + .artdeco-search-icon {
      opacity: 1;
    }

    /* Status Badge - Simplified */
    .artdeco-topbar-actions {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-3);  // 24px
    }

    .artdeco-status {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-2);  // 16px
      padding: 6px 12px;
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
      font-family: var(--artdeco-font-mono);
      color: var(--artdeco-fg-secondary);
      background: transparent;
      border: 1px solid rgba(212, 175, 55, 0.2);
      border-radius: var(--artdeco-radius-none);
      transition: all var(--artdeco-transition-base);
    }

    .artdeco-status:hover {
      border-color: var(--artdeco-accent-gold);
      color: var(--artdeco-accent-gold);
      box-shadow: var(--artdeco-glow-subtle);
    }

    .artdeco-status-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      animation: artdeco-pulse 2s ease-in-out infinite;
    }

    .artdeco-status-dot.online {
      background: var(--artdeco-success);
      box-shadow: 0 0 6px rgba(39, 174, 96, 0.6);
    }

    .artdeco-status-dot.warning {
      background: var(--artdeco-warning);
      box-shadow: 0 0 6px rgba(230, 126, 34, 0.6);
    }

    .artdeco-status-dot.offline {
      background: var(--artdeco-danger);
      box-shadow: 0 0 6px rgba(231, 76, 60, 0.6);
    }

    @keyframes artdeco-pulse {
      0%, 100% {
        opacity: 1;
      }
      50% {
        opacity: 0.5;
      }
    }

    /* Corner Ornaments - Simplified */
    .artdeco-corner-tl,
    .artdeco-corner-tr {
      position: absolute;
      width: 12px;
      height: 12px;
      pointer-events: none;
    }

    .artdeco-corner-tl {
      top: 0;
      left: var(--artdeco-spacing-5);  // 40px
      border-top: 2px solid var(--artdeco-accent-gold);
      border-left: 2px solid var(--artdeco-accent-gold);
      opacity: 0.3;
    }

    .artdeco-corner-tr {
      top: 0;
      right: var(--artdeco-spacing-5);  // 40px
      border-top: 2px solid var(--artdeco-accent-gold);
      border-right: 2px solid var(--artdeco-accent-gold);
      opacity: 0.3;
    }

    // ============================================
    //   DESIGN NOTE - 设计说明
    //   本项目仅支持桌面端，不包含移动端响应式代码
    // ============================================
</style>
