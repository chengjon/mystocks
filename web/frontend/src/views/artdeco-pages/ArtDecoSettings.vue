<template>
    <div class="artdeco-settings">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-content">
                <h1 class="page-title">系统设置</h1>
                <p class="page-subtitle">个性化配置您的量化交易平台</p>
            </div>
            <div class="header-actions">
                <ArtDecoButton variant="outline" size="sm" @click="resetToDefaults">重置默认</ArtDecoButton>
                <ArtDecoButton variant="solid" @click="saveSettings">保存设置</ArtDecoButton>
            </div>
        </div>

        <!-- Settings Tabs -->
        <nav class="settings-tabs">
            <button
                v-for="(tab, _idx) in settingsTabs"
                :key="tab.key"
                class="settings-tab"
                :class="{ active: activeTab === tab.key }"
                @click="switchTab(tab.key)"
            >
                <span class="tab-icon">{{ tab.icon }}</span>
                <span class="tab-label">{{ tab.label }}</span>
            </button>
        </nav>

        <!-- Tab Content -->
        <div class="tab-content">
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

            <!-- 通知设置 -->
            <div v-if="activeTab === 'notifications'" class="tab-panel">
                <ArtDecoCard title="通知偏好" hoverable class="notifications-card">
                    <div class="notification-settings">
                        <div class="notification-category">
                            <h4>交易通知</h4>
                            <div class="setting-group">
                                <div class="setting-item">
                                    <div class="setting-info">
                                        <div class="setting-label">订单成交通知</div>
                                        <div class="setting-desc">订单成交时发送通知</div>
                                    </div>
                                    <div class="notification-options">
                                        <label class="option-label">
                                            <input type="checkbox" v-model="settings.notifications.trade.orderFilled" />
                                            启用
                                        </label>
                                        <ArtDecoSelect
                                            v-model="settings.notifications.trade.orderFilledChannel"
                                            :options="channelOptions"
                                            size="sm"
                                            class="channel-select"
                                        />
                                    </div>
                                </div>

                                <div class="setting-item">
                                    <div class="setting-info">
                                        <div class="setting-label">止损触发通知</div>
                                        <div class="setting-desc">止损规则触发时发送通知</div>
                                    </div>
                                    <div class="notification-options">
                                        <label class="option-label">
                                            <input type="checkbox" v-model="settings.notifications.trade.stopLoss" />
                                            启用
                                        </label>
                                        <ArtDecoSelect
                                            v-model="settings.notifications.trade.stopLossChannel"
                                            :options="channelOptions"
                                            size="sm"
                                            class="channel-select"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="notification-category">
                            <h4>风险通知</h4>
                            <div class="setting-group">
                                <div class="setting-item">
                                    <div class="setting-info">
                                        <div class="setting-label">VaR阈值告警</div>
                                        <div class="setting-desc">VaR超过阈值时发送告警</div>
                                    </div>
                                    <div class="notification-options">
                                        <label class="option-label">
                                            <input type="checkbox" v-model="settings.notifications.risk.varAlert" />
                                            启用
                                        </label>
                                        <ArtDecoSelect
                                            v-model="settings.notifications.risk.varAlertChannel"
                                            :options="channelOptions"
                                            size="sm"
                                            class="channel-select"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="notification-category">
                            <h4>系统通知</h4>
                            <div class="setting-group">
                                <div class="setting-item">
                                    <div class="setting-info">
                                        <div class="setting-label">维护通知</div>
                                        <div class="setting-desc">系统维护和更新通知</div>
                                    </div>
                                    <div class="notification-options">
                                        <label class="option-label">
                                            <input
                                                type="checkbox"
                                                v-model="settings.notifications.system.maintenance"
                                            />
                                            启用
                                        </label>
                                        <ArtDecoSelect
                                            v-model="settings.notifications.system.maintenanceChannel"
                                            :options="channelOptions"
                                            size="sm"
                                            class="channel-select"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </ArtDecoCard>

                <ArtDecoCard title="通知渠道配置" hoverable class="channels-card">
                    <div class="channel-config">
                        <div class="channel-item">
                            <div class="channel-header">
                                <div class="channel-name">📧 邮件通知</div>
                                <label class="toggle-label">
                                    <input type="checkbox" v-model="settings.channels.email.enabled" />
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>
                            <div class="channel-settings" v-if="settings.channels.email.enabled">
                                <div class="setting-row">
                                    <label>SMTP服务器:</label>
                                    <ArtDecoInput
                                        v-model="settings.channels.email.smtp"
                                        placeholder="smtp.example.com"
                                        class="channel-input"
                                    />
                                </div>
                                <div class="setting-row">
                                    <label>端口:</label>
                                    <ArtDecoInput
                                        v-model.number="settings.channels.email.port"
                                        type="number"
                                        placeholder="587"
                                        class="channel-input"
                                    />
                                </div>
                                <div class="setting-row">
                                    <label>邮箱地址:</label>
                                    <ArtDecoInput
                                        v-model="settings.channels.email.address"
                                        type="email"
                                        placeholder="your@email.com"
                                        class="channel-input"
                                    />
                                </div>
                            </div>
                        </div>

                        <div class="channel-item">
                            <div class="channel-header">
                                <div class="channel-name">📱 短信通知</div>
                                <label class="toggle-label">
                                    <input type="checkbox" v-model="settings.channels.sms.enabled" />
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>
                            <div class="channel-settings" v-if="settings.channels.sms.enabled">
                                <div class="setting-row">
                                    <label>手机号码:</label>
                                    <ArtDecoInput
                                        v-model="settings.channels.sms.phone"
                                        placeholder="+86 13800138000"
                                        class="channel-input"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </ArtDecoCard>
            </div>

            <!-- 安全设置 -->
            <div v-if="activeTab === 'security'" class="tab-panel">
                <ArtDecoCard title="账户安全" hoverable class="security-card">
                    <div class="security-settings">
                        <div class="setting-item">
                            <div class="setting-info">
                                <div class="setting-label">双因子认证</div>
                                <div class="setting-desc">启用两步验证增强账户安全</div>
                            </div>
                            <div class="security-status">
                                <span class="status-text" :class="settings.security.twoFactor ? 'enabled' : 'disabled'">
                                    {{ settings.security.twoFactor ? '已启用' : '未启用' }}
                                </span>
                                <ArtDecoButton variant="outline" size="sm">
                                    {{ settings.security.twoFactor ? '管理' : '启用' }}
                                </ArtDecoButton>
                            </div>
                        </div>

                        <div class="setting-item">
                            <div class="setting-info">
                                <div class="setting-label">登录会话管理</div>
                                <div class="setting-desc">查看和管理活跃登录会话</div>
                            </div>
                            <ArtDecoButton variant="outline" size="sm">查看会话</ArtDecoButton>
                        </div>

                        <div class="setting-item">
                            <div class="setting-info">
                                <div class="setting-label">API访问令牌</div>
                                <div class="setting-desc">管理API访问令牌和权限</div>
                            </div>
                            <ArtDecoButton variant="outline" size="sm">管理令牌</ArtDecoButton>
                        </div>
                    </div>
                </ArtDecoCard>

                <ArtDecoCard title="密码安全" hoverable class="password-card">
                    <div class="password-settings">
                        <div class="setting-item">
                            <div class="setting-info">
                                <div class="setting-label">密码强度要求</div>
                                <div class="setting-desc">设置密码复杂性要求</div>
                            </div>
                            <ArtDecoSelect
                                v-model="settings.security.passwordStrength"
                                :options="passwordStrengthOptions"
                                class="setting-control"
                            />
                        </div>

                        <div class="setting-item">
                            <div class="setting-info">
                                <div class="setting-label">自动登出时间</div>
                                <div class="setting-desc">无活动时的自动登出时间</div>
                            </div>
                            <ArtDecoSelect
                                v-model="settings.security.autoLogout"
                                :options="autoLogoutOptions"
                                class="setting-control"
                            />
                        </div>

                        <div class="setting-item">
                            <div class="setting-info">
                                <div class="setting-label">修改密码</div>
                                <div class="setting-desc">定期更换密码以增强安全性</div>
                            </div>
                            <ArtDecoButton variant="solid">修改密码</ArtDecoButton>
                        </div>
                    </div>
                </ArtDecoCard>
            </div>

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
        </div>
    </div>
