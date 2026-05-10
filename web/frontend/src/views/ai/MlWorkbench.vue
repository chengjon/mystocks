<script setup lang="ts">
import { onMounted } from 'vue'

import { useMlWorkbench } from './composables/useMlWorkbench'

const {
  loading,
  trainingLoading,
  predictionLoading,
  runtimeStatus,
  models,
  selectedModelId,
  trainingForm,
  predictionForm,
  lastTrainingResult,
  lastPredictionResult,
  runtimeMessage,
  readinessLabel,
  readinessClass,
  modelFamilyOptions,
  selectedModelFamilyBlocked,
  refreshRuntime,
  submitTraining,
  submitPrediction,
  selectModel,
} = useMlWorkbench()

onMounted(() => {
  void refreshRuntime()
})
</script>

<template>
  <div class="ai-ml-workbench page-enter">
    <header class="workbench-header">
      <div>
        <p class="eyebrow">AI ML workbench</p>
        <h1>模型训练 / 预测</h1>
        <p class="subtitle">统一查看运行时状态、提交训练请求、选择模型并执行预测推理。</p>
      </div>
      <button class="icon-button" type="button" :disabled="loading" @click="refreshRuntime">
        刷新
      </button>
    </header>

    <section class="status-band" :class="readinessClass">
      <div>
        <span class="status-label">{{ readinessLabel }}</span>
        <strong>{{ runtimeStatus?.model_backend || 'runtime_registry' }}</strong>
      </div>
      <div class="status-meta">
        <span>legacy API: {{ runtimeStatus?.legacy_api_available ? 'available' : 'unknown' }}</span>
        <span>LightGBM: {{ runtimeStatus?.optional_dependencies?.lightgbm?.available ? 'available' : 'unavailable' }}</span>
      </div>
    </section>

    <p class="safety-copy">
      ML predictions are analytical outputs, not a trade instruction or execution fact.
    </p>

    <p v-if="runtimeMessage" class="runtime-message">{{ runtimeMessage }}</p>

    <main class="workbench-grid">
      <section class="panel">
        <div class="panel-heading">
          <h2>训练配置</h2>
          <span>{{ trainingLoading ? '提交中' : '待提交' }}</span>
        </div>
        <label>
          模型族
          <select
            v-model="trainingForm.model_family"
            data-testid="ml-model-family"
          >
            <option
              v-for="option in modelFamilyOptions"
              :key="option.value"
              :value="option.value"
              :disabled="!option.available"
              :data-testid="`ml-model-family-${option.value}`"
            >
              {{ option.label }} · {{ option.status }}
            </option>
          </select>
        </label>
        <p v-if="selectedModelFamilyBlocked" class="runtime-message compact">
          当前模型族后端依赖不可用，请先切换模型族或安装对应运行时依赖。
        </p>
        <label>
          标的
          <input v-model="trainingForm.symbol" type="text" />
        </label>
        <label>
          开始日期
          <input v-model="trainingForm.start_date" type="date" />
        </label>
        <label>
          结束日期
          <input v-model="trainingForm.end_date" type="date" />
        </label>
        <label>
          特征窗口
          <input v-model.number="trainingForm.feature_window" type="number" min="5" max="120" />
        </label>
        <label>
          预测周期
          <input v-model.number="trainingForm.prediction_horizon" type="number" min="1" max="30" />
        </label>
        <button
          data-testid="ml-train-submit"
          class="primary-button"
          type="button"
          :disabled="trainingLoading || selectedModelFamilyBlocked"
          @click="submitTraining"
        >
          提交训练
        </button>
      </section>

      <section class="panel">
        <div class="panel-heading">
          <h2>模型列表</h2>
          <span>{{ models.length }} 个模型</span>
        </div>
        <div v-if="models.length === 0" class="empty-state">暂无运行时模型</div>
        <button
          v-for="model in models"
          v-else
          :key="model.model_id"
          data-testid="ml-model-row"
          class="model-row"
          :class="{ active: selectedModelId === model.model_id }"
          type="button"
          @click="selectModel(model.model_id)"
        >
          <span>{{ model.model_id }}</span>
          <small>{{ model.symbol }} · {{ model.artifact_status }}</small>
        </button>
      </section>

      <section class="panel">
        <div class="panel-heading">
          <h2>预测推理</h2>
          <span>{{ predictionLoading ? '计算中' : '待执行' }}</span>
        </div>
        <label>
          模型 ID
          <input v-model="predictionForm.model_id" type="text" />
        </label>
        <label>
          标的
          <input v-model="predictionForm.symbol" type="text" />
        </label>
        <label>
          预测周期
          <input v-model.number="predictionForm.prediction_horizon" type="number" min="1" max="30" />
        </label>
        <button
          data-testid="ml-predict-submit"
          class="primary-button"
          type="button"
          :disabled="predictionLoading || !predictionForm.model_id"
          @click="submitPrediction"
        >
          执行预测
        </button>
      </section>

      <section class="panel result-panel">
        <div class="panel-heading">
          <h2>结果摘要</h2>
          <span>metrics</span>
        </div>
        <dl>
          <div>
            <dt>训练模型</dt>
            <dd>{{ lastTrainingResult?.model_id || '-' }}</dd>
          </div>
          <div>
            <dt>验证分数</dt>
            <dd>{{ lastTrainingResult?.metrics?.validation_score ?? '-' }}</dd>
          </div>
          <div>
            <dt>预测方向</dt>
            <dd>{{ lastPredictionResult?.prediction?.signal || '-' }}</dd>
          </div>
          <div>
            <dt>置信度</dt>
            <dd>{{ lastPredictionResult?.confidence ?? '-' }}</dd>
          </div>
        </dl>
        <p class="safety-copy compact">
          {{ lastPredictionResult?.safety?.disclaimer || lastTrainingResult?.safety?.disclaimer || 'ML predictions are analytical outputs, not a trade instruction or execution fact.' }}
        </p>
      </section>
    </main>
  </div>
