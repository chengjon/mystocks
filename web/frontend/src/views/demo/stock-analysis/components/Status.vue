<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">✅ 集成状态</span>
    </div>

    <div class="content-section">
      <div class="section">
        <h3>📦 已集成功能</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">通达信数据解析</span>
            <span class="badge badge-success">✅ 已集成到 tdx_parser_service</span>
          </div>
          <div class="info-item">
            <span class="info-label">技术指标计算</span>
            <span class="badge badge-success">✅ 已集成到 feature_engineering</span>
          </div>
          <div class="info-item">
            <span class="info-label">筛选策略文档</span>
            <span class="badge badge-success">✅ 已整理</span>
          </div>
          <div class="info-item">
            <span class="info-label">回测框架</span>
            <span class="badge badge-info">⏳ 待集成</span>
          </div>
          <div class="info-item">
            <span class="info-label">实时监控</span>
            <span class="badge badge-info">⏳ 计划中</span>
          </div>
          <div class="info-item">
            <span class="info-label">Web UI</span>
            <span class="badge badge-info">⏳ 计划中</span>
          </div>
        </div>
      </div>

      <div class="section">
        <h3>🎯 后续集成计划</h3>
        <div class="timeline">
          <div v-for="(item, index) in timelineItems" :key="index" class="timeline-item">
            <div class="timeline-marker"></div>
            <div class="timeline-content">
              <div class="timeline-header">
                <span class="timeline-phase">{{ item.phase }}</span>
              </div>
              <div class="timeline-card">
                <h4>{{ item.title }}</h4>
                <p>{{ item.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="section">
        <div class="alert-card">
          <div class="alert-content">
            <strong>💡 数据源说明</strong>
            <p>Stock-Analysis 使用通达信本地数据,优势在于:</p>
            <ul class="advantage-list">
              <li>数据完整: 覆盖所有A股从上市到最新的历史数据</li>
              <li>访问快速: 本地文件读取,无需网络请求</li>
              <li>数据可靠: 通达信是专业的行情软件,数据质量有保障</li>
              <li>成本低廉: 无需购买数据接口,免费使用</li>
            </ul>
            <p class="path-hint">
              需要配置通达信数据目录路径,通常为:
              <code>D:/tdx/vipdoc</code>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const timelineItems = [
  { phase: 'Phase 1', title: '策略库管理', description: '在 Web 界面中管理和执行各种筛选策略' },
  { phase: 'Phase 2', title: '回测系统集成', description: '集成 RQAlpha 回测引擎,在线运行回测' },
  { phase: 'Phase 3', title: '实时监控', description: '实现盘中实时监控和推送通知功能' },
  { phase: 'Phase 4', title: '策略优化', description: '支持策略参数优化和性能对比分析' }
]
</script>

<style scoped lang="scss">
@use '../../../../styles/artdeco-tokens.scss' as *;

.content-section {
  padding: var(--artdeco-spacing-3) 0;
  line-height: 1.8;
}

.section {
  margin-bottom: calc(var(--artdeco-spacing-5) + var(--artdeco-spacing-2) + (var(--artdeco-spacing-px) * 2));

  &:last-child {
    margin-bottom: 0;
  }

  h3 {
    margin: 0 0 calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px)) 0;
    padding-left: var(--artdeco-spacing-3);
    border-left: calc(var(--artdeco-spacing-px) * 3) solid var(--artdeco-gold-primary);
    color: var(--artdeco-gold-primary);
    font-size: calc(var(--artdeco-text-base) + (var(--artdeco-spacing-px) * 2));
    font-weight: var(--artdeco-font-semibold);
    letter-spacing: var(--artdeco-tracking-wide);
  }
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow: hidden;
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: calc(var(--artdeco-spacing-4) - (var(--artdeco-spacing-px) * 2)) var(--artdeco-spacing-5);
  border-bottom: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 12%, transparent);

  &:last-child {
    border-bottom: none;
  }
}

