<template>
  <div>
    <!-- ArtDeco Header -->
    <div class="decision-header">
      <h1 class="page-title">TRADING DECISION CENTER</h1>
      <p class="page-subtitle">一体化交易决策中心</p>
      <div class="header-actions">
        <el-button class="artdeco-gold-cta" size="small" @click="handleQuickAction('new-trade')" plain>
          新建交易
        </el-button>
        <el-button class="artdeco-gold-cta" size="small" @click="handleQuickAction('quick-sell')" plain>
          快速卖出
        </el-button>
        <el-button class="artdeco-gold-cta" size="small" @click="toggleAutoRefresh" plain>
          {{ autoRefreshEnabled ? '暂停刷新' : '自动刷新' }}
        </el-button>
      </div>
    </div>

    <!-- ArtDeco Tab Navigation -->
    <div class="decision-tabs">
      <button
        v-for="(tab, _idx) in decisionTabs"
        :key="tab.id"
        :class="['artdeco-tab', { active: activeTab === tab.id }]"
        @click="scrollToSection(tab.id)"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Tab Content -->
    <div class="decision-content">


          <!-- Quick Actions -->
          <ArtDecoCardCompact>
            <template #header>
              <h3>快捷操作</h3>
            </template>
            <div class="quick-actions-grid">
              <div class="action-card" @click="handleQuickAction('new-buy')">
                <div class="action-icon">
                  <el-icon><Plus /></el-icon>
                </div>
                <div class="action-label">新建买单</div>
              </div>
              <div class="action-card" @click="handleQuickAction('new-sell')">
                <div class="action-icon">
                  <el-icon><Minus /></el-icon>
                </div>
                <div class="action-label">新建卖单</div>
              </div>
              <div class="action-card" @click="handleQuickAction('view-all')">
                <div class="action-icon">
                  <el-icon><Grid /></el-icon>
                </div>
                <div class="action-label">查看全部持仓</div>
              </div>
            </div>
          </ArtDecoCardCompact>
        </div>

        <!-- Positions Tab -->
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Minus, Grid } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import ArtDecoCardCompact from '@/components/artdeco/ArtDecoCardCompact.vue'

const AUTO_REFRESH_EVENT = 'trading-decision:auto-refresh'
const AUTO_REFRESH_INTERVAL_MS = 30000

const router = useRouter()
const activeTab = ref('portfolio-panel')
const autoRefreshEnabled = ref(true)
const autoRefreshTimer = ref<ReturnType<typeof setInterval> | null>(null)

const decisionTabs = [
  { id: 'portfolio-panel', label: '资产组合' },
  { id: 'positions-panel', label: '持仓管理' },
  { id: 'orders-panel', label: '委托下单' }
]

const scrollToSection = (sectionId: string): void => {
  const section = document.getElementById(sectionId)
  if (!section) {
    ElMessage.warning('目标面板暂不可用')
    return
  }

  activeTab.value = sectionId
  section.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const handleQuickAction = async (action: string): Promise<void> => {
  if (action === 'new-trade' || action === 'new-buy' || action === 'new-sell') {
    scrollToSection('orders-panel')
    return
  }

  if (action === 'quick-sell' || action === 'view-all') {
    scrollToSection('positions-panel')
    return
  }

  await router.push({ name: 'trade-terminal' })
}

const dispatchAutoRefresh = (): void => {
  window.dispatchEvent(new CustomEvent(AUTO_REFRESH_EVENT))
}

const syncAutoRefreshTimer = (): void => {
  if (autoRefreshTimer.value) {
    clearInterval(autoRefreshTimer.value)
    autoRefreshTimer.value = null
  }

  if (!autoRefreshEnabled.value) {
    return
  }

  autoRefreshTimer.value = setInterval(() => {
    dispatchAutoRefresh()
  }, AUTO_REFRESH_INTERVAL_MS)
}

const toggleAutoRefresh = (): void => {
  autoRefreshEnabled.value = !autoRefreshEnabled.value
  syncAutoRefreshTimer()
  ElMessage.info(autoRefreshEnabled.value ? '已开启自动刷新，每 30 秒同步一次面板数据' : '已暂停自动刷新')
}

onMounted(() => {
  syncAutoRefreshTimer()
})

onBeforeUnmount(() => {
  if (autoRefreshTimer.value) {
    clearInterval(autoRefreshTimer.value)
  }
})
</script>
