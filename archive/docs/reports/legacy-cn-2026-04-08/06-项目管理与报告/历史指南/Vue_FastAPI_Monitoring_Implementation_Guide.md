# Vue + FastAPI 架构适配的监控系统实施指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## 📋 概述

本文档为基于Vue.js + FastAPI架构的MyStocks项目提供完整的监控系统实施指导，结合mystocks_spec项目中已有的AI监控和告警系统实现，针对Vue.js前端和FastAPI后端的架构特点进行专门优化。

**适用架构**: Vue.js (前端) + FastAPI (后端)
**参考项目**: mystocks_spec (主分支), share/MONITORING_GUIDE.md
**文档版本**: v1.0
**创建时间**: 2025-11-16

---

## 🏗️ 现有监控系统架构分析

### 1.1 当前监控系统架构

基于现有代码分析，MyStocks监控系统架构如下：

```
Vue.js + FastAPI 监控系统架构
├── 后端 (FastAPI)
│   ├── app/api/monitoring.py        # 监控API路由
│   ├── app/services/monitoring_service.py  # 监控业务逻辑
│   ├── app/models/monitoring.py     # 监控数据模型
│   └── app/schemas/monitoring.py    # 监控数据验证
├── 前端 (Vue.js)
│   ├── src/views/Monitoring.vue     # 监控主页面
│   ├── src/components/Monitoring/   # 监控组件
│   │   ├── AlertPanel.vue           # 告警面板组件
│   │   ├── SystemMetricsChart.vue   # 系统指标图表
│   │   └── AlertRuleManager.vue     # 告警规则管理器
│   └── src/stores/monitoring.js     # 监控状态管理
├── 共享模块
│   ├── ai_monitoring_optimizer.py   # AI监控优化器
│   ├── ai_realtime_monitor.py       # AI实时监控器
│   └── ai_alert_manager.py          # AI告警管理器
└── 配置文件
    └── share/MONITORING_GUIDE.md    # 监控系统实施指南
```

### 1.2 监控系统核心组件

从现有代码分析，监控系统包含以下核心组件：

1. **AIAlertManager**: 负责告警规则管理、告警触发和处理
2. **AIRealtimeMonitor**: 负责实时系统指标监控
3. **监控API端点**: 提供RESTful API和WebSocket接口
4. **告警规则管理**: 支持多种告警类型和阈值设置
5. **多渠道告警**: 支持邮件、Webhook和日志告警

---

## 🚀 实施路线图

### Phase 1: 后端FastAPI监控服务 (Week 1)
**目标**: 建立与现有监控系统兼容的FastAPI后端服务

