import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiGet } from '@/api/apiClient';
import type { UnifiedResponse } from '@/api/apiClient';

// 补充缺失的类型定义
interface SystemHealthData {
  status: string;
  api_status?: 'online' | 'offline' | 'degraded';
  total_endpoints?: number;
  api_status_text?: string;
  data_quality_status?: 'good' | 'warning' | 'error';
  data_quality_score?: number;
  system_load_status?: 'low' | 'medium' | 'high';
  system_load_percent?: number;
}

interface SystemInfoData {
  version: string;
}

export interface TradeOrder {
  id: string;
  symbol: string;
  type: 'buy' | 'sell';
  quantity: number;
  price: number;
  status: 'pending' | 'filled' | 'cancelled';
  timestamp: Date;
}

export const useTradingStore = defineStore('trading', () => {
  // State
  const orders = ref<TradeOrder[]>([]);
  const currentSymbol = ref<string>('');
  const isTradingEnabled = ref(true);

  // System Status State (for ArtDecoTradingCenter)
  const systemStatus = ref('正在初始化...');
  const statusType = ref<'success' | 'warning' | 'error'>('warning');
  const apiStatus = ref<'online' | 'offline' | 'degraded'>('degraded');
  const apiStatusText = ref('加载中...');
  const dataQualityStatus = ref<'good' | 'warning' | 'error'>('warning');
  const dataQualityScore = ref('--');
  const systemLoadStatus = ref<'low' | 'medium' | 'high'>('medium');
  const systemLoadPercent = ref('0%');
  const version = ref('...'); // Initial placeholder for version
  const lastUpdateTime = ref('--:--:--');


  // Actions
  const addOrder = (order: Omit<TradeOrder, 'id' | 'timestamp'>) => {
    const newOrder: TradeOrder = {
      ...order,
      id: Date.now().toString(),
      timestamp: new Date(),
    };
    orders.value.push(newOrder);
  };

  const cancelOrder = (orderId: string) => {
    const order = orders.value.find((o) => o.id === orderId);
    if (order) {
      order.status = 'cancelled';
    }
  };

  const setCurrentSymbol = (symbol: string) => {
    currentSymbol.value = symbol;
  };

  const clearOrders = () => {
    orders.value = [];
  };

  const switchActiveFunction = (funcName: string) => {
    console.log('Switching to function:', funcName);
  };

  const fetchSystemStatus = async () => {
    try {
      // Fetch system health
      const healthResponse = await apiGet<UnifiedResponse<SystemHealthData>>('/api/health'); // Assuming this endpoint exists
      if (healthResponse.success && healthResponse.data) {
        systemStatus.value = healthResponse.data.status === 'ok' ? '正常运行' : '部分故障';
        statusType.value = healthResponse.data.status === 'ok' ? 'success' : 'warning';
        apiStatus.value = healthResponse.data.api_status || 'degraded';
        apiStatusText.value = `${healthResponse.data.total_endpoints || 'N/A'}个端点 (${healthResponse.data.api_status_text || '部分故障'})`;
        dataQualityStatus.value = healthResponse.data.data_quality_status || 'warning';
        dataQualityScore.value = healthResponse.data.data_quality_score ? `${healthResponse.data.data_quality_score}%` : '--';
        systemLoadStatus.value = healthResponse.data.system_load_status || 'medium';
        systemLoadPercent.value = healthResponse.data.system_load_percent ? `${healthResponse.data.system_load_percent}%` : '0%';
      } else {
        throw new Error(healthResponse.message || 'Failed to fetch system health');
      }

      // Fetch system info for version
      const infoResponse = await apiGet<UnifiedResponse<SystemInfoData>>('/api/system/info'); // Assuming this endpoint exists
      if (infoResponse.success && infoResponse.data) {
        version.value = infoResponse.data.version || 'unknown';
      } else {
        throw new Error(infoResponse.message || 'Failed to fetch system info');
      }

    } catch (error) {
      console.error('Failed to fetch system status:', error);
      systemStatus.value = '系统故障';
      statusType.value = 'error';
      apiStatus.value = 'offline';
      apiStatusText.value = 'API服务离线';
      dataQualityStatus.value = 'error';
      dataQualityScore.value = '0%';
      systemLoadStatus.value = 'high';
      systemLoadPercent.value = '100%';
      version.value = 'error';
    } finally {
      updateLastUpdateTime();
    }
  };

  const refreshAllData = async () => {
    console.log('Refreshing all trading data and system status...');
    await fetchSystemStatus();
    // Potentially add other data refresh calls here later
  };

  const updateLastUpdateTime = () => {
    const now = new Date();
    lastUpdateTime.value = now.toLocaleTimeString('zh-CN', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  // Initial fetch on store creation
  fetchSystemStatus();
  setInterval(fetchSystemStatus, 60000); // Refresh every minute

  return {
    // State
    orders,
    currentSymbol,
    isTradingEnabled,
    systemConfig: ref({ refreshRate: 5000, notifications: true }), // Keep as ref to satisfy existing usage
    systemStatus,
    statusType,
    apiStatus,
    apiStatusText,
    dataQualityStatus,
    dataQualityScore,
    systemLoadStatus,
    systemLoadPercent,
    version,
    lastUpdateTime,

    // Actions
    addOrder,
    cancelOrder,
    setCurrentSymbol,
    clearOrders,
    switchActiveFunction,
    refreshAllData,
    fetchSystemStatus,
    updateLastUpdateTime,
  };
});

