/**
 * Composables Unit Tests
 *
 * Tests for Vue 3 composables (useMarket, useStrategy, useTrading)
 */

import { describe, it, expect } from 'vitest';
import { useMarket } from '@/composables/useMarket';
import { useStrategy } from '@/composables/useStrategy';

describe('useMarket Composable', () => {
  it('should be defined', () => {
    expect(useMarket).toBeDefined();
  });

  it('should return market overview state', () => {
    const { marketOverview, loading, error } = useMarket({ autoFetch: false });

    expect(marketOverview.value).toBeNull();
    expect(loading.value).toBe(false);
    expect(error.value).toBeNull();
  });

  it('should return fund flow data state', () => {
    const { fundFlowData } = useMarket({ autoFetch: false });

    expect(fundFlowData.value).toEqual([]);
  });

  it('should return kline data state', () => {
    const { klineData } = useMarket({ autoFetch: false });

    expect(klineData.value).toBeNull();
  });

  it('should provide fetch methods', () => {
    const { fetchMarketOverview, fetchFundFlow, fetchKLineData } = useMarket({ autoFetch: false });

    expect(fetchMarketOverview).toBeInstanceOf(Function);
    expect(fetchFundFlow).toBeInstanceOf(Function);
    expect(fetchKLineData).toBeInstanceOf(Function);
  });

  it('should provide cache management methods', () => {
    const { clearCache, getCacheStats } = useMarket({ autoFetch: false });

    expect(clearCache).toBeInstanceOf(Function);
    expect(getCacheStats).toBeInstanceOf(Function);
  });
});

describe('useStrategy Composable', () => {
  it('should be defined', () => {
    expect(useStrategy).toBeDefined();
  });

  it('should return strategies state', () => {
    const { strategies, loading, error } = useStrategy(false);

    expect(strategies.value).toEqual([]);
    expect(loading.value).toBe(false);
    expect(error.value).toBeNull();
  });

  it('should provide CRUD methods', () => {
    const {
      fetchStrategies,
      getStrategyById,
      createStrategy,
      updateStrategy,
      deleteStrategy
    } = useStrategy(false);

    expect(fetchStrategies).toBeInstanceOf(Function);
    expect(getStrategyById).toBeInstanceOf(Function);
    expect(createStrategy).toBeInstanceOf(Function);
    expect(updateStrategy).toBeInstanceOf(Function);
    expect(deleteStrategy).toBeInstanceOf(Function);
  });

  it('should provide lifecycle methods', () => {
    const {
      startStrategy,
      stopStrategy,
      pauseStrategy,
      resumeStrategy
    } = useStrategy(false);

    expect(startStrategy).toBeInstanceOf(Function);
    expect(stopStrategy).toBeInstanceOf(Function);
    expect(pauseStrategy).toBeInstanceOf(Function);
    expect(resumeStrategy).toBeInstanceOf(Function);
  });
});

describe('Composable Export Structure', () => {
  it('should export useMarket as default', async () => {
    const module = await import('@/composables/useMarket');
    expect(module.default).toBeDefined();
    expect(module.useMarket).toBeDefined();
  });

  it('should export useStrategy as default', async () => {
    const module = await import('@/composables/useStrategy');
    expect(module.default).toBeDefined();
    expect(module.useStrategy).toBeDefined();
  });

  it('should export useTrading as default', async () => {
    const module = await import('@/composables/useTrading');
    expect(module.default).toBeDefined();
    expect(module.useTrading).toBeDefined();
    expect(module.usePositions).toBeDefined();
  });
});