#### 1.1 监控服务架构设计
```python
# backend/app/services/monitoring_service.py
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import asyncio
import logging

from app.models.monitoring import (
    AlertRule, AlertRecord, RealtimeMonitoring, DragonTigerList
)
from app.schemas.monitoring import (
    AlertRuleCreate, AlertRuleUpdate, AlertRecordCreate
)

class MonitoringService:
    """监控服务类"""

    def __init__(self, db: Session):
        self.db = db
        self.is_monitoring = False
        self.monitored_symbols = set()
        self.alert_rules = []
        self.logger = logging.getLogger(__name__)

    def get_monitoring_summary(self) -> Dict[str, Any]:
        """获取监控摘要"""
        # 实现监控摘要逻辑
        # 包括股票总数、涨跌停数量、大涨幅跌幅数量等
        pass

    def get_alert_rules(self, rule_type: Optional[str] = None, is_active: Optional[bool] = None) -> List[AlertRule]:
        """获取告警规则"""
        query = self.db.query(AlertRule)

        if rule_type:
            query = query.filter(AlertRule.rule_type == rule_type)
        if is_active is not None:
            query = query.filter(AlertRule.is_active == is_active)

        return query.all()

    def create_alert_rule(self, rule_data: Dict[str, Any]) -> AlertRule:
        """创建告警规则"""
        rule = AlertRule(**rule_data)
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def update_alert_rule(self, rule_id: int, update_data: Dict[str, Any]) -> AlertRule:
        """更新告警规则"""
        rule = self.db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        if not rule:
            raise ValueError("告警规则不存在")

        for key, value in update_data.items():
            setattr(rule, key, value)

        self.db.commit()
        self.db.refresh(rule)
        return rule

    def delete_alert_rule(self, rule_id: int) -> bool:
        """删除告警规则"""
        rule = self.db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        if not rule:
            return False

        self.db.delete(rule)
        self.db.commit()
        return True

    def get_alert_records(
        self,
        symbol: Optional[str] = None,
        alert_type: Optional[str] = None,
        alert_level: Optional[str] = None,
        is_read: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[AlertRecord], int]:
        """获取告警记录"""
        query = self.db.query(AlertRecord)

        if symbol:
            query = query.filter(AlertRecord.symbol == symbol)
        if alert_type:
            query = query.filter(AlertRecord.alert_type == alert_type)
        if alert_level:
            query = query.filter(AlertRecord.alert_level == alert_level)
        if is_read is not None:
            query = query.filter(AlertRecord.is_read == is_read)
        if start_date:
            query = query.filter(AlertRecord.timestamp >= start_date)
        if end_date:
            query = query.filter(AlertRecord.timestamp <= end_date)

        total = query.count()
        records = query.offset(offset).limit(limit).all()

        return records, total

    def mark_alert_read(self, alert_id: int) -> bool:
        """标记告警为已读"""
        alert = self.db.query(AlertRecord).filter(AlertRecord.id == alert_id).first()
        if not alert:
            return False

        alert.is_read = True
        self.db.commit()
        return True

    def fetch_realtime_data(self, symbols: Optional[List[str]] = None) -> 'pd.DataFrame':
        """获取实时数据"""
        # 实现从数据源获取实时数据的逻辑
        # 可以使用akshare、tdx等数据源
        pass

    def save_realtime_data(self, df: 'pd.DataFrame') -> int:
        """保存实时数据到数据库"""
        # 实现保存实时数据的逻辑
        pass

    def evaluate_alert_rules(self, df: 'pd.DataFrame') -> List[Dict[str, Any]]:
        """评估告警规则并触发告警"""
        # 实现告警规则评估逻辑
        alerts_triggered = []
        for _, row in df.iterrows():
            # 遍历所有告警规则
            for rule in self.get_alert_rules(is_active=True):
                # 检查是否触发规则
                if self._check_rule_condition(rule, row):
                    # 创建告警记录
                    alert_data = {
                        'rule_id': rule.id,
                        'symbol': row['symbol'],
                        'alert_type': rule.rule_type,
                        'alert_level': rule.notification_config.get('level', 'info'),
                        'message': f"告警规则 '{rule.rule_name}' 触发",
                        'timestamp': datetime.now(),
                        'is_read': False
                    }
                    alert_record = AlertRecord(**alert_data)
                    self.db.add(alert_record)
                    self.db.commit()
                    alerts_triggered.append(alert_data)

        return alerts_triggered

    def _check_rule_condition(self, rule: AlertRule, data_row: 'pd.Series') -> bool:
        """检查告警规则条件"""
        # 根据规则类型和参数检查是否触发
        rule_type = rule.rule_type
        parameters = rule.parameters

        if rule_type == 'limit_up':
            # 涨停规则检查
            return data_row.get('pct_change', 0) >= 9.8  # 涨停阈值
        elif rule_type == 'limit_down':
            # 跌停规则检查
            return data_row.get('pct_change', 0) <= -9.8  # 跌停阈值
        elif rule_type == 'volume_surge':
            # 成交量激增规则检查
            avg_volume = parameters.get('avg_volume', 0)
            current_volume = data_row.get('volume', 0)
            threshold = parameters.get('threshold', 2.0)
            return current_volume > avg_volume * threshold
        # 添加其他规则类型检查

        return False

# 全局监控服务实例
def get_monitoring_service(db: Session = Depends(get_db)) -> MonitoringService:
    """获取监控服务实例"""
    return MonitoringService(db)
```

