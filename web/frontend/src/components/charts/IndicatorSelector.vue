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
              v-for="(indicator, _idx) in mainIndicators"
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
              v-for="(indicator, _idx) in oscillatorIndicators"
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
            v-for="[key, indicator] in activeIndicators"
            :key="key"
            class="active-item"
          >
            <span class="active-name">{{ indicator.shortName }}</span>
            <span class="active-params">({{ indicator.params.join(', ') }})</span>
            <button class="active-remove" @click="removeIndicator(key)">×</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">

</script>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { IndicatorConfig, IndicatorType } from '@/utils/indicator';
import type { OscillatorConfig, OscillatorType } from '@/utils/indicator';

type _IndicatorEntry = [IndicatorType, IndicatorConfig];
type _OscillatorEntry = [OscillatorType, OscillatorConfig];

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
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-default);
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: calc(var(--artdeco-spacing-5) / 2) var(--artdeco-spacing-3);
  border-bottom: 1px solid var(--artdeco-border-default);
}

.selector-title {
  font-family: var(--artdeco-font-body, var(--font-body));
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-primary);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}

.selector-toggle {
  background: transparent;
  border: none;
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-body, var(--font-body));
  font-size: var(--artdeco-text-compact-xs);
  cursor: pointer;
}

.selector-content {
  padding: var(--artdeco-spacing-3);
}

.indicator-groups {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-3);
}

.indicator-group {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.group-title {
  font-family: var(--artdeco-font-body, var(--font-body));
  font-size: var(--artdeco-text-compact-xs);
  color: var(--artdeco-fg-muted);
  text-transform: uppercase;
}

.indicator-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: calc(var(--artdeco-spacing-3) / 2);
}

.indicator-btn {
  height: calc(var(--artdeco-spacing-6) + calc(var(--artdeco-spacing-1) / 2));
  padding: 0 calc(var(--artdeco-spacing-5) / 2);
  background: var(--artdeco-bg-elevated);
  border: 1px solid var(--artdeco-border-default);
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-accent, var(--font-mono));
  font-size: var(--artdeco-text-compact-xs);
  cursor: pointer;
  transition: all 0.2s;
}

.indicator-btn:hover {
  border-color: var(--artdeco-gold-primary);
  color: var(--artdeco-gold-primary);
}

.indicator-btn.active {
  background: color-mix(in srgb, var(--artdeco-gold-primary) 15%, var(--artdeco-bg-card));
  border-color: var(--artdeco-gold-primary);
  color: var(--artdeco-gold-primary);
}

.indicator-settings {
  margin-top: var(--artdeco-spacing-3);
  padding: var(--artdeco-spacing-3);
  background: var(--artdeco-bg-elevated);
  border: 1px solid var(--artdeco-border-default);
}

.settings-title {
  font-family: var(--artdeco-font-body, var(--font-body));
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-gold-primary);
  margin-bottom: calc(var(--artdeco-spacing-5) / 2);
}

.settings-content {
  display: flex;
  gap: calc(var(--artdeco-spacing-5) / 2);
  flex-wrap: wrap;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-1);
}

.setting-label {
  font-family: var(--artdeco-font-body, var(--font-body));
  font-size: calc(var(--artdeco-spacing-5) / 4);
  color: var(--artdeco-fg-muted);
}

.setting-input {
  width: calc(var(--artdeco-spacing-10) + var(--artdeco-spacing-5));
  height: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1));
  padding: 0 var(--artdeco-spacing-2);
  background: var(--artdeco-bg-global);
  border: 1px solid var(--artdeco-border-default);
  color: var(--artdeco-fg-primary);
  font-family: var(--artdeco-font-accent, var(--font-mono));
  font-size: var(--artdeco-text-xs);
  text-align: center;
}

.setting-input:focus {
  outline: none;
  border-color: var(--artdeco-gold-primary);
}

.settings-actions {
  display: flex;
  gap: var(--artdeco-spacing-2);
  margin-top: calc(var(--artdeco-spacing-5) / 2);
}

.settings-btn {
  height: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1));
  padding: 0 calc(var(--artdeco-spacing-3) + calc(var(--artdeco-spacing-1) / 2));
  border: 1px solid var(--artdeco-border-default);
  font-family: var(--artdeco-font-body, var(--font-body));
  font-size: var(--artdeco-text-compact-xs);
  cursor: pointer;
  transition: all 0.2s;
}

.settings-btn.apply {
  background: color-mix(in srgb, var(--artdeco-gold-primary) 15%, var(--artdeco-bg-card));
  border-color: var(--artdeco-gold-primary);
  color: var(--artdeco-gold-primary);
}

.settings-btn.apply:hover {
  background: color-mix(in srgb, var(--artdeco-gold-primary) 25%, var(--artdeco-bg-card));
}

.settings-btn.reset {
  background: transparent;
  border-color: var(--artdeco-border-default);
  color: var(--artdeco-fg-muted);
}

.settings-btn.reset:hover {
  border-color: var(--artdeco-fg-muted);
  color: var(--artdeco-fg-primary);
}

.active-indicators {
  margin-top: var(--artdeco-spacing-3);
  padding-top: var(--artdeco-spacing-3);
  border-top: 1px solid var(--artdeco-border-default);
}

.active-title {
  font-family: var(--artdeco-font-body, var(--font-body));
  font-size: var(--artdeco-text-compact-xs);
  color: var(--artdeco-fg-muted);
  margin-bottom: var(--artdeco-spacing-2);
}

.active-list {
  display: flex;
  flex-direction: column;
  gap: calc(var(--artdeco-spacing-3) / 2);
}

.active-item {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  padding: calc(var(--artdeco-spacing-3) / 2) calc(var(--artdeco-spacing-5) / 2);
  background: var(--artdeco-bg-elevated);
  border: 1px solid var(--artdeco-border-default);
}

.active-name {
  font-family: var(--artdeco-font-accent, var(--font-mono));
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-gold-primary);
}

.active-params {
  font-family: var(--artdeco-font-accent, var(--font-mono));
  font-size: var(--artdeco-text-compact-xs);
  color: var(--artdeco-fg-muted);
}

.active-remove {
  margin-left: auto;
  width: var(--artdeco-text-lg);
  height: var(--artdeco-text-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  cursor: pointer;
  transition: color 0.2s;
}

.active-remove:hover {
  color: var(--artdeco-rise);
}
</style>
