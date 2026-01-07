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
          v-for="strategy in filteredStrategies"
          :key="strategy.strategy_code"
          class="strategy-card"
        >
          <div class="strategy-header">
            <h3>{{ strategy.strategy_name_cn }}</h3>
            <span class="status-badge" :class="strategy.is_active ? 'active' : 'inactive'">
              {{ strategy.is_active ? '启用' : '禁用' }}
            </span>
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

.strategy-list {
  padding: 20px;
  min-height: 100vh;
  background: var(--bg-primary);
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
}

.card {
  background: var(--bg-secondary);
  border: 1px solid var(--gold-dim);
  padding: 30px;
  position: relative;
  border-radius: 0;

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 16px;
    height: 16px;
    border: 2px solid var(--gold-primary);
  }

  &::before {
    top: 12px;
    left: 12px;
    border-right: none;
    border-bottom: none;
  }

  &::after {
    bottom: 12px;
    right: 12px;
    border-left: none;
    border-top: none;
  }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--gold-dim);

  .header-content {
    flex: 1;
  }

  .page-title {
    font-family: var(--font-display);
    font-size: 28px;
    color: var(--gold-primary);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 0 0 8px 0;
  }

  .page-subtitle {
    font-family: var(--font-display);
    font-size: 12px;
    color: var(--gold-dim);
    text-transform: uppercase;
    letter-spacing: 3px;
  }

  .decorative-line {
    position: absolute;
    bottom: -1px;
    left: 0;
    width: 200px;
    height: 2px;
    background: linear-gradient(90deg, var(--gold-primary), transparent);

    &::before {
      content: '';
      position: absolute;
      bottom: -6px;
      left: 0;
      width: 60px;
      height: 1px;
      background: linear-gradient(90deg, var(--gold-dim), transparent);
    }
  }
}

.filter-bar {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-bottom: 25px;
  flex-wrap: wrap;
  padding: 20px;
  background: rgba(212, 175, 55, 0.03);
  border: 1px solid var(--gold-dim);

  .search-box {
    position: relative;
    display: flex;
    align-items: center;
    flex: 1;
    min-width: 280px;
    max-width: 400px;

    .search-icon {
      position: absolute;
      left: 15px;
      pointer-events: none;
    }

    .input {
      width: 100%;
      padding: 10px 15px 10px 45px;
      background: var(--bg-primary);
      border: 1px solid var(--gold-dim);
      color: var(--text-primary);
      font-family: var(--font-body);
      font-size: 14px;
      border-radius: 0;
      outline: none;
      transition: all 0.3s ease;

      &:focus {
        border-color: var(--gold-primary);
        box-shadow: 0 0 8px rgba(212, 175, 55, 0.3);
      }

      &::placeholder {
        color: var(--text-muted);
      }
    }
  }

  .filter-stats {
    margin-left: auto;
  }

  .stats-tag {
    display: inline-block;
    padding: 6px 14px;
    background: rgba(212, 175, 55, 0.15);
    border: 1px solid var(--gold-dim);
    color: var(--gold-primary);
    font-family: var(--font-display);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
}

.select {
  padding: 10px 15px;
  background: var(--bg-primary);
  border: 1px solid var(--gold-dim);
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: 14px;
  border-radius: 0;
  outline: none;
  cursor: pointer;
  transition: all 0.3s ease;

  &:focus {
    border-color: var(--gold-primary);
    box-shadow: 0 0 8px rgba(212, 175, 55, 0.3);
  }
}

.button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--gold-primary);
  color: var(--bg-primary);
  border: none;
  font-family: var(--font-display);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
  border-radius: 0;
  transition: all 0.3s ease;

  &:hover:not(:disabled) {
    background: var(--gold-muted);
    box-shadow: 0 0 12px rgba(212, 175, 55, 0.4);
  }

  &:disabled {
    background: var(--gold-dim);
    cursor: not-allowed;
    opacity: 0.5;
  }

  &.secondary {
    background: transparent;
    border: 1px solid var(--gold-primary);
    color: var(--gold-primary);

    &:hover:not(:disabled) {
      background: var(--gold-primary);
      color: var(--bg-primary);
    }
  }
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: 20px;

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--gold-dim);
    border-top-color: var(--gold-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  p {
    color: var(--text-muted);
    font-family: var(--font-body);
    font-size: 14px;
  }
}