</template>

<script setup>
    import { ref } from 'vue'
    import { _ArtDecoStatCard, ArtDecoCard, ArtDecoButton, ArtDecoInput, ArtDecoSelect } from '@/components/artdeco'

    // 响应式数据
    const activeTab = ref('appearance')

    // 设置数据
    const settings = ref({
        theme: 'artdeco',
        fontSize: 'medium',
        compactMode: false,
        decimalPlaces: '2',
        thousandSeparator: true,
        updateFrequency: '30',
        language: 'zh-CN',
        timezone: 'Asia/Shanghai',
        currency: 'CNY',
        dataValidation: true,
        anomalyDetection: true,
        dataCaching: true,
        security: {
            twoFactor: false,
            passwordStrength: 'strong',
            autoLogout: '60'
        },
        notifications: {
            trade: {
                orderFilled: true,
                orderFilledChannel: 'email',
                stopLoss: true,
                stopLossChannel: 'sms'
            },
            risk: {
                varAlert: true,
                varAlertChannel: 'email'
            },
            system: {
                maintenance: true,
                maintenanceChannel: 'email'
            }
        },
        channels: {
            email: {
                enabled: true,
                smtp: 'smtp.gmail.com',
                port: 587,
                address: 'user@example.com'
            },
            sms: {
                enabled: false,
                phone: ''
            }
        }
    })

    // 数据源配置
    const dataSources = ref([
        {
            id: 'akshare',
            name: 'AKShare',
            type: '股票数据',
            status: 'healthy',
            statusText: '正常',
            apiKey: '',
            secretKey: '',
            rateLimit: 100,
            enabled: true
        },
        {
            id: 'tdx',
            name: '通达信',
            type: '实时行情',
            status: 'healthy',
            statusText: '正常',
            apiKey: '',
            secretKey: '',
            rateLimit: 200,
            enabled: true
        },
        {
            id: 'efinance',
            name: '东方财富',
            type: '财务数据',
            status: 'warning',
            statusText: '警告',
            apiKey: '',
            secretKey: '',
            rateLimit: 50,
            enabled: true
        }
    ])

    // 系统信息
    const systemInfo = ref({
        cpuUsage: 45,
        memoryUsage: 67,
        diskUsage: 78,
        networkLatency: 25,
        version: '2.1.0',
        buildTime: '2024-01-15 10:30:00',
        lastUpdate: '2024-01-15',
        license: 'Professional',
        dataStats: {
            totalRecords: '2,345,678',
            dataSources: 8,
            cacheHitRate: 94.5,
            apiCalls: '1,234,567'
        }
    })

    // 设置标签页
    const settingsTabs = [
        { key: 'appearance', label: '外观设置', icon: '🎨' },
        { key: 'data-sources', label: '数据源', icon: '🔗' },
        { key: 'notifications', label: '通知', icon: '🔔' },
        { key: 'security', label: '安全', icon: '🔒' },
        { key: 'system', label: '系统', icon: '⚙️' }
    ]

    // 选项配置
    const themeOptions = [
        { label: 'ArtDeco奢华', value: 'artdeco' },
        { label: '深色主题', value: 'dark' },
        { label: '浅色主题', value: 'light' }
    ]

    const fontSizeOptions = [
        { label: '小', value: 'small' },
        { label: '中', value: 'medium' },
        { label: '大', value: 'large' }
    ]

    const decimalOptions = [
        { label: '1位', value: '1' },
        { label: '2位', value: '2' },
        { label: '3位', value: '3' },
        { label: '4位', value: '4' }
    ]

    const frequencyOptions = [
        { label: '10秒', value: '10' },
        { label: '30秒', value: '30' },
        { label: '1分钟', value: '60' },
        { label: '5分钟', value: '300' }
    ]

    const languageOptions = [
        { label: '中文(简体)', value: 'zh-CN' },
        { label: 'English', value: 'en-US' }
    ]

    const timezoneOptions = [
        { label: '北京时间 (UTC+8)', value: 'Asia/Shanghai' },
        { label: '纽约时间 (UTC-5)', value: 'America/New_York' },
        { label: '伦敦时间 (UTC+0)', value: 'Europe/London' }
    ]

    const currencyOptions = [
        { label: '人民币 (CNY)', value: 'CNY' },
        { label: '美元 (USD)', value: 'USD' },
        { label: '港币 (HKD)', value: 'HKD' }
    ]

    const channelOptions = [
        { label: '邮件', value: 'email' },
        { label: '短信', value: 'sms' },
        { label: '应用内通知', value: 'app' }
    ]

    const passwordStrengthOptions = [
        { label: '弱', value: 'weak' },
        { label: '中', value: 'medium' },
        { label: '强', value: 'strong' },
        { label: '极强', value: 'very-strong' }
    ]

    const autoLogoutOptions = [
        { label: '15分钟', value: '15' },
        { label: '30分钟', value: '30' },
        { label: '60分钟', value: '60' },
        { label: '永不', value: 'never' }
    ]

    // 方法
    const switchTab = tabKey => {
        activeTab.value = tabKey
    }

    const saveSettings = () => {
        // 保存设置逻辑
        console.log('Saving settings:', settings.value)
    }

    const resetToDefaults = () => {
        // 重置默认设置逻辑
        console.log('Resetting to defaults')
    }
</script>

<style scoped lang="scss">
@import './styles/ArtDecoSettings.scss';
</style>
