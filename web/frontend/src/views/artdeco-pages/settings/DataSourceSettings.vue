<template>
            <!-- 数据源设置 -->
            <div v-if="activeTab === 'data-sources'" class="tab-panel">
                <ArtDecoCard title="数据源配置" hoverable class="data-sources-card">
                    <div class="data-source-list">
                        <div class="data-source-item" v-for="source in dataSources" :key="source.id">
                            <div class="source-header">
                                <div class="source-info">
                                    <div class="source-name">{{ source.name }}</div>
                                    <div class="source-type">{{ source.type }}</div>
                                </div>
                                <div class="source-status" :class="source.status">
                                    {{ source.statusText }}
                                </div>
                            </div>

                            <div class="source-config">
                                <div class="config-row">
                                    <label>API Key:</label>
                                    <ArtDecoInput
                                        v-model="source.apiKey"
                                        type="password"
                                        placeholder="输入API密钥"
                                        class="config-input"
                                    />
                                </div>

                                <div class="config-row">
                                    <label>Secret Key:</label>
                                    <ArtDecoInput
                                        v-model="source.secretKey"
                                        type="password"
                                        placeholder="输入密钥"
                                        class="config-input"
                                    />
                                </div>

                                <div class="config-row">
                                    <label>请求频率限制:</label>
                                    <ArtDecoInput
                                        v-model.number="source.rateLimit"
                                        type="number"
                                        placeholder="每分钟请求次数"
                                        class="config-input"
                                    />
                                </div>

                                <div class="config-row">
                                    <label>启用状态:</label>
                                    <label class="toggle-label">
                                        <input type="checkbox" v-model="source.enabled" />
                                        <span class="toggle-slider"></span>
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                </ArtDecoCard>

                <ArtDecoCard title="数据质量监控" hoverable class="data-quality-card">
                    <div class="quality-settings">
                        <div class="setting-item">
                            <div class="setting-info">
                                <div class="setting-label">数据验证</div>
                                <div class="setting-desc">启用数据完整性验证</div>
                            </div>
                            <label class="toggle-label">
                                <input type="checkbox" v-model="settings.dataValidation" />
                                <span class="toggle-slider"></span>
                            </label>
                        </div>

                        <div class="setting-item">
                            <div class="setting-info">
                                <div class="setting-label">异常检测</div>
                                <div class="setting-desc">自动检测数据异常</div>
                            </div>
                            <label class="toggle-label">
                                <input type="checkbox" v-model="settings.anomalyDetection" />
                                <span class="toggle-slider"></span>
                            </label>
                        </div>

                        <div class="setting-item">
                            <div class="setting-info">
                                <div class="setting-label">数据缓存</div>
                                <div class="setting-desc">启用本地数据缓存</div>
                            </div>
                            <label class="toggle-label">
                                <input type="checkbox" v-model="settings.dataCaching" />
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                    </div>
                </ArtDecoCard>
            </div>

</template>

<script setup lang="ts">
import { ArtDecoCard, ArtDecoInput } from '@/components/artdeco'

interface DataSource {
  id: string
  name: string
  type: string
  status: string
  statusText: string
  apiKey: string
  secretKey: string
  rateLimit: number
  enabled: boolean
}

interface DataSettings {
  dataValidation: boolean
  anomalyDetection: boolean
  dataCaching: boolean
}

defineProps<{
  activeTab: string
  dataSources: DataSource[]
  settings: DataSettings
}>()
</script>