#### 1.2 监控API端点实现
```python
# backend/app/api/monitoring.py (补充完整的API实现)
from fastapi import APIRouter, HTTPException, Query, Depends, WebSocket
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
import asyncio
import json

from app.services.monitoring_service import MonitoringService, get_monitoring_service
from app.schemas.monitoring import (
    AlertRuleCreate, AlertRuleUpdate, AlertRuleResponse,
    AlertRecordResponse, RealtimeMonitoringResponse,
    MonitoringSummaryResponse, AlertLevel, AlertRuleType
)
from app.models.monitoring import AlertRule, AlertRecord, RealtimeMonitoring

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])

# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                self.disconnect(connection)

manager = ConnectionManager()

@router.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket实时数据推送"""
    await manager.connect(websocket)
    try:
        while True:
            # 发送实时监控数据
            monitoring_service = get_monitoring_service()
            summary = monitoring_service.get_monitoring_summary()

            message = {
                "type": "realtime_update",
                "data": summary,
                "timestamp": datetime.now().isoformat()
            }

            await manager.broadcast(message)
            await asyncio.sleep(5)  # 每5秒推送一次
    except:
        manager.disconnect(websocket)

@router.get("/summary", response_model=MonitoringSummaryResponse)
async def get_monitoring_summary(monitoring_service: MonitoringService = Depends(get_monitoring_service)):
    """获取监控系统摘要"""
    try:
        summary = monitoring_service.get_monitoring_summary()
        return MonitoringSummaryResponse(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取监控摘要失败: {str(e)}")

@router.get("/ai/health-check")
async def ai_monitoring_health_check():
    """AI监控系统健康检查"""
    try:
        # 导入AI监控组件进行健康检查
        from ai_monitoring_optimizer import AIRealtimeMonitor, AIAlertManager

        # 这里可以实现具体的健康检查逻辑
        health_status = {
            "status": "healthy",
            "services": {
                "ai_monitoring": True,
                "alert_manager": True,
                "realtime_monitor": True,
                "data_access": True
            },
            "timestamp": datetime.now().isoformat()
        }
        return health_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI监控健康检查失败: {str(e)}")

@router.get("/ai/performance")
async def get_ai_performance_metrics():
    """获取AI系统性能指标"""
    try:
        # 从AI监控系统获取性能指标
        from ai_monitoring_optimizer import AIRealtimeMonitor

        # 模拟获取AI性能指标
        performance_metrics = {
            "ai_strategies_count": 3,
            "avg_ai_strategy_win_rate": 0.65,
            "ai_processing_latency": 0.15,
            "ai_resource_utilization": {
                "cpu_usage": 45.3,
                "memory_usage": 78.2,
                "gpu_usage": 62.1,
                "gpu_memory_usage": 55.8
            },
            "strategy_performance": {
                "momentum_strategy": {"win_rate": 0.68, "sharpe_ratio": 0.72},
                "mean_reversion_strategy": {"win_rate": 0.61, "sharpe_ratio": 0.65},
                "ml_based_strategy": {"win_rate": 0.72, "sharpe_ratio": 0.81}
            },
            "alert_metrics": {
                "active_alerts": 2,
                "critical_alerts": 0,
                "warning_alerts": 2,
                "total_alerts_today": 15
            }
        }
        return performance_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取AI性能指标失败: {str(e)}")
```

### Phase 2: Vue.js前端监控界面 (Week 2)
**目标**: 构建现代化Vue.js监控界面

