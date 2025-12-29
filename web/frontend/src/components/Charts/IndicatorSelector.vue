<template>
  <div class="indicator-selector">
    <div class="selector-header">
      <span class="selector-title">技术指标</span>
      <button class="selector-toggle" @click="expanded = !expanded">
        {{ expanded ? '收起' : '展开' }}
      </button>
    </div>

    <div v-show="expanded" class="selector-content">
      <div class="indicator-groups">
        <div class="indicator-group">
          <div class="group-title">主图叠加</div>
          <div class="indicator-buttons">
            <button
              v-for="indicator in mainIndicators"
              :key="indicator.type"
              :class="['indicator-btn', { active: activeIndicators.has(indicator.type) }]"
              @click="toggleIndicator(indicator.type)"
            >
              {{ indicator.shortName }}
            </button>
          </div>
        </div>

        <div class="indicator-group">
          <div class="group-title">副图指标</div>
          <div class="indicator-buttons">
            <button
              v-for="indicator in oscillatorIndicators"
              :key="indicator.type"
              :class="['indicator-btn', { active: activeIndicators.has(indicator.type) }]"
              @click="toggleIndicator(indicator.type)"
            >
              {{ indicator.shortName }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="selectedIndicator" class="indicator-settings">
        <div class="settings-title">{{ selectedIndicator.name }} 参数设置</div>
        <div class="settings-content">
          <div v-for="(param, index) in selectedIndicator.params" :key="index" class="setting-item">
            <label class="setting-label">周期{{ index + 1 }}</label>
            <input
              type="number"
              :value="param"
              min="1"
              max="500"
              class="setting-input"
              @input="updateParam(index, ($event.target as HTMLInputElement).value)"
            />
          </div>
        </div>
        <div class="settings-actions">
          <button class="settings-btn apply" @click="applySettings">应用</button>
          <button class="settings-btn reset" @click="resetSettings">重置</button>
        </div>
      </div>

      <div v-if="activeIndicators.size > 0" class="active-indicators">
        <div class="active-title">已选指标</div>
        <div class="active-list">
          <div
            v-for="indicator in activeIndicators"
            :key="indicator.type"
            class="active-item"
          >
            <span class="active-name">{{ indicator.shortName }}</span>
            <span class="active-params">({{ indicator.params.join(', ') }})</span>
            <button class="active-remove" @click="removeIndicator(indicator.type)">×</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { IndicatorConfig, IndicatorType } from '@/utils/indicator';
import type { OscillatorConfig, OscillatorType } from '@/utils/indicator';

type IndicatorEntry = [IndicatorType, IndicatorConfig];
type OscillatorEntry = [OscillatorType, OscillatorConfig];

const props = defineProps<{
  modelValue: (IndicatorConfig | OscillatorConfig)[];
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: (IndicatorConfig | OscillatorConfig)[]): void;
  (e: 'change', indicators: (IndicatorConfig | OscillatorConfig)[]): void;
}>();

const expanded = ref(true);
const activeIndicators = ref<Map<string, IndicatorConfig | OscillatorConfig>>(new Map());
const originalConfigs = ref<Map<string, IndicatorConfig | OscillatorConfig>>(new Map());

const mainIndicators: IndicatorConfig[] = [
  { name: '移动平均线', shortName: 'MA', type: 'MA', params: [5, 10, 20, 60], colors: ['#2DC08E', '#D4AF37', '#F92855', '#1E3D59'], visible: true },
  { name: '指数移动平均', shortName: 'EMA', type: 'EMA', params: [12, 26], colors: ['#D4AF37', '#2DC08E'], visible: false },
  { name: '布林带', shortName: 'BOLL', type: 'BOLL', params: [20, 2], colors: ['#D4AF37', '#D4AF37', '#D4AF37'], visible: false },
  { name: '抛物线指标', shortName: 'SAR', type: 'SAR', params: [0.02, 0.2], colors: ['#D4AF37'], visible: false },
  { name: '考夫曼自适应', shortName: 'KAMA', type: 'KAMA', params: [10, 2, 30], colors: ['#2DC08E'], visible: false }
];

const oscillatorIndicators: OscillatorConfig[] = [
  { name: 'MACD', shortName: 'MACD', type: 'MACD', params: [12, 26, 9], colors: ['#2DC08E', '#F92855', '#D4AF37'], visible: false },
  { name: '相对强弱', shortName: 'RSI', type: 'RSI', params: [6, 12, 24], colors: ['#D4AF37', '#2DC08E', '#1E3D59'], visible: false },
  { name: '随机指标', shortName: 'KDJ', type: 'KDJ', params: [9, 3, 3], colors: ['#D4AF37', '#2DC08E', '#F92855'], visible: false },
  { name: '威廉指标', shortName: 'WR', type: 'WR', params: [6, 10], colors: ['#D4AF37', '#2DC08E'], visible: false },
  { name: '顺势指标', shortName: 'CCI', type: 'CCI', params: [14], colors: ['#D4AF37'], visible: false }
];

const selectedIndicator = computed(() => {
  const types = Array.from(activeIndicators.value.keys());
  if (types.length === 0) return null;
  const firstType = types[0];
  return mainIndicators.find(m => m.type === firstType) || oscillatorIndicators.find(o => o.type === firstType) || null;
});

