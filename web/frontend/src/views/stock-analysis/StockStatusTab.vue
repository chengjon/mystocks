<template>
  <div v-show="activeTab === 'status'" class="status-tab-container">
    <ArtDecoHeader title="INTEGRATION STATUS" show-status status-text="SYSTEM NOMINAL">
      <template #actions>
        <ArtDecoStatusIndicator status="online" label="CORE" animated />
        <ArtDecoStatusIndicator status="online" label="DB" animated />
      </template>
    </ArtDecoHeader>

    <div class="content-section content-section-padded">
      <h3 class="section-title">📦 INTEGRATED MODULES</h3>
      <ArtDecoCard variant="bordered" class="status-card-spaced">
        <div class="status-list">
          <div class="status-item">
            <span class="diamond-marker"></span>
            <span class="label">TongDaxin Parser</span>
            <el-tag type="success" effect="dark" class="artdeco-tag">ACTIVE</el-tag>
          </div>
          <div class="status-item">
            <span class="diamond-marker"></span>
            <span class="label">Feature Engineering</span>
            <el-tag type="success" effect="dark" class="artdeco-tag">ACTIVE</el-tag>
          </div>
          <div class="status-item">
            <span class="diamond-marker"></span>
            <span class="label">Strategy Documentation</span>
            <el-tag type="success" effect="dark" class="artdeco-tag">COMPLETE</el-tag>
          </div>
          <div class="status-item muted">
            <span class="diamond-marker gray"></span>
            <span class="label">Backtest Integration</span>
            <el-tag type="info" effect="plain" class="artdeco-tag">PENDING</el-tag>
          </div>
          <div class="status-item muted">
            <span class="diamond-marker gray"></span>
            <span class="label">Real-time Monitor</span>
            <el-tag type="info" effect="plain" class="artdeco-tag">PLANNED</el-tag>
          </div>
        </div>
      </ArtDecoCard>

      <h3 class="section-title section-title-spaced">🎯 ROADMAP</h3>
      <el-timeline class="artdeco-timeline timeline-spaced">
        <el-timeline-item timestamp="PHASE I" placement="top">
          <ArtDecoCard variant="bordered" title="STRATEGY MANAGEMENT">
            <p class="timeline-desc">Manage and execute screening strategies within the ArtDeco interface.</p>
          </ArtDecoCard>
        </el-timeline-item>
        <el-timeline-item timestamp="PHASE II" placement="top">
          <ArtDecoCard variant="bordered" title="BACKTEST SYSTEM">
            <p class="timeline-desc">Full RQAlpha engine integration for online strategy verification.</p>
          </ArtDecoCard>
        </el-timeline-item>
        <el-timeline-item timestamp="PHASE III" placement="top">
          <ArtDecoCard variant="bordered" title="REAL-TIME MONITOR">
            <p class="timeline-desc">Intra-day monitoring with geometric push notifications.</p>
          </ArtDecoCard>
        </el-timeline-item>
      </el-timeline>

      <ArtDecoCard variant="elevated" class="data-source-info data-source-info-spaced">
        <template #header>
          <div class="info-header">
            <span class="diamond-marker"></span>
            <h3>💡 DATA SOURCE SPECIFICATION</h3>
          </div>
        </template>
        <div class="info-content">
          <p>Stock-Analysis utilizes local TongDaxin data for structural advantages:</p>
          <ul class="luxury-list">
            <li><span>COMPREHENSIVENESS</span>: Full A-share history covered.</li>
            <li><span>PERFORMANCE</span>: Local binary parsing for zero latency.</li>
            <li><span>RELIABILITY</span>: Professional-grade data quality.</li>
            <li><span>EFFICIENCY</span>: Zero-cost structural data access.</li>
          </ul>
          <div class="path-box">
            <span>CONFIG PATH: </span>
            <code>D:/tdx/vipdoc</code>
          </div>
        </div>
      </ArtDecoCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import ArtDecoHeader from '@/components/artdeco/core/ArtDecoHeader.vue'
import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
import ArtDecoStatusIndicator from '@/components/artdeco/core/ArtDecoStatusIndicator.vue'

defineProps<{
  activeTab: string
}>()
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.status-tab-container {
  background: var(--artdeco-bg-base);
  min-height: 100%;
}

.section-title {
  font-family: var(--font-display);
  color: var(--artdeco-gold-primary);
  letter-spacing: var(--artdeco-tracking-wider);
  text-transform: uppercase;
}

.content-section-padded {
  padding: var(--artdeco-spacing-6);
}

.status-card-spaced {
  margin-top: var(--artdeco-spacing-4);
}

.section-title-spaced {
  margin-top: var(--artdeco-spacing-8);
}

.timeline-spaced {
  margin-top: var(--artdeco-spacing-6);
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-3);
}

.status-item {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-3);
  padding: var(--artdeco-spacing-2) 0;
  border-bottom: 1px solid var(--artdeco-gold-opacity-10);

  &.muted { opacity: 0.6; }

  .label {
    flex: 1;
    font-family: var(--font-body);
    color: var(--artdeco-fg-primary);
    text-transform: uppercase;
    font-size: var(--artdeco-text-sm);
  }
}

.diamond-marker {
  width: calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) * 2);
  height: calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) * 2);
  background: var(--artdeco-gold-primary);
  transform: rotate(45deg);
  border: 1px solid var(--artdeco-gold-light);
  box-shadow: var(--artdeco-glow-subtle);

  &.gray {
    background: var(--artdeco-fg-muted);
    border-color: color-mix(in srgb, var(--artdeco-fg-muted) 55%, var(--artdeco-bg-global));
    box-shadow: none;
  }
}

.timeline-desc {
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

.data-source-info {
  border: 1px solid var(--artdeco-border-default) !important;
}

.data-source-info-spaced {
  margin-top: var(--artdeco-spacing-8);
}

.info-header {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-3);

  h3 {
    margin: 0;
    font-size: var(--artdeco-text-lg);
  }
}

.luxury-list {
  list-style: none;
  padding: 0;
  margin: var(--artdeco-spacing-4) 0;
  li {
    margin-bottom: var(--artdeco-spacing-2);
    color: var(--artdeco-fg-primary);

    span {
      color: var(--artdeco-gold-primary);
      font-weight: bold;
    }
  }
}

.path-box {
  background: color-mix(in srgb, var(--artdeco-bg-global) 30%, transparent);
  padding: var(--artdeco-spacing-3);
  border-left: calc(var(--artdeco-spacing-px) * 3) solid var(--artdeco-gold-primary);
  font-family: var(--font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-gold-light);
}

.artdeco-timeline :deep(.el-timeline-item__node) {
  background-color: var(--artdeco-gold-primary);
  border: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-bg-base);
}

.artdeco-timeline :deep(.el-timeline-item__timestamp) {
  color: var(--artdeco-gold-primary);
  font-family: var(--font-display);
  font-weight: bold;
}
</style>
