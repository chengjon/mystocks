<template>
  <div class="demo-card card">
    <div class="card-header">
      <div class="header-content">
        <span class="header-icon">📋</span>
        <span class="header-title">项目概览</span>
      </div>
      <span class="status-badge success">已迁移</span>
    </div>

    <div class="content-section">
      <div class="intro-section">
        <h3 class="section-title">
          <span class="title-icon">🎯</span>
          Stock-Analysis 简介
        </h3>
        <p class="intro-text">
          Stock-Analysis 是一个基于通达信数据的中国 A 股股票筛选和回测分析系统。
          它利用通达信强大的本地数据优势，结合 Python 的灵活性，提供高效的股票筛选策略和完整的回测框架。
        </p>
      </div>

      <div class="features-section">
        <h3 class="section-title">
          <span class="title-icon">✨</span>
          核心功能
        </h3>
        <div class="features-grid">
          <div class="feature-card">
            <h4 class="feature-title">
              <span class="feature-icon">📂</span>
              通达信数据解析
            </h4>
            <ul class="feature-list">
              <li>解析通达信 .day/.lc1/.lc5 等二进制文件</li>
              <li>支持日线、分钟线、5分钟线数据</li>
              <li>自动识别股票代码和市场</li>
              <li>高效的数据缓存机制</li>
              <li>支持历史数据和实时数据</li>
            </ul>
          </div>

          <div class="feature-card">
            <h4 class="feature-title">
              <span class="feature-icon">🔍</span>
              股票筛选策略
            </h4>
            <ul class="feature-list">
              <li>技术指标筛选 (MA, MACD, RSI, KDJ等)</li>
              <li>形态识别 (突破、金叉、底部等)</li>
              <li>量价分析 (放量、缩量、量比等)</li>
              <li>基本面筛选 (PE, PB, 净利润等)</li>
              <li>自定义组合条件筛选</li>
            </ul>
          </div>

          <div class="feature-card">
            <h4 class="feature-title">
              <span class="feature-icon">📈</span>
              回测分析
            </h4>
            <ul class="feature-list">
              <li>集成 rqalpha 回测引擎</li>
              <li>支持多策略并行回测</li>
              <li>完整的交易记录和分析</li>
              <li>资金曲线和回撤分析</li>
              <li>夏普比率等性能指标</li>
            </ul>
          </div>

          <div class="feature-card">
            <h4 class="feature-title">
              <span class="feature-icon">⏰</span>
              实时和盘后筛选
            </h4>
            <ul class="feature-list">
              <li>盘中实时数据更新</li>
              <li>盘后自动筛选</li>
              <li>邮件/微信通知推送</li>
              <li>自定义筛选时间</li>
              <li>历史筛选结果保存</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="tech-section">
        <h3 class="section-title">
          <span class="title-icon">🔧</span>
          技术架构
        </h3>
        <div class="tech-grid">
          <div class="tech-item">
            <label>数据源</label>
            <span>通达信本地数据 (.day/.lc1/.lc5)</span>
          </div>
          <div class="tech-item">
            <label>数据解析</label>
            <span>struct 二进制解析</span>
          </div>
          <div class="tech-item">
            <label>策略语言</label>
            <span>Python 3.x</span>
          </div>
          <div class="tech-item">
            <label>回测引擎</label>
            <span>rqalpha</span>
          </div>
          <div class="tech-item">
            <label>技术指标</label>
            <span>TA-Lib</span>
          </div>
          <div class="tech-item">
            <label>数据存储</label>
            <span>SQLite / PostgreSQL</span>
          </div>
        </div>
      </div>

      <div class="advantages-section">
        <div class="advantages-header">
          <span class="advantages-icon">💡</span>
          <span class="advantages-title">项目优势</span>
        </div>
        <ul class="advantages-list">
          <li><strong>数据本地化</strong>: 使用通达信本地数据，无需网络，速度快</li>
          <li><strong>数据全面性</strong>: 覆盖所有 A 股历史数据，包括分钟级</li>
          <li><strong>策略灵活性</strong>: 支持复杂的自定义筛选条件</li>
          <li><strong>回测可靠性</strong>: 基于真实历史数据，避免未来函数</li>
          <li><strong>实时性</strong>: 支持盘中实时监控和筛选</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 项目概览组件
