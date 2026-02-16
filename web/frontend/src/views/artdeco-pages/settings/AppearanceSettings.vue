<template>
            <!-- 外观设置 -->
            <div v-if="activeTab === 'appearance'" class="tab-panel">
                <div class="settings-grid">
                    <ArtDecoCard title="主题设置" hoverable class="theme-card">
                        <div class="setting-group">
                            <div class="setting-item">
                                <div class="setting-info">
                                    <div class="setting-label">界面主题</div>
                                    <div class="setting-desc">选择您偏好的视觉主题</div>
                                </div>
                                <ArtDecoSelect
                                    v-model="settings.theme"
                                    :options="themeOptions"
                                    class="setting-control"
                                />
                            </div>

                            <div class="setting-item">
                                <div class="setting-info">
                                    <div class="setting-label">字体大小</div>
                                    <div class="setting-desc">调整界面字体大小</div>
                                </div>
                                <ArtDecoSelect
                                    v-model="settings.fontSize"
                                    :options="fontSizeOptions"
                                    class="setting-control"
                                />
                            </div>

                            <div class="setting-item">
                                <div class="setting-info">
                                    <div class="setting-label">紧凑模式</div>
                                    <div class="setting-desc">减少界面空白，提升信息密度</div>
                                </div>
                                <label class="toggle-label">
                                    <input type="checkbox" v-model="settings.compactMode" />
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>
                        </div>
                    </ArtDecoCard>

                    <ArtDecoCard title="数据显示" hoverable class="display-card">
                        <div class="setting-group">
                            <div class="setting-item">
                                <div class="setting-info">
                                    <div class="setting-label">小数位数</div>
                                    <div class="setting-desc">价格和数值的显示精度</div>
                                </div>
                                <ArtDecoSelect
                                    v-model="settings.decimalPlaces"
                                    :options="decimalOptions"
                                    class="setting-control"
                                />
                            </div>

                            <div class="setting-item">
                                <div class="setting-info">
                                    <div class="setting-label">千分位分隔符</div>
                                    <div class="setting-desc">数字显示时是否使用千分位分隔</div>
                                </div>
                                <label class="toggle-label">
                                    <input type="checkbox" v-model="settings.thousandSeparator" />
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>

                            <div class="setting-item">
                                <div class="setting-info">
                                    <div class="setting-label">实时更新频率</div>
                                    <div class="setting-desc">数据自动刷新的间隔时间</div>
                                </div>
                                <ArtDecoSelect
                                    v-model="settings.updateFrequency"
                                    :options="frequencyOptions"
                                    class="setting-control"
                                />
                            </div>
                        </div>
                    </ArtDecoCard>

                    <ArtDecoCard title="语言与地区" hoverable class="language-card">
                        <div class="setting-group">
                            <div class="setting-item">
                                <div class="setting-info">
                                    <div class="setting-label">界面语言</div>
                                    <div class="setting-desc">选择界面显示语言</div>
                                </div>
                                <ArtDecoSelect
                                    v-model="settings.language"
                                    :options="languageOptions"
                                    class="setting-control"
                                />
                            </div>

                            <div class="setting-item">
                                <div class="setting-info">
                                    <div class="setting-label">时区</div>
                                    <div class="setting-desc">数据显示时区设置</div>
                                </div>
                                <ArtDecoSelect
                                    v-model="settings.timezone"
                                    :options="timezoneOptions"
                                    class="setting-control"
                                />
                            </div>

                            <div class="setting-item">
                                <div class="setting-info">
                                    <div class="setting-label">货币单位</div>
                                    <div class="setting-desc">默认货币显示单位</div>
                                </div>
                                <ArtDecoSelect
                                    v-model="settings.currency"
                                    :options="currencyOptions"
                                    class="setting-control"
                                />
                            </div>
                        </div>
                    </ArtDecoCard>
                </div>
            </div>

</template>

<script setup lang="ts">
import { reactive } from 'vue'
import ArtDecoCard from '@/components/artdeco/ArtDecoCard.vue'
import ArtDecoSelect from '@/components/artdeco/ArtDecoSelect.vue'

defineProps<{
  activeTab?: string
}>()

const settings = reactive({
  theme: 'dark',
  fontSize: 'medium',
  compactMode: false,
  decimalPlaces: 2,
  thousandSeparator: true,
  updateFrequency: '5s',
  language: 'zh-CN',
  timezone: 'Asia/Shanghai',
  currency: 'CNY'
})

const themeOptions = [
  { value: 'dark', label: '深色主题' },
  { value: 'light', label: '浅色主题' },
  { value: 'auto', label: '跟随系统' }
]

const fontSizeOptions = [
  { value: 'small', label: '小' },
  { value: 'medium', label: '中' },
  { value: 'large', label: '大' }
]

const decimalOptions = [
  { value: 0, label: '0位' },
  { value: 2, label: '2位' },
  { value: 3, label: '3位' },
  { value: 4, label: '4位' }
]

const frequencyOptions = [
  { value: '1s', label: '1秒' },
  { value: '5s', label: '5秒' },
  { value: '10s', label: '10秒' },
  { value: '30s', label: '30秒' }
]

const languageOptions = [
  { value: 'zh-CN', label: '简体中文' },
  { value: 'en-US', label: 'English' }
]

const timezoneOptions = [
  { value: 'Asia/Shanghai', label: '北京时间 (UTC+8)' },
  { value: 'UTC', label: 'UTC' }
]

const currencyOptions = [
  { value: 'CNY', label: '人民币 (CNY)' },
  { value: 'USD', label: '美元 (USD)' }
]
</script>