const toggleIndicator = (type: string) => {
  if (activeIndicators.value.has(type)) {
    activeIndicators.value.delete(type);
  } else {
    const config = [...mainIndicators, ...oscillatorIndicators].find(i => i.type === type);
    if (config) {
      activeIndicators.value.set(type, { ...config });
      originalConfigs.value.set(type, { ...config });
    }
  }
  emitChange();
};

const removeIndicator = (type: string) => {
  activeIndicators.value.delete(type);
  emitChange();
};

const updateParam = (index: number, value: string) => {
  const numValue = parseInt(value, 10);
  if (isNaN(numValue) || numValue < 1) return;

  const selected = selectedIndicator.value;
  if (selected) {
    const newParams = [...selected.params];
    newParams[index] = numValue;
    selected.params = newParams;

    const active = activeIndicators.value.get(selected.type);
    if (active) {
      active.params = newParams;
      activeIndicators.value.set(selected.type, active);
    }
  }
};

const applySettings = () => {
  emitChange();
};

const resetSettings = () => {
  const selected = selectedIndicator.value;
  if (selected) {
    const original = originalConfigs.value.get(selected.type);
    if (original) {
      selected.params = [...original.params];
      const active = activeIndicators.value.get(selected.type);
      if (active) {
        active.params = [...original.params];
        activeIndicators.value.set(selected.type, active);
      }
    }
  }
};

const emitChange = () => {
  const configs = Array.from(activeIndicators.value.values());
  emit('update:modelValue', configs);
  emit('change', configs);
};

watch(() => props.modelValue, (newVal) => {
  activeIndicators.value = new Map(newVal.map((c: IndicatorConfig | OscillatorConfig) => [c.type, c]));
}, { immediate: true });
</script>

<style scoped>
.indicator-selector {
  background: var(--art-deco-bg-secondary);
  border: 1px solid var(--art-deco-border);
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-bottom: 1px solid var(--art-deco-border);
}

.selector-title {
  font-family: var(--art-deco-font-body);
  font-size: 12px;
  color: var(--art-deco-fg-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.selector-toggle {
  background: transparent;
  border: none;
  color: var(--art-deco-gold);
  font-family: var(--art-deco-font-body);
  font-size: 11px;
  cursor: pointer;
}

.selector-content {
  padding: 12px;
}

.indicator-groups {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.indicator-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.group-title {
  font-family: var(--art-deco-font-body);
  font-size: 11px;
  color: var(--art-deco-fg-muted);
  text-transform: uppercase;
}

.indicator-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.indicator-btn {
  height: 26px;
  padding: 0 10px;
  background: var(--art-deco-bg-tertiary);
  border: 1px solid var(--art-deco-border);
  color: var(--art-deco-fg-secondary);
  font-family: var(--art-deco-font-mono);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}

.indicator-btn:hover {
  border-color: var(--art-deco-gold);
  color: var(--art-deco-gold);
}

.indicator-btn.active {
  background: rgba(212, 175, 55, 0.15);
  border-color: var(--art-deco-gold);
  color: var(--art-deco-gold);
}

.indicator-settings {
  margin-top: 12px;
  padding: 12px;
  background: var(--art-deco-bg-tertiary);
  border: 1px solid var(--art-deco-border);
}

.settings-title {
  font-family: var(--art-deco-font-body);
  font-size: 12px;
  color: var(--art-deco-gold);
  margin-bottom: 10px;
}

.settings-content {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.setting-label {
  font-family: var(--art-deco-font-body);
  font-size: 10px;
  color: var(--art-deco-fg-muted);
}

.setting-input {
  width: 60px;
  height: 28px;
  padding: 0 8px;
  background: var(--art-deco-bg-primary);
  border: 1px solid var(--art-deco-border);
  color: var(--art-deco-fg-primary);
  font-family: var(--art-deco-font-mono);
  font-size: 12px;
  text-align: center;
}

.setting-input:focus {
  outline: none;
  border-color: var(--art-deco-gold);
}

.settings-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.settings-btn {
  height: 28px;
  padding: 0 14px;
  border: 1px solid var(--art-deco-border);
  font-family: var(--art-deco-font-body);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}

.settings-btn.apply {
  background: rgba(212, 175, 55, 0.15);
  border-color: var(--art-deco-gold);
  color: var(--art-deco-gold);
}

.settings-btn.apply:hover {
  background: rgba(212, 175, 55, 0.25);
}

.settings-btn.reset {
  background: transparent;
  border-color: var(--art-deco-border);
  color: var(--art-deco-fg-muted);
}

.settings-btn.reset:hover {
  border-color: var(--art-deco-fg-muted);
  color: var(--art-deco-fg-secondary);
}

.active-indicators {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--art-deco-border);
}

.active-title {
  font-family: var(--art-deco-font-body);
  font-size: 11px;
  color: var(--art-deco-fg-muted);
  margin-bottom: 8px;
}

.active-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.active-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: var(--art-deco-bg-tertiary);
  border: 1px solid var(--art-deco-border);
}

.active-name {
  font-family: var(--art-deco-font-mono);
  font-size: 12px;
  color: var(--art-deco-gold);
}

.active-params {
  font-family: var(--art-deco-font-mono);
  font-size: 11px;
  color: var(--art-deco-fg-muted);
}

.active-remove {
  margin-left: auto;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--art-deco-fg-muted);
  font-size: 14px;
  cursor: pointer;
  transition: color 0.2s;
}

.active-remove:hover {
  color: var(--art-deco-red);
}
</style>
