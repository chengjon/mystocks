<template>
  <div class="demo-card card">
    <div class="card-header">
      <div class="header-content">
        <span class="header-icon">📋</span>
        <span class="header-title">项目概览</span>
      </div>
      <span class="status-badge success">已迁移</span>
    </div>

    <div class="overview-section">
      <div class="info-grid">
        <div class="info-item">
          <label>项目名称</label>
          <span>PyProfiling - 股票预测与性能分析工具包</span>
        </div>
        <div class="info-item">
          <label>主要用途</label>
          <span>使用 LightGBM 预测股票价格 + Python 性能分析</span>
        </div>
        <div class="info-item">
          <label>数据源</label>
          <span>通达信（Tongdaxin）二进制 .day 文件</span>
        </div>
        <div class="info-item">
          <label>核心模型</label>
          <span>LightGBM Regressor（GBDT 回归）</span>
        </div>
        <div class="info-item">
          <label>特征工程</label>
          <span>滚动窗口特征（10步 × 6特征 = 60列）</span>
        </div>
        <div class="info-item">
          <label>评估指标</label>
          <span>RMSE（均方根误差）</span>
        </div>
      </div>

      <div class="features-section">
        <h3 class="section-title">
          <span class="title-icon">🔧</span>
          核心功能模块
        </h3>
        <div class="features-grid">
          <div class="feature-card">
            <h4 class="feature-title">
              <span class="feature-icon">📈</span>
              股票价格预测
            </h4>
            <ul class="feature-list">
              <li>通达信数据解析</li>
              <li>滚动窗口特征工程</li>
              <li>LightGBM 模型训练</li>
              <li>预测结果可视化</li>
            </ul>
          </div>

          <div class="feature-card">
            <h4 class="feature-title">
              <span class="feature-icon">🎯</span>
              特征选择
            </h4>
            <ul class="feature-list">
              <li>RFE（递归特征消除）</li>
              <li>Mutual Information</li>
              <li>LinearSVC 特征选择</li>
              <li>ExtraTreesClassifier</li>
            </ul>
          </div>

          <div class="feature-card">
            <h4 class="feature-title">
              <span class="feature-icon">⚡</span>
              性能分析
            </h4>
            <ul class="feature-list">
              <li>cProfile 函数分析</li>
              <li>line_profiler 逐行分析</li>
              <li>memory_profiler 内存分析</li>
              <li>timeit 执行时间测量</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="info-alert">
        <svg class="alert-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" :stroke="'var(--artdeco-gold-primary)'" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="16" x2="12" y2="12"></line>
          <line x1="12" y1="8" x2="12.01" y2="8"></line>
        </svg>
        <div class="alert-content">
          <div class="alert-title">数据流程</div>
          <div class="alert-text">
            <strong>完整数据流程：</strong>
            通达信 .day 文件 → 二进制解析（32字节结构）→ OHLCV DataFrame →
            滚动窗口特征工程 → CSV 数据集 → LightGBM 训练 → 预测结果
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 项目概览组件 - 无需额外逻辑
</script>

<style scoped lang="scss">
@use '../../../../styles/artdeco-tokens.scss' as *;

.demo-card {
  position: relative;
  padding: var(--artdeco-spacing-5);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-none);
  box-shadow: var(--artdeco-shadow-md);

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
    border-top: none;
    border-left: none;
  }

  &:hover {
    border-color: var(--artdeco-gold-primary);
    box-shadow: var(--artdeco-shadow-lg), var(--artdeco-glow-subtle);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-5);
  padding-bottom: var(--artdeco-spacing-4);
  border-bottom: 1px solid var(--artdeco-gold-dim);

  .header-content {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-3);
  }

  .header-icon {
    font-size: var(--artdeco-text-lg);
  }

  .header-title {
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-heading, var(--font-display));
    font-size: var(--artdeco-text-lg);
    letter-spacing: calc(var(--artdeco-spacing-px) * 2);
    text-transform: uppercase;
  }
}

.status-badge {
  padding: var(--artdeco-spacing-1) var(--artdeco-spacing-3);
  font-family: var(--artdeco-font-heading, var(--font-display));
  font-size: var(--artdeco-text-compact-xs);
  letter-spacing: var(--artdeco-spacing-px);
  text-transform: uppercase;

  &.success {
    background: color-mix(in srgb, var(--artdeco-rise) 15%, var(--artdeco-bg-card));
    border: 1px solid color-mix(in srgb, var(--artdeco-rise) 35%, transparent);
    color: var(--artdeco-rise);
  }
}