.strategies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.strategy-card {
  background: var(--bg-primary);
  border: 1px solid var(--gold-dim);
  padding: 20px;
  position: relative;
  transition: all 0.3s ease;

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 12px;
    height: 12px;
    border: 2px solid var(--gold-primary);
  }

  &::before {
    top: 8px;
    left: 8px;
    border-right: none;
    border-bottom: none;
  }

  &::after {
    bottom: 8px;
    right: 8px;
    border-left: none;
    border-top: none;
  }

  &:hover {
    border-color: var(--gold-primary);
    box-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
    transform: translateY(-2px);
  }

  .strategy-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;

    h3 {
      margin: 0;
      font-family: var(--font-display);
      font-size: 18px;
      color: var(--gold-primary);
      text-transform: uppercase;
      letter-spacing: 1px;
      flex: 1;
    }

    .status-badge {
      display: inline-block;
      padding: 4px 10px;
      font-family: var(--font-display);
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 1px;
      border-radius: 0;

      &.active {
        background: rgba(0, 230, 118, 0.15);
        border: 1px solid rgba(0, 230, 118, 0.3);
        color: var(--fall);
      }

      &.inactive {
        background: rgba(212, 175, 55, 0.15);
        border: 1px solid var(--gold-dim);
        color: var(--gold-primary);
      }
    }
  }

  .strategy-code {
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 10px;

    .code-tag {
      display: inline-block;
      padding: 3px 8px;
      background: rgba(212, 175, 55, 0.1);
      border: 1px solid var(--gold-dim);
      color: var(--gold-primary);
      font-family: var(--font-display);
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 1px;
    }

    .en-name {
      font-size: 12px;
      color: var(--text-muted);
      font-family: var(--font-body);
    }
  }

  .strategy-desc {
    font-size: 14px;
    color: var(--text-primary);
    line-height: 1.6;
    margin-bottom: 15px;
    font-family: var(--font-body);
    min-height: 40px;
  }

  .strategy-params {
    margin-bottom: 15px;

    .params-collapse {
      summary {
        cursor: pointer;
        padding: 8px 12px;
        background: rgba(212, 175, 55, 0.05);
        border: 1px solid var(--gold-dim);
        color: var(--gold-primary);
        font-family: var(--font-display);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        list-style: none;

        &:hover {
          border-color: var(--gold-primary);
          background: rgba(212, 175, 55, 0.1);
        }

        &::-webkit-details-marker {
          display: none;
        }

        &::after {
          content: '+';
          float: right;
          font-weight: bold;
        }
      }

      &[open] summary::after {
        content: '-';
      }

      .params-content {
        margin-top: 10px;
        padding: 12px;
        background: var(--bg-secondary);
        border: 1px solid var(--gold-dim);

        .param-item {
          display: flex;
          justify-content: space-between;
          padding: 6px 0;
          font-size: 13px;
          border-bottom: 1px solid rgba(212, 175, 55, 0.1);

          &:last-child {
            border-bottom: none;
          }

          .param-key {
            color: var(--gold-dim);
            font-family: var(--font-display);
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
          }

          .param-value {
            color: var(--text-primary);
            font-family: var(--font-body);
          }
        }
      }
    }
  }

  .strategy-actions {
    display: flex;
    gap: 10px;
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px solid var(--gold-dim);

    .button {
      flex: 1;
      justify-content: center;
    }
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: 20px;

  p {
    color: var(--text-muted);
    font-family: var(--font-body);
    font-size: 14px;
  }
}

@media (max-width: 768px) {
  .strategy-list {
    padding: 10px;
  }

  .card {
    padding: 15px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .filter-bar {
    flex-direction: column;

    .search-box {
      width: 100%;
      max-width: 100%;
    }

    .filter-stats {
      margin-left: 0;
      width: 100%;
    }
  }

  .strategies-grid {
    grid-template-columns: 1fr;
  }
}
</style>
