<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi';
import { useStrategyCrossTabContext } from '@/composables/strategy/useStrategyCrossTabContext';
import { strategyApi } from '@/api';
import type { StrategyConfig } from '@/api/types/common';
import { extractStrategyIdFromQuery } from './strategyCrossTabNavigation';
import {
  extractStrategyConfigs,
  normalizeProcessTimeMs
} from './strategyParametersData';

type ParametersDataSource = 'real';

const { loading, error, lastRequestId, lastProcessTime, exec } = useArtDecoApi();
const strategies = ref<StrategyConfig[]>([]);
const dataSource = ref<ParametersDataSource>('real');
const fallbackReason = ref('');
const route = useRoute();
const { getSnapshot, setActiveStrategy } = useStrategyCrossTabContext();

const selectedStrategyId = computed(() => extractStrategyIdFromQuery(route.query as Record<string, unknown>));
const selectedStrategySnapshot = computed(() => {
  if (!selectedStrategyId.value) {
    return null;
  }
  return getSnapshot(selectedStrategyId.value);
});

const traceRequestId = computed(() => {
  const requestId = lastRequestId.value.trim();
  return requestId.length > 0 ? requestId : 'N/A';
});
const traceProcessTimeMs = computed(() => normalizeProcessTimeMs(lastProcessTime.value));

const displayedStrategies = computed(() => {
  if (!selectedStrategyId.value) {
    return strategies.value;
  }

  return strategies.value.filter((strategy) => String(strategy.strategy_id ?? '') === selectedStrategyId.value);
});

const selectedStrategyMissing = computed(() => {
  return Boolean(selectedStrategyId.value) && displayedStrategies.value.length === 0;
});

const hydratedStrategies = computed(() => {
  return displayedStrategies.value.map((strategy) => {
    const strategyId = getStrategyId(strategy);
    const snapshot = getSnapshot(strategyId);
    if (!snapshot) {
      return strategy;
    }

    return {
      ...strategy,
      status: mapSnapshotStatus(snapshot.status, strategy.status),
      parameters: toStrategyParameters(snapshot.parameters, strategy.parameters)
    };
  });
});

const headerError = computed(() => {
  return error.value || fallbackReason.value;
});

function getStrategyId(strategy: StrategyConfig): string {
  return String(strategy.strategy_id ?? '');
}

function mapSnapshotStatus(snapshotStatus: string, fallback?: StrategyConfig['status']): StrategyConfig['status'] {
  if (snapshotStatus === 'running') return 'active';
  if (snapshotStatus === 'paused') return 'paused';
  if (snapshotStatus === 'stopped') return 'draft';
  if (snapshotStatus === 'error') return 'paused';
  return fallback;
}

function toStrategyParameters(
  snapshotParameters: Record<string, unknown>,
  fallback?: StrategyConfig['parameters']
): StrategyConfig['parameters'] {
  const entries = Object.entries(snapshotParameters);
  if (!entries.length) {
    return fallback;
  }

  return entries.map(([name, value]) => ({
    name,
    value,
    data_type: typeof value
  }));
}

function getOptimizationScore(strategy: StrategyConfig): number | null {
  const strategyId = getStrategyId(strategy);
  if (!strategyId) {
    return null;
  }

  const snapshot = getSnapshot(strategyId);
  return snapshot?.optimization?.score ?? null;
}

const fetchStrategies = async () => {
  const payload = await exec(() => strategyApi.getStrategies({}), {
    silent: true,
    errorMsg: '获取策略参数失败'
  });

  if (!payload) {
    strategies.value = [];
    dataSource.value = 'real';
    fallbackReason.value = error.value || '获取策略参数失败';
    return;
  }

  const extracted = extractStrategyConfigs(payload);
  if (extracted === null) {
    strategies.value = [];
    dataSource.value = 'real';
    fallbackReason.value = '策略参数数据格式异常';
    return;
  }

  strategies.value = extracted;
  dataSource.value = 'real';
  fallbackReason.value = '';
};

onMounted(() => {
  void fetchStrategies();
});

watch(selectedStrategyId, (value) => {
  setActiveStrategy(value);
}, { immediate: true });
</script>

<template>
  <div class="strategy-parameters-tab page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">Strategy Parameters</h2>
      <div class="header-meta">
        <div class="trace-id">REQ_ID: {{ traceRequestId }}</div>
        <div class="trace-id">PROCESS: {{ traceProcessTimeMs }} ms</div>
        <div :class="['source-badge', dataSource]">SOURCE: {{ dataSource.toUpperCase() }}</div>
        <div class="strategy-context" v-if="selectedStrategyId">策略ID: {{ selectedStrategyId }}</div>
        <div class="strategy-context" v-if="selectedStrategySnapshot?.optimization">
          OPT_SCORE: {{ selectedStrategySnapshot.optimization.score }}
        </div>
      </div>
    </div>

    <p v-if="headerError" class="error-tip">{{ headerError }}</p>

    <div class="strategy-grid" v-loading="loading">
      <div
        v-for="strategy in hydratedStrategies"
        :key="getStrategyId(strategy)"
        class="artdeco-card strategy-card"
        :class="{ selected: getStrategyId(strategy) === selectedStrategyId }"
      >
        <div class="card-decoration"></div>
        <div class="card-content">
          <div class="strategy-info">
            <h3 class="strategy-name">{{ strategy.strategy_name }}</h3>
            <span :class="['status-badge', strategy.status]">
              {{ strategy.status?.toUpperCase() }}
            </span>
            <span v-if="getOptimizationScore(strategy) !== null" class="optimization-badge">
              OPT {{ getOptimizationScore(strategy) }}
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

      <div v-if="!loading && selectedStrategyMissing" class="empty-state artdeco-card">
        <p>未找到策略 {{ selectedStrategyId }} 的参数配置，请返回策略管理页重试。</p>
      </div>
      <div v-else-if="!loading && strategies.length === 0" class="empty-state artdeco-card">
        <p>REAL 数据为空，请先在 Strategy Management 中创建策略。</p>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import './styles/StrategyParametersTab';
</style>
