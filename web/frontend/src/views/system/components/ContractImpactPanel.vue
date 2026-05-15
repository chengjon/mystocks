<template>
  <section class="contract-impact-panel" aria-labelledby="contract-impact-title">
    <div class="panel-header">
      <div>
        <p class="panel-kicker">contract governance</p>
        <h3 id="contract-impact-title">契约影响分析</h3>
        <p class="panel-copy">
          对比两个契约版本，识别 endpoint、schema、client 域影响，并给出迁移工作量估算。
        </p>
      </div>
      <div class="panel-meta">
        <span>API: /api/contracts/impact</span>
        <span v-if="requestId">REQ_ID: {{ requestId }}</span>
      </div>
    </div>

    <form class="impact-form" @submit.prevent="runImpactAnalysis">
      <label>
        源版本 ID
        <input
          v-model.number="fromVersionId"
          data-test="from-version-input"
          min="1"
          type="number"
        >
      </label>
      <label>
        目标版本 ID
        <input
          v-model.number="toVersionId"
          data-test="to-version-input"
          min="1"
          type="number"
        >
      </label>
      <button
        data-test="analyze-impact-button"
        type="submit"
        :disabled="loading || !canAnalyze"
      >
        {{ loading ? '分析中' : '运行影响分析' }}
      </button>
    </form>

    <p v-if="errorMessage" class="impact-error" role="alert">{{ errorMessage }}</p>

    <div v-if="assessment" class="impact-results" aria-live="polite">
      <div class="risk-card" :class="`risk-${assessment.analysis.risk_level}`">
        <span>综合风险</span>
        <strong>{{ assessment.analysis.risk_level }}</strong>
        <small>{{ assessment.analysis.from_version }} → {{ assessment.analysis.to_version }}</small>
      </div>
      <div class="metric-card">
        <span>影响项</span>
        <strong>{{ assessment.analysis.summary.total_impacts }}</strong>
        <small>breaking {{ assessment.analysis.summary.breaking_impacts }}</small>
      </div>
      <div class="metric-card">
        <span>迁移工作量</span>
        <strong>{{ assessment.analysis.migration_effort.level }}</strong>
        <small>{{ assessment.analysis.migration_effort.estimated_hours_min }}-{{ assessment.analysis.migration_effort.estimated_hours_max }}h</small>
      </div>

      <section class="impact-section">
        <h4>受影响端点</h4>
        <ul>
          <li v-for="endpoint in assessment.analysis.affected_endpoints" :key="endpoint">{{ endpoint }}</li>
          <li v-if="assessment.analysis.affected_endpoints.length === 0" class="empty-row">未发现端点影响</li>
        </ul>
      </section>

      <section class="impact-section">
        <h4>主要影响</h4>
        <ul>
          <li v-for="impact in topImpacts" :key="`${impact.category}:${impact.path}:${impact.change_type}`">
            <strong>{{ impact.severity }}</strong>
            <span>{{ impact.category }} / {{ impact.change_type }} / {{ impact.path }}</span>
            <small>{{ impact.reason }}</small>
          </li>
          <li v-if="topImpacts.length === 0" class="empty-row">未发现破坏性影响</li>
        </ul>
      </section>

      <section class="impact-section">
        <h4>治理建议</h4>
        <ul>
          <li v-for="recommendation in assessment.analysis.recommendations" :key="recommendation">
            {{ recommendation }}
          </li>
          <li v-if="assessment.analysis.recommendations.length === 0" class="empty-row">暂无额外建议</li>
        </ul>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import {
  assessContractImpact,
  type ContractImpactAssessment,
} from '@/api/contractImpact'

const fromVersionId = ref<number | string>(1)
const toVersionId = ref<number | string>(2)
const loading = ref(false)
const errorMessage = ref('')
const requestId = ref('')
const assessment = ref<ContractImpactAssessment | null>(null)

const normalizedFromVersionId = computed(() => Number(fromVersionId.value))
const normalizedToVersionId = computed(() => Number(toVersionId.value))

