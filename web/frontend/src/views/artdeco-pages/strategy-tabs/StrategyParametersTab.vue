<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi';
import { strategyApi } from '@/api/index';
import type { StrategyConfig } from '@/api/types/common';

const { loading, lastRequestId, exec } = useArtDecoApi();
const strategies = ref<StrategyConfig[]>([]);

const fetchStrategies = async () => {
  const data = await exec(() => strategyApi.getStrategies({}), {
    errorMsg: '获取策略参数失败'
  });
  if (data) {
    strategies.value = data;
  }
};

onMounted(() => {
  fetchStrategies();
});
</script>

<template>
  <div class="strategy-parameters-tab page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">Strategy Parameters</h2>
      <div class="trace-id" v-if="lastRequestId">REQ_ID: {{ lastRequestId }}</div>
    </div>

    <div class="strategy-grid" v-loading="loading">
      <div v-for="strategy in strategies" :key="strategy.strategy_id || 0" class="artdeco-card strategy-card">
        <div class="card-decoration"></div>
        <div class="card-content">
          <div class="strategy-info">
            <h3 class="strategy-name">{{ strategy.strategy_name }}</h3>
            <span :class="['status-badge', strategy.status]">
              {{ strategy.status?.toUpperCase() }}
            </span>
          </div>
          
          <p class="description">{{ strategy.description }}</p>

          <div class="params-list">
            <div v-for="param in strategy.parameters" :key="param.name" class="param-item">
              <span class="param-label">{{ param.name }}</span>
              <span class="param-value">{{ param.value }}</span>
            </div>
          </div>

          <div class="card-footer">
            <button class="artdeco-button gold-outline">Edit Parameters</button>
            <button class="artdeco-button gold-solid" v-if="strategy.status !== 'active'">Activate</button>
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-if="!loading && strategies.length === 0" class="empty-state artdeco-card">
        <p>No strategies found. Create one in Strategy Management.</p>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.strategy-parameters-tab {
  padding: var(--artdeco-spacing-6);
}

.artdeco-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-8);
  border-bottom: 2px solid var(--artdeco-gold-primary);
  padding-bottom: var(--artdeco-spacing-2);

  .section-title {
    margin: 0;
    font-size: var(--artdeco-text-2xl);
    color: var(--artdeco-gold-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
  }

  .trace-id {
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-xs);
    color: var(--artdeco-fg-muted);
    letter-spacing: var(--artdeco-tracking-wide);
  }
}

.strategy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: var(--artdeco-spacing-6);
}

.strategy-card {
  position: relative;
  background: var(--artdeco-bg-card);
  transition: all 0.3s ease;
  overflow: hidden;
  border: 1px solid var(--artdeco-border-default);

  &:hover {
    @include artdeco-hover-lift-glow;
  }

  .card-decoration {
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: var(--artdeco-gold-primary);
  }

  .card-content {
    padding: var(--artdeco-spacing-6);
  }
}

.strategy-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--artdeco-spacing-4);

  .strategy-name {
    margin: 0;
    font-family: var(--artdeco-font-display);
    font-size: var(--artdeco-text-xl);
    color: var(--artdeco-fg-primary);
  }
}

.status-badge {
  padding: 2px 8px;
  font-size: var(--artdeco-text-xs);
  font-family: var(--artdeco-font-mono);
  border: 1px solid currentColor;
  
  &.active { color: var(--artdeco-rise); }
  &.paused { color: var(--artdeco-warning); }
  &.draft { color: var(--artdeco-fg-muted); }
}

.description {
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  margin-bottom: var(--artdeco-spacing-6);
  height: 3em;
  overflow: hidden;
}

.params-list {
  background: var(--artdeco-bg-elevated);
  padding: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-6);

  @include artdeco-corner-brackets;

  .param-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--artdeco-spacing-2);
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-sm);

    &:last-child { margin-bottom: 0; }

    .param-label { color: var(--artdeco-fg-muted); }
    .param-value { color: var(--artdeco-gold-primary); }
  }
}

.card-footer {
  display: flex;
  gap: var(--artdeco-spacing-4);

  .artdeco-button {
    flex: 1;
    padding: 8px;
    cursor: pointer;
    font-family: var(--artdeco-font-display);
    text-transform: uppercase;
    transition: all 0.3s ease;
    border: 1px solid var(--artdeco-gold-primary);

    &.gold-outline {
      background: transparent;
      color: var(--artdeco-gold-primary);
      &:hover { background: var(--artdeco-gold-opacity-10); }
    }

    &.gold-solid {
      background: var(--artdeco-gold-primary);
      color: var(--artdeco-bg-global);
      &:hover { background: var(--artdeco-gold-light); }
    }
  }
}
</style>
