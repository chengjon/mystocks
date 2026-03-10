<template>
  <div class="settings">

    <div class="page-header">
      <h1 class="page-title">SYSTEM SETTINGS</h1>
      <p class="page-subtitle">CONFIGURATION | DISPLAY | DATABASE | LOGS</p>
    </div>

    <div class="main-card">
      <el-tabs v-model="activeTab" class="tabs">
        <el-tab-pane label="BASIC" name="basic">
          <div class="form">
            <div class="form-group">
              <label class="label">SYSTEM NAME</label>
              <input class="input" value="MyStocks" readonly>
            </div>
            <div class="form-group">
              <label class="label">VERSION</label>
              <input class="input" value="1.0.0" readonly>
            </div>
            <div class="form-group">
              <label class="label">API URL</label>
              <input class="input" :value="apiBaseUrl" readonly>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="DISPLAY" name="display">
          <div class="form">
            <div class="form-group">
              <label class="label">FONT FAMILY</label>
              <el-select v-model="displaySettings.fontFamily" @change="applyDisplaySettings">
                <el-option label="SYSTEM DEFAULT" value="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto" />
                <el-option label="MICROSOFT YAHEI" value="'Microsoft YaHei', sans-serif" />
                <el-option label="PINGFANG SC" value="'PingFang SC', sans-serif" />
                <el-option label="SOURCE HAN SANS" value="'Source Han Sans CN', sans-serif" />
                <el-option label="SIMSUN" value="SimSun, serif" />
                <el-option label="SIMHEI" value="SimHei, sans-serif" />
                <el-option label="ARIAL" value="Arial, sans-serif" />
                <el-option label="HELVETICA" value="Helvetica, sans-serif" />
              </el-select>
            </div>
            <div class="form-group">
              <label class="label">FONT SIZE</label>
              <el-radio-group v-model="displaySettings.fontSize" @change="applyDisplaySettings">
                <el-radio label="small">SMALL (12px)</el-radio>
                <el-radio label="default">DEFAULT (14px)</el-radio>
                <el-radio label="large">LARGE (16px)</el-radio>
                <el-radio label="extra-large">EXTRA LARGE (18px)</el-radio>
              </el-radio-group>
            </div>
            <div class="form-group">
              <label class="label">PREVIEW</label>
              <div class="font-preview" :style="previewStyle">
                <p>THIS IS A FONT PREVIEW TEXT - 这是字体预览效果</p>
                <p>NUMBERS: 0123456789</p>
                <p>STOCK CODE: 600519 / 000858 / 300750</p>
              </div>
            </div>
            <div class="form-actions">
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="DATABASE" name="database">
          <el-table :data="databases" stripe border class="table">
            <el-table-column prop="name" label="TYPE" width="150" />
            <el-table-column prop="host" label="HOST" width="200" />
            <el-table-column prop="port" label="PORT" width="100" />
            <el-table-column prop="status" label="STATUS" width="120">
              <template #default="{ row }">
                <span class="badge" :class="getStatusBadgeClass(row.status)">
                  {{ getStatusText(row.status) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="ACTIONS" width="150">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="testConnection(row)">
                  TEST
                </el-button>
              </template>
            </el-table-column>
            <el-table-column prop="message" label="MESSAGE" min-width="200" />
          </el-table>
          <div class="table-actions">
          </div>
        </el-tab-pane>

        <el-tab-pane label="USERS" name="users">
          <div class="table-actions">
          </div>
          <el-table :data="[]" stripe border class="table">
            <el-table-column prop="username" label="USERNAME" />
            <el-table-column prop="email" label="EMAIL" />
            <el-table-column prop="role" label="ROLE" />
            <el-table-column label="ACTIONS" width="200">
              <template #default>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="LOGS" name="logs">
          <div class="logs-toolbar">
            <el-button @click="filterErrors = !filterErrors" size="small">
              {{ filterErrors ? 'SHOW ALL' : 'ERRORS ONLY' }}
            </el-button>
            <el-select v-model="selectedLevel" placeholder="LEVEL" clearable @change="fetchLogs">
              <el-option label="INFO" value="INFO"></el-option>
              <el-option label="WARNING" value="WARNING"></el-option>
              <el-option label="ERROR" value="ERROR"></el-option>
              <el-option label="CRITICAL" value="CRITICAL"></el-option>
            </el-select>
            <el-select v-model="selectedCategory" placeholder="CATEGORY" clearable @change="fetchLogs">
              <el-option label="DATABASE" value="database"></el-option>
              <el-option label="API" value="api"></el-option>
              <el-option label="ADAPTER" value="adapter"></el-option>
              <el-option label="SYSTEM" value="system"></el-option>
            </el-select>
            <el-button @click="fetchLogs" size="small" :loading="logsLoading">
              REFRESH
            </el-button>
          </div>

          <div class="subcard" v-if="logSummary.total_logs">
            <el-row :gutter="24">
              <el-col :span="6">
                <div class="stat-item">
                  <span class="stat-label">TOTAL LOGS</span>
                  <span class="stat-value gold">{{ logSummary.total_logs }}</span>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <span class="stat-label">RECENT ERRORS</span>
                  <span class="stat-value profit-up">{{ logSummary.recent_errors_1h }}</span>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <span class="stat-label">INFO</span>
                  <span class="stat-value">{{ logSummary.level_counts?.INFO || 0 }}</span>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <span class="stat-label">WARNING</span>
                  <span class="stat-value">{{ logSummary.level_counts?.WARNING || 0 }}</span>
                </div>
              </el-col>
            </el-row>
          </div>

          <el-table :data="logs" stripe border class="table" v-loading="logsLoading">
            <el-table-column prop="timestamp" label="TIME" width="180">
              <template #default="{ row }">
                {{ formatTime(row.timestamp) }}
              </template>
            </el-table-column>
            <el-table-column prop="level" label="LEVEL" width="100">
              <template #default="{ row }">
                <span class="badge" :class="getLevelBadgeClass(row.level)">
                  {{ row.level }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="CATEGORY" width="100" />
            <el-table-column prop="operation" label="OPERATION" width="150" />
            <el-table-column prop="message" label="MESSAGE" min-width="200" />
            <el-table-column label="ACTIONS" width="100">
              <template #default="{ row }">
                <el-button size="small" type="info" @click="viewLogDetails(row)">
                  DETAILS
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="currentPage"
            :page-sizes="[20, 50, 100, 200]"
            :page-size="pageSize"
            :total="totalLogs"
            layout="total, sizes, prev, pager, next, jumper"
            class="pagination"
          />
        </el-tab-pane>

        <el-tab-pane label="ABOUT" name="about">
          <el-descriptions :column="1" border class="descriptions">
            <el-descriptions-item label="PROJECT NAME">MyStocks QUANTITATIVE TRADING SYSTEM</el-descriptions-item>
            <el-descriptions-item label="VERSION">v2.2.0</el-descriptions-item>
            <el-descriptions-item label="TECH STACK">FastAPI + Vue3 + Element Plus</el-descriptions-item>
            <el-descriptions-item label="DATABASE">MySQL + PostgreSQL + TDengine + Redis</el-descriptions-item>
            <el-descriptions-item label="DESCRIPTION">
              PROFESSIONAL QUANTITATIVE TRADING DATA MANAGEMENT SYSTEM, SUPPORTS MULTIPLE DATA SOURCES, INTELLIGENT CLASSIFICATION STORAGE, REAL-TIME MONITORING AND ANALYSIS
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSettings } from './composables/useSettings'
import { API_BASE_URL as apiBaseUrl } from '@/config/runtime-endpoints'

const {
  activeTab,
  displaySettings,
  previewStyle,
  applyDisplaySettings,
  _saveDisplaySettings,
  _resetDisplaySettings,
  databases,
  testConnection,
  _testAllConnections,
  logs,
  logSummary,
  logsLoading,
  filterErrors,
  selectedLevel,
  selectedCategory,
  currentPage,
  pageSize,
  totalLogs,
  fetchLogs,
  _toggleFilter,
  _refreshLogs,
  handleSizeChange,
  handleCurrentChange,
  viewLogDetails,
  getStatusBadgeClass,
  getStatusText,
  getLevelBadgeClass,
  formatTime,
  _showLogDetails
} = useSettings()
</script>

<style scoped lang="scss">
@import "./styles/Settings";
</style>
