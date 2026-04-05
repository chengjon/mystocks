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
@use '../../../../styles/artdeco-tokens.scss' as *;

.demo-card {
  position: relative;
  padding: var(--artdeco-spacing-5);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
  transition:
    border-color var(--artdeco-transition-quick) var(--artdeco-ease-out),
    box-shadow var(--artdeco-transition-quick) var(--artdeco-ease-out);

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: var(--artdeco-spacing-4);
    height: var(--artdeco-spacing-4);
    border: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-gold-primary);
  }

  &::before {
    top: var(--artdeco-spacing-3);
    left: var(--artdeco-spacing-3);
    border-right: none;
    border-bottom: none;
  }

  &::after {
    right: var(--artdeco-spacing-3);
    bottom: var(--artdeco-spacing-3);
    border-left: none;
    border-top: none;
  }

  &:hover {
    border-color: var(--artdeco-gold-primary);
    box-shadow: 0 0 var(--artdeco-spacing-4) color-mix(in srgb, var(--artdeco-gold-primary) 30%, transparent);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-5);
  padding-bottom: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
  border-bottom: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);

  .header-content {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-3);
  }

  .header-icon {
    font-size: calc(var(--artdeco-text-base) + var(--artdeco-spacing-px) * 4);
  }

  .header-title {
    font-family: var(--font-display);
    font-size: calc(var(--artdeco-text-base) + (var(--artdeco-spacing-px) * 2));
    color: var(--artdeco-gold-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wider);
  }
}

.status-badge {
  padding: calc(var(--artdeco-spacing-2) - (var(--artdeco-spacing-px) * 2))
    calc(var(--artdeco-spacing-3) + (var(--artdeco-spacing-px) * 2));
  border: 1px solid var(--artdeco-gold-primary);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 15%, transparent);
  color: var(--artdeco-fg-primary);
  font-family: var(--font-display);
  font-size: var(--artdeco-text-xs);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);

  &.success {
    background: color-mix(in srgb, var(--artdeco-gold-primary) 15%, transparent);
    border-color: var(--artdeco-gold-primary);
    color: var(--artdeco-fg-muted);
  }
}

.content-section {
  padding: var(--artdeco-spacing-3) 0;
  line-height: 1.8;
}

.section-title {
  display: flex;
  align-items: center;
  gap: calc(var(--artdeco-spacing-3) - (var(--artdeco-spacing-px) * 2));
  margin: 0 0 var(--artdeco-spacing-5) 0;
  font-family: var(--font-display);
  font-size: calc(var(--artdeco-text-base) + (var(--artdeco-spacing-px) * 2));
  color: var(--artdeco-gold-primary);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wider);

  .title-icon {
    font-size: calc(var(--artdeco-text-base) + var(--artdeco-spacing-px) * 4);
  }
}

.intro-section {
  margin-bottom: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-px));

  .intro-text {
    margin: 0;
    padding: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px)) var(--artdeco-spacing-5);
    background: var(--artdeco-bg-global);
    border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
       color: var(--artdeco-fg-muted);
    font-family: var(--font-body);
    font-size: calc(var(--artdeco-text-sm) + var(--artdeco-spacing-px));
    line-height: 1.8;
  }
}

.features-section,
.tech-section {
  margin-bottom: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-px));
}

.features-grid,
.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(calc((var(--artdeco-spacing-20) * 3) + var(--artdeco-spacing-10)), 1fr));
}

.features-grid {
  gap: var(--artdeco-spacing-5);
}