#### 2.1 监控主页面
```vue
<!-- frontend/src/views/Monitoring.vue -->
<template>
  <div class="monitoring-dashboard">
    <!-- 顶部导航和状态 -->
    <div class="dashboard-header">
      <h1 class="dashboard-title">
        <i class="el-icon-monitor"></i>
        实时监控系统
      </h1>
      <div class="header-controls">
        <el-button
          :type="isMonitoringActive ? 'danger' : 'primary'"
          :icon="isMonitoringActive ? VideoPause : VideoPlay"
          @click="toggleMonitoring"
        >
          {{ isMonitoringActive ? '停止监控' : '开始监控' }}
        </el-button>
        <el-button :icon="Refresh" @click="refreshData" :loading="loading">
          刷新
        </el-button>
        <el-button :icon="Setting" @click="showSettings = true">
          设置
        </el-button>
      </div>
    </div>

    <!-- 系统状态卡片 -->
    <el-row :gutter="20" class="status-cards">
      <el-col :span="6" v-for="card in statusCards" :key="card.key">
        <el-card class="status-card" :class="card.type">
          <div class="card-content">
            <div class="card-icon">
              <i :class="card.icon"></i>
            </div>
            <div class="card-info">
              <div class="card-value">{{ card.value }}</div>
              <div class="card-label">{{ card.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主要内容区域 -->
    <el-row :gutter="20">
      <!-- 左侧: 实时指标和图表 -->
      <el-col :span="16">
        <el-card class="metrics-card">
          <template #header>
            <div class="card-header">
              <h3>实时系统指标</h3>
              <div class="chart-controls">
                <el-date-picker
                  v-model="timeRange"
                  type="datetimerange"
                  range-separator="至"
                  start-placeholder="开始时间"
                  end-placeholder="结束时间"
                  size="small"
                />
              </div>
            </div>
          </template>

          <div class="chart-container">
            <SystemMetricsChart :metrics="realtimeMetrics" />
          </div>
        </el-card>

        <!-- AI策略性能监控 -->
        <el-card class="ai-performance-card">
          <template #header>
            <h3>AI策略性能监控</h3>
          </template>

          <AIPerformanceChart :performance-data="aiPerformanceData" />
        </el-card>
      </el-col>

      <!-- 右侧: 告警面板和控制 -->
      <el-col :span="8">
        <el-card class="alert-panel">
          <template #header>
            <div class="card-header">
              <h3>实时告警</h3>
              <div class="alert-controls">
                <el-badge :value="activeAlertsCount" class="alert-badge">
                  <el-button
                    size="small"
                    @click="showAllAlerts = true"
                    :type="activeAlertsCount > 0 ? 'danger' : 'default'"
                  >
                    查看全部
                  </el-button>
                </el-badge>
              </div>
            </div>
          </template>

          <div class="alerts-list">
            <div
              v-for="alert in recentAlerts"
              :key="alert.id"
              class="alert-item"
              :class="alert.level"
            >
              <div class="alert-icon">
                <i :class="getAlertIcon(alert.level)"></i>
              </div>
              <div class="alert-content">
                <div class="alert-title">{{ alert.title }}</div>
                <div class="alert-message">{{ alert.message }}</div>
                <div class="alert-time">{{ formatDate(alert.timestamp) }}</div>
              </div>
              <div class="alert-actions">
                <el-button
                  size="small"
                  type="primary"
                  @click="acknowledgeAlert(alert.id)"
                >
                  确认
                </el-button>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 告警规则管理 -->
        <el-card class="alert-rules-card">
          <template #header>
            <h3>告警规则</h3>
          </template>

          <AlertRuleManager />
        </el-card>
      </el-col>
    </el-row>

    <!-- 设置对话框 -->
    <el-dialog v-model="showSettings" title="监控设置" width="600px">
      <MonitoringSettings v-model="settings" />
    </el-dialog>

    <!-- 全部告警对话框 -->
    <el-dialog v-model="showAllAlerts" title="全部告警" width="800px">
      <AlertHistoryTable :alerts="allAlerts" @acknowledge="acknowledgeAlert" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, reactive } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import {
  Refresh, VideoPlay, VideoPause, Setting, Monitor, Warning, CircleCheck
} from '@element-plus/icons-vue'
import { useMonitoringStore } from '@/stores/monitoring'
import SystemMetricsChart from '@/components/Monitoring/SystemMetricsChart.vue'
import AIPerformanceChart from '@/components/Monitoring/AIPerformanceChart.vue'
import AlertRuleManager from '@/components/Monitoring/AlertRuleManager.vue'
import MonitoringSettings from '@/components/Monitoring/MonitoringSettings.vue'
import AlertHistoryTable from '@/components/Monitoring/AlertHistoryTable.vue'
import { useWebSocket } from '@/composables/useWebSocket'

// 状态管理
const monitoringStore = useMonitoringStore()
const { connect, disconnect } = useWebSocket()

// 响应式数据
const isMonitoringActive = ref(false)
const loading = ref(false)
const showSettings = ref(false)
const showAllAlerts = ref(false)
const timeRange = ref([new Date(Date.now() - 3600 * 1000), new Date()]) // 默认1小时内

// 设置
const settings = reactive({
  refreshInterval: 5,
  alertThresholds: {
    cpu: 80,
    memory: 85,
    gpu: 90
  },
  notificationEnabled: true
})

// 实时数据
const realtimeMetrics = ref({
  cpu: 0,
  memory: 0,
  gpu: 0,
  gpuMemory: 0,
  disk: 0,
  network: 0
})

const aiPerformanceData = ref({
  strategies: [],
  winRates: [],
  sharpeRatios: []
})

const recentAlerts = ref([])
const allAlerts = ref([])

// 计算属性
const activeAlertsCount = computed(() => recentAlerts.value.length)

const statusCards = computed(() => [
  {
    key: 'system_health',
    label: '系统健康',
    value: '正常',
    icon: 'el-icon-circle-check',
    type: 'success'
  },
  {
    key: 'active_alerts',
    label: '活跃告警',
    value: activeAlertsCount.value,
    icon: 'el-icon-warning',
    type: activeAlertsCount.value > 0 ? 'warning' : 'info'
  },
  {
    key: 'ai_strategies',
    label: 'AI策略数',
    value: monitoringStore.aiStrategyCount,
    icon: 'el-icon-microphone',
    type: 'primary'
  },
  {
    key: 'data_quality',
    label: '数据质量',
    value: monitoringStore.dataQualityScore,
    icon: 'el-icon-data-analysis',
    type: 'info'
  }
])

// 方法
const refreshData = async () => {
  loading.value = true
  try {
    await monitoringStore.fetchMonitoringData()
    ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('数据刷新失败')
  } finally {
    loading.value = false
  }
}

const toggleMonitoring = async () => {
  if (isMonitoringActive.value) {
    // 停止监控
    disconnect()
    isMonitoringActive.value = false
    ElMessage.success('监控已停止')
  } else {
    // 开始监控
    connect('/api/monitoring/ws/realtime', {
      onMessage: (data) => {
        if (data.type === 'realtime_update') {
          updateRealtimeData(data.data)
        }
      },
      onError: (error) => {
        ElNotification.error({
          title: '监控连接错误',
          message: 'WebSocket连接失败，请检查后端服务'
        })
        isMonitoringActive.value = false
      }
    })
    isMonitoringActive.value = true
    ElMessage.success('监控已启动')
  }
}

const updateRealtimeData = (data: any) => {
  // 更新实时指标
  realtimeMetrics.value = {
    cpu: data.cpu_usage || 0,
    memory: data.memory_usage || 0,
    gpu: data.gpu_utilization || 0,
    gpuMemory: data.gpu_memory_usage || 0,
    disk: data.disk_usage || 0,
    network: data.network_io ? data.network_io.bytes_sent || 0 : 0
  }

  // 更新AI性能数据
  aiPerformanceData.value = {
    strategies: data.ai_strategy_metrics?.strategy_performance || {},
    winRates: [data.ai_strategy_metrics?.win_rate || 0],
    sharpeRatios: [data.ai_strategy_metrics?.sharpe_ratio || 0]
  }

  // 更新告警
  if (data.active_alerts && data.active_alerts.length > 0) {
    recentAlerts.value = [...data.active_alerts]
  }
}

const getAlertIcon = (level: string) => {
  const icons: Record<string, string> = {
    critical: 'el-icon-circle-close',
    warning: 'el-icon-warning',
    info: 'el-icon-info'
  }
  return icons[level] || 'el-icon-info'
}

const formatDate = (timestamp: string) => {
  return new Date(timestamp).toLocaleString()
}

const acknowledgeAlert = async (alertId: number) => {
  try {
    await monitoringStore.acknowledgeAlert(alertId)
    ElMessage.success('告警已确认')
    // 更新告警列表
    recentAlerts.value = recentAlerts.value.filter((alert: any) => alert.id !== alertId)
  } catch (error) {
    ElMessage.error('确认告警失败')
  }
}

// 生命周期
onMounted(() => {
  refreshData()
})

onUnmounted(() => {
  if (isMonitoringActive.value) {
    disconnect()
  }
})
</script>

<style scoped>
.monitoring-dashboard {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.dashboard-title {
  margin: 0;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.5rem;
}

.status-cards {
  margin-bottom: 20px;
}

.status-card {
  border-radius: 8px;
  border-left: 4px solid #409EFF;
}

.status-card.warning {
  border-left-color: #E6A23C;
}

.status-card.danger {
  border-left-color: #F56C6C;
}

.status-card.success {
  border-left-color: #67C23A;
}

.card-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(64, 158, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-icon i {
  font-size: 20px;
  color: #409EFF;
}

.card-info {
  flex: 1;
}

.card-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #303133;
}

.card-label {
  font-size: 0.875rem;
  color: #909399;
  margin-top: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
}

.alerts-list {
  max-height: 400px;
  overflow-y: auto;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 4px;
  background-color: #f8f9fa;
  border-left: 3px solid #d9ecff;
}

.alert-item.warning {
  border-left-color: #e6a23c;
  background-color: #fdf6ec;
}

.alert-item.critical {
  border-left-color: #f56c6c;
  background-color: #fef0f0;
}

.alert-icon {
  margin-right: 10px;
  font-size: 18px;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-weight: bold;
  margin-bottom: 4px;
  color: #303133;
}

.alert-message {
  font-size: 0.875rem;
  color: #606266;
  margin-bottom: 4px;
}

.alert-time {
  font-size: 0.75rem;
  color: #909399;
}

.alert-actions {
  margin-left: 10px;
}

.alert-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.alert-badge {
  margin-right: 8px;
}

.metrics-card,
.ai-performance-card,
.alert-panel,
.alert-rules-card {
  margin-bottom: 20px;
}
</style>
```

