<template>
  <div class="architecture-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>系统架构概览</h1>
      <el-tag type="success" size="large">Week 3 简化后 - 双数据库架构</el-tag>
    </div>

    <!-- 架构摘要卡片 -->
    <el-card class="summary-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Grid /></el-icon>
          <span>架构简化成果</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-box">
            <div class="stat-value">4 → 2</div>
            <div class="stat-label">数据库数量</div>
            <el-tag type="success" size="small">简化 50%</el-tag>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-box">
            <div class="stat-value">299</div>
            <div class="stat-label">MySQL迁移数据（行）</div>
            <el-tag type="info" size="small">已完成</el-tag>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-box">
            <div class="stat-value">18</div>
            <div class="stat-label">迁移表数量</div>
            <el-tag type="info" size="small">已验证</el-tag>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-box">
            <div class="stat-value">100%</div>
            <div class="stat-label">Redis清理完成</div>
            <el-tag type="warning" size="small">已移除</el-tag>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 数据库架构图 -->
    <el-card class="architecture-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><DataBoard /></el-icon>
          <span>双数据库架构</span>
        </div>
      </template>
      <el-row :gutter="30">
        <!-- TDengine -->
        <el-col :xs="24" :md="12">
          <div class="database-box tdengine-box">
            <div class="db-icon">
              <el-icon :size="40"><DataLine /></el-icon>
            </div>
            <h3>TDengine 3.3.x</h3>
            <div class="db-subtitle">高频时序数据专用库</div>
            <el-divider />
            <div class="db-details">
              <div class="detail-item">
                <el-icon><Timer /></el-icon>
                <span>用途: Tick数据、分钟K线、实时深度</span>
              </div>
              <div class="detail-item">
                <el-icon><TrendCharts /></el-icon>
                <span>压缩比: 20:1 极致压缩</span>
              </div>
              <div class="detail-item">
                <el-icon><DArrowRight /></el-icon>
                <span>端口: 6030 (WebSocket), 6041 (REST)</span>
              </div>
              <div class="detail-item">
                <el-icon><Database /></el-icon>
                <span>数据库: market_data</span>
              </div>
            </div>
            <el-tag type="danger" effect="dark" class="db-tag">高频专用</el-tag>
          </div>
        </el-col>

        <!-- PostgreSQL -->
        <el-col :xs="24" :md="12">
          <div class="database-box postgresql-box">
            <div class="db-icon">
              <el-icon :size="40"><Coin /></el-icon>
            </div>
            <h3>PostgreSQL 17.x</h3>
            <div class="db-subtitle">通用数据仓库 + TimescaleDB扩展</div>
            <el-divider />
            <div class="db-details">
              <div class="detail-item">
                <el-icon><Files /></el-icon>
                <span>日线K线、参考数据、衍生数据</span>
              </div>
              <div class="detail-item">
                <el-icon><Document /></el-icon>
                <span>交易数据、元数据、系统配置</span>
              </div>
              <div class="detail-item">
                <el-icon><DArrowRight /></el-icon>
                <span>端口: 5432 (默认) / 5438</span>
              </div>
              <div class="detail-item">
                <el-icon><Database /></el-icon>
                <span>数据库: mystocks</span>
              </div>
            </div>
            <el-tag type="primary" effect="dark" class="db-tag">通用仓库</el-tag>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 数据分类路由 -->
    <el-card class="routing-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Share /></el-icon>
          <span>5大数据分类路由策略</span>
        </div>
      </template>
      <el-table :data="dataClassifications" stripe>
        <el-table-column prop="category" label="数据分类" width="150">
          <template #default="{ row }">
            <el-tag :type="row.tagType">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="特点" min-width="200" />
        <el-table-column prop="database" label="目标数据库" width="150">
          <template #default="{ row }">
            <el-tag :type="row.dbType" effect="dark">{{ row.database }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="examples" label="数据示例" min-width="250" />
      </el-table>
    </el-card>

    <!-- 移除的数据库 -->
    <el-card class="removed-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><DeleteFilled /></el-icon>
          <span>已移除的数据库</span>
        </div>
      </template>
      <el-alert
        title="MySQL 已完全移除"
        type="success"
        description="所有参考数据和元数据（18张表，299行数据）已成功迁移至PostgreSQL。MySQL连接和依赖已从代码库中移除。"
        :closable="false"
        show-icon
      />
      <el-alert
        title="Redis 已完全移除"
        type="warning"
        description="配置的db1为空，未在生产环境使用。应用层缓存现通过Python内置cachetools和functools.lru_cache实现。"
        :closable="false"
        show-icon
        style="margin-top: 16px"
      />
    </el-card>

    <!-- 技术栈信息 -->
    <el-card class="tech-stack-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Setting /></el-icon>
          <span>核心技术栈</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :xs="24" :md="12">
          <h4><el-icon><DataLine /></el-icon> 时序数据库</h4>
          <ul class="tech-list">
            <li>TDengine 3.3.6.13 - 高频时序数据专用</li>
            <li>TimescaleDB 2.22.0 - PostgreSQL时序扩展</li>
          </ul>
        </el-col>
        <el-col :xs="24" :md="12">
          <h4><el-icon><Coin /></el-icon> 关系数据库</h4>
          <ul class="tech-list">
            <li>PostgreSQL 17.6 - 主数据仓库</li>
            <li>psycopg2-binary - Python数据库驱动</li>
          </ul>
        </el-col>
      </el-row>
      <el-divider />
      <el-row :gutter="20">
        <el-col :xs="24" :md="12">
          <h4><el-icon><Platform /></el-icon> 后端框架</h4>
          <ul class="tech-list">
            <li>FastAPI 0.109+ - 高性能异步API</li>
            <li>Pydantic v2 - 数据验证</li>
            <li>Loguru 0.7.3 - 日志管理</li>
          </ul>
        </el-col>
        <el-col :xs="24" :md="12">
          <h4><el-icon><Monitor /></el-icon> 前端框架</h4>
          <ul class="tech-list">
            <li>Vue.js 3.4.0 - 前端框架</li>
            <li>Element Plus 2.8.0 - UI组件库</li>
            <li>ECharts 5.5.0 - 数据可视化</li>
          </ul>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  Grid,
  DataBoard,
  DataLine,
  Timer,
  TrendCharts,
  DArrowRight,
  Coin,
  Files,
  Document,
  Share,
  DeleteFilled,
  Setting,
  Platform,
  Monitor
} from '@element-plus/icons-vue'