const canAnalyze = computed(() => (
  Number.isInteger(normalizedFromVersionId.value)
  && Number.isInteger(normalizedToVersionId.value)
  && normalizedFromVersionId.value > 0
  && normalizedToVersionId.value > 0
  && normalizedFromVersionId.value !== normalizedToVersionId.value
))

const topImpacts = computed(() => assessment.value?.topImpacts.slice(0, 5) ?? [])

const runImpactAnalysis = async () => {
  if (!canAnalyze.value) {
    errorMessage.value = '请选择两个不同的有效契约版本 ID'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    const response = await assessContractImpact({
      fromVersionId: normalizedFromVersionId.value,
      toVersionId: normalizedToVersionId.value,
    })
    assessment.value = response.data
    requestId.value = response.request_id || ''
  } catch (error) {
    assessment.value = null
    errorMessage.value = error instanceof Error ? error.message : '契约影响分析失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.contract-impact-panel {
  display: grid;
  gap: 18px;
  padding: 22px;
  border: 1px solid var(--artdeco-border-primary, rgba(218, 165, 32, 0.28));
  border-radius: 20px;
  background:
    linear-gradient(135deg, rgba(218, 165, 32, 0.10), transparent 32%),
    rgba(8, 16, 28, 0.72);
  color: var(--artdeco-text-primary, #f7f0dc);
}

.panel-header,
.impact-form,
.impact-results {
  display: grid;
  gap: 16px;
}

.panel-header {
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: start;
}

.panel-kicker,
.panel-meta,
.metric-card span,
.risk-card span {
  color: var(--artdeco-text-muted, #9aa4b2);
  font-size: 0.72rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.panel-header h3 {
  margin: 4px 0;
  font-size: 1.35rem;
}

.panel-copy {
  margin: 0;
  color: var(--artdeco-text-secondary, #c9d0d8);
}

.panel-meta {
  justify-items: end;
}

.impact-form {
  grid-template-columns: repeat(2, minmax(160px, 1fr)) auto;
  align-items: end;
}

.impact-form label {
  display: grid;
  gap: 8px;
  color: var(--artdeco-text-secondary, #c9d0d8);
  font-size: 0.86rem;
}

.impact-form input {
  min-height: 38px;
  border: 1px solid var(--artdeco-border-secondary, rgba(255, 255, 255, 0.18));
  border-radius: 12px;
  background: rgba(4, 10, 18, 0.74);
  color: var(--artdeco-text-primary, #f7f0dc);
  padding: 0 12px;
}

.impact-form button {
  min-height: 40px;
  border: 0;
  border-radius: 12px;
  background: var(--artdeco-accent-gold, #d4af37);
  color: #121820;
  cursor: pointer;
  font-weight: 700;
  padding: 0 16px;
}

.impact-form button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.impact-error {
  margin: 0;
  color: var(--artdeco-danger, #ff7a7a);
}

.impact-results {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.metric-card,
.risk-card,
.impact-section {
  border: 1px solid var(--artdeco-border-secondary, rgba(255, 255, 255, 0.14));
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.045);
  padding: 16px;
}

.metric-card strong,
.risk-card strong {
  display: block;
  margin-top: 8px;
  font-size: 1.6rem;
}

.metric-card small,
.risk-card small,
.impact-section small {
  color: var(--artdeco-text-muted, #9aa4b2);
}

.risk-critical strong,
.risk-high strong {
  color: var(--artdeco-danger, #ff7a7a);
}

.risk-medium strong {
  color: var(--artdeco-warning, #f5c542);
}

.impact-section {
  grid-column: 1 / -1;
}

.impact-section h4 {
  margin: 0 0 10px;
}

.impact-section ul {
  display: grid;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.impact-section li {
  display: grid;
  gap: 4px;
  color: var(--artdeco-text-secondary, #c9d0d8);
}

.impact-section li strong {
  color: var(--artdeco-text-primary, #f7f0dc);
}

.empty-row {
  color: var(--artdeco-text-muted, #9aa4b2);
}

@media (max-width: 860px) {
  .panel-header,
  .impact-form,
  .impact-results {
    grid-template-columns: 1fr;
  }

  .panel-meta {
    justify-items: start;
  }
}
</style>
