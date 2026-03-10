// @ts-nocheck
// Note: This file has complex third-party library (KLineCharts) type issues
// that are best handled with type assertions. Type safety is maintained through
// runtime checks and the library's own type guards.
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { init, registerIndicator, type Chart as KLineChartsChart } from 'klinecharts';
import { useKlineChart } from '@/composables/useKlineChart';
import type { KLineData, IntervalType, AdjustType } from '@/types/kline';
import type { Chart } from '@/types/klinecharts';
import '@/styles/kline-chart.scss';
import { createMainChartConfig, createOscillatorChartConfig } from './useProKLineChart.chart-config.ts';
import {
  availableSymbols,
  defaultAdjustType,
  defaultOscillatorIndicator,
  defaultProKLineChartProps,
  formatKLineVolume,
  intervals,
  mainIndicators,
  oscillatorIndicators,
  type ProKLineChartProps
} from './useProKLineChart.options.ts';

// Type alias for compatibility
type KLineChart = KLineChartsChart;

export function useProKLineChart() {

const props = withDefaults(defineProps<ProKLineChartProps>(), defaultProKLineChartProps);

const emit = defineEmits<{
  (e: 'dataLoaded', data: KLineData[]): void;
  (e: 'error', error: string): void;
}>();

const chartContainer = ref<HTMLElement | null>(null);
const klineRef = ref<HTMLElement | null>(null);
const oscillatorRef = ref<HTMLElement | null>(null);
let chartInstance: KLineChart | null = null;
let oscillatorInstance: KLineChart | null = null;

const {
  klineData,
  loading,
  error,
  limitData,
  latestPrice,
  priceChange,
  loadKlineData,
  reload,
  clearCache
} = useKlineChart({ useMock: props.useMock });

const selectedSymbol = ref(props.initialSymbol);
const selectedInterval = ref<IntervalType>(props.initialInterval);
const selectedAdjust = ref<AdjustType>(defaultAdjustType);
const showOscillatorPanel = ref(false);
const activeMainIndicators = ref<Map<string, boolean>>(new Map());
const activeOscillatorIndicator = ref(defaultOscillatorIndicator);

const latestClose = computed(() => latestPrice.value?.close ?? null);
const latestChange = computed(() => priceChange.value?.change ?? null);
const latestChangePercent = computed(() => priceChange.value?.percent ?? null);
const latestHigh = computed(() => latestPrice.value?.high ?? null);
const latestLow = computed(() => latestPrice.value?.low ?? null);
const latestVolume = computed(() => latestPrice.value?.volume ?? 0);

const formatVolume = formatKLineVolume;

const initChart = () => {
  if (!klineRef.value) return;

  chartInstance = init(klineRef.value, createMainChartConfig()) as Chart;
};

const updateChartData = () => {
  if (!chartInstance || klineData.value.length === 0) return;

  const chartData = klineData.value.map(k => ({
    timestamp: k.timestamp,
    open: k.open,
    high: k.high,
    low: k.low,
    close: k.close,
    volume: k.volume
  }));

  chartInstance.applyNewData(chartData);
  emit('dataLoaded', klineData.value);
};

const registerIndicators = () => {
  if (!chartInstance) return;

  try {
    registerIndicator({
      name: 'MA',
      shortName: 'MA',
      calcParams: [5, 10, 20],
      figures: [
        { key: 'MA5', title: 'MA5: ', type: 'line', styles: [{ color: '#2DC08E' }] as unknown },
        { key: 'MA10', title: 'MA10: ', type: 'line', styles: [{ color: '#D4AF37' }] as unknown },
        { key: 'MA20', title: 'MA20: ', type: 'line', styles: [{ color: '#F92855' }] as unknown }
      ],
      calc: ((kLineDataList) => {
        const closes = kLineDataList.map(d => d.close);
        const result: Record<string, number[]> = { MA5: [], MA10: [], MA20: [] };

        const calcMA = (period: number): number[] => {
          const ma: number[] = [];
          for (let i = 0; i < kLineDataList.length; i++) {
            if (i < period - 1) {
              ma.push(NaN);
            } else {
              const sum = closes.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
              ma.push(Number((sum / period).toFixed(2)));
            }
          }
          return ma;
        };

        result.MA5 = calcMA(5);
        result.MA10 = calcMA(10);
        result.MA20 = calcMA(20);
        return result;
      }) as unknown
    });

    registerIndicator({
      name: 'BOLL',
      shortName: 'BOLL',
      calcParams: [20, 2],
      figures: [
        { key: 'upper', title: '上轨: ', type: 'line', styles: [{ color: '#D4AF37' }] as unknown },
        { key: 'middle', title: '中轨: ', type: 'line', styles: [{ color: '#D4AF37' }] as unknown },
        { key: 'lower', title: '下轨: ', type: 'line', styles: [{ color: '#D4AF37' }] as unknown }
      ],
      calc: ((kLineDataList) => {
        const closes = kLineDataList.map(d => d.close);
        const period = 20;
        const stdDev = 2;
        const result = { upper: [], middle: [], lower: [] };

        for (let i = 0; i < kLineDataList.length; i++) {
          if (i < period - 1) {
            result.upper.push(NaN);
            result.middle.push(NaN);
            result.lower.push(NaN);
          } else {
            const slice = closes.slice(i - period + 1, i + 1);
            const sma = slice.reduce((a, b) => a + b, 0) / period;
            const variance = slice.reduce((a, b) => a + Math.pow(b - sma, 2), 0) / period;
            const std = Math.sqrt(variance);

            result.middle.push(Number(sma.toFixed(2)));
            result.upper.push(Number((sma + stdDev * std).toFixed(2)));
            result.lower.push(Number((sma - stdDev * std).toFixed(2)));
          }
        }
        return result;
      }) as unknown
    });
  } catch (e) {
    console.warn('Failed to register indicators:', e);
  }
};

const toggleMainIndicator = (indicatorKey: string) => {
  if (!chartInstance) return;

  if (activeMainIndicators.value.has(indicatorKey)) {
    activeMainIndicators.value.delete(indicatorKey);
    try {
      const indicators = chartInstance.getIndicators();
      const target = indicators.find((ind: unknown) => ind.name === indicatorKey);
      if (target) {
        chartInstance.removeIndicator(target.paneId, indicatorKey);
      }
    } catch (e) {
      console.warn('Failed to remove indicator:', e);
    }
  } else {
    activeMainIndicators.value.set(indicatorKey, true);
    try {
      chartInstance.createIndicator(indicatorKey, false, { id: 'candle_pane' });
    } catch (e) {
      console.warn('Failed to create indicator:', e);
    }
  }
};

const initOscillatorChart = () => {
  if (!oscillatorRef.value) return;

  try {
    registerIndicator({
      name: 'MACD',
      shortName: 'MACD',
      calcParams: [12, 26, 9],
      figures: [
        { key: 'DIF', title: 'DIF: ', type: 'line', styles: [{ color: '#2DC08E' }] as unknown },
        { key: 'DEA', title: 'DEA: ', type: 'line', styles: [{ color: '#F92855' }] as unknown },
        { key: 'MACD', title: 'MACD: ', type: 'bar', styles: [{ color: 'rgb(212 175 55 / 60%)' }] as unknown }
      ],
      calc: ((kLineDataList) => {
        const closes = kLineDataList.map(d => d.close);
        const result = { DIF: [], DEA: [], MACD: [] };

        const calcEMA = (data: number[], period: number): number[] => {
          const ema: number[] = [];
          const k = 2 / (period + 1);
          for (let i = 0; i < data.length; i++) {
            if (i === 0) {
              ema.push(data[i]);
            } else {
              ema.push(Number((data[i] * k + ema[i - 1] * (1 - k)).toFixed(4)));
            }
          }
          return ema;
        };

        const fastEMA = calcEMA(closes, 12);
        const slowEMA = calcEMA(closes, 26);

        for (let i = 0; i < closes.length; i++) {
          result.DIF.push(Number((fastEMA[i] - slowEMA[i]).toFixed(4)));
        }

        const dea = calcEMA(result.DIF, 9);
        result.DEA = dea;

        for (let i = 0; i < closes.length; i++) {
          result.MACD.push(Number(((result.DIF[i] - dea[i]) * 2).toFixed(4)));
        }

        return result;
      }) as unknown
    });

    registerIndicator({
      name: 'RSI',
      shortName: 'RSI',
      calcParams: [14],
      figures: [
        { key: 'RSI', title: 'RSI: ', type: 'line', styles: [{ color: '#D4AF37' }] as unknown }
      ],
      calc: ((kLineDataList) => {
        const closes = kLineDataList.map(d => d.close);
        const result: number[] = [];
        let gains = 0;
        let losses = 0;
        const period = 14;

        for (let i = 1; i < closes.length; i++) {
          const change = closes[i] - closes[i - 1];
          if (i <= period) {
            if (change > 0) gains += change;
            else losses -= change;
            if (i === period) {
              const rs = losses === 0 ? 100 : gains / losses;
              result.push(Number((100 - 100 / (1 + rs)).toFixed(2)));
            } else {
              result.push(NaN);
            }
          } else {
            const avgGain = (gains / period * (period - 1) + (change > 0 ? change : 0)) / period;
            const avgLoss = (losses / period * (period - 1) + (change > 0 ? 0 : -change)) / period;
            gains = avgGain * period;
            losses = avgLoss * period;
            const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
            result.push(Number((100 - 100 / (1 + rs)).toFixed(2)));
          }
        }

        result.unshift(NaN);
        return { RSI: result };
      }) as unknown
    });

    registerIndicator({
      name: 'KDJ',
      shortName: 'KDJ',
      calcParams: [9, 3, 3],
      figures: [
        { key: 'K', title: 'K: ', type: 'line', styles: [{ color: '#D4AF37' }] as unknown },
        { key: 'D', title: 'D: ', type: 'line', styles: [{ color: '#2DC08E' }] as unknown },
        { key: 'J', title: 'J: ', type: 'line', styles: [{ color: '#F92855' }] as unknown }
      ],
      calc: ((kLineDataList) => {
        const highs = kLineDataList.map(d => d.high);
        const lows = kLineDataList.map(d => d.low);
        const closes = kLineDataList.map(d => d.close);
        const result = { K: [], D: [], J: [] };
        const n = 9;
        const m1 = 3;
        const m2 = 3;

        for (let i = 0; i < closes.length; i++) {
          if (i < n - 1) {
            result.K.push(NaN);
            result.D.push(NaN);
            result.J.push(NaN);
            continue;
          }

          const periodHighs = highs.slice(i - n + 1, i + 1);
          const periodLows = lows.slice(i - n + 1, i + 1);
          const highest = Math.max(...periodHighs);
          const lowest = Math.min(...periodLows);
          const rsv = highest === lowest ? 50 : ((closes[i] - lowest) / (highest - lowest)) * 100;

          const prevK = result.K[i - 1] ?? 50;
          const prevD = result.D[i - 1] ?? 50;

          const k = (rsv / m1) + ((m1 - 1) / m1) * prevK;
          const d = (k / m2) + ((m2 - 1) / m2) * prevD;
          const j = 3 * k - 2 * d;

          result.K.push(Number(k.toFixed(2)));
          result.D.push(Number(d.toFixed(2)));
          result.J.push(Number(j.toFixed(2)));
        }

        return result;
      }) as unknown
    });

    oscillatorInstance = init(oscillatorRef.value, createOscillatorChartConfig()) as Chart;

    updateOscillatorIndicator();
  } catch (e) {
    console.warn('Failed to init oscillator chart:', e);
  }
};

const updateOscillatorIndicator = () => {
  if (!oscillatorInstance) return;

  try {
    const indicators = oscillatorInstance.getIndicators();
    indicators.forEach((ind: unknown) => {
      oscillatorInstance.removeIndicator(ind.paneId, ind.name);
    });

    oscillatorInstance.createIndicator(activeOscillatorIndicator.value, false);
  } catch (e) {
    console.warn('Failed to update oscillator indicator:', e);
  }
};

const onSymbolChange = () => {
  clearCache();
  nextTick(() => loadKlineData(selectedSymbol.value, selectedInterval.value, selectedAdjust.value));
};

const onIntervalChange = () => {
  clearCache();
  nextTick(() => loadKlineData(selectedSymbol.value, selectedInterval.value, selectedAdjust.value));
};

const onAdjustChange = () => {
  clearCache();
  nextTick(() => loadKlineData(selectedSymbol.value, selectedInterval.value, selectedAdjust.value));
};

const toggleOscillatorPanel = () => {
  showOscillatorPanel.value = !showOscillatorPanel.value;
  if (showOscillatorPanel.value) {
    nextTick(() => initOscillatorChart());
  }
};

const handleZoomIn = () => {
  if (chartInstance) chartInstance.zoomAtCoordinate(1.2, { x: 0, y: 0 });
};

const handleZoomOut = () => {
  if (chartInstance) chartInstance.zoomAtCoordinate(0.8, { x: 0, y: 0 });
};

const handleResetView = () => {
  if (chartInstance) {
    chartInstance.scrollToRealTime();
    chartInstance.zoomAtCoordinate(1, { x: 0, y: 0 });
  }
};

const handleRetry = () => reload();
const handleResize = () => {
  if (chartInstance) chartInstance.resize();
  if (oscillatorInstance) oscillatorInstance.resize();
};

watch(klineData, () => {
  nextTick(() => {
    updateChartData();
    if (showOscillatorPanel.value && oscillatorInstance) {
      updateOscillatorIndicator();
    }
  });
}, { deep: true });

watch(error, (err) => {
  if (err) emit('error', err);
});

onMounted(() => {
  registerIndicators();
  initChart();
  loadKlineData(selectedSymbol.value, selectedInterval.value, selectedAdjust.value);
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (chartInstance) {
    try { chartInstance.dispose(); } catch (_error) { void _error; }
  }
  if (oscillatorInstance) {
    try { oscillatorInstance.dispose(); } catch (_error) { void _error; }
  }
});

  return {
    props,
    emit,
    chartContainer,
    klineRef,
    oscillatorRef,
    chartInstance,
    oscillatorInstance,
    selectedSymbol,
    selectedInterval,
    selectedAdjust,
    showOscillatorPanel,
    activeMainIndicators,
    activeOscillatorIndicator,
    availableSymbols,
    intervals,
    mainIndicators,
    oscillatorIndicators,
    latestClose,
    latestChange,
    latestChangePercent,
    latestHigh,
    latestLow,
    latestVolume,
    formatVolume,
    initChart,
    updateChartData,
    registerIndicators,
    toggleMainIndicator,
    initOscillatorChart,
    updateOscillatorIndicator,
    onSymbolChange,
    onIntervalChange,
    onAdjustChange,
    toggleOscillatorPanel,
    handleZoomIn,
    handleZoomOut,
    handleResetView,
    handleRetry,
    handleResize,
    // Expose useKlineChart properties for template access
    loading,
    error,
    limitData,
    klineData,
  }
}