// 数据分类路由配置
const dataClassifications = ref([
  {
    category: '第1类：市场数据',
    description: '高频时序数据，写入密集，时间范围查询',
    database: 'TDengine',
    dbType: 'danger',
    tagType: 'danger',
    examples: 'Tick数据、分钟K线、实时深度'
  },
  {
    category: '第1类：市场数据',
    description: '历史K线数据，复杂分析查询',
    database: 'PostgreSQL',
    dbType: 'primary',
    tagType: 'danger',
    examples: '日线、周线、月线数据'
  },
  {
    category: '第2类：参考数据',
    description: '相对静态，关系型结构，频繁JOIN操作',
    database: 'PostgreSQL',
    dbType: 'primary',
    tagType: 'success',
    examples: '股票信息、成分股信息、交易日历'
  },
  {
    category: '第3类：衍生数据',
    description: '计算密集，时序分析，复杂查询',
    database: 'PostgreSQL',
    dbType: 'primary',
    tagType: 'warning',
    examples: '技术指标、量化因子、模型输出、交易信号'
  },
  {
    category: '第4类：交易数据',
    description: '事务完整性要求高，需要ACID保证',
    database: 'PostgreSQL',
    dbType: 'primary',
    tagType: 'info',
    examples: '订单记录、成交记录、持仓记录、账户状态'
  },
  {
    category: '第5类：元数据',
    description: '配置管理，系统状态，结构化存储',
    database: 'PostgreSQL',
    dbType: 'primary',
    tagType: '',
    examples: '数据源状态、任务调度、策略参数、系统配置'
  }
])
</script>

<style scoped lang="scss">
.architecture-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 10px;

  h1 {
    margin: 0;
    font-size: 28px;
    color: #303133;
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;

  .el-icon {
    font-size: 20px;
  }
}

/* 摘要卡片样式 */
.summary-card {
  margin-bottom: 20px;

  .stat-box {
    text-align: center;
    padding: 20px 10px;
    border-radius: 8px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;

    .stat-value {
      font-size: 32px;
      font-weight: bold;
      margin-bottom: 8px;
    }

    .stat-label {
      font-size: 14px;
      margin-bottom: 10px;
      opacity: 0.9;
    }

    .el-tag {
      background-color: rgba(255, 255, 255, 0.2);
      border: none;
      color: white;
    }
  }

  .stat-box:nth-child(1) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  .stat-box:nth-child(2) {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  }

  .stat-box:nth-child(3) {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  }

  .stat-box:nth-child(4) {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  }
}

/* 数据库架构卡片 */
.architecture-card {
  margin-bottom: 20px;

  .database-box {
    padding: 30px;
    border-radius: 12px;
    background: white;
    border: 2px solid #e4e7ed;
    transition: all 0.3s;
    height: 100%;

    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }

    .db-icon {
      text-align: center;
      margin-bottom: 15px;
      color: #409eff;
    }

    h3 {
      text-align: center;
      margin: 0 0 5px 0;
      font-size: 22px;
      color: #303133;
    }

    .db-subtitle {
      text-align: center;
      color: #909399;
      font-size: 14px;
      margin-bottom: 15px;
    }

    .db-details {
      margin-top: 15px;

      .detail-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 0;
        font-size: 14px;
        color: #606266;

        .el-icon {
          color: #409eff;
          flex-shrink: 0;
        }
      }
    }

    .db-tag {
      width: 100%;
      margin-top: 15px;
      text-align: center;
      font-size: 14px;
      padding: 8px;
    }
  }

  .tdengine-box {
    border-color: #f56c6c;

    .db-icon {
      color: #f56c6c;
    }

    .detail-item .el-icon {
      color: #f56c6c;
    }
  }

  .postgresql-box {
    border-color: #409eff;

    .db-icon {
      color: #409eff;
    }
  }
}

/* 路由卡片样式 */
.routing-card {
  margin-bottom: 20px;
}

/* 移除数据库卡片 */
.removed-card {
  margin-bottom: 20px;

  .el-alert {
    border-radius: 8px;
  }
}

/* 技术栈卡片 */
.tech-stack-card {
  margin-bottom: 20px;

  h4 {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #303133;
    margin-bottom: 12px;

    .el-icon {
      color: #409eff;
    }
  }

  .tech-list {
    list-style: none;
    padding: 0;
    margin: 0;

    li {
      padding: 8px 0 8px 20px;
      color: #606266;
      position: relative;

      &::before {
        content: '•';
        position: absolute;
        left: 0;
        color: #409eff;
        font-weight: bold;
      }
    }
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;

    h1 {
      font-size: 22px;
    }
  }

  .stat-box {
    margin-bottom: 15px;

    .stat-value {
      font-size: 24px !important;
    }
  }

  .database-box {
    margin-bottom: 20px;
  }
}
</style>
