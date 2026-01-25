export interface VisualThreshold {
  maxDiffPixels: number;
  maxDiffPercentage: number;
  threshold: number;
}

export interface ComponentThreshold extends VisualThreshold {
  componentName: string;
  priority: 'P0' | 'P1' | 'P2';
}

export const CHART_THRESHOLDS: ComponentThreshold[] = [
  {
    componentName: 'Dashboard-KLineChart',
    priority: 'P0',
    maxDiffPixels: 50,
    maxDiffPercentage: 0.01,
    threshold: 0.2
  },
  {
    componentName: 'Dashboard-MACrossPanel',
    priority: 'P0',
    maxDiffPixels: 50,
    maxDiffPercentage: 0.01,
    threshold: 0.2
  },
  {
    componentName: 'Dashboard-RSIChart',
    priority: 'P0',
    maxDiffPixels: 50,
    maxDiffPercentage: 0.01,
    threshold: 0.2
  },
  {
    componentName: 'Dashboard-VolumeChart',
    priority: 'P0',
    maxDiffPixels: 50,
    maxDiffPercentage: 0.01,
    threshold: 0.2
  },
  {
    componentName: 'TechnicalAnalysis-MainChart',
    priority: 'P0',
    maxDiffPixels: 50,
    maxDiffPercentage: 0.01,
    threshold: 0.2
  },
  {
    componentName: 'TechnicalAnalysis-IndicatorPanel',
    priority: 'P0',
    maxDiffPixels: 50,
    maxDiffPercentage: 0.01,
    threshold: 0.2
  },
  {
    componentName: 'Backtest-EquityCurve',
    priority: 'P1',
    maxDiffPixels: 100,
    maxDiffPercentage: 0.02,
    threshold: 0.25
  },
  {
    componentName: 'Backtest-DrawdownChart',
    priority: 'P1',
    maxDiffPixels: 100,
    maxDiffPercentage: 0.02,
    threshold: 0.25
  },
  {
    componentName: 'Backtest-ReturnDistribution',
    priority: 'P1',
    maxDiffPixels: 100,
    maxDiffPercentage: 0.02,
    threshold: 0.25
  },
  {
    componentName: 'Backtest-TradesChart',
    priority: 'P1',
    maxDiffPixels: 100,
    maxDiffPercentage: 0.02,
    threshold: 0.25
  },
  {
    componentName: 'Strategy-RSIIndicator',
    priority: 'P2',
    maxDiffPixels: 150,
    maxDiffPercentage: 0.03,
    threshold: 0.3
  },
  {
    componentName: 'Strategy-MACDIndicator',
    priority: 'P2',
    maxDiffPixels: 150,
    maxDiffPercentage: 0.03,
    threshold: 0.3
  }
];

export function getThreshold(componentName: string): VisualThreshold {
  const threshold = CHART_THRESHOLDS.find(t => t.componentName === componentName);
  if (threshold) {
    return {
      maxDiffPixels: threshold.maxDiffPixels,
      maxDiffPercentage: threshold.maxDiffPercentage,
      threshold: threshold.threshold
    };
  }
  return {
    maxDiffPixels: 100,
    maxDiffPercentage: 0.02,
    threshold: 0.25
  };
}

export const ARTDECO_GOLD_PRIMARY = '#D4AF37';
export const ARTDECO_GOLD_LIGHT = '#F0E68C';
export const ARTDECO_BRONZE = '#CD7F32';
export const ARTDECO_CHAMPAGNE = '#F7E7CE';

export const MARKET_UP = '#FF5252';
export const MARKET_DOWN = '#00E676';
export const MARKET_FLAT = '#888888';
