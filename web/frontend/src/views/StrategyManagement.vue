<template>
  <div class="strategy-list">
    <!-- 头部 -->
    <div class="header">
      <div>
        <h1>策略管理</h1>
        <p class="subtitle">管理和回测您的量化交易策略</p>
      </div>
      <button @click="showCreateDialog = true" class="btn-primary">
        ➕ 创建策略
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && strategies.length === 0" class="loading-state">
      <div class="spinner"></div>
      <p>加载策略中...</p>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>加载失败</h3>
      <p>{{ error }}</p>
      <button @click="fetchStrategies" class="btn-retry">重试</button>
    </div>

    <!-- 空状态 -->
    <div v-else-if="strategies.length === 0" class="empty-state">
      <div class="empty-icon">📊</div>
      <h3>暂无策略</h3>
      <p>您还没有创建任何量化交易策略</p>
      <button @click="showCreateDialog = true" class="btn-primary">
        创建第一个策略
      </button>
    </div>

    <!-- 策略列表 -->
    <div v-else class="strategy-grid">
      <StrategyCard
        v-for="strategy in strategies"
        :key="strategy.id"
        :strategy="strategy"
        @edit="handleEdit"
        @delete="handleDelete"
        @backtest="handleBacktest"
      />
    </div>

    <!-- 创建/编辑对话框 -->
    <StrategyDialog
      v-if="showCreateDialog || editingStrategy"
      :strategy="editingStrategy"
      @save="handleSave"
      @cancel="handleCancel"
    />

    <!-- 回测面板 -->
    <BacktestPanel
      v-if="backtestingStrategy"
      :strategy="backtestingStrategy"
      @close="backtestingStrategy = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useStrategy } from '@/composables/useStrategy';
import StrategyCard from '@/components/StrategyCard.vue';
import StrategyDialog from '@/components/StrategyDialog.vue';
import BacktestPanel from '@/components/BacktestPanel.vue';
import type { Strategy } from '@/api/types/strategy';
import type { CreateStrategyRequest, UpdateStrategyRequest } from '@/api/types/strategy';

// Composables
const { strategies, loading, error, fetchStrategies, createStrategy, updateStrategy, deleteStrategy } = useStrategy();

// 状态
const showCreateDialog = ref(false);
const editingStrategy = ref<Strategy | null>(null);
const backtestingStrategy = ref<Strategy | null>(null);

// 事件处理
const handleEdit = (strategy: Strategy) => {
  editingStrategy.value = strategy;
};

const handleDelete = async (strategy: Strategy) => {
  const success = await deleteStrategy(strategy.id);
  if (success) {
    console.log(`[StrategyList] 策略 "${strategy.name}" 删除成功`);
    // 可选：显示成功提示
  }
};

const handleBacktest = (strategy: Strategy) => {
  backtestingStrategy.value = strategy;
};

const handleSave = async (data: CreateStrategyRequest | UpdateStrategyRequest) => {
  if (editingStrategy.value) {
    // 更新现有策略
    const success = await updateStrategy(editingStrategy.value.id, data);
    if (success) {
      console.log(`[StrategyList] 策略 "${editingStrategy.value.name}" 更新成功`);
      editingStrategy.value = null;
    }
  } else {
    // 创建新策略
    const success = await createStrategy(data as CreateStrategyRequest);
    if (success) {
      console.log('[StrategyList] 新策略创建成功');
      showCreateDialog.value = false;
    }
  }
};

const handleCancel = () => {
  editingStrategy.value = null;
  showCreateDialog.value = false;
};
</script>

<style scoped>
.strategy-list {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  flex-wrap: wrap;
  gap: 16px;
}

.header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #262626;
}

.subtitle {
  margin: 4px 0 0 0;
  font-size: 14px;
  color: #737373;
}

.btn-primary {
  padding: 12px 24px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 16px;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-icon,
.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-state h3,
.empty-state h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #262626;
}

.error-state p,
.empty-state p {
  margin: 0 0 24px 0;
  color: #737373;
}

.btn-retry {
  padding: 10px 20px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.strategy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

@media (max-width: 768px) {
  .strategy-list {
    padding: 16px;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header h1 {
    font-size: 24px;
  }

  .strategy-grid {
    grid-template-columns: 1fr;
  }
}
</style>
