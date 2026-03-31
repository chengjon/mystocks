<template>
  <div class="announcement-monitor">
    <div class="page-header">
      <h1 class="page-title">ANNOUNCEMENT MONITOR</h1>
      <p class="page-subtitle">REAL-TIME ANNOUNCEMENTS | INTELLIGENT ANALYSIS | CUSTOM RULES</p>
    </div>

    <!-- 功能说明 -->
    <el-alert
      title="公告监控功能说明"
      type="info"
      :closable="false"
      show-icon
      class="info-banner"
    >
      <template #default>
        <p>
          本系统提供实时公告监控功能，支持设置自定义规则监控重要公告。
          系统会自动获取巨潮资讯等官方公告信息，对重要事件进行标记和提醒。
        </p>
        <el-space wrap>
          <el-tag>实时获取</el-tag>
          <el-tag>智能分析</el-tag>
          <el-tag>自定义规则</el-tag>
          <el-tag>重要提醒</el-tag>
        </el-space>
      </template>
    </el-alert>

    <div class="stats-grid">
      <el-col :span="6">
        <el-card :hoverable="true" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.total_count || 0 }}</div>
              <div class="stat-label">公告总数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card :hoverable="true" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">TODAY</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card :hoverable="true" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">IMPORTANT</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card :hoverable="true" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Bell /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">TRIGGERED</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </div>

    <el-card :hoverable="true" class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="股票代码">
          <el-input
            v-model="searchForm.stock_code"
            placeholder="请输入股票代码"
            clearable
            class="announcement-filter-input"
          />
        </el-form-item>

        <el-form-item label="公告类型">
          <el-select
            v-model="searchForm.announcement_type"
            placeholder="请选择公告类型"
            class="announcement-filter-type"
          >
            <el-option value="" label="全部类型" />
            <el-option value="业绩预告" label="业绩预告" />
            <el-option value="分红派息" label="分红派息" />
            <el-option value="重组并购" label="重组并购" />
            <el-option value="风险提示" label="风险提示" />
          </el-select>
        </el-form-item>

        <el-form-item label="重要性">
          <el-select
            v-model="searchForm.min_importance"
            placeholder="重要性级别"
            class="announcement-filter-input"
          >
            <el-option :value="0" label="全部" />
            <el-option :value="1" label="1级" />
            <el-option :value="2" label="2级" />
            <el-option :value="3" label="3级" />
            <el-option :value="4" label="4级" />
            <el-option :value="5" label="5级" />
          </el-select>
        </el-form-item>

        <el-form-item label="日期范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="fetchAnnouncements" :loading="loading.announcements">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 公告列表 -->
    <el-card class="announcements-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Document /></el-icon>
            公告列表
          </span>
          <div class="card-actions">
            <el-button size="small" @click="fetchTodayAnnouncements">
              <el-icon><Calendar /></el-icon>
              今日公告
            </el-button>
            <el-button size="small" @click="fetchImportantAnnouncements">
              <el-icon><Warning /></el-icon>
              重要公告
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="announcements"
        class="announcement-table"
        v-loading="loading.announcements"
        row-key="id"
      >
        <el-table-column prop="stock_code" label="代码" width="100" fixed="left" />
        <el-table-column prop="stock_name" label="名称" width="120" />
        <el-table-column prop="title" label="标题" min-width="250">
          <template #default="{ row }">
            <span :class="getImportanceClass(row.importance_level)">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="importance_level" label="重要性" width="100">
          <template #default="{ row }">
            <el-rate
              v-model="row.importance_level"
              :max="5"
              :allow-half="false"
              :show-text="false"
              :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
              disabled
              style="line-height: 24px;"
            />
          </template>
        </el-table-column>
        <el-table-column prop="sentiment" label="情感倾向" width="100">
          <template #default="{ row }">
            <el-tag :type="getSentimentType(row.sentiment)" size="small">
              {{ formatSentiment(row.sentiment) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="publish_date" label="发布日期" width="120" sortable />
        <el-table-column prop="data_source" label="数据源" width="100" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.url"
              size="small"
              type="primary"
              link
              @click="openAnnouncement(row.url)"
            >
              查看原文
            </el-button>
            <el-button
              v-else
              size="small"
              type="info"
              link
              disabled
            >
              无链接
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; text-align: right;"
      />
    </el-card>

    <!-- 监控规则管理 -->
    <el-card class="rules-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Setting /></el-icon>
            监控规则管理
          </span>
          <el-button size="small" type="primary" @click="showRuleDialog = true">
            <el-icon><Plus /></el-icon>
            新增规则
          </el-button>
        </div>
      </template>

      <el-table
        :data="monitorRules"
        class="announcement-table"
        v-loading="loading.rules"
      >
        <el-table-column prop="rule_name" label="规则名称" width="150" />
        <el-table-column prop="stock_codes" label="监控股票" width="150">
          <template #default="{ row }">
            <span v-if="row.stock_codes && row.stock_codes.length > 0">
              {{ row.stock_codes.slice(0, 2).join(', ') }}
              <span v-if="row.stock_codes.length > 2">等{{ row.stock_codes.length }}只</span>
            </span>
            <span v-else>全部股票</span>
          </template>
        </el-table-column>
        <el-table-column prop="keywords" label="关键词" width="200">
          <template #default="{ row }">
            <el-tag
              v-for="(keyword, _idx) in row.keywords.slice(0, 3)"
              :key="keyword"
              size="small"
              class="keyword-tag"
            >
              {{ keyword }}
            </el-tag>
            <el-tag v-if="row.keywords.length > 3" size="small" type="info">
              +{{ row.keywords.length - 3 }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="min_importance_level" label="最低重要性" width="120">
          <template #default="{ row }">
            <el-rate
              v-model="row.min_importance_level"
              :max="5"
              :allow-half="false"
              :show-text="false"
              :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
              disabled
            />
          </template>
        </el-table-column>
        <el-table-column prop="notify_enabled" label="通知" width="80">
          <template #default="{ row }">
            <el-tag :type="row.notify_enabled ? 'success' : 'info'" size="small">
              {{ row.notify_enabled ? '开启' : '关闭' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="editRule(row)">
              编辑
            </el-button>
            <el-button size="small" type="danger" link @click="deleteRule(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 规则编辑对话框 -->
      <el-dialog
        v-model="showRuleDialog"
        :title="editingRule.id ? '编辑监控规则' : '新增监控规则'"
        width="600px"
      >
        <el-form :model="editingRule" :rules="ruleFormRules" ref="ruleFormRef" label-width="120px">
          <el-form-item label="规则名称" prop="rule_name">
            <el-input v-model="editingRule.rule_name" placeholder="请输入规则名称" />
          </el-form-item>

          <el-form-item label="监控股票">
            <el-input
              v-model="editingRule.stock_codes_str"
              placeholder="请输入股票代码，逗号分隔（留空表示全部股票）"
              type="textarea"
              :rows="2"
            />
          </el-form-item>

          <el-form-item label="关键词" prop="keywords_str">
            <el-input
              v-model="editingRule.keywords_str"
              placeholder="请输入关键词，逗号分隔"
              type="textarea"
              :rows="2"
            />
          </el-form-item>

          <el-form-item label="最低重要性">
            <el-rate
              v-model="editingRule.min_importance_level"
              :max="5"
              :allow-half="false"
              :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
            />
          </el-form-item>

          <el-form-item label="通知设置">
            <el-switch v-model="editingRule.notify_enabled" />
          </el-form-item>

          <el-form-item label="是否启用">
            <el-switch v-model="editingRule.is_active" />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="showRuleDialog = false">取消</el-button>
            <el-button type="primary" @click="saveRule">确定</el-button>
          </span>
        </template>
      </el-dialog>
    </el-card>

    <!-- 已触发监控记录 -->
    <el-card class="records-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Collection /></el-icon>
            触发记录
          </span>
          <el-button size="small" @click="evaluateRules" :loading="loading.evaluation">
            <el-icon><Lightning /></el-icon>
            评估规则
          </el-button>
        </div>
      </template>

      <el-table
        :data="triggeredRecords"
        class="announcement-table"
        v-loading="loading.records"
      >
        <el-table-column prop="rule_name" label="规则名称" width="150" />
        <el-table-column prop="stock_code" label="股票代码" width="100" />
        <el-table-column prop="announcement_title" label="公告标题" min-width="200" />
        <el-table-column prop="matched_keywords" label="匹配关键词" width="150">
          <template #default="{ row }">
            <el-tag
              v-for="(keyword, _idx) in row.matched_keywords"
              :key="keyword"
              size="small"
              class="keyword-tag"
            >
              {{ keyword }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="triggered_at" label="触发时间" width="160" sortable />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { useAnnouncementMonitor } from './composables/useAnnouncementMonitor'

const {
  stats,
  announcements,
  monitorRules,
  triggeredRecords,
  loading,
  searchForm,
  pagination,
  showRuleDialog,
  ruleFormRef,
  editingRule,
  ruleFormRules,
  fetchAnnouncements,
  fetchTodayAnnouncements,
  fetchImportantAnnouncements,
  evaluateRules,
  editRule,
  deleteRule,
  saveRule,
  openAnnouncement,
  getImportanceClass,
  getSentimentType,
  formatSentiment,
  handleSizeChange,
  handleCurrentChange,
  refreshData
} = useAnnouncementMonitor()
</script>

<style scoped lang="scss">
@use "./styles/AnnouncementMonitor.scss" as *;
</style>