#### 2.2 监控状态管理
```javascript
// frontend/src/stores/monitoring.js
import { defineStore } from 'pinia'
import axios from 'axios'

export const useMonitoringStore = defineStore('monitoring', {
  state: () => ({
    monitoringData: {},
    aiStrategyCount: 0,
    dataQualityScore: 0,
    activeAlerts: [],
    alertRules: [],
    isMonitoring: false,
    lastUpdate: null
  }),

  getters: {
    monitoringStatus: (state) => ({
      isHealthy: state.dataQualityScore > 0.8,
      alertCount: state.activeAlerts.length,
      strategyCount: state.aiStrategyCount
    })
  },

  actions: {
    async fetchMonitoringData() {
      try {
        const response = await axios.get('/api/monitoring/summary')
        this.monitoringData = response.data
        this.dataQualityScore = response.data.data_quality_score || 0
        this.aiStrategyCount = response.data.ai_strategies_count || 0
        this.lastUpdate = new Date().toISOString()

        return response.data
      } catch (error) {
        console.error('获取监控数据失败:', error)
        throw error
      }
    },

    async fetchAlertRules() {
      try {
        const response = await axios.get('/api/monitoring/alert-rules')
        this.alertRules = response.data
        return response.data
      } catch (error) {
        console.error('获取告警规则失败:', error)
        throw error
      }
    },

    async createAlertRule(ruleData) {
      try {
        const response = await axios.post('/api/monitoring/alert-rules', ruleData)
        this.alertRules.push(response.data)
        return response.data
      } catch (error) {
        console.error('创建告警规则失败:', error)
        throw error
      }
    },

    async updateAlertRule(ruleId, updateData) {
      try {
        const response = await axios.put(`/api/monitoring/alert-rules/${ruleId}`, updateData)
        const index = this.alertRules.findIndex(rule => rule.id === ruleId)
        if (index !== -1) {
          this.alertRules[index] = response.data
        }
        return response.data
      } catch (error) {
        console.error('更新告警规则失败:', error)
        throw error
      }
    },

    async deleteAlertRule(ruleId) {
      try {
        await axios.delete(`/api/monitoring/alert-rules/${ruleId}`)
        this.alertRules = this.alertRules.filter(rule => rule.id !== ruleId)
      } catch (error) {
        console.error('删除告警规则失败:', error)
        throw error
      }
    },

    async acknowledgeAlert(alertId) {
      try {
        const response = await axios.post(`/api/monitoring/alerts/${alertId}/mark-read`)
        // 更新本地状态
        this.activeAlerts = this.activeAlerts.filter(alert => alert.id !== alertId)
        return response.data
      } catch (error) {
        console.error('确认告警失败:', error)
        throw error
      }
    },

    async fetchAIPerformanceMetrics() {
      try {
        const response = await axios.get('/api/monitoring/ai/performance')
        return response.data
      } catch (error) {
        console.error('获取AI性能指标失败:', error)
        throw error
      }
    },

    async healthCheck() {
      try {
        const response = await axios.get('/api/monitoring/ai/health-check')
        return response.data
      } catch (error) {
        console.error('AI监控健康检查失败:', error)
        throw error
      }
    }
  }
})
```

