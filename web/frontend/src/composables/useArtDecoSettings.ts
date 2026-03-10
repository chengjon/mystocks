// ArtDeco Settings composable
import { ref } from 'vue'

export function useArtDecoSettings() {
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
              autoLogout: 60
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
      const switchTab = (tabKey: string) => {
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

  // Return all reactive state and methods for template binding
  return {
    activeTab,
    settings,
    dataSources,
    systemInfo,
    settingsTabs,
    themeOptions,
    fontSizeOptions,
    decimalOptions,
    frequencyOptions,
    languageOptions,
    timezoneOptions,
    currencyOptions,
    channelOptions,
    passwordStrengthOptions,
    autoLogoutOptions,
    switchTab,
    saveSettings,
    resetToDefaults,
  }
}
