<template>
  <div class="artdeco-page-template">
    <a class="skip-to-content" href="#artdeco-main-content">
      跳转到主内容
    </a>

    <!-- 页面头部：标题+操作按钮 -->
    <ArtDecoHeader
      :title="pageConfig.title"
      :subtitle="pageConfig.subtitle"
      :show-status="pageConfig.showStatus"
      :status-text="statusText"
      :status-type="statusType"
    >
      <template #actions>
        <slot name="header-actions">
          <!-- 默认刷新按钮 -->
          <ArtDecoButton
            v-if="pageConfig.showRefresh !== false"
            variant="outline"
            priority="secondary"
            motion="data"
            size="sm"
            :loading="loading"
            @click="handleRefresh"
          >
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新
          </ArtDecoButton>
        </slot>
      </template>
    </ArtDecoHeader>

    <!-- 页面主体 -->
    <main
      id="artdeco-main-content"
      class="artdeco-page-content"
      tabindex="-1"
      :aria-busy="loading ? 'true' : 'false'"
    >
      <!-- 权限检查 -->
      <div v-if="!hasPermission(pageConfig.permission)" class="permission-denied">
        <ArtDecoIcon name="lock" size="xl" class="lock-icon" />
        <h3>访问受限</h3>
        <p>您没有权限访问此页面，请联系管理员</p>
      </div>

      <!-- 加载状态 -->
      <div v-else-if="loading && !dataLoaded" class="loading-state" role="status" aria-live="polite">
        <ArtDecoSkeleton
          :columns="pageConfig.skeleton?.columns || 4"
          :rows="pageConfig.skeleton?.rows || 3"
        />
      </div>

      <!-- 错误状态 -->
      <div v-else-if="hasError" class="error-boundary" role="alert" aria-live="assertive">
        <ArtDecoIcon name="alert" size="xl" class="error-icon" />
        <h3>加载失败</h3>
        <p>{{ errorMessage }}</p>
        <ArtDecoButton variant="solid" priority="primary" motion="data" size="sm" @click="handleRefresh">
          <template #icon>
            <ArtDecoIcon name="refresh" />
          </template>
          重试
        </ArtDecoButton>
      </div>

      <!-- 空数据状态 -->
      <div v-else-if="isEmptyData" class="empty-state" role="status" aria-live="polite">
        <ArtDecoIcon name="inbox" size="xl" class="empty-icon" />
        <p>{{ pageConfig.emptyMessage || '暂无数据' }}</p>
        <slot name="empty-action">
          <ArtDecoButton
            v-if="pageConfig.showRefresh !== false"
            variant="outline"
            priority="secondary"
            motion="data"
            size="sm"
            @click="handleRefresh"
          >
            刷新
          </ArtDecoButton>
        </slot>
      </div>

      <!-- 核心内容区（留给子页面扩展） -->
      <template v-else>
        <!-- 统计卡片区（可选） -->
        <div v-if="showStatsSection" class="stats-section">
          <slot name="stats" :stats="stats" :data="pageData" :refresh="handleRefresh">
            <ArtDecoStatCard
              v-for="(stat, index) in stats"
              :key="index"
              :label="stat.label"
              :value="stat.value"
              :change="stat.change"
              :change-percent="stat.changePercent"
              :variant="stat.variant"
              :size="stat.size || 'medium'"
            />
          </slot>
        </div>

        <!-- 标签页导航（可选） -->
        <div v-if="showTabsSection" class="tabs-shell">
          <slot
            name="tabs"
            :tabs="tabs"
            :active-tab="activeTab"
            :change-tab="handleTabChange"
            :trace-id="lastRequestId"
          >
            <nav class="page-tabs" role="tablist" aria-label="页面标签">
              <button
                v-for="(tab, index) in tabs"
                :id="tabButtonId(tab.key)"
                :key="tab.key"
                :ref="(el) => setTabButtonRef(el, index)"
                class="tab-button"
                :class="{ active: activeTab === tab.key }"
                role="tab"
                :aria-selected="activeTab === tab.key"
                :aria-controls="tabPanelId(tab.key)"
                :tabindex="activeTab === tab.key ? 0 : -1"
                @click="handleTabChange(tab.key)"
                @keydown="handleTabKeydown($event, index)"
              >
                <ArtDecoIcon v-if="tab.icon" :name="tab.icon" size="sm" />
                {{ tab.label }}
              </button>
            </nav>
          </slot>
          <div v-if="pageConfig.showTraceId !== false" class="tabs-trace" aria-live="polite">
            REQ_ID: {{ lastRequestId || 'N/A' }}
          </div>
        </div>

        <!-- 内容面板 -->
        <div class="content-panel" :class="{ 'with-tabs': showTabsSection }">
          <transition name="fade" mode="out-in">
            <div
              :id="tabPanelId(activeTab)"
              :key="activeTab || 'default'"
              class="tab-content"
              role="tabpanel"
              :aria-labelledby="activeTab ? tabButtonId(activeTab) : undefined"
            >
              <slot
                name="content"
                :data="pageData"
                :loading="loading"
                :active-tab="activeTab"
                :refresh="handleRefresh"
              >
                <!-- 默认内容提示 -->
                <div class="placeholder-content">
                  <ArtDecoIcon name="activity" size="lg" />
                  <p>页面内容区域</p>
                  <p class="hint">请通过 #content 插槽自定义内容</p>
                </div>
              </slot>
            </div>
          </transition>
        </div>
      </template>
    </main>

    <!-- 页面底部（可选） -->
    <div v-if="$slots.footer" class="page-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSlots } from 'vue'
import ArtDecoHeader from '@/components/artdeco/core/ArtDecoHeader.vue'
import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
import ArtDecoSkeleton from '@/components/artdeco/core/ArtDecoSkeleton.vue'
import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
import {
  useArtDecoPageTemplate,
  type ArtDecoPageConfig,
  type StatItem,
  type TabItem
} from './composables/useArtDecoPageTemplate'

const props = withDefaults(defineProps<{
  pageConfig: ArtDecoPageConfig
  stats?: StatItem[]
  tabs?: TabItem[]
  defaultTab?: string
}>(), {
  stats: () => [],
  tabs: () => [],
  defaultTab: ''
})

const emit = defineEmits<{
  'tab-change': [tabKey: string]
  'data-loaded': [data: unknown]
  'data-error': [error: Error]
}>()

const slots = useSlots()

const {
  loading,
  error,
  hasError,
  dataLoaded,
  pageData,
  lastRequestId,
  activeTab,
  statusText,
  statusType,
  errorMessage,
  showStatsSection,
  showTabsSection,
  isEmptyData,
  hasPermission,
  tabButtonId,
  tabPanelId,
  setTabButtonRef,
  handleTabChange,
  handleTabKeydown,
  handleRefresh
} = useArtDecoPageTemplate(
  {
    pageConfig: props.pageConfig,
    stats: props.stats,
    tabs: props.tabs,
    defaultTab: props.defaultTab
  },
  slots,
  emit
)

defineExpose({
  refresh: handleRefresh,
  pageData,
  loading,
  hasError,
  error,
  activeTab,
  lastRequestId
})
</script>

<style scoped lang="scss">
@use './styles/ArtDecoPageTemplate';
</style>
