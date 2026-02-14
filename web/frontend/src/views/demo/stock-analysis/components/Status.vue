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

.content-section {
  padding: 10px 0;
  line-height: 1.8;
}

.section {
  margin-bottom: 30px;

  &:last-child {
    margin-bottom: 0;
  }

  h3 {
    margin: 0 0 15px 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--primary);
    border-left: 3px solid var(--primary);
    padding-left: 12px;
  }
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 0;
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border-light);

  &:last-child {
    border-bottom: none;
  }
}

.info-label {
  font-size: 14px;
  color: var(--text-primary);
}

.timeline {
  position: relative;
  padding-left: 30px;
  margin-top: 20px;

  &::before {
    content: '';
    position: absolute;
    left: 6px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: var(--border-light);
  }
}

.timeline-item {
  position: relative;
  padding-bottom: 24px;

  &:last-child {
    padding-bottom: 0;
  }
}

.timeline-marker {
  position: absolute;
  left: -30px;
  top: 0;
  width: 14px;
  height: 14px;
  background: var(--primary);
  border-radius: 50%;
  border: 3px solid var(--bg-primary);
}

.timeline-content {
  padding-left: 10px;
}

.timeline-header {
  margin-bottom: 8px;
}

.timeline-phase {
  display: inline-block;
  padding: 4px 12px;
  background: var(--primary);
  color: white;
  font-size: 12px;
  font-weight: 600;
  border-radius: var(--radius-sm);
}

.timeline-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 16px;

  h4 {
    margin: 0 0 8px 0;
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
  }

  p {
    margin: 0;
    font-size: 13px;
    color: var(--text-secondary);
  }
}

.alert-content {
  strong {
    display: block;
    margin-bottom: 10px;
    color: var(--text-primary);
  }

  p {
    margin: 0 0 10px 0;
    color: var(--text-secondary);
  }
}

.advantage-list {
  margin: 0 0 10px 0;
  padding-left: 20px;
  color: var(--text-secondary);

  li {
    margin: 6px 0;
  }
}

.path-hint {
  margin: 10px 0 0 0;
  font-size: 13px;
  color: var(--text-muted);

  code {
    display: inline-block;
    padding: 4px 8px;
    background: var(--bg-dark);
    border-radius: var(--radius-sm);
    font-family: 'SF Mono', Monaco, Consolas, monospace;
    font-size: 12px;
    margin-left: 8px;
  }
}
</style>
