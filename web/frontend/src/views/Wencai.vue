<template>
  <div class="wencai-container">
    <!-- 页面头部 -->
    <el-card class="header-card">
      <template #header>
        <div class="card-header">
          <div>
            <h1>问财股票筛选系统</h1>
            <p class="subtitle">基于自然语言处理的智能股票筛选工具</p>
          </div>
          <div class="status">
            <el-statistic title="预定义查询" :value="9" />
            <el-statistic title="总筛选数" :value="totalRecords" />
            <el-statistic title="API状态" value="正常" />
          </div>
        </div>
      </template>

      <!-- 简介 -->
      <el-row :gutter="20">
        <el-col :xs="24" :sm="24" :md="12">
          <div class="info-box">
            <h3>📊 功能介绍</h3>
            <ul>
              <li>9个精选问财查询模板</li>
              <li>支持实时数据刷新</li>
              <li>CSV数据导出</li>
              <li>查询历史记录</li>
              <li>自定义查询模板</li>
            </ul>
          </div>
        </el-col>
        <el-col :xs="24" :sm="24" :md="12">
          <div class="info-box">
            <h3>🚀 快速开始</h3>
            <ul>
              <li>选择下方的查询模板</li>
              <li>点击"执行查询"获取数据</li>
              <li>点击"查看结果"查看完整数据</li>
              <li>使用"导出CSV"保存数据</li>
              <li>查看"历史"了解查询记录</li>
            </ul>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 标签页 -->
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 问财查询标签页 -->
      <el-tab-pane label="问财查询" name="wencai">
        <WencaiPanel />
      </el-tab-pane>

      <!-- 我的查询标签页 -->
      <el-tab-pane label="我的查询" name="my-queries">
        <div class="my-queries">
          <el-empty description="还没有保存的查询，执行查询后可以保存" />
          <!-- TODO: 实现我的查询功能 -->
        </div>
      </el-tab-pane>

      <!-- 查询统计标签页 -->
      <el-tab-pane label="统计分析" name="statistics">
        <div class="statistics">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="6">
              <el-statistic title="今日查询次数" :value="0" />
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-statistic title="本周查询次数" :value="0" />
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-statistic title="本月查询次数" :value="0" />
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-statistic title="总筛选数" :value="totalRecords" />
            </el-col>
          </el-row>
          <!-- TODO: 实现统计图表 -->
        </div>
      </el-tab-pane>

      <!-- 文档标签页 -->
      <el-tab-pane label="使用指南" name="guide">
        <div class="guide">
          <el-timeline>
            <el-timeline-item
              v-for="(item, index) in guide"
              :key="index"
              :timestamp="item.step"
              placement="top"
              :type="item.type"
            >
              <p><strong>{{ item.title }}</strong></p>
              <p>{{ item.description }}</p>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import WencaiPanel from '@/components/market/WencaiPanel.vue'

const activeTab = ref('wencai')
const totalRecords = ref(0)

const guide = [
  {
    step: '步骤 1',
    type: 'primary',
    title: '选择查询模板',
    description: '从问财查询标签页选择您感兴趣的查询模板。系统内置了9个常用的筛选模板。'
  },
  {
    step: '步骤 2',
    type: 'primary',
    title: '执行查询',
    description: '点击查询卡片上的"执行查询"按钮，系统会调用问财API获取最新数据。'
  },
  {
    step: '步骤 3',
    type: 'primary',
    title: '查看结果',
    description: '执行完成后，点击"查看结果"按钮可以看到详细的筛选结果，支持排序和搜索。'
  },
  {
    step: '步骤 4',
    type: 'primary',
    title: '导出数据',
    description: '在结果页面点击"导出CSV"按钮，可以将数据下载到本地进行进一步分析。'
  },
  {
    step: '步骤 5',
    type: 'success',
    title: '查看历史',
    description: '点击"历史"按钮可以查看该查询的历史执行记录和数据量变化趋势。'
  }
]

// 加载统计信息
const loadStatistics = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/market/wencai/queries')
    if (response.ok) {
      const data = await response.json()
      totalRecords.value = data.total || 0
    }
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

onMounted(() => {
  loadStatistics()
})
</script>

<style scoped lang="scss">
.wencai-container {
  padding: 20px;

  .header-card {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 20px;

      h1 {
        margin: 0 0 8px 0;
        font-size: 28px;
        color: #333;
      }

      .subtitle {
        margin: 0;
        color: #666;
        font-size: 14px;
      }

      .status {
        display: flex;
        gap: 30px;
        min-width: 300px;

        :deep(.el-statistic) {
          flex: 1;

          .el-statistic__title {
            font-size: 12px;
          }

          .el-statistic__content {
            font-size: 24px;
            color: #409eff;
          }
        }
      }
    }

    :deep(.el-card__body) {
      padding: 20px;
    }

    .info-box {
      h3 {
        margin: 0 0 15px 0;
        font-size: 16px;
        color: #333;
      }

      ul {
        margin: 0;
        padding-left: 20px;
        list-style: disc;

        li {
          margin-bottom: 8px;
          color: #666;
          font-size: 14px;
          line-height: 1.5;
        }
      }
    }
  }

  :deep(.el-tabs) {
    .el-tabs__nav-wrap {
      border-bottom: 1px solid #e0e6f6;
    }

    .el-tabs__content {
      padding: 20px;
    }
  }

  .my-queries,
  .statistics,
  .guide {
    min-height: 400px;
  }

  .guide {
    padding: 20px;

    :deep(.el-timeline) {
      padding: 0;

      .el-timeline-item__wrapper {
        padding-left: 30px;
      }

      .el-timeline-item__content {
        p {
          margin: 5px 0;
          color: #666;
          font-size: 14px;

          strong {
            color: #333;
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .wencai-container {
    .header-card {
      .card-header {
        flex-direction: column;

        .status {
          width: 100%;
          margin-top: 15px;
        }
      }
    }
  }
}
</style>
