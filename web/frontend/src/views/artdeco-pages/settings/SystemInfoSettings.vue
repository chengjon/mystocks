<template>
            <!-- 系统信息 -->
            <div v-if="activeTab === 'system'" class="tab-panel">
                <div class="system-info-grid">
                    <ArtDecoCard title="系统状态" hoverable class="system-status-card">
                        <div class="system-metrics">
                            <div class="metric-item">
                                <div class="metric-label">系统负载</div>
                                <div class="metric-value">{{ systemInfo.cpuUsage }}%</div>
                                <div class="metric-bar">
                                    <div class="bar-fill" :style="{ width: systemInfo.cpuUsage + '%' }"></div>
                                </div>
                            </div>

                            <div class="metric-item">
                                <div class="metric-label">内存使用</div>
                                <div class="metric-value">{{ systemInfo.memoryUsage }}%</div>
                                <div class="metric-bar">
                                    <div class="bar-fill" :style="{ width: systemInfo.memoryUsage + '%' }"></div>
                                </div>
                            </div>

                            <div class="metric-item">
                                <div class="metric-label">磁盘使用</div>
                                <div class="metric-value">{{ systemInfo.diskUsage }}%</div>
                                <div class="metric-bar">
                                    <div class="bar-fill" :style="{ width: systemInfo.diskUsage + '%' }"></div>
                                </div>
                            </div>

                            <div class="metric-item">
                                <div class="metric-label">网络延迟</div>
                                <div class="metric-value">{{ systemInfo.networkLatency }}ms</div>
                                <div
                                    class="metric-status"
                                    :class="systemInfo.networkLatency < 100 ? 'good' : 'warning'"
                                >
                                    {{ systemInfo.networkLatency < 100 ? '良好' : '一般' }}
                                </div>
                            </div>
                        </div>
                    </ArtDecoCard>

                    <ArtDecoCard title="版本信息" hoverable class="version-card">
                        <div class="version-info">
                            <div class="version-item">
                                <div class="version-label">MyStocks版本</div>
                                <div class="version-value">{{ systemInfo.version }}</div>
                            </div>

                            <div class="version-item">
                                <div class="version-label">构建时间</div>
                                <div class="version-value">{{ systemInfo.buildTime }}</div>
                            </div>

                            <div class="version-item">
                                <div class="version-label">最后更新</div>
                                <div class="version-value">{{ systemInfo.lastUpdate }}</div>
                            </div>

                            <div class="version-item">
                                <div class="version-label">许可证</div>
                                <div class="version-value">{{ systemInfo.license }}</div>
                            </div>
                        </div>
                    </ArtDecoCard>

                    <ArtDecoCard title="数据统计" hoverable class="data-stats-card">
                        <div class="data-statistics">
                            <div class="stat-item">
                                <div class="stat-label">历史数据条数</div>
                                <div class="stat-value">{{ systemInfo.dataStats.totalRecords }}</div>
                            </div>

                            <div class="stat-item">
                                <div class="stat-label">数据源数量</div>
                                <div class="stat-value">{{ systemInfo.dataStats.dataSources }}</div>
                            </div>

                            <div class="stat-item">
                                <div class="stat-label">缓存命中率</div>
                                <div class="stat-value">{{ systemInfo.dataStats.cacheHitRate }}%</div>
                            </div>

                            <div class="stat-item">
                                <div class="stat-label">API调用次数</div>
                                <div class="stat-value">{{ systemInfo.dataStats.apiCalls }}</div>
                            </div>
                        </div>
                    </ArtDecoCard>
                </div>
            </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import ArtDecoCard from '@/components/artdeco/ArtDecoCard.vue'

defineProps<{
  activeTab?: string
}>()

const systemInfo = reactive({
  cpuUsage: 45,
  memoryUsage: 62,
  diskUsage: 38,
  networkLatency: 85,
  version: '1.0.0',
  buildTime: '2024-01-15 10:30:00',
  lastUpdate: '2024-01-20 14:22:33',
  databaseSize: '2.3 GB',
  logSize: '128 MB',
  cacheSize: '512 MB',
  license: 'MIT',
  dataStats: {
    totalRecords: '1,234,567',
    dataSources: 12,
    cacheHitRate: 92.5,
    apiCalls: '45,678'
  }
})
</script>