.feature-card {
  position: relative;
  padding: var(--artdeco-spacing-5);
  background: var(--artdeco-bg-global);
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  transition:
    transform var(--artdeco-transition-quick) var(--artdeco-ease-out),
    box-shadow var(--artdeco-transition-quick) var(--artdeco-ease-out),
    border-color var(--artdeco-transition-quick) var(--artdeco-ease-out);

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: calc(var(--artdeco-spacing-2) + (var(--artdeco-spacing-px) * 2));
    height: calc(var(--artdeco-spacing-2) + (var(--artdeco-spacing-px) * 2));
    border: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-gold-primary);
  }

  &::before {
    top: var(--artdeco-spacing-2);
    left: var(--artdeco-spacing-2);
    border-right: none;
    border-bottom: none;
  }

  &::after {
    right: var(--artdeco-spacing-2);
    bottom: var(--artdeco-spacing-2);
    border-left: none;
    border-top: none;
  }

  &:hover {
    transform: translateY(calc(var(--artdeco-spacing-px) * -2));
    border-color: var(--artdeco-gold-primary);
    box-shadow: 0 0 var(--artdeco-spacing-3) color-mix(in srgb, var(--artdeco-gold-primary) 25%, transparent);
  }

  .feature-title {
    display: flex;
    align-items: center;
    gap: calc(var(--artdeco-spacing-3) - (var(--artdeco-spacing-px) * 2));
    margin: 0 0 calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px)) 0;
    font-family: var(--font-display);
    font-size: calc(var(--artdeco-text-sm) + var(--artdeco-spacing-px));
       color: var(--artdeco-fg-muted);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);

    .feature-icon {
      font-size: calc(var(--artdeco-text-base) + (var(--artdeco-spacing-px) * 2));
    }
  }

  .feature-list {
    margin: 0;
    padding-left: var(--artdeco-spacing-5);
    list-style: none;

    li {
      position: relative;
      padding: calc(var(--artdeco-spacing-2) - (var(--artdeco-spacing-px) * 2)) 0
        calc(var(--artdeco-spacing-2) - (var(--artdeco-spacing-px) * 2)) var(--artdeco-spacing-5);
      color: var(--artdeco-fg-primary);
      font-family: var(--font-body);
      font-size: calc(var(--artdeco-text-sm) - var(--artdeco-spacing-px));
      line-height: 1.6;

      &::before {
        content: '•';
        position: absolute;
        left: 0;
        color: var(--artdeco-gold-primary);
        font-weight: var(--artdeco-font-bold);
      }
    }
  }
}

.tech-grid {
  gap: 0;
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);

  .tech-item {
    display: flex;
    flex-direction: column;
    padding: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px)) var(--artdeco-spacing-5);
    border-bottom: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
    background: var(--artdeco-bg-global);

    &:nth-child(even) {
      background: color-mix(in srgb, var(--artdeco-gold-primary) 3%, var(--artdeco-bg-global));
    }

    label {
      margin-bottom: var(--artdeco-spacing-2);
      color: var(--artdeco-gold-dim);
      font-family: var(--font-display);
      font-size: var(--artdeco-text-xs);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
    }

    span {
      color: var(--artdeco-fg-primary);
      font-family: var(--font-body);
      font-size: var(--artdeco-text-sm);
    }
  }
}

.advantages-section {
  padding: var(--artdeco-spacing-5);
  background: color-mix(in srgb, var(--artdeco-info) 8%, var(--artdeco-bg-card));
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);

  .advantages-header {
    display: flex;
    align-items: center;
    gap: calc(var(--artdeco-spacing-3) - (var(--artdeco-spacing-px) * 2));
    margin-bottom: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));

    .advantages-icon {
      font-size: calc(var(--artdeco-text-base) + var(--artdeco-spacing-px) * 4);
    }

    .advantages-title {
      color: var(--artdeco-gold-primary);
      font-family: var(--font-display);
      font-size: var(--artdeco-text-base);
      font-weight: var(--artdeco-font-semibold);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
    }
  }

  .advantages-list {
    margin: 0;
    padding-left: var(--artdeco-spacing-5);
    list-style: none;

    li {
      position: relative;
      padding: var(--artdeco-spacing-2) 0 var(--artdeco-spacing-2) var(--artdeco-spacing-5);
      color: var(--artdeco-fg-primary);
      font-family: var(--font-body);
      font-size: var(--artdeco-text-sm);
      line-height: 1.6;

      &::before {
        content: '•';
        position: absolute;
        left: 0;
        color: var(--artdeco-gold-primary);
        font-weight: var(--artdeco-font-bold);
      }
    }
  }
}

@media (width <= 48rem) {
  .demo-card {
    padding: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--artdeco-spacing-3);
  }

  .features-grid,
  .tech-grid {
    grid-template-columns: 1fr;
  }
}
</style>