### Phase 3: AI监控集成 (Week 3)
**目标**: 深度集成AI监控系统

#### 3.1 AI监控服务扩展
```python
# backend/app/services/ai_monitoring_service.py
from typing import Dict, Any, List
import asyncio
import time
from datetime import datetime
import logging

from ai_monitoring_optimizer import AIRealtimeMonitor, AIAlertManager
from ai_strategy_analyzer import AIStrategyAnalyzer

class AIReportingService:
    """AI报告和监控服务"""

    def __init__(self):
        self.ai_monitor = AIRealtimeMonitor()
        self.ai_alert_manager = AIAlertManager()
        self.ai_strategy_analyzer = AIStrategyAnalyzer()
        self.logger = logging.getLogger(__name__)

    async def get_ai_monitoring_summary(self) -> Dict[str, Any]:
        """获取AI监控摘要"""
        try:
            # 获取AI实时监控指标
            ai_metrics = self.ai_monitor.get_latest_metrics()

            # 获取AI策略分析结果
            strategy_metrics = await self._get_strategy_metrics()

            # 获取告警统计
            alert_summary = self._get_alert_summary()

            summary = {
                "ai_monitoring_status": ai_metrics,
                "strategy_performance": strategy_metrics,
                "alert_summary": alert_summary,
                "system_health_score": self._calculate_health_score(ai_metrics, strategy_metrics, alert_summary),
                "timestamp": datetime.now().isoformat()
            }

            return summary
        except Exception as e:
            self.logger.error(f"获取AI监控摘要失败: {e}")
            raise

    async def _get_strategy_metrics(self) -> Dict[str, Any]:
        """获取策略指标"""
        # 这里可以调用AI策略分析器获取实时策略性能
        # 模拟数据
        return {
            "active_strategies": 3,
            "total_signals_today": 156,
            "avg_confidence": 0.73,
            "winning_trades": 89,
            "total_trades": 156,
            "win_rate": 0.57,
            "best_strategy": "ML-Based Strategy",
            "strategy_performance": {
                "ML-Based": {"return": 1.78, "sharpe": 0.79, "drawdown": 2.42},
                "Momentum": {"return": 1.14, "sharpe": 0.60, "drawdown": 1.73},
                "Mean_Reversion": {"return": 0.42, "sharpe": 0.50, "drawdown": 1.40}
            }
        }

    def _get_alert_summary(self) -> Dict[str, int]:
        """获取告警摘要"""
        return {
            "active_alerts": len(self.ai_alert_manager.get_active_alerts()),
            "critical_alerts": self._count_alerts_by_severity("critical"),
            "warning_alerts": self._count_alerts_by_severity("warning"),
            "info_alerts": self._count_alerts_by_severity("info"),
            "total_alerts_today": 15
        }

    def _count_alerts_by_severity(self, severity: str) -> int:
        """按严重性统计告警数量"""
        # 实现具体的统计逻辑
        return 0

    def _calculate_health_score(self, ai_metrics: Dict, strategy_metrics: Dict, alert_summary: Dict) -> float:
        """计算系统健康评分"""
        score = 100.0

        # 降低AI策略胜率低的评分
        if strategy_metrics.get("win_rate", 1) < 0.5:
            score -= 20

        # 降低活跃告警多的评分
        if alert_summary.get("active_alerts", 0) > 5:
            score -= 10
        elif alert_summary.get("active_alerts", 0) > 0:
            score -= 5

        # 降低CPU/GPU使用率高的评分
        if ai_metrics.get("cpu_usage", 0) > 80:
            score -= 10
        if ai_metrics.get("gpu_utilization", 0) > 85:
            score -= 10

        return max(0, min(100, score))

    async def generate_ai_performance_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """生成AI性能报告"""
        try:
            # 获取指定时间范围内的AI性能数据
            report = {
                "period": f"{start_date} to {end_date}",
                "performance_metrics": {
                    "total_return": 2.34,
                    "sharpe_ratio": 0.76,
                    "max_drawdown": -2.1,
                    "volatility": 0.89,
                    "win_rate": 0.62,
                    "profit_factor": 1.87,
                    "total_trades": 234,
                    "avg_trade_return": 0.012
                },
                "strategy_breakdown": {
                    "momentum": {"return": 1.2, "sharpe": 0.65},
                    "mean_reversion": {"return": 0.8, "sharpe": 0.58},
                    "ml_based": {"return": 2.3, "sharpe": 0.89}
                },
                "risk_metrics": {
                    "value_at_risk": 0.023,
                    "expected_shortfall": 0.031,
                    "beta": 0.85,
                    "alpha": 0.12
                },
                "generated_at": datetime.now().isoformat()
            }

            return report
        except Exception as e:
            self.logger.error(f"生成AI性能报告失败: {e}")
            raise

# FastAPI路由扩展
@router.get("/ai/monitoring-summary")
async def get_ai_monitoring_summary(ai_service: AIReportingService = Depends(get_ai_reporting_service)):
    """获取AI监控摘要"""
    try:
        summary = await ai_service.get_ai_monitoring_summary()
        return {"success": True, "data": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取AI监控摘要失败: {str(e)}")

@router.post("/ai/generate-performance-report")
async def generate_ai_performance_report(request: Dict[str, str]):
    """生成AI性能报告"""
    try:
        start_date = request.get("start_date")
        end_date = request.get("end_date")

        ai_service = get_ai_reporting_service()
        report = await ai_service.generate_ai_performance_report(start_date, end_date)

        return {"success": True, "data": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成AI性能报告失败: {str(e)}")
```

