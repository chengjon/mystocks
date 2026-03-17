<template>
  <div class="wencai-panel-v2">
    <!-- 头部：标题 + 自定义查询输入 -->
    <el-card class="header-card">
      <template #header>
        <div class="card-header">
          <div class="title-section">
            <el-icon class="title-icon"><Search /></el-icon>
            <span class="title">问财股票筛选器</span>
          </div>
        </div>
      </template>

      <!-- 自定义查询输入区 -->
      <div class="custom-query-section">
        <el-input
          v-model="customQueryText"
          placeholder="输入您的查询条件，例如：请列出今天涨幅超过5%的股票"
          clearable
          :maxlength="500"
          show-word-limit
          class="query-input"
        >
          <template #prepend>
            <el-icon><Edit /></el-icon>
          </template>
        </el-input>
        <el-button
          type="primary"
          :loading="executingCustomQuery"
          @click="executeCustomQuery"
          :disabled="!customQueryText"
          class="query-button"
        >
          <el-icon><Search /></el-icon> 查询
        </el-button>
      </div>
    </el-card>

    <!-- 主体：左侧树形 + 右侧结果 -->
    <div class="main-content">
      <!-- 左侧：查询树形结构 -->
      <el-card class="tree-card" shadow="never">
        <template #header>
          <div class="tree-header">
            <span>查询列表</span>
            <el-button size="small" link @click="loadQueries">
              <el-icon><Refresh /></el-icon>
            </el-button>
          </div>
        </template>

        <el-tree
          :data="treeData"
          :props="treeProps"
          default-expand-all
          highlight-current
          @node-click="handleNodeClick"
          v-loading="loadingQueries"
        >
          <template #default="{ node, data }">
            <div class="custom-tree-node">
              <span class="node-label">
                <el-icon v-if="data.type === 'folder'"><Folder /></el-icon>
                <el-icon v-else><Document /></el-icon>
                {{ node.label }}
              </span>
              <span class="node-actions" v-if="data.type === 'query'">
                <el-button
                  type="primary"
                  size="small"
                  link
                  @click.stop="executeQuery(data.data)"
                >
                  执行
                </el-button>
              </span>
            </div>
          </template>
        </el-tree>
      </el-card>

      <!-- 右侧：查询结果表格 -->
      <el-card class="result-card" shadow="never">
        <template #header>
          <div class="result-header">
            <span>{{ currentQueryName || '查询结果' }}</span>
            <div class="header-actions">
              <el-button
                v-if="tableData.length > 0"
                type="success"
                size="small"
                @click="exportData"
              >
                <el-icon><Download /></el-icon> 导出CSV
              </el-button>
            </div>
          </div>
        </template>

        <!-- 查询语句显示 -->
        <div v-if="currentQueryText" class="query-text-display">
          <el-tag type="info">查询语句：{{ currentQueryText }}</el-tag>
        </div>

        <!-- 数据表格 -->
        <el-table
          :data="paginatedTableData"
          stripe
          border
          size="default"
          v-loading="loadingResults"
          height="600"
          :default-sort="{ prop: '序号', order: 'ascending' }"
          class="result-table"
        >
          <el-table-column
            prop="序号"
            label="序号"
            width="80"
            align="center"
            sortable
          />
          <el-table-column
            prop="股票代码"
            label="股票代码"
            width="100"
            align="center"
            sortable
          />
          <el-table-column
            prop="股票简称"
            label="股票简称"
            width="120"
            align="center"
          />
          <el-table-column
            prop="最新价"
            label="最新价"
            width="100"
            align="right"
            sortable
          >
            <template #default="{ row }">
              {{ formatNumber(row['最新价'], 3) }}
            </template>
          </el-table-column>
          <el-table-column
            prop="涨跌幅"
            label="涨跌幅"
            width="100"
            align="right"
            sortable
          >
            <template #default="{ row }">
              <span :class="getPriceChangeClass(row['涨跌幅'])">
                {{ formatPercent(row['涨跌幅']) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column
            prop="涨停次数"
            label="涨停次数"
            width="100"
            align="center"
            sortable
          />
          <el-table-column
            prop="量比"
            label="量比"
            width="100"
            align="right"
            sortable
          >
            <template #default="{ row }">
              {{ formatNumber(row['量比'], 3) }}
            </template>
          </el-table-column>
          <el-table-column
            prop="换手率"
            label="换手率"
            width="100"
            align="right"
            sortable
          >
            <template #default="{ row }">
              {{ formatNumber(row['换手率'], 3) }}
            </template>
          </el-table-column>
          <el-table-column
            prop="振幅"
            label="振幅"
            width="100"
            align="right"
            sortable
          >
            <template #default="{ row }">
              {{ formatNumber(row['振幅'], 3) }}
            </template>
          </el-table-column>
          <el-table-column
            prop="查询日期"
            label="查询日期"
            width="120"
            align="center"
            sortable
          />
          <el-table-column
            label="操作"
            width="120"
            fixed="right"
            align="center"
          >
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                size="small"
                @click="showGroupDialog(row)"
              >
                加入分组
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[20, 50, 100, 200]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @change="handlePageChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 加入分组对话框 -->
    <el-dialog
      v-model="groupDialogVisible"
      title="加入分组"
      width="400px"
    >
      <el-form :model="groupForm" label-width="80px">
        <el-form-item label="股票">
          <el-tag>{{ selectedStock?.['股票代码'] }} {{ selectedStock?.['股票简称'] }}</el-tag>
        </el-form-item>
        <el-form-item label="选择分组">
          <el-select v-model="groupForm.groupName" placeholder="请选择分组">
            <el-option label="默认" value="default" />
            <el-option label="分组 A" value="A" />
            <el-option label="分组 B" value="B" />
            <el-option label="分组 C" value="C" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="groupDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAddToGroup">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { useWencaiPanelV2 } from './composables/useWencaiPanelV2'

const {
  loadingQueries,
  customQueryText,
  executingCustomQuery,
  currentQueryName,
  currentQueryText,
  tableData,
  loadingResults,
  currentPage,
  pageSize,
  total,
  groupDialogVisible,
  selectedStock,
  groupForm,
  treeProps,
  treeData,
  paginatedTableData,
  loadQueries,
  handleNodeClick,
  executeQuery,
  executeCustomQuery,
  formatNumber,
  formatPercent,
  getPriceChangeClass,
  handlePageChange,
  exportData,
  showGroupDialog,
  confirmAddToGroup
} = useWencaiPanelV2()
</script>

<style scoped lang="scss">
@import "./styles/WencaiPanelV2.scss";
</style>
