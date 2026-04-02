<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click.self="handleClose">
        <div class="modal-container backtest-panel">
          <div class="modal-header">
            <h2>策略回测 - {{ strategy?.name }}</h2>
            <button @click="handleClose" class="btn-close">✕</button>
          </div>

          <div class="modal-body">
            <div v-if="backtestError" class="backtest-error" role="alert">
              {{ backtestError }}
            </div>

            <!-- 回测配置 -->
            <div v-if="!hasStarted" class="backtest-config">
              <h3>回测参数配置</h3>

              <div class="form-row">
                <div class="form-group">
                  <label>开始日期</label>
                  <input
                    v-model="config.startDate"
                    type="date"
                    class="form-input"
                  />
                </div>

                <div class="form-group">
                  <label>结束日期</label>
                  <input
                    v-model="config.endDate"
                    type="date"
                    class="form-input"
                  />
                </div>
              </div>

              <div class="form-group">
                <label>初始资金</label>
                <input
                  v-model.number="config.initialCapital"
                  type="number"
                  step="10000"
                  class="form-input"
                  placeholder="100000"
                />
              </div>

              <div class="form-group">
                <label>回测标的（可选）</label>
                <input
                  v-model="config.symbols"
                  type="text"
                  class="form-input"
                  placeholder="600519,000001,000002"
                />
              </div>

              <button
                @click="handleStartBacktest"
                :disabled="isStarting || !isConfigValid"
                class="btn-start"
              >
                {{ isStarting ? '启动中...' : '🚀 开始回测' }}
              </button>
            </div>

            <!-- 回测进度 -->
            <div v-else-if="isRunning" class="backtest-progress">
              <div class="progress-container">
                <div class="progress-bar">
                  <div
                    class="progress-fill"
                    :style="{ width: `${progress}%` }"
                  ></div>
                </div>
                <div class="progress-text">
                  {{ progress }}% - {{ statusText }}
                </div>
              </div>

              <div class="log-output">
                <div v-for="(log, index) in logs" :key="index" class="log-entry">
                  {{ log }}
                </div>
              </div>
            </div>

            <!-- 回测结果 -->
            <div v-else-if="isCompleted" class="backtest-results">
              <h3>回测结果</h3>

              <div v-if="result" class="result-summary">
                <div class="metric-card">
                  <span class="label">总收益率</span>
                  <span class="value" :class="{ positive: result.totalReturn > 0 }">
                    {{ (result.totalReturn * 100).toFixed(2) }}%
                  </span>
                </div>

                <div class="metric-card">
                  <span class="label">年化收益</span>
                  <span class="value" :class="{ positive: result.annualReturn > 0 }">
                    {{ (result.annualReturn * 100).toFixed(2) }}%
                  </span>
                </div>

                <div class="metric-card">
                  <span class="label">夏普比率</span>
                  <span class="value">{{ result.sharpeRatio.toFixed(2) }}</span>
                </div>

                <div class="metric-card">
                  <span class="label">最大回撤</span>
                  <span class="value negative">
                    {{ (result.maxDrawdown * 100).toFixed(2) }}%
                  </span>
                </div>

                <div class="metric-card">
                  <span class="label">胜率</span>
                  <span class="value">{{ (result.winRate * 100).toFixed(2) }}%</span>
                </div>

                <div class="metric-card">
                  <span class="label">交易次数</span>
                  <span class="value">{{ result.totalTrades }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button @click="handleClose" class="btn-close">
              {{ isCompleted ? '关闭' : '取消' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useBacktest } from '@/composables/useStrategy';
import type { StrategyVM as Strategy } from '@/api/types/extensions';

const props = defineProps<{
  strategy: Strategy;
}>();

const emit = defineEmits<{
  close: [];
}>();

const show = computed(() => !!props.strategy);

const { startBacktest, pollBacktestStatus, error: backtestErrorState } = useBacktest();

// Result type
interface BacktestResult {
  totalReturn: number;
  annualReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  totalTrades: number;
}

// State
const hasStarted = ref(false);
const isRunning = ref(false);
const isCompleted = ref(false);
const isStarting = ref(false);
const backtestError = ref<string | null>(null);
const progress = ref(0);
const statusText = ref('正在初始化...');
const logs = ref<string[]>([]);
const result = ref<BacktestResult | null>(null);

// Configuration
const config = ref({
  startDate: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000)
    .toISOString()
    .split('T')[0],
  endDate: new Date().toISOString().split('T')[0],
  initialCapital: 100000,
  symbols: '',
});

const isConfigValid = computed(() => {
  return (
    config.value.startDate &&
    config.value.endDate &&
    config.value.initialCapital > 0
  );
});

function appendLog(message: string) {
  logs.value = [
    `[${new Date().toLocaleTimeString()}] ${message}`,
    ...logs.value,
  ];
}

function applyStatusText(status: 'queued' | 'running' | 'completed' | 'failed', message: string) {
  statusText.value = message;

  if (status === 'queued') {
    progress.value = 15;
    return;
  }

  if (status === 'running') {
    progress.value = 60;
    return;
  }

  if (status === 'completed') {
    progress.value = 100;
    return;
  }

  progress.value = 0;
}

const handleStartBacktest = async () => {
  isStarting.value = true;
  backtestError.value = null;
  result.value = null;

  try {
    const symbols = config.value.symbols
      ? config.value.symbols.split(',').map((s) => s.trim())
      : undefined;

    const task = await startBacktest(props.strategy.id || '', {
      startDate: config.value.startDate,
      endDate: config.value.endDate,
      initialCapital: config.value.initialCapital,
      symbols,
    });

    if (!task) {
      backtestError.value = backtestErrorState.value || '启动回测失败';
      return;
    }

    hasStarted.value = true;
    isRunning.value = true;
    isCompleted.value = false;
    applyStatusText(task.status, task.message);
    appendLog(task.message);

    const finalTask = await pollBacktestStatus(task.taskId, {
      onUpdate: (nextTask) => {
        applyStatusText(nextTask.status, nextTask.message);
        appendLog(nextTask.message);
      }
    });

    isRunning.value = false;
    isCompleted.value = finalTask.status === 'completed';
    hasStarted.value = finalTask.status === 'completed';
  } catch (error) {
    isRunning.value = false;
    isCompleted.value = false;
    hasStarted.value = false;
    progress.value = 0;
    const message = error instanceof Error ? error.message : '启动回测失败';
    backtestError.value = message;
    statusText.value = message;
    appendLog(message);
  } finally {
    isStarting.value = false;
  }
};

const handleClose = () => {
  emit('close');
};

// Reset state when strategy changes
watch(
  () => props.strategy,
  () => {
    hasStarted.value = false;
    isRunning.value = false;
    isCompleted.value = false;
    backtestError.value = null;
    progress.value = 0;
    logs.value = [];
    result.value = null;
  }
);
</script>

<style scoped>
.backtest-panel {
  max-width: 800px;
}

.modal-body {
  padding: 24px;
}

.backtest-error {
  margin-bottom: 16px;
  padding: 12px 14px;
  border: 1px solid #fecaca;
  border-radius: 8px;
  background: #fef2f2;
  color: #b91c1c;
}

.backtest-config h3,
.backtest-results h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #262626;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgb(59 130 246 / 10%);
}

.btn-start {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-start:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgb(16 185 129 / 30%);
}

.btn-start:disabled {
  opacity: 60%;
  cursor: not-allowed;
}

.backtest-progress {
  text-align: center;
}

.progress-container {
  margin-bottom: 24px;
}

.progress-bar {
  width: 100%;
  height: 24px;
  background-color: #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
  transition: width 0.5s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-text {
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
}

.log-output {
  background-color: #1f2937;
  border-radius: 8px;
  padding: 16px;
  max-height: 200px;
  overflow-y: auto;
  text-align: left;
}

.log-entry {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #10b981;
  line-height: 1.6;
}

.result-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.metric-card {
  background: linear-gradient(135deg, var(--color-bg-primary) 0%, var(--color-bg-secondary) 100%);
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  border: 1px solid var(--color-border-light);
}

.metric-card .label {
  display: block;
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-bottom: 8px;
  font-weight: 500;
}

.metric-card .value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.metric-card .value.positive {
  color: #dc2626;
}

.metric-card .value.negative {
  color: #16a34a;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border-light);
}

.btn-close {
  padding: 10px 20px;
  background-color: #6b7280;
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.btn-close:hover {
  background-color: #4b5563;
}
</style>
