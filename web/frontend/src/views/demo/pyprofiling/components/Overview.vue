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
        <svg class="alert-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
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

.overview-section {
  padding: 10px 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 0;
  border: 1px solid var(--gold-dim);

  .info-item {
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
      line-height: 1.5;
    }
  }
}

.features-section {
  margin-top: 25px;

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
    color: var(--gold-primary);
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

.info-alert {
  display: flex;
  gap: 16px;
  margin-top: 25px;
  padding: 20px;
  background: rgb(64 158 255 / 8%);
  border: 1px solid var(--gold-dim);
  position: relative;

  .alert-icon {
    flex-shrink: 0;
    margin-top: 2px;
  }

  .alert-content {
    flex: 1;

    .alert-title {
      font-family: var(--font-display);
      font-size: 14px;
      color: var(--gold-primary);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 8px;
    }

    .alert-text {
      font-family: var(--font-body);
      font-size: 14px;
      color: var(--text-primary);
      line-height: 1.8;
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

  .info-grid {
    grid-template-columns: 1fr;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .info-alert {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
