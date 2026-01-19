<template>
  <div class="strategy-card">
    <div class="card-header">
      <h3 class="strategy-name">{{ strategy.name }}</h3>
      <span :class="['status-badge', strategy.status]">
        {{ statusText }}
      </span>
    </div>

    <div class="card-body">
      <p class="description">{{ strategy.description }}</p>

      <div class="meta">
        <span class="type-badge">{{ typeLabel }}</span>
        <span class="date">创建于 {{ strategy.createdAt ? formatDate(strategy.createdAt) : '未知' }}</span>
      </div>

      <!-- 性能指标 -->
      <div v-if="strategy.performance" class="performance">
        <div class="metric">
          <span class="label">总收益</span>
          <span class="value" :class="{ positive: (strategy.performance.totalReturn || 0) > 0, negative: (strategy.performance.totalReturn || 0) < 0 }">
            {{ ((strategy.performance.totalReturn || 0) * 100).toFixed(2) }}%
          </span>
        </div>
        <div class="metric">
          <span class="label">夏普比率</span>
          <span class="value">{{ (strategy.performance.sharpeRatio || 0).toFixed(2) }}</span>
        </div>
        <div class="metric">
          <span class="label">胜率</span>
          <span class="value">{{ ((strategy.performance.winRate || 0) * 100).toFixed(2) }}%</span>
        </div>
      </div>

      <!-- 测试中状态 -->
      <div v-else class="testing-notice">
        <span>⚠️ 策略测试中，暂无性能数据</span>
      </div>
    </div>

    <div class="card-footer">
      <button @click="$emit('edit', strategy)" class="btn btn-edit" title="编辑">
        ✏️ 编辑
      </button>
      <button
        @click="$emit('backtest', strategy)"
        class="btn btn-backtest"
        title="回测"
      >
        📊 回测
      </button>
      <button
        @click="handleDelete"
        class="btn btn-delete"
        title="删除"
      >
        🗑️ 删除
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { StrategyVM as Strategy } from '@/api/types/extensions';

const props = defineProps<{
  strategy: Strategy;
}>();

const emit = defineEmits<{
  edit: [strategy: Strategy];
  delete: [strategy: Strategy];
  backtest: [strategy: Strategy];
}>();

const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(date);
};

const statusTextMap: Record<string, string> = {
  active: '运行中',
  inactive: '未激活',
  testing: '测试中',
};

const typeLabelMap: Record<string, string> = {
  trend_following: '趋势跟踪',
  mean_reversion: '均值回归',
  momentum: '动量策略',
};

const statusText = statusTextMap[props.strategy.status || ''] || '未知';
const typeLabel = typeLabelMap[props.strategy.type || ''] || '自定义';

const handleDelete = () => {
  if (confirm(`确定要删除策略 "${props.strategy.name}" 吗？此操作不可撤销。`)) {
    emit('delete', props.strategy);
  }
};
</script>

<style scoped>
.strategy-card {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 16px;
  background: white;
  transition: all 0.3s ease;
}

.strategy-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.strategy-name {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.status-badge.active {
  background-color: #f0f9ff;
  color: #0284c7;
}

.status-badge.inactive {
  background-color: #f5f5f5;
  color: #737373;
}

.status-badge.testing {
  background-color: #fff7ed;
  color: #ea580c;
}

.description {
  color: #737373;
  margin-bottom: 12px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 12px;
  color: #737373;
}

.type-badge {
  padding: 2px 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  font-size: 12px;
}

.performance {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding: 12px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
  border-radius: 6px;
  margin-bottom: 12px;
}

.metric {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.metric .label {
  font-size: 11px;
  color: #737373;
  margin-bottom: 4px;
  font-weight: 500;
}

.metric .value {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.metric .value.positive {
  color: #dc2626;
}

.metric .value.negative {
  color: #16a34a;
}

.testing-notice {
  padding: 12px;
  background-color: #fff7ed;
  border: 1px dashed #f97316;
  border-radius: 6px;
  text-align: center;
  color: #ea580c;
  font-size: 13px;
  margin-bottom: 12px;
}

.card-footer {
  display: flex;
  gap: 8px;
}

.btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.btn:active {
  transform: translateY(0);
}

.btn-edit {
  background-color: #3b82f6;
  color: white;
}

.btn-edit:hover {
  background-color: #2563eb;
}

.btn-backtest {
  background-color: #10b981;
  color: white;
}

.btn-backtest:hover {
  background-color: #059669;
}

.btn-delete {
  background-color: #ef4444;
  color: white;
}

.btn-delete:hover {
  background-color: #dc2626;
}

@media (max-width: 768px) {
  .strategy-card {
    padding: 12px;
  }

  .performance {
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    padding: 10px;
  }

  .metric .value {
    font-size: 14px;
  }
}
</style>