</template>

<style scoped>
.ai-ml-workbench {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
}

.workbench-header,
.status-band,
.panel {
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(15, 23, 42, 0.72);
}

.workbench-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  padding: 20px;
  border-radius: 8px;
}

.eyebrow,
.subtitle,
.status-meta,
.panel-heading span,
small,
.safety-copy,
.runtime-message,
dt {
  color: rgba(226, 232, 240, 0.72);
}

h1,
h2,
p {
  margin: 0;
}

h1 {
  font-size: 28px;
  line-height: 1.2;
}

h2 {
  font-size: 16px;
}

.status-band {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 8px;
}

.status-band.is-ready {
  border-color: rgba(34, 197, 94, 0.42);
}

.status-label {
  margin-right: 10px;
  color: #86efac;
}

.status-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.workbench-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
}

.panel-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: rgba(226, 232, 240, 0.84);
  font-size: 13px;
}

input,
select {
  min-height: 36px;
  border: 1px solid rgba(148, 163, 184, 0.26);
  border-radius: 6px;
  padding: 0 10px;
  background: rgba(15, 23, 42, 0.88);
  color: #f8fafc;
}

select:disabled,
option:disabled {
  color: rgba(226, 232, 240, 0.42);
}

button {
  min-height: 36px;
  border-radius: 6px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  color: #f8fafc;
  background: rgba(30, 41, 59, 0.9);
  cursor: pointer;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.58;
}

.primary-button {
  background: #2563eb;
  border-color: #3b82f6;
}

.icon-button {
  min-width: 72px;
}

.model-row {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  padding: 10px;
  text-align: left;
}

.model-row.active {
  border-color: #60a5fa;
  background: rgba(37, 99, 235, 0.24);
}

.empty-state {
  min-height: 80px;
  display: grid;
  place-items: center;
  color: rgba(226, 232, 240, 0.62);
  border: 1px dashed rgba(148, 163, 184, 0.24);
  border-radius: 8px;
}

dl {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin: 0;
}

dd {
  margin: 4px 0 0;
  color: #f8fafc;
}

.compact {
  font-size: 12px;
}

@media (max-width: 900px) {
  .workbench-header,
  .status-band {
    flex-direction: column;
  }

  .workbench-grid {
    grid-template-columns: 1fr;
  }
}
</style>
