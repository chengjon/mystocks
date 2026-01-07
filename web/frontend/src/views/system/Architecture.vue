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
    examples: '数据源状态、任务调度、策略参数、系统配置'
  }
])
</script>

<style scoped lang="scss">

.architecture-container {
  padding: 20px;
  min-height: 100vh;
  background: var(--bg-primary);
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
}

.background-pattern {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.04;
  background-image:
    repeating-linear-gradient(45deg, var(--gold-primary) 0px, var(--gold-primary) 1px, transparent 1px, transparent 10px),
    repeating-linear-gradient(-45deg, var(--gold-primary) 0px, var(--gold-primary) 1px, transparent 1px, transparent 10px);
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 30px 0;
  position: relative;

  .page-title {
    font-family: var(--font-display);
    font-size: 32px;
    color: var(--gold-primary);
    text-transform: uppercase;
    letter-spacing: 4px;
    margin: 0 0 8px 0;
    display: inline-block;
    vertical-align: middle;
  }

  .version-badge {
    display: inline-block;
    vertical-align: middle;
    margin-left: 20px;
    padding: 8px 16px;
    background: rgba(0, 230, 118, 0.15);
    border: 1px solid var(--fall);
    color: var(--fall);
    font-family: var(--font-display);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .decorative-line {
    display: block;
    width: 200px;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold-primary), transparent);
    margin: 20px auto 0;

    &::before {
      content: '';
      position: absolute;
      bottom: -6px;
      left: 50%;
      transform: translateX(-50%);
      width: 60px;
      height: 1px;
      background: linear-gradient(90deg, transparent, var(--gold-muted), transparent);
    }
  }
}

.card {
  background: var(--bg-secondary);
  border: 1px solid var(--gold-dim);
  padding: 20px;
  position: relative;
  border-radius: 0;
  margin-bottom: 20px;

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 16px;
    height: 16px;
    border: 2px solid var(--gold-primary);
  }

  &::before {
    top: 12px;
    left: 12px;
    border-right: none;
    border-bottom: none;
  }

  &::after {
    bottom: 12px;
    right: 12px;
    border-left: none;
    border-top: none;
  }

  &:hover {
    border-color: var(--gold-primary);
    box-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
  }
}

.section-title {
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--gold-primary);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin: 0 0 20px 0;
}

.summary-card .stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-box {
  text-align: center;
  padding: 25px 20px;
  background: var(--bg-primary);
  border: 1px solid var(--gold-dim);

  .stat-value {
    font-family: var(--font-display);
    font-size: 36px;
    color: var(--gold-primary);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 8px;
    font-weight: 600;
  }

  .stat-label {
    font-family: var(--font-body);
    font-size: 13px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .stat-badge {
    display: inline-block;
    margin-top: 10px;
    padding: 4px 12px;
    background: rgba(212, 175, 55, 0.1);
    border: 1px solid var(--gold-dim);
    color: var(--gold-primary);
    font-family: var(--font-display);
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;

    &.info {
      background: rgba(64, 158, 255, 0.15);
      border-color: #409EFF;
      color: #409EFF;
    }

    &.warning {
      background: rgba(255, 82, 82, 0.15);
      border-color: #F56C6C;
      color: #F56C6C;
    }
  }
}

.databases-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.database-box {
  background: var(--bg-primary);
  border: 1px solid var(--artde-co-gold-dim);
  padding: 20px;
  position: relative;

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 12px;
    height: 12px;
    border: 2px solid var(--gold-primary);
  }

  &::before {
    top: 8px;
    left: 8px;
    border-right: none;
    border-bottom: none;
  }

  &::after {
    bottom: 8px;
    right: 8px;
    border-left: none;
    border-top: none;
  }

  .db-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 15px;

    h3 {
      font-family: var(--font-display);
      font-size: 18px;
      color: var(--gold-primary);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin: 0 0 8px 0;
    }

    .db-subtitle {
      color: var(--text-muted);
      font-family: var(--font-body);
      font-size: 13px;
      margin-bottom: 8px;
    }

    .db-tag {
      padding: 4px 12px;
      font-family: var(--font-display);
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 1px;

      &.danger {
        background: rgba(255, 82, 82, 0.15);
        border: 1px solid var(--rise);
        color: var(--rise);
      }

      &.primary {
        background: rgba(64, 158, 255, 0.15);
        border: 1px solid #409EFF;
        color: #409EFF;
      }
    }
  }

  .db-details {
    .detail-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 0;
      color: var(--text-primary);
      font-family: var(--font-body);
      font-size: 14px;

      .detail-icon {
        font-size: 16px;
      }

      .detail-text {
        flex: 1;
      }
    }
  }
}