.overview-section {
  padding: var(--artdeco-spacing-3) 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(17.5rem, 1fr));
  gap: 0;
  border: 1px solid var(--artdeco-gold-dim);

  .info-item {
    display: flex;
    flex-direction: column;
    padding: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px)) var(--artdeco-spacing-5);
    border-bottom: 1px solid var(--artdeco-gold-dim);
    background: var(--artdeco-bg-global);

    &:nth-child(even) {
      background: color-mix(in srgb, var(--artdeco-gold-primary) 3%, var(--artdeco-bg-card));
    }

    label {
      margin-bottom: var(--artdeco-spacing-2);
        color: var(--artdeco-fg-muted);
      font-family: var(--artdeco-font-heading, var(--font-display));
      font-size: var(--artdeco-text-compact-xs);
      letter-spacing: var(--artdeco-spacing-px);
      text-transform: uppercase;
    }

    span {
      color: var(--artdeco-fg-primary);
      font-family: var(--artdeco-font-body, var(--font-body));
      font-size: var(--artdeco-text-sm);
      line-height: 1.5;
    }
  }
}

.features-section {
  margin-top: calc(var(--artdeco-spacing-5) + var(--artdeco-spacing-px) * 5);

  .section-title {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-2);
    margin: 0 0 var(--artdeco-spacing-5) 0;
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-heading, var(--font-display));
    font-size: var(--artdeco-text-lg);
    letter-spacing: calc(var(--artdeco-spacing-px) * 2);
    text-transform: uppercase;

    .title-icon {
      font-size: var(--artdeco-text-lg);
    }
  }
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(17.5rem, 1fr));
  gap: var(--artdeco-spacing-5);
}

.feature-card {
  position: relative;
  padding: var(--artdeco-spacing-5);
  background: var(--artdeco-bg-global);
  border: 1px solid var(--artdeco-gold-dim);
  transition:
    border-color var(--artdeco-transition-quick) var(--artdeco-ease-out),
    box-shadow var(--artdeco-transition-quick) var(--artdeco-ease-out),
    transform var(--artdeco-transition-quick) var(--artdeco-ease-out);

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: calc(var(--artdeco-spacing-3) - var(--artdeco-spacing-px));
    height: calc(var(--artdeco-spacing-3) - var(--artdeco-spacing-px));
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
    border-top: none;
    border-left: none;
  }

  &:hover {
    border-color: var(--artdeco-gold-primary);
    box-shadow: var(--artdeco-shadow-lg);
    transform: translateY(calc(var(--artdeco-spacing-px) * -2));
  }

  .feature-title {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-2);
    margin: 0 0 var(--artdeco-spacing-4) 0;
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-heading, var(--font-display));
    font-size: calc(var(--artdeco-text-sm) + var(--artdeco-spacing-px));
    letter-spacing: var(--artdeco-spacing-px);
    text-transform: uppercase;

    .feature-icon {
      font-size: var(--artdeco-text-base);
    }
  }

  .feature-list {
    margin: 0;
    padding-left: var(--artdeco-spacing-5);
    list-style: none;

    li {
      position: relative;
      padding: calc(var(--artdeco-spacing-2) - var(--artdeco-spacing-px)) 0 calc(var(--artdeco-spacing-2) - var(--artdeco-spacing-px)) var(--artdeco-spacing-5);
      color: var(--artdeco-fg-primary);
      font-family: var(--artdeco-font-body, var(--font-body));
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

.info-alert {
  display: flex;
  gap: var(--artdeco-spacing-4);
  margin-top: calc(var(--artdeco-spacing-5) + var(--artdeco-spacing-px) * 5);
  padding: var(--artdeco-spacing-5);
  background: color-mix(in srgb, var(--artdeco-info) 8%, var(--artdeco-bg-card));
  border: 1px solid color-mix(in srgb, var(--artdeco-info) 30%, transparent);

  .alert-icon {
    flex-shrink: 0;
    margin-top: calc(var(--artdeco-spacing-px) * 2);
  }

  .alert-content {
    flex: 1;

    .alert-title {
      margin-bottom: var(--artdeco-spacing-2);
      color: var(--artdeco-gold-primary);
      font-family: var(--artdeco-font-heading, var(--font-display));
      font-size: var(--artdeco-text-sm);
      letter-spacing: var(--artdeco-spacing-px);
      text-transform: uppercase;
    }

    .alert-text {
      color: var(--artdeco-fg-primary);
      font-family: var(--artdeco-font-body, var(--font-body));
      font-size: var(--artdeco-text-sm);
      line-height: 1.8;
    }
  }
}

@media (width <= 48rem) {
  .demo-card {
    padding: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
  }

  .card-header {
    flex-direction: column;
    gap: var(--artdeco-spacing-3);
    align-items: flex-start;
  }

  .info-grid,
  .features-grid {
    grid-template-columns: 1fr;
  }

  .info-alert {
    flex-direction: column;
    gap: var(--artdeco-spacing-3);
  }
}
</style>
