<template>
  <div class="strategy-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>📋 可用策略列表</span>
          <el-button type="primary" size="small" @click="loadStrategies" :loading="loading">
            <el-icon><Refresh /></el-icon> 刷新
          </el-button>
        </div>
      </template>

      <!-- 加载状态 -->
      <el-skeleton v-if="loading" :rows="5" animated />

      <!-- 策略列表 -->
      <div v-else-if="strategies.length > 0" class="strategies-grid">
        <el-card
          v-for="strategy in strategies"
          :key="strategy.strategy_code"
          class="strategy-card"
          shadow="hover"
        >
          <div class="strategy-header">
            <h3>{{ strategy.strategy_name_cn }}</h3>
            <el-tag :type="strategy.is_active ? 'success' : 'info'">
              {{ strategy.is_active ? '启用' : '禁用' }}
            </el-tag>
          </div>

          <div class="strategy-code">
            <el-tag size="small" type="info">{{ strategy.strategy_code }}</el-tag>
            <span class="en-name">{{ strategy.strategy_name_en }}</span>
          </div>

          <p class="strategy-desc">{{ strategy.description }}</p>

          <div class="strategy-params" v-if="strategy.parameters">
            <el-collapse>
              <el-collapse-item title="策略参数" name="params">
                <div class="params-content">
                  <div v-for="(value, key) in strategy.parameters" :key="key" class="param-item">
                    <span class="param-key">{{ key }}:</span>
                    <span class="param-value">{{ value }}</span>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>

          <div class="strategy-actions">
            <el-button type="primary" size="small" @click="runStrategy(strategy)">
              <el-icon><VideoPlay /></el-icon> 运行策略
            </el-button>
            <el-button size="small" @click="viewResults(strategy)">
              <el-icon><View /></el-icon> 查看结果
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- 空状态 -->
      <el-empty v-else description="暂无可用策略" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, VideoPlay, View } from '@element-plus/icons-vue'
import axios from 'axios'
import { API_ENDPOINTS } from '@/config/api'

// 定义事件
const emit = defineEmits(['run-strategy', 'view-results'])

// 响应式数据
const loading = ref(false)
const strategies = ref([])

// 加载策略列表
const loadStrategies = async () => {
  loading.value = true
  try {
    const response = await axios.get(API_ENDPOINTS.strategy.definitions)
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

// 运行策略
const runStrategy = (strategy) => {
  emit('run-strategy', strategy)
}

// 查看结果
const viewResults = (strategy) => {
  emit('view-results', strategy)
}

// 组件挂载时加载数据
onMounted(() => {
  loadStrategies()
})
</script>

<style scoped lang="scss">
.strategy-list {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .strategies-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 16px;

    .strategy-card {
      .strategy-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;

        h3 {
          margin: 0;
          font-size: 18px;
          color: #303133;
        }
      }

      .strategy-code {
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;

        .en-name {
          font-size: 12px;
          color: #909399;
        }
      }

      .strategy-desc {
        font-size: 14px;
        color: #606266;
        line-height: 1.6;
        margin-bottom: 12px;
      }

      .strategy-params {
        margin-bottom: 12px;

        .params-content {
          .param-item {
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
            font-size: 13px;

            .param-key {
              color: #909399;
              font-weight: 500;
            }

            .param-value {
              color: #606266;
            }
          }
        }

        :deep(.el-collapse-item__header) {
          font-size: 13px;
          color: #606266;
        }
      }

      .strategy-actions {
        display: flex;
        gap: 8px;
        margin-top: 16px;
        padding-top: 12px;
        border-top: 1px solid #ebeef5;

        .el-button {
          flex: 1;
        }
      }
    }
  }
}
</style>