.info-label {
  color: var(--artdeco-fg-primary);
  font-size: var(--artdeco-text-sm);
}

.timeline {
  position: relative;
  margin-top: var(--artdeco-spacing-5);
  padding-left: calc(var(--artdeco-spacing-5) + var(--artdeco-spacing-2) + (var(--artdeco-spacing-px) * 2));

  &::before {
    content: '';
    position: absolute;
    top: 0;
    bottom: 0;
    left: calc(var(--artdeco-spacing-2) - (var(--artdeco-spacing-px) * 2));
    width: calc(var(--artdeco-spacing-px) * 2);
    background: color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  }
}

.timeline-item {
  position: relative;
  padding-bottom: var(--artdeco-spacing-6);

  &:last-child {
    padding-bottom: 0;
  }
}

.timeline-marker {
  position: absolute;
  top: 0;
  left: calc((var(--artdeco-spacing-5) + var(--artdeco-spacing-2) + (var(--artdeco-spacing-px) * 2)) * -1);
  width: calc(var(--artdeco-spacing-3) + (var(--artdeco-spacing-px) * 2));
  height: calc(var(--artdeco-spacing-3) + (var(--artdeco-spacing-px) * 2));
  background: var(--artdeco-gold-primary);
  border: calc(var(--artdeco-spacing-px) * 3) solid var(--artdeco-bg-global);
  border-radius: var(--artdeco-radius-full);
}

.timeline-content {
  padding-left: calc(var(--artdeco-spacing-2) + (var(--artdeco-spacing-px) * 2));
}

.timeline-header {
  margin-bottom: var(--artdeco-spacing-2);
}

.timeline-phase {
  display: inline-block;
  padding: var(--artdeco-spacing-1) var(--artdeco-spacing-3);
  background: var(--artdeco-gold-primary);
  color: var(--artdeco-bg-global);
  font-size: var(--artdeco-text-xs);
  font-weight: var(--artdeco-font-semibold);
  border-radius: var(--artdeco-radius-none);
}

.timeline-card {
  padding: var(--artdeco-spacing-4);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);

  h4 {
    margin: 0 0 var(--artdeco-spacing-2) 0;
    color: var(--artdeco-fg-primary);
    font-size: calc(var(--artdeco-text-sm) + var(--artdeco-spacing-px));
    font-weight: var(--artdeco-font-semibold);
  }

  p {
    margin: 0;
    color: var(--artdeco-fg-muted);
    font-size: calc(var(--artdeco-text-sm) - var(--artdeco-spacing-px));
  }
}

.alert-card {
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
}

.alert-content {
  padding: var(--artdeco-spacing-4);

  strong {
    display: block;
    margin-bottom: calc(var(--artdeco-spacing-3) - (var(--artdeco-spacing-px) * 2));
    color: var(--artdeco-fg-primary);
  }

  p {
    margin: 0 0 calc(var(--artdeco-spacing-3) - (var(--artdeco-spacing-px) * 2)) 0;
    color: var(--artdeco-fg-muted);
  }
}

.advantage-list {
  margin: 0 0 calc(var(--artdeco-spacing-3) - (var(--artdeco-spacing-px) * 2)) 0;
  padding-left: var(--artdeco-spacing-5);
  color: var(--artdeco-fg-muted);

  li {
    margin: calc(var(--artdeco-spacing-2) - (var(--artdeco-spacing-px) * 2)) 0;
  }
}

.path-hint {
  margin: calc(var(--artdeco-spacing-3) - (var(--artdeco-spacing-px) * 2)) 0 0 0;
  color: var(--artdeco-fg-muted);
  font-size: calc(var(--artdeco-text-sm) - var(--artdeco-spacing-px));

  code {
    display: inline-block;
    margin-left: var(--artdeco-spacing-2);
    padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
    background: var(--artdeco-bg-elevated);
    border-radius: var(--artdeco-radius-none);
    font-family: var(--font-mono);
    font-size: var(--artdeco-text-xs);
  }
}
</style>