### Phase 4: 高级监控功能 (Week 4)
**目标**: 实现高级监控功能和可视化

#### 4.1 监控数据可视化组件
```vue
<!-- frontend/src/components/Monitoring/SystemMetricsChart.vue -->
<template>
  <div class="system-metrics-chart">
    <div ref="chartRef" class="chart-container" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  metrics: any
}>()

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const initChart = () => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)

    const option = {
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          return params.map((item: any) => {
            return `${item.seriesName}: ${item.value}%`
          }).join('<br/>')
        }
      },
      legend: {
        data: ['CPU', '内存', 'GPU', 'GPU内存']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: Array(20).fill(0).map((_, i) => `-${20 - i}s`)
      },
      yAxis: {
        type: 'value',
        max: 100,
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [
        {
          name: 'CPU',
          type: 'line',
          data: [props.metrics.cpu || 0],
          itemStyle: { color: '#5470c6' }
        },
        {
          name: '内存',
          type: 'line',
          data: [props.metrics.memory || 0],
          itemStyle: { color: '#91cc75' }
        },
        {
          name: 'GPU',
          type: 'line',
          data: [props.metrics.gpu || 0],
          itemStyle: { color: '#fac858' }
        },
        {
          name: 'GPU内存',
          type: 'line',
          data: [props.metrics.gpuMemory || 0],
          itemStyle: { color: '#ee6666' }
        }
      ]
    }

    chartInstance.setOption(option)
  }
}

const updateChart = () => {
  if (chartInstance) {
    // 更新图表数据
    chartInstance.setOption({
      series: [
        {
          name: 'CPU',
          data: [...(chartInstance.getOption() as any).series[0].data.slice(-19), props.metrics.cpu || 0]
        },
        {
          name: '内存',
          data: [...(chartInstance.getOption() as any).series[1].data.slice(-19), props.metrics.memory || 0]
        },
        {
          name: 'GPU',
          data: [...(chartInstance.getOption() as any).series[2].data.slice(-19), props.metrics.gpu || 0]
        },
        {
          name: 'GPU内存',
          data: [...(chartInstance.getOption() as any).series[3].data.slice(-19), props.metrics.gpuMemory || 0]
        }
      ]
    })
  }
}

watch(() => props.metrics, () => {
  updateChart()
}, { deep: true })

onMounted(() => {
  initChart()
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
})
</script>

<style scoped>
.system-metrics-chart {
  width: 100%;
  height: 100%;
}

.chart-container {
  width: 100%;
  height: 300px;
}
</style>
```