.routing-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--font-body);

  thead {
    tr {
      background: rgba(212, 175, 55, 0.08);

      th {
        padding: 16px 12px;
        text-align: left;
        font-family: var(--font-display);
        font-size: 11px;
        font-weight: 600;
        color: var(--gold-primary);
        text-transform: uppercase;
        letter-spacing: 2px;
        border-bottom: 2px solid var(--gold-primary);
      }
    }
  }

  tbody {
    tr {
      border-bottom: 1px solid var(--gold-dim);
      transition: all 0.3s ease;

      &:hover {
        background: rgba(212, 175, 55, 0.05);
      }

      td {
        padding: 14px 12px;
        color: var(--text-primary);
        font-size: 14px;
      }
    }
  }
}

.category-tag {
  display: inline-block;
  padding: 4px 10px;
  font-family: var(--font-display);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;

  &.danger {
    background: rgba(255, 82, 82, 0.15);
    border: 1px solid var(--rise);
    color: var(--rise);
  }

  &.success {
    background: rgba(0, 230, 118, 0.15);
    border: 1px solid var(--fall);
    color: var(--fall);
  }

  &.warning {
    background: rgba(244, 179, 67, 0.15);
    border: 1px solid #F4A738;
    color: #F4A738;
  }

  &.info {
    background: rgba(64, 158, 255, 0.15);
    border: 1px solid #409EFF;
    color: #409EFF;
  }
}

.db-tag {
  display: inline-block;
  padding: 4px 10px;
  font-family: var(--font-display);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;

  &.danger {
    background: rgba(255, 82, 82, 0.15);
    border: 1px solid var(--rise);
    color: var(--rise);
  }

  &.primary {
    background: rgba(64, 158, 255, 0.15);
    border: 1px solid #409EFF;
    color: #409EFF;
  }
}

.alert-box {
  display: flex;
  gap: 16px;
  padding: 20px;
  margin: 20px 0;
  background: var(--bg-primary);
  border: 1px solid var(--gold-dim);

  .alert-icon {
    flex-shrink: 0;
  }

  .alert-content {
    flex: 1;

    .alert-title {
      font-family: var(--font-display);
      font-size: 16px;
      color: var(--gold-primary);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 8px;
      font-weight: 600;
    }

    .alert-desc {
      color: var(--text-primary);
      font-family: var(--font-body);
      font-size: 14px;
      line-height: 1.6;
    }
  }

  &.success {
    border-color: var(--fall);
    background: rgba(0, 230, 118, 0.05);
  }

  &.warning {
    border-color: var(--gold-primary);
    background: rgba(212, 175, 55, 0.05);
  }
}

.tech-stack-card .tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.tech-section {
  h4.tech-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: var(--font-display);
    font-size: 14px;
    color: var(--gold-primary);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 0 0 12px 0;
  }
}

.tech-list {
  list-style: none;
  padding: 0;
  margin: 0;

  li {
    padding: 8px 0 8px 20px;
    color: var(--text-primary);
    font-family: var(--font-body);
    font-size: 14px;
    line-height: 1.6;
    position: relative;
    padding-left: 20px;

    &::before {
      content: '•';
      position: absolute;
      left: 0;
      color: #409EFF;
      font-weight: bold;
    }
  }
}

.tech-divider {
  grid-column: 1 / -1;
  border-top: 1px solid var(--gold-dim);
  margin: 20px 0;
}

@media (max-width: 768px) {
  .page-header {
    padding: 20px 0;

    .page-title {
      font-size: 24px;
      letter-spacing: 2px;
    }
  }

  .summary-card .stats-grid {
    grid-template-columns: 1fr;
  }

  .databases-section {
    grid-template-columns: 1fr;
  }

  .routing-table {
    font-size: 12px;

    thead th, tbody td {
      padding: 12px 8px;
    }
  }

  .tech-grid {
    grid-template-columns: 1fr;
  }
}
</style>
