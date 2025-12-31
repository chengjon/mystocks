<template>
  <div class="database-monitor">
    <el-page-header @back="() => $router.back()" content="数据库监控">
      <template #extra>
        <el-button :icon="RefreshIcon as any" @click="refreshData" :loading="loading">
          刷新
        </el-button>
      </template>
    </el-page-header>

    <div class="monitor-content">
      <!-- Summary Cards -->
      <el-row :gutter="20" style="margin: 20px 0">
        <el-col :span="12">
          <el-card shadow="hover">
            <div class="stat-card">
              <div class="stat-icon tdengine">
                <span style="font-size: 32px; font-weight: bold;">🔲</span>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ healthData.summary?.healthy || 0 }}/{{ healthData.summary?.total_databases || 2 }}</div>
                <div class="stat-label">健康数据库</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <div class="stat-card">
              <div class="stat-icon postgresql">
                <el-icon :size="40"><ConnectionIcon as any /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ statsData.total_classifications || 34 }}</div>
                <div class="stat-label">数据分类总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Database Health Status -->
      <el-card shadow="hover" style="margin: 20px 0">
        <template #header>
          <div class="card-header">
            <span>数据库健康状态</span>
            <el-tag :type="healthData.summary?.healthy === 2 ? 'success' : 'danger'" size="small">
              {{ healthData.summary?.healthy === 2 ? '全部正常' : '存在异常' }}
            </el-tag>
          </div>
        </template>

        <el-row :gutter="20">
          <el-col :span="12">
            <div class="database-status">
              <div class="db-header">
                <h3>TDengine</h3>
                <el-tag :type="healthData.tdengine?.status === 'healthy' ? 'success' : 'danger'" size="small">
                  {{ healthData.tdengine?.status === 'healthy' ? '正常' : '异常' }}
                </el-tag>
              </div>
              <div class="db-details" v-if="healthData.tdengine">
                <div class="detail-item">
                  <span class="label">主机:</span>
                  <span class="value">{{ healthData.tdengine.host }}:{{ healthData.tdengine.port }}</span>
                </div>
                <div class="detail-item" v-if="healthData.tdengine.database">
                  <span class="label">数据库:</span>
                  <span class="value">{{ healthData.tdengine.database }}</span>
                </div>
                <div class="detail-item" v-if="healthData.tdengine.version">
                  <span class="label">版本:</span>
                  <span class="value">{{ healthData.tdengine.version }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">状态:</span>
                  <span class="value">{{ healthData.tdengine.message }}</span>
                </div>
              </div>
            </div>
          </el-col>

          <el-col :span="12">
            <div class="database-status">
              <div class="db-header">
                <h3>PostgreSQL</h3>
                <el-tag :type="healthData.postgresql?.status === 'healthy' ? 'success' : 'danger'" size="small">
                  {{ healthData.postgresql?.status === 'healthy' ? '正常' : '异常' }}
                </el-tag>
              </div>
              <div class="db-details" v-if="healthData.postgresql">
                <div class="detail-item">
                  <span class="label">主机:</span>
                  <span class="value">{{ healthData.postgresql.host }}:{{ healthData.postgresql.port }}</span>
                </div>
                <div class="detail-item" v-if="healthData.postgresql.database">
                  <span class="label">数据库:</span>
                  <span class="value">{{ healthData.postgresql.database }}</span>
                </div>
                <div class="detail-item" v-if="healthData.postgresql.version">
                  <span class="label">版本:</span>
                  <span class="value">{{ healthData.postgresql.version }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">状态:</span>
                  <span class="value">{{ healthData.postgresql.message }}</span>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- Database Routing -->
      <el-card shadow="hover" style="margin: 20px 0">
        <template #header>
          <div class="card-header">
            <span>数据路由分布</span>
          </div>
        </template>

        <el-row :gutter="20">
          <el-col :span="12">
            <div class="routing-section">
              <h4 class="routing-title">
                <el-icon color="#FF6B6B"><Database /></el-icon>
                TDengine ({{ statsData.routing?.tdengine?.count || 5 }}项)
              </h4>
              <p class="routing-purpose">{{ statsData.routing?.tdengine?.purpose }}</p>
              <el-tag
                v-for="item in statsData.routing?.tdengine?.classifications"
                :key="item"
                style="margin: 5px"
                type="danger"
                effect="plain"
              >
                {{ item }}
              </el-tag>
              <div class="routing-features" v-if="statsData.routing?.tdengine?.features">
                <p><strong>特性:</strong></p>
                <ul>
                  <li v-for="feature in statsData.routing.tdengine.features" :key="feature">{{ feature }}</li>
                </ul>
              </div>
            </div>
          </el-col>

          <el-col :span="12">
            <div class="routing-section">
              <h4 class="routing-title">
                <el-icon color="#4E89AE"><ConnectionIcon as any /></el-icon>
                PostgreSQL ({{ statsData.routing?.postgresql?.count || 29 }}项)
              </h4>
              <p class="routing-purpose">{{ statsData.routing?.postgresql?.purpose }}</p>
              <el-tag
                v-for="category in statsData.routing?.postgresql?.categories"
                :key="category"
                style="margin: 5px"
                type="primary"
                effect="plain"
              >
                {{ category }}
              </el-tag>
              <div class="routing-features" v-if="statsData.routing?.postgresql?.features">
                <p><strong>特性:</strong></p>
                <ul>
                  <li v-for="feature in statsData.routing.postgresql.features" :key="feature">{{ feature }}</li>
                </ul>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- Architecture Info -->
      <el-card shadow="hover" style="margin: 20px 0">
        <template #header>
          <div class="card-header">
            <span>架构简化历史</span>
          </div>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="架构类型">{{ statsData.architecture }}</el-descriptions-item>
          <el-descriptions-item label="简化日期">{{ statsData.simplification_date }}</el-descriptions-item>
          <el-descriptions-item label="简化前">{{ statsData.simplified_from }}</el-descriptions-item>
          <el-descriptions-item label="简化后">{{ statsData.simplified_to }}</el-descriptions-item>
          <el-descriptions-item label="MySQL状态" :span="2">
            <el-tag type="info" size="small">{{ statsData.removed_databases?.mysql?.status }}</el-tag>
            已迁移至{{ statsData.removed_databases?.mysql?.migrated_to }} ({{ statsData.removed_databases?.mysql?.rows_migrated }}行)
          </el-descriptions-item>
          <el-descriptions-item label="Redis状态" :span="2">
            <el-tag type="info" size="small">{{ statsData.removed_databases?.redis?.status }}</el-tag>
            {{ statsData.removed_databases?.redis?.reason }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Connection } from '@element-plus/icons-vue'
import { request } from '@/utils/request'
import type { Component } from 'vue'

// Type for icon components
const RefreshIcon = Refresh as Component
const ConnectionIcon = Connection as Component

interface DatabaseHealth {
  status: 'healthy' | 'unhealthy' | 'unknown'
  host: string
  port: number
  database?: string
  version?: string
  message: string
}

interface DatabaseSummary {
  healthy: number
  total_databases: number
}

interface HealthData {
  summary?: DatabaseSummary
  tdengine?: DatabaseHealth
  postgresql?: DatabaseHealth
}

interface StatsData {
  total_classifications?: number
  routing?: {
    tdengine?: {
      count: number
      purpose?: string
      classifications?: string[]
      features?: string[]
    }
    postgresql?: {
      count: number
      purpose?: string
      categories?: string[]
      features?: string[]
    }
  }
  architecture?: string
  simplification_date?: string
  simplified_from?: string
  simplified_to?: string
  removed_databases?: {
    mysql?: {
      status: string
      migrated_to: string
      rows_migrated: number
    }
    redis?: {
      status: string
      reason: string
    }
  }
}

const loading = ref<boolean>(false)
const healthData = ref<HealthData>({})
const statsData = ref<StatsData>({})

const fetchHealthData = async (): Promise<void> => {
  try {
    const response = await request.get<HealthData>('/api/system/database/health')
    healthData.value = response
  } catch (error) {
    console.error('获取数据库健康状态失败:', error)
    ElMessage.error('获取数据库健康状态失败')
  }
}

const fetchStatsData = async (): Promise<void> => {
  try {
    const response = await request.get<StatsData>('/api/system/database/stats')
    statsData.value = response
  } catch (error) {
    console.error('获取数据库统计信息失败:', error)
    ElMessage.error('获取数据库统计信息失败')
  }
}

const refreshData = async (): Promise<void> => {
  loading.value = true
  try {
    await Promise.all([fetchHealthData(), fetchStatsData()])
    ElMessage.success('刷新成功')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped lang="scss">
.database-monitor {
  padding: 20px;
}

.monitor-content {
  margin-top: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;

  .stat-icon {
    width: 80px;
    height: 80px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;

    &.tdengine {
      background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
      color: white;
    }

    &.postgresql {
      background: linear-gradient(135deg, #4E89AE 0%, #5AB9EA 100%);
      color: white;
    }
  }

  .stat-info {
    flex: 1;

    .stat-value {
      font-size: 32px;
      font-weight: bold;
      color: #303133;
    }

    .stat-label {
      font-size: 14px;
      color: #909399;
      margin-top: 5px;
    }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.database-status {
  .db-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #EBEEF5;

    h3 {
      margin: 0;
      font-size: 18px;
      color: #303133;
    }
  }

  .db-details {
    .detail-item {
      display: flex;
      padding: 8px 0;
      border-bottom: 1px solid #F2F6FC;

      &:last-child {
        border-bottom: none;
      }

      .label {
        width: 80px;
        color: #909399;
        font-size: 14px;
      }

      .value {
        flex: 1;
        color: #606266;
        font-size: 14px;
        word-break: break-all;
      }
    }
  }
}

.routing-section {
  padding: 15px;
  background: #F8F9FA;
  border-radius: 8px;
  min-height: 300px;

  .routing-title {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0 0 10px 0;
    font-size: 16px;
    color: #303133;
  }

  .routing-purpose {
    color: #606266;
    margin: 10px 0;
    font-size: 14px;
  }

  .routing-features {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #E4E7ED;

    p {
      margin: 0 0 10px 0;
      color: #303133;
      font-size: 14px;
    }

    ul {
      margin: 0;
      padding-left: 20px;

      li {
        color: #606266;
        font-size: 13px;
        line-height: 1.8;
      }
    }
  }
}
</style>
