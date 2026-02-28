<template>
  <div class="architecture-container">

    <div class="page-header">
      <h1 class="page-title">系统架构概览</h1>
      <div class="version-badge">WEEK 3 SIMPLIFICATION</div>
      <div class="decorative-line"></div>
    </div>

    <div class="artde-card summary-card">
      <div class="card-header">
        <h2 class="section-title">架构简化成果</h2>
      </div>

      <div class="stats-grid">
        <div class="stat-box">
          <div class="stat-value">4 → 2</div>
          <div class="stat-label">数据库数量</div>
          <div class="stat-badge">简化50%</div>
        </div>
        <div class="stat-box">
          <div class="stat-value">299</div>
          <div class="stat-label">MySQL迁移数据（行）</div>
          <div class="stat-badge info">已完成</div>
        </div>
        <div class="stat-box">
          <div class="stat-value">18</div>
          <div class="stat-label">迁移表数量</div>
          <div class="stat-badge info">已验证</div>
        </div>
        <div class="stat-box">
          <div class="stat-value">100%</div>
          <div class="stat-label">Redis清理完成</div>
          <div class="stat-badge warning">已移除</div>
        </div>
      </div>
    </div>

    <div class="artde-card architecture-card">
      <div class="card-header">
        <h2 class="section-title">双数据库架构</h2>
      </div>

      <div class="databases-section">
        <div class="database-box tdengine-box">
          <div class="db-header">
            <h3>TDengine 3.3.x</h3>
            <div class="db-subtitle">高频时序数据专用库</div>
            <div class="db-tag danger">高频专用</div>
          </div>
          <div class="db-details">
            <div class="detail-item">
              <span class="detail-icon">⏱</span>
              <span class="detail-text">用途: Tick数据、分钟K线、实时深度</span>
            </div>
            <div class="detail-item">
              <span class="detail-icon">📈</span>
              <span class="detail-text">压缩比: 20:1 一致压缩</span>
            </div>
            <div class="detail-item">
              <span class="detail-icon">🔌</span>
              <span class="detail-text">端口: 6030 (WebSocket), 6041 (REST)</span>
            </div>
            <div class="detail-item">
              <span class="detail-icon">📊</span>
              <span class="detail-text">数据库: market_data</span>
            </div>
          </div>
        </div>

        <div class="database-box postgresql-box">
          <div class="db-header">
            <h3>PostgreSQL 17.x</h3>
            <div class="db-subtitle">通用数据仓库 + TimescaleDB扩展</div>
            <div class="db-tag primary">通用仓库</div>
          </div>
          <div class="db-details">
            <div class="detail-item">
              <span class="detail-icon">📋</span>
              <span class="detail-text">日线K线、参考数据、衍生数据</span>
            </div>
            <div class="detail-item">
              <span class="detail-icon">📄</span>
              <span class="detail-text">交易数据、元数据、系统配置</span>
            </div>
            <div class="detail-item">
              <span class="detail-icon">🔌</span>
              <span class="detail-text">端口: 5432 (默认) / 5438</span>
            </div>
            <div class="detail-item">
              <span class="detail-icon">📊</span>
              <span class="detail-text">数据库: mystocks</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="artde-card routing-card">
      <div class="card-header">
        <h2 class="section-title">5大数据分类路由策略</h2>
      </div>

      <table class="routing-table">
        <thead>
          <tr>
            <th>数据分类</th>
            <th>特点</th>
            <th>目标数据库</th>
            <th>数据示例</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><span class="category-tag danger">第1类</span></td>
            <td>高频时序数据，写入密集，时间范围查询</td>
            <td><span class="db-tag danger">TDengine</span></td>
            <td>Tick数据、分钟K线、实时深度</td>
          </tr>
          <tr>
            <td><span class="category-tag">第1类</span></td>
            <td>历史K线数据，复杂分析查询</td>
            <td><span class="db-tag primary">PostgreSQL</span></td>
            <td>日线、周线、月线数据</td>
          </tr>
          <tr>
            <td><span class="category-tag success">第2类</span></td>
            <td>相对静态，关系型结构，频繁JOIN操作</td>
            <td><span class="db-tag primary">PostgreSQL</span></td>
            <td>股票信息、成分股信息、交易日历</td>
          </tr>
          <tr>
            <td><span class="category-tag warning">第3类</span></td>
            <td>计算密集，时序分析，复杂查询</td>
            <td><span class="db-tag primary">PostgreSQL</span></td>
            <td>技术指标、量化因子、模型输出、交易信号</td>
          </tr>
          <tr>
            <td><span class="category-tag info">第4类</span></td>
            <td>事务完整性要求高，需要ACID保证</td>
            <td><span class="db-tag primary">PostgreSQL</span></td>
            <td>订单记录、成交记录、持仓记录、账户状态</td>
          </tr>
          <tr>
            <td><span class="category-tag">第5类</span></td>
            <td>配置管理，系统状态，结构化存储</td>
            <td><span class="db-tag primary">PostgreSQL</span></td>
            <td>数据源状态、任务调度、策略参数、系统配置</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="alert-box success">
      <svg class="alert-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" :stroke="'var(--fall)'" stroke-width="2">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
        <polyline points="22,4 12,14.01 9,11.01"></polyline>
      </svg>
      <div class="alert-content">
        <div class="alert-title">MySQL 已完全移除</div>
        <div class="alert-desc">所有参考数据和元数据（18张表，299行数据）已成功迁移至PostgreSQL。MySQL连接和依赖已从代码库中移除。</div>
      </div>
    </div>

    <div class="alert-box warning">
      <svg class="alert-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
      </svg>
      <div class="alert-content">
        <div class="alert-title">Redis 已完全移除</div>
        <div class="alert-desc">配置的db1为空，未在生产环境使用。应用层缓存现通过Python内置cachetools和functools.lru_cache实现。</div>
      </div>
    </div>

    <div class="artde-card tech-stack-card">
      <div class="card-header">
        <h2 class="section-title">核心技术栈</h2>
      </div>

      <div class="tech-grid">
        <div class="tech-section">
          <h4 class="tech-title">
            <span>⏱</span>
            时序数据库
          </h4>
          <ul class="tech-list">
            <li>TDengine 3.3.6.13 - 高频时序数据专用</li>
            <li>TimescaleDB 2.2.0 - PostgreSQL时序扩展</li>
          </ul>
        </div>

        <div class="tech-section">
          <h4 class="tech-title">
            <span>🐘</span>
            关系数据库
          </h4>
          <ul class="tech-list">
            <li>PostgreSQL 17.6 - 主数据仓库</li>
            <li>psycopg2-binary - Python数据库驱动</li>
          </ul>
        </div>

        <div class="tech-section">
          <h4 class="tech-title">
            <span>🚀</span>
            后端框架
          </h4>
          <ul class="tech-list">
            <li>FastAPI 0.109+ - 高性能异步API</li>
            <li>Pydantic v2 - 数据验证</li>
            <li>Loguru 0.7.3 - 日志管理</li>
          </ul>
        </div>

        <div class="tech-section">
          <h4 class="tech-title">
            <span>🖥️</span>
            前端框架
          </h4>
          <ul class="tech-list">
            <li>Vue.js 3.4.0 - 前端框架</li>
            <li>Element Plus 2.8.0 - UI组件库</li>
            <li>ECharts 5.5.0 - 数据可视化</li>
          </ul>
        </div>
      </div>

      <div class="tech-divider"></div>

      <div class="tech-grid">
        <div class="tech-section">
          <h4 class="tech-title">
            <span>📡</span>
            WebSocket实时通信
          </h4>
          <ul class="tech-list">
            <li>TickWebSocket - Tick数据推送</li>
            <li>市场数据实时推送</li>
            <li>K线图实时更新</li>
          </ul>
        </div>

        <div class="tech-section">
          <h4 class="tech-title">
            <span>🔄</span>
            任务调度
          </h4>
          <ul class="tech-list">
            <li>Celery Beat - 分布式任务队列</li>
            <li>定时数据采集任务</li>
            <li>策略定时评估任务</li>
          </ul>
        </div>

        <div class="tech-section">
          <h4 class="tech-title">
            <span>📊</span>
            数据分析
          </h4>
          <ul class="tech-list">
            <li>Pandas - 数据处理</li>
            <li>NumPy - 数值计算</li>
            <li>Ta-Lib - 技术指标库</li>
          </ul>
        </div>

        <div class="tech-section">
          <h4 class="tech-title">
            <span>⚡</span>
            量化框架
          </h4>
          <ul class="tech-list">
            <li>Backtrader - 回测框架</li>
            <li>TA-Lib - 技术分析</li>
            <li>自定义策略框架</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const _dataClassifications = ref([
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
    examples: '数据源状态、任务调度、策略参数、系统配置'
  }
])
</script>

<style scoped lang="scss">
@import "./styles/Architecture";
</style>
