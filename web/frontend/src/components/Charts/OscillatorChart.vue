<template>
  <div class="oscillator-chart" ref="chartContainer">
    <div class="oscillator-header">
      <div class="oscillator-title">{{ displayTitle }}</div>
      <div class="oscillator-values" v-if="currentValues.length > 0">
        <span
          v-for="(item, index) in currentValues"
          :key="index"
          class="oscillator-value"
          :style="{ color: item.color }"
        >
          {{ item.label }}: {{ item.value }}
        </span>
      </div>
    </div>
    <div ref="chartRef" class="chart-area"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import * as klinecharts from 'klinecharts';
import type { KLineData } from '@/types/kline';
import type { OscillatorType } from '@/utils/indicator';
import { calculateOscillator, formatOscillatorValue } from '@/utils/indicator/oscillator';

const props = withDefaults(defineProps<{
  type: OscillatorType;
  klineData: KLineData[];
  params?: number[];
  colors?: string[];
  range?: [number, number];
  title?: string;
}>(), {
  params: () => [12, 26, 9]
});

const chartContainer = ref<HTMLElement | null>(null);
const chartRef = ref<HTMLElement | null>(null);
let chartInstance: ReturnType<typeof klinecharts.init> | null = null;

const currentValues = ref<{ label: string; value: string; color: string }[]>([]);

const defaultColors: Record<OscillatorType, string[]> = {
  MACD: ['#2DC08E', '#F92855', '#D4AF37'],
  RSI: ['#D4AF37', '#2DC08E', '#1E3D59'],
  KDJ: ['#D4AF37', '#2DC08E', '#F92855'],
  WR: ['#D4AF37', '#2DC08E'],
  CCI: ['#D4AF37'],
  OBV: ['#D4AF37'],
  ATR: ['#D4AF37']
};

const defaultRanges: Record<OscillatorType, [number, number] | undefined> = {
  MACD: [-5, 5],
  RSI: [0, 100],
  KDJ: [0, 100],
  WR: [-100, 0],
  CCI: undefined,
  OBV: undefined,
  ATR: undefined
};

const displayTitle = computed(() => props.title || props.type);

const displayColors = computed(() => props.colors || defaultColors[props.type] || ['#D4AF37']);
const displayRange = computed(() => props.range || defaultRanges[props.type]);

const getIndicatorNames = (type: OscillatorType): string[] => {
  const names: Record<OscillatorType, string[]> = {
    MACD: ['DIF', 'DEA', 'MACD'],
    RSI: props.params?.map(p => `RSI${p}`) || ['RSI'],
    KDJ: ['K', 'D', 'J'],
    WR: props.params?.map(p => `WR${p}`) || ['WR'],
    CCI: ['CCI'],
    OBV: ['OBV'],
    ATR: ['ATR']
  };
  return names[type] || [type];
};

const updateChart = () => {
  if (!chartInstance || props.klineData.length === 0) return;

  const result = calculateOscillator(
    props.klineData,
    props.type,
    props.params || [12, 26, 9]
  );

  const indicatorNames = getIndicatorNames(props.type);
  const colors = displayColors.value;

  const chartData = props.klineData.map((kline, i) => {
    const data: Record<string, unknown> = {
      timestamp: kline.timestamp,
      open: kline.open,
      high: kline.high,
      low: kline.low,
      close: kline.close,
      volume: kline.volume
    };
    indicatorNames.forEach((name, idx) => {
      data[name] = result[name]?.[i] ?? null;
    });
    return data;
  });

  try {
    chartInstance.applyNewData(chartData);
  } catch (e) {
    console.warn('Failed to update oscillator chart:', e);
  }

  const lastIndex = props.klineData.length - 1;
  currentValues.value = indicatorNames.map((name, idx) => ({
    label: name,
    value: formatOscillatorValue(result[name]?.[lastIndex] ?? NaN, props.type),
    color: (colors as string[])[idx % colors.length]
  }));
};

const initChart = () => {
  if (!chartRef.value) return;

  const range = displayRange.value;

  const chartStyles = {
    grid: {
      show: true,
      horizontal: { show: true, size: 1, color: '#1A1A1A' },
      vertical: { show: false, size: 1, color: '#1A1A1A' }
    },
    xAxis: {
      axisLine: { show: true, color: '#333333' },
      tickLine: { show: false, color: '#333333' },
      tickText: { color: '#888888', size: 10 }
    },
    yAxis: {
      axisLine: { show: true, color: '#333333' },
      tickLine: { show: true, color: '#333333' },
      tickText: { color: '#888888', size: 10 },
      ...(range ? { min: range[0], max: range[1] } : {})
    },
    crosshair: {
      show: true,
      horizontal: { show: true, lineColor: '#D4AF37', lineWidth: 1, lineStyle: 'dashed' as const },
      vertical: { show: true, lineColor: '#D4AF37', lineWidth: 1, lineStyle: 'dashed' as const }
    },
    tooltip: {
      show: true,
      type: 'standard' as const,
      labels: ['时间', ...getIndicatorNames(props.type)],
      labelColor: '#F2F0E4',
      labelColorDot: '#D4AF37'
    }
  };

  chartInstance = klinecharts.init(chartRef.value, {
    locale: 'zh-CN',
    styles: chartStyles,
    layout: [
      { type: 'xAxis' as const, height: 25 }
    ]
  });

  if (props.klineData.length > 0) {
    updateChart();
  }

  try {
    chartInstance.subscribeAction('onCrosshairChange' as any, (data: unknown) => {
      const crosshair = data as { data?: Record<string, unknown> };
      if (crosshair.data) {
        const indicatorNames = getIndicatorNames(props.type);
        const colors = displayColors.value;
        currentValues.value = indicatorNames.map((name, idx) => ({
          label: name,
          value: formatOscillatorValue(crosshair.data?.[name] as number ?? NaN, props.type),
          color: (colors as string[])[idx % colors.length]
        }));
      }
    });
  } catch (e) {
    console.warn('Failed to subscribe to crosshair change:', e);
  }
};

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize();
  }
};

watch(() => props.klineData, () => {
  nextTick(() => updateChart());
}, { deep: true });

watch(() => props.params, () => {
  nextTick(() => updateChart());
});

onMounted(() => {
  nextTick(() => initChart());
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (chartInstance) {
    try {
      chartInstance.dispose();
    } catch (e) {
      console.warn('Failed to dispose chart:', e);
    }
  }
});
</script>

<style scoped>
.oscillator-chart {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--art-deco-bg-secondary);
}

.oscillator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  border-bottom: 1px solid var(--art-deco-border);
}

.oscillator-title {
  font-family: var(--art-deco-font-mono);
  font-size: 11px;
  color: var(--art-deco-gold);
  text-transform: uppercase;
}

.oscillator-values {
  display: flex;
  gap: 12px;
}

.oscillator-value {
  font-family: var(--art-deco-font-mono);
  font-size: 10px;
}

.chart-area {
  flex: 1;
  width: 100%;
}
</style>
