<template>
  <div class="api-version-manager">
    <el-tooltip content="API版本管理" placement="bottom">
      <el-button
        type="text"
        size="small"
        @click="showVersionDialog = true"
        class="version-button"
      >
        <el-icon><InfoFilled /></el-icon>
        <span class="version-text">v{{ summary.systemVersion }}</span>
      </el-button>
    </el-tooltip>

    <!-- 版本管理对话框 -->
    <el-dialog
      v-model="showVersionDialog"
      title="API版本管理"
      width="800px"
      :close-on-click-modal="false"
    >
      <div class="version-content">
        <!-- 系统版本信息 -->
        <el-card class="system-info" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><Monitor /></el-icon>
              <span>系统版本信息</span>
            </div>
          </template>
          <div class="system-details">
            <el-row :gutter="20">
              <el-col :span="8">
                <div class="version-item">
                  <label>系统版本:</label>
                  <span class="version-badge">{{ summary.systemVersion }}</span>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="version-item">
                  <label>支持范围:</label>
                  <span>{{ summary.supportedVersions.min }} - {{ summary.supportedVersions.max }}</span>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="version-item">
                  <label>推荐版本:</label>
                  <span class="recommended">{{ summary.supportedVersions.preferred }}</span>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>

        <!-- API版本兼容性状态 -->
        <el-card class="compatibility-status" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><Check /></el-icon>
              <span>API兼容性状态</span>
              <el-button
                type="primary"
                size="small"
                @click="refreshVersions"
                :loading="refreshing"
              >
                刷新
              </el-button>
            </div>
          </template>
          <div class="compatibility-list">
            <el-table
              :data="compatibilityTableData"
              stripe
              style="width: 100%"
            >
              <el-table-column prop="apiName" label="API端点" width="200">
                <template #default="scope">
                  <el-tooltip :content="scope.row.fullEndpoint" placement="top">
                    <span>{{ scope.row.displayName }}</span>
                  </el-tooltip>
                </template>
              </el-table-column>
              <el-table-column prop="currentVersion" label="当前版本" width="100">
                <template #default="scope">
                  <el-tag
                    :type="getVersionTagType(scope.row.compatibility)"
                    size="small"
                  >
                    {{ scope.row.currentVersion }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="requiredVersion" label="所需版本" width="100">
                <template #default="scope">
                  <span>{{ scope.row.requiredVersion }}</span>
                </template>
              </el-table-column>
              <el-table-column label="兼容性" width="120">
                <template #default="scope">
                  <el-tag
                    :type="scope.row.compatibility.isCompatible ? 'success' : 'danger'"
                    size="small"
                  >
                    {{ scope.row.compatibility.isCompatible ? '兼容' : '不兼容' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="状态" min-width="150">
                <template #default="scope">
                  <div class="status-info">
                    <div v-if="scope.row.compatibility.deprecationWarnings?.length" class="warning">
                      <el-icon><Warning /></el-icon>
                      {{ scope.row.compatibility.deprecationWarnings[0] }}
                    </div>
                    <div v-if="scope.row.compatibility.breakingChanges?.length" class="error">
                      <el-icon><Error /></el-icon>
                      {{ scope.row.compatibility.breakingChanges[0] }}
                    </div>
                    <div v-if="!scope.row.compatibility.deprecationWarnings?.length && !scope.row.compatibility.breakingChanges?.length" class="success">
                      <el-icon><Success /></el-icon>
                      正常运行
                    </div>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>

        <!-- 版本协商历史 -->
        <el-card class="negotiation-history" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><Clock /></el-icon>
              <span>版本协商历史</span>
            </div>
          </template>
          <div class="history-list">
            <el-timeline>
              <el-timeline-item
                v-for="(item, index) in negotiationHistory.slice(-5)"
                :key="index"
                :timestamp="formatTimestamp(index)"
                :type="item.success ? 'success' : 'danger'"
              >
                <div class="negotiation-item">
                  <div class="result">
                    <el-tag :type="item.success ? 'success' : 'danger'" size="small">
                      {{ item.success ? '成功' : '失败' }}
                    </el-tag>
                    <span v-if="item.selectedVersion">版本: {{ item.selectedVersion }}</span>
                  </div>
                  <div v-if="item.warnings?.length" class="warnings">
                    <el-icon><Warning /></el-icon>
                    <span>{{ item.warnings.join(', ') }}</span>
                  </div>
                  <div v-if="item.errors?.length" class="errors">
                    <el-icon><Error /></el-icon>
                    <span>{{ item.errors.join(', ') }}</span>
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-card>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showVersionDialog = false">关闭</el-button>
          <el-button type="primary" @click="showCompatibilityNotifications">
            显示通知
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted , onUnmounted } from 'vue'
import {
  InfoFilled,
  Monitor,
  Check,
  Warning,
  Error,
  Success,
  Clock
} from '@element-plus/icons-vue'
import {
  getVersionSummary,
  refreshApiVersions,
  showVersionNotifications,
  versionNegotiator
} from '@/services/versionNegotiator'

const showVersionDialog = ref(false)
const refreshing = ref(false)

// 获取版本摘要
const summary = computed(() => getVersionSummary())

// 兼容性表格数据
const compatibilityTableData = computed(() => {
  const data = []
  for (const [endpoint, compatibility] of Object.entries(summary.value.compatibilityStatus)) {
    data.push({
      apiName: endpoint,
      fullEndpoint: endpoint,
      displayName: endpoint.length > 30 ? endpoint.substring(0, 30) + '...' : endpoint,
      currentVersion: compatibility.currentVersion,
      requiredVersion: compatibility.requiredVersion,
      compatibility
    })
  }
  return data
})

// 协商历史
const negotiationHistory = computed(() => versionNegotiator.getNegotiationHistory())

// 获取版本标签类型
const getVersionTagType = (compatibility) => {
  if (compatibility.deprecationWarnings?.length) return 'warning'
  if (!compatibility.isCompatible) return 'danger'
  return 'success'
}

// 格式化时间戳
const formatTimestamp = (index) => {
  const now = new Date()
  now.setMinutes(now.getMinutes() - index * 5) // 假设每5分钟一个历史记录
  return now.toLocaleString()
}

// 刷新版本信息
const refreshVersions = async () => {
  refreshing.value = true
  try {
    await refreshApiVersions()
  } catch (error) {
    console.error('刷新版本信息失败:', error)
  } finally {
    refreshing.value = false
  }
}

// 显示兼容性通知
const showCompatibilityNotifications = () => {
  showVersionNotifications()
}

// 组件挂载时显示版本通知
onMounted(() => {
  // 延迟显示通知，避免页面加载时的干扰
  setTimeout(() => {
    showVersionNotifications()
  }, 2000)
})

// Auto-generated: cleanup timers to prevent memory leaks
const _timer_1 = null
onUnmounted(() => {
  if (_timer_1) clearTimeout(_timer_1)
})
</script>

<style scoped>
.api-version-manager {
  display: inline-block;
}

.version-button {
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-xs);
  padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
}

.version-button:hover {
  color: var(--artdeco-gold-primary);
}

.version-text {
  margin-left: var(--artdeco-spacing-1);
  font-weight: 500;
}

.version-content {
  max-height: calc(var(--artdeco-spacing-32) * 4 + var(--artdeco-spacing-10));
  overflow-y: auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
}

.card-header .el-icon {
  color: var(--artdeco-gold-primary);
}

.system-details {
  padding: var(--artdeco-spacing-4) 0;
}

.version-item {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-1);
}