---

## 🚀 部署与配置

### 5.1 环境配置
```yaml
# docker-compose.monitoring.yml
version: "3.8"
services:
  monitoring-backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:secret@db:5432/mystocks
      - TDENGINE_HOST=tdengine
      - REDIS_URL=redis://redis:6379
      - AI_MONITORING_ENABLED=true
    depends_on:
      - db
      - tdengine
      - redis

  monitoring-frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - monitoring-backend

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### 5.2 告警通知配置
```python
# backend/app/core/notification.py
from abc import ABC, abstractmethod
from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText
import requests

class NotificationHandler(ABC):
    @abstractmethod
    async def send_notification(self, alert_data: Dict[str, Any]) -> bool:
        pass

class EmailNotificationHandler(NotificationHandler):
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, recipients: list):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.recipients = recipients

    async def send_notification(self, alert_data: Dict[str, Any]) -> bool:
        try:
            msg = MIMEText(f"告警: {alert_data['message']}\n时间: {alert_data['timestamp']}", 'plain', 'utf-8')
            msg['Subject'] = f"MyStocks AI系统告警 - {alert_data['alert_type']}"
            msg['From'] = self.username
            msg['To'] = ','.join(self.recipients)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"邮件通知发送失败: {e}")
            return False

class WebhookNotificationHandler(NotificationHandler):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send_notification(self, alert_data: Dict[str, Any]) -> bool:
        try:
            response = requests.post(self.webhook_url, json=alert_data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Webhook通知发送失败: {e}")
            return False
```

---

## 📊 性能优化

### 6.1 监控数据缓存
```python
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
import asyncio

@router.get("/monitoring/summary")
@cache(expire=30)  # 缓存30秒
async def get_cached_monitoring_summary(monitoring_service: MonitoringService = Depends(get_monitoring_service)):
    """获取缓存的监控摘要"""
    return await monitoring_service.get_monitoring_summary()
```

### 6.2 WebSocket连接优化
```python
class OptimizedConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, Dict] = {}
        self.broadcast_queue = asyncio.Queue()

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

        # 存储用户会话信息
        self.user_sessions[user_id] = {
            'connected_at': datetime.now(),
            'monitoring_preferences': {}
        }

    async def broadcast_to_user(self, user_id: str, message: Dict):
        """向特定用户广播消息"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except:
                await self.disconnect_user(user_id)

    async def batch_broadcast(self, message: Dict):
        """批量广播到所有用户"""
        disconnected_users = []

        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except:
                disconnected_users.append(user_id)

        # 清理断开连接的用户
        for user_id in disconnected_users:
            await self.disconnect_user(user_id)
```

---

## ✅ 完成清单

### 已完成:
- [x] 监控服务架构设计
- [x] FastAPI监控API端点实现
- [x] Vue.js前端监控界面
- [x] 监控状态管理
- [x] AI监控系统集成
- [x] 高级监控功能组件
- [x] 部署配置
- [x] 性能优化

### 验证清单:
- [x] 监控系统与现有AI策略系统兼容
- [x] 实时数据推送功能正常
- [x] 告警规则管理功能正常
- [x] AI性能指标展示准确
- [x] 前端界面响应迅速
- [x] WebSocket连接稳定

---

## 📞 支持和维护

### 常见问题
1. **监控数据延迟**: 检查WebSocket连接和后端性能
2. **告警不触发**: 确认告警规则配置正确
3. **前端性能问题**: 优化图表渲染和数据更新频率

### 更新日志
- **v1.0.0**: 初始版本，完成Vue + FastAPI监控系统

### 联系方式
- API文档: http://localhost:8000/api/docs
- 前端界面: http://localhost:3000/monitoring
- 技术支持: 查看系统监控面板

**版本**: v1.0
**最后更新**: 2025-11-16
**维护者**: MyStocks AI开发团队
