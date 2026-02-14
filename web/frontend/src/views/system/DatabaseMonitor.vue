<template>
  <div class="database-monitor">

    <div class="page-header">
      <h1 class="page-title">数据库监控</h1>
      <p class="page-subtitle">DATABASE MONITORING | HEALTH CHECK | ROUTING INFO</p>
      <div class="decorative-line"></div>
    </div>

    <div class="monitor-content">
      <div class="stats-grid">
        <div class="artde-card stat-card">
          <div class="stat-icon tdengine">
            <span>🔲</span>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ healthData.summary?.healthy || 0 }}/{{ healthData.summary?.total_databases || 2 }}</div>
            <div class="stat-label">健康数据库</div>
          </div>
        </div>

        <div class="artde-card stat-card">
          <div class="stat-icon postgresql">
            <span>🐘</span>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statsData.total_classifications || 34 }}</div>
            <div class="stat-label">数据分类总数</div>
          </div>
        </div>
      </div>

      <div class="artde-card health-card">
        <div class="card-header">
          <span class="section-title">数据库健康状态</span>
          <span class="status-badge" :class="healthData.summary?.healthy === 2 ? 'success' : 'danger'">
            {{ healthData.summary?.healthy === 2 ? '全部正常' : '存在异常' }}
          </span>
        </div>

        <div class="databases-section">
          <div class="database-status" v-if="healthData.tdengine">
            <div class="db-header">
              <h3 class="db-title">TDengine</h3>
              <span class="status-badge small" :class="healthData.tdengine?.status === 'healthy' ? 'success' : 'danger'">
                {{ healthData.tdengine?.status === 'healthy' ? '正常' : '异常' }}
              </span>
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

          <div class="database-status" v-if="healthData.postgresql">
            <div class="db-header">
              <h3 class="db-title">PostgreSQL</h3>
              <span class="status-badge small" :class="healthData.postgresql?.status === 'healthy' ? 'success' : 'danger'">
                {{ healthData.postgresql?.status === 'healthy' ? '正常' : '异常' }}
              </span>
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
        </div>
      </div>

      <div class="artde-card routing-card">
        <div class="card-header">
          <span class="section-title">数据路由分布</span>
        </div>

        <div class="routing-grid">
          <div class="routing-box tdengine">
            <h4 class="routing-title">
              <span>🗃️</span>
              TDengine ({{ statsData.routing?.tdengine?.count || 5 }}项)
            </h4>
            <p class="routing-purpose">{{ statsData.routing?.tdengine?.purpose }}</p>
            <div class="routing-tags">
              <span
                v-for="(item, _idx) in statsData.routing?.tdengine?.classifications"
                :key="item"
                class="tag danger"
              >
                {{ item }}
              </span>
            </div>
          </div>

          <div class="routing-box postgresql">
            <h4 class="routing-title">
              <span>🐘</span>
              PostgreSQL ({{ statsData.routing?.postgresql?.count || 29 }}项)
            </h4>
            <p class="routing-purpose">{{ statsData.routing?.postgresql?.purpose }}</p>
            <div class="routing-tags">
              <span
                v-for="(category, _idx) in statsData.routing?.postgresql?.categories"
                :key="category"
                class="tag primary"
              >
                {{ category }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="artde-card info-card">
        <div class="card-header">
          <span class="section-title">架构简化历史</span>
        </div>

        <div class="info-grid">
          <div class="info-item">
            <label>架构类型</label>
            <span>{{ statsData.architecture }}</span>
          </div>
          <div class="info-item">
            <label>简化日期</label>
            <span>{{ statsData.simplification_date }}</span>
          </div>
          <div class="info-item">
            <label>简化前</label>
            <span>{{ statsData.simplified_from }}</span>
          </div>
          <div class="info-item">
            <label>简化后</label>
            <span>{{ statsData.simplified_to }}</span>
          </div>
          <div class="info-item">
            <label>MySQL状态</label>
            <span>
              <span class="tag">{{ statsData.removed_databases?.mysql?.status }}</span>
              已迁移至{{ statsData.removed_databases?.mysql?.migrated_to }} ({{ statsData.removed_databases?.mysql?.rows_migrated }}行)
            </span>
          </div>
          <div class="info-item">
            <label>Redis状态</label>
            <span>
              <span class="tag">{{ statsData.removed_databases?.redis?.status }}</span>
              {{ statsData.removed_databases?.redis?.reason }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

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

const _loading = ref<boolean>(false)
const healthData = ref<HealthData>({})
const statsData = ref<StatsData>({})

const fetchHealthData = async (): Promise<void> => {
  try {
    const response = await fetch('/api/system/database/health')
    healthData.value = await response.json()
  } catch (error) {
    console.error('获取数据库健康状态失败:', error)
    ElMessage.error('获取数据库健康状态失败')
  }
}

const fetchStatsData = async (): Promise<void> => {
  try {
    const response = await fetch('/api/system/database/stats')
    statsData.value = await response.json()
  } catch (error) {
    console.error('获取数据库统计信息失败:', error)
    ElMessage.error('获取数据库统计信息失败')
  }
}

onMounted(() => {
  fetchHealthData()
  fetchStatsData()
})
</script>

<style scoped lang="scss">
@import "./styles/DatabaseMonitor.scss";
</style>