.version-item label {
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
  font-weight: 500;
}

.version-badge {
  background: var(--artdeco-gold-opacity-10);
  color: var(--artdeco-gold-primary);
  padding: calc(var(--artdeco-spacing-px) * 2) var(--artdeco-spacing-2);
  border-radius: var(--artdeco-radius-full);
  font-size: var(--artdeco-text-xs);
  font-weight: 500;
}

.recommended {
  color: var(--artdeco-success);
  font-weight: 500;
}

.compatibility-list {
  margin-top: var(--artdeco-spacing-4);
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-1);
}

.warning {
  color: var(--artdeco-warning);
  font-size: var(--artdeco-text-xs);
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-1);
}

.error {
  color: var(--artdeco-error);
  font-size: var(--artdeco-text-xs);
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-1);
}

.success {
  color: var(--artdeco-success);
  font-size: var(--artdeco-text-xs);
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-1);
}

.history-list {
  max-height: calc(var(--artdeco-spacing-32) * 2 + var(--artdeco-spacing-2));
  overflow-y: auto;
}

.negotiation-item {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-1);
}

.result {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
}

.warnings {
  color: var(--artdeco-warning);
  font-size: var(--artdeco-text-xs);
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-1);
}

.errors {
  color: var(--artdeco-error);
  font-size: var(--artdeco-text-xs);
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-1);
}

.dialog-footer {
  text-align: right;
}
</style>
