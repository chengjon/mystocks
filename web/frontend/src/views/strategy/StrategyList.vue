<template>
  <div class="strategy-list">
    <div class="card">
      <div class="page-header">
        <div class="header-content">
          <h1 class="page-title">可用策略列表</h1>
          <div class="page-subtitle">Available Strategies</div>
          <div class="decorative-line"></div>
        </div>
        <button class="button" @click="loadStrategies" :disabled="loading">
          <svg v-if="loading" class="spinner" width="16" height="16" viewBox="0 0 50 50">
            <circle cx="25" cy="25" r="20" fill="none" :stroke="'var(--gold-primary)'" stroke-width="4"></circle>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
            <path d="M23 4v6h-6"></path>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
          </svg>
          刷新
        </button>
      </div>

      <div class="filter-bar">
        <div class="search-box">
          <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-dim)'" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input
            v-model="searchKeyword"
            type="text"
            class="input"
            placeholder="搜索策略名称或代码..."
          />
        </div>

        <select v-model="filterStatus" class="select">
          <option value="">状态筛选</option>
          <option :value="true">启用</option>
          <option :value="false">禁用</option>
        </select>

        <div class="filter-stats">
          <span class="stats-tag">共 {{ filteredStrategies.length }} 个策略</span>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="filteredStrategies.length > 0" class="strategies-grid">
        <div
          v-for="(strategy, _idx) in filteredStrategies"
          :key="strategy.strategy_code"
          class="strategy-card"
        >
          <div class="strategy-header">
            <h3>{{ strategy.strategy_name_cn }}</h3>
            <ArtDecoBadge :variant="strategy.is_active ? 'active' : 'neutral'" size="sm">
              {{ strategy.is_active ? '启用' : '禁用' }}
            </ArtDecoBadge>
          </div>

          <div class="strategy-code">
            <span class="code-tag">{{ strategy.strategy_code }}</span>
            <span class="en-name">{{ strategy.strategy_name_en }}</span>
          </div>

          <p class="strategy-desc">{{ strategy.description }}</p>

          <div v-if="strategy.parameters" class="strategy-params">
            <details class="params-collapse">
              <summary>策略参数</summary>
              <div class="params-content">
                <div v-for="(value, key) in strategy.parameters" :key="key" class="param-item">
                  <span class="param-key">{{ key }}:</span>
                  <span class="param-value">{{ value }}</span>
                </div>
              </div>
            </details>
          </div>

          <div class="strategy-actions">
            <button class="button" @click="runStrategy(strategy)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
                <polygon points="5,3 19,12 5,21 5,3"></polygon>
              </svg>
              运行策略
            </button>
            <button class="button secondary" @click="viewResults(strategy)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
                <path d="M1,12 L4,12 L6,20 L18,4 L20,12 L23,12"></path>
                <path d="M1,12 L4,12 L6,20 L18,4 L20,12 L23,12 M5.5,12 L18.5,12" stroke-dasharray="2 2"></path>
              </svg>
              查看结果
            </button>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-dim)'" stroke-width="1">
          <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
          <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
        </svg>
        <p>{{ strategies.length === 0 ? '暂无可用策略' : '没有符合条件的策略' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { strategyApi } from '@/api'
import { ArtDecoBadge } from '@/components/artdeco'

const emit = defineEmits(['run-strategy', 'view-results'])

const loading = ref(false)
const strategies = ref([])
const searchKeyword = ref('')
const filterStatus = ref('')

const filteredStrategies = computed(() => {
  let result = strategies.value

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(s =>
      s.strategy_name_cn.toLowerCase().includes(keyword) ||
      s.strategy_name_en.toLowerCase().includes(keyword) ||
      s.strategy_code.toLowerCase().includes(keyword) ||
      (s.description && s.description.toLowerCase().includes(keyword))
    )
  }

  if (filterStatus.value !== '') {
    result = result.filter(s => s.is_active === filterStatus.value)
  }

  return result
})

const loadStrategies = async () => {
  loading.value = true
  try {
    const response = await strategyApi.getDefinitions()
    if (response.data.success) {
      strategies.value = response.data.data
      ElMessage.success(`加载成功，共${strategies.value.length}个策略`)
    } else {
      ElMessage.error(response.data.message || '加载失败')
    }
  } catch (error) {
    console.error('加载策略列表失败:', error)
    ElMessage.error('加载策略列表失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const runStrategy = (strategy) => {
  emit('run-strategy', strategy)
}

const viewResults = (strategy) => {
  emit('view-results', strategy)
}

onMounted(() => {
  loadStrategies()
})
</script>

<style scoped lang="scss">
@use "./styles/StrategyList.scss" as *;
</style>
