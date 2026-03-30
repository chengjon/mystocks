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
        @click="activeTab = tab.id"
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
import { ref } from 'vue'
import { Plus, Minus, Grid } from '@element-plus/icons-vue'
import ArtDecoCardCompact from '@/components/artdeco/ArtDecoCardCompact.vue'

const activeTab = ref('portfolio')
const autoRefreshEnabled = ref(true)

const decisionTabs = [
  { id: 'portfolio', label: '资产组合' },
  { id: 'positions', label: '持仓管理' },
  { id: 'orders', label: '委托下单' }
]

const handleQuickAction = (_action: string): void => {
}

const toggleAutoRefresh = (): void => {
  autoRefreshEnabled.value = !autoRefreshEnabled.value
}
</script>
