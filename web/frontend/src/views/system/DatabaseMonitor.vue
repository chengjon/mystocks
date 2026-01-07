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
                v-for="item in statsData.routing?.tdengine?.classifications"
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
                v-for="category in statsData.routing?.postgresql?.categories"
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

const loading = ref<boolean>(false)
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

.database-monitor {
  padding: 20px;
  min-height: 100vh;
  background: var(--bg-primary);
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
}

  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.04;
  background-image:
    repeating-linear-gradient(45deg, var(--gold-primary) 0px, var(--gold-primary) 1px, transparent 1px, transparent 10px),
    repeating-linear-gradient(-45deg, var(--gold-primary) 0px, var(--gold-primary) 1px, transparent 1px, transparent 10px);
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 30px 0;
  position: relative;

  .page-title {
    font-family: var(--font-display);
    font-size: 32px;
    color: var(--gold-primary);
    text-transform: uppercase;
    letter-spacing: 4px;
    margin: 0 0 8px 0;
  }

  .page-subtitle {
    font-family: var(--font-body);
    font-size: 12px;
    color: var(--gold-muted);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin: 0;
  }

  .decorative-line {
    width: 200px;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold-primary), transparent);
    margin: 20px auto 0;

    &::before {
      content: '';
      position: absolute;
      bottom: -6px;
      left: 50%;
      transform: translateX(-50%);
      width: 60px;
      height: 1px;
      background: linear-gradient(90deg, transparent, var(--gold-muted), transparent);
    }
  }
}

.artde-card {
  background: var(--bg-secondary);
  border: 1px solid var(--gold-dim);
  padding: 20px;
  position: relative;
  border-radius: 0;
  margin-bottom: 20px;

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

  &:hover {
    border-color: var(--gold-primary);
    box-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
  }
}

.monitor-content {
  margin-top: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;

  .stat-icon {
    width: 64px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(212, 175, 55, 0.1);
    border: 1px solid var(--gold-dim);
    font-size: 32px;
  }

  .stat-info {
    flex: 1;

    .stat-value {
      font-family: var(--font-display);
      font-size: 32px;
      color: var(--gold-primary);
      text-transform: uppercase;
      letter-spacing: 2px;
      margin-bottom: 4px;
    }

    .stat-label {
      font-family: var(--font-body);
      font-size: 12px;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 1px;
    }
  }
}

.section-title {
  font-family: var(--font-display);
  font-size: 16px;
  color: var(--gold-primary);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin: 0 0 15px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--gold-dim);
  margin-bottom: 20px;
}

.status-badge {
  padding: 6px 14px;
  background: rgba(212, 175, 55, 0.1);
  border: 1px solid var(--gold-dim);
  color: var(--gold-primary);
  font-family: var(--font-display);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;

  &.success {
    background: rgba(0, 230, 118, 0.15);
    border-color: var(--fall);
    color: var(--fall);
  }

  &.danger {
    background: rgba(255, 82, 82, 0.15);
    border-color: var(--rise);
    color: var(--rise);
  }

  &.small {
    padding: 4px 10px;
    font-size: 10px;
  }
}

.databases-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.database-status {
  background: var(--bg-primary);
  border: 1px solid var(--gold-dim);

  .db-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    background: rgba(212, 175, 55, 0.05);
    border-bottom: 1px solid var(--gold-dim);

    .db-title {
      font-family: var(--font-display);
      font-size: 16px;
      color: var(--gold-primary);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin: 0;
    }
  }

  .db-details {
    .detail-item {
      display: flex;
      padding: 12px 20px;
      border-bottom: 1px solid var(--gold-dim);

      &:last-child {
        border-bottom: none;
      }

      .label {
        width: 80px;
        color: var(--text-muted);
        font-family: var(--font-body);
        font-size: 14px;
      }

      .value {
        flex: 1;
        color: var(--text-primary);
        font-family: var(--font-body);
        font-size: 14px;
        word-break: break-all;
      }
    }
  }
}

.routing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.routing-box {
  background: var(--bg-primary);
  border: 1px solid var(--gold-dim);
  padding: 20px;

  .routing-title {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;

    span {
      font-size: 20px;
    }

    h4 {
      font-family: var(--font-display);
      font-size: 14px;
      color: var(--gold-primary);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin: 0;
    }
  }

  .routing-purpose {
    color: var(--text-muted);
    font-family: var(--font-body);
    font-size: 13px;
    margin: 0 0 15px 0;
  }
}

.routing-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;

  .tag {
    padding: 4px 10px;
    font-family: var(--font-display);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;

    &.danger {
      background: rgba(255, 82, 82, 0.15);
      border-color: var(--rise);
      color: var(--rise);
    }

    &.primary {
      background: rgba(64, 158, 255, 0.15);
      border-color: #409EFF;
      color: #409EFF;
    }
  }
}

.info-card {
  .info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 15px;

    .info-item {
      display: flex;
      flex-direction: column;
      gap: 8px;

      label {
        font-family: var(--font-display);
        font-size: 11px;
        color: var(--gold-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
      }

      span {
        color: var(--text-primary);
        font-family: var(--font-body);
        font-size: 14px;
      }

      .tag {
        display: inline-block;
        padding: 4px 10px;
        font-family: var(--font-display);
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        background: rgba(212, 175, 55, 0.15);
        border: 1px solid var(--gold-dim);
        color: var(--gold-primary);
        margin-right: 5px;
      }
    }
  }
}

@media (max-width: 768px) {
  .database-monitor {
    padding: 10px;
  }

  .page-header {
    padding: 20px 0;

    .page-title {
      font-size: 24px;
      letter-spacing: 2px;
    }
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .databases-section {
    grid-template-columns: 1fr;
  }

  .routing-grid {
    grid-template-columns: 1fr;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