</script>

<style scoped lang="scss">

.demo-card {
  background: var(--bg-secondary);
  border: 1px solid var(--gold-dim);
  padding: 20px;
  position: relative;
  border-radius: 0;

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
    box-shadow: 0 0 15px rgb(212 175 55 / 30%);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--gold-dim);

  .header-content {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .header-icon {
    font-size: 20px;
  }

  .header-title {
    font-family: var(--font-display);
    font-size: 18px;
    color: var(--gold-primary);
    text-transform: uppercase;
    letter-spacing: 2px;
  }
}

.status-badge {
  padding: 6px 14px;
  background: rgb(0 230 118 / 15%);
  border: 1px solid var(--fall);
  color: var(--fall);
  font-family: var(--font-display);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;

  &.success {
    background: rgb(0 230 118 / 15%);
    border-color: var(--fall);
    color: var(--fall);
  }
}

.content-section {
  padding: 10px 0;
  line-height: 1.8;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--gold-primary);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin: 0 0 20px 0;

  .title-icon {
    font-size: 20px;
  }
}

.intro-section {
  margin-bottom: 25px;

  .intro-text {
    font-family: var(--font-body);
    font-size: 15px;
    color: var(--text-primary);
    line-height: 1.8;
    margin: 0;
    padding: 15px 20px;
    background: var(--bg-primary);
    border: 1px solid var(--gold-dim);
  }
}

.features-section {
  margin-bottom: 25px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.feature-card {
  background: var(--bg-primary);
  border: 1px solid var(--gold-dim);
  padding: 20px;
  position: relative;
  transition: all 0.3s ease;

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 10px;
    height: 10px;
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

  &:hover {
    border-color: var(--gold-primary);
    box-shadow: 0 0 12px rgb(212 175 55 / 25%);
    transform: translateY(-2px);
  }

  .feature-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: var(--font-display);
    font-size: 15px;
    color: var(--text-primary);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 0 0 15px 0;

    .feature-icon {
      font-size: 18px;
    }
  }

  .feature-list {
    margin: 0;
    padding-left: 20px;
    list-style: none;

    li {
      position: relative;
      padding: 6px 0 6px 20px;
      font-family: var(--font-body);
      font-size: 13px;
      color: var(--text-primary);
      line-height: 1.6;

      &::before {
        content: '•';
        position: absolute;
        left: 0;
        color: var(--gold-primary);
        font-weight: bold;
      }
    }
  }
}

.tech-section {
  margin-bottom: 25px;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 0;
  border: 1px solid var(--gold-dim);

  .tech-item {
    display: flex;
    flex-direction: column;
    padding: 15px 20px;
    border-bottom: 1px solid var(--gold-dim);
    background: var(--bg-primary);

    &:nth-child(odd) {
      background: var(--bg-primary);
    }

    &:nth-child(even) {
      background: rgb(212 175 55 / 3%);
    }

    label {
      font-family: var(--font-display);
      font-size: 11px;
      color: var(--gold-muted);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 8px;
    }

    span {
      font-family: var(--font-body);
      font-size: 14px;
      color: var(--text-primary);
    }
  }
}

.advantages-section {
  background: rgb(64 158 255 / 8%);
  border: 1px solid var(--gold-dim);
  padding: 20px;

  .advantages-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 15px;

    .advantages-icon {
      font-size: 20px;
    }

    .advantages-title {
      font-family: var(--font-display);
      font-size: 16px;
      color: var(--gold-primary);
      text-transform: uppercase;
      letter-spacing: 1px;
      font-weight: 600;
    }
  }

  .advantages-list {
    margin: 0;
    padding-left: 20px;
    list-style: none;

    li {
      position: relative;
      padding: 8px 0 8px 20px;
      font-family: var(--font-body);
      font-size: 14px;
      color: var(--text-primary);
      line-height: 1.6;

      &::before {
        content: '•';
        position: absolute;
        left: 0;
        color: var(--gold-primary);
        font-weight: bold;
      }
    }
  }
}

@media (width <= 768px) {
  .demo-card {
    padding: 15px;
  }

  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .tech-grid {
    grid-template-columns: 1fr;
  }
}
</style>
