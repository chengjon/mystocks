/**
 * Composables Unit Tests
 *
 * Tests for Vue 3 composables (useMarket, useStrategy, useTrading)
 */

import { mount } from '@vue/test-utils';
import { defineComponent } from 'vue';
import { describe, it, expect, vi } from 'vitest';
import { useMarket } from '@/composables/useMarket';
import { useStrategy } from '@/composables/useStrategy';

function mountUseMarketHarness() {
  return mount(defineComponent({
    setup() {
      return useMarket({ autoFetch: false });
    },
    template: '<div />',
  }));
}

describe('useMarket Composable', () => {
  it('should be defined', () => {
    expect(useMarket).toBeDefined();
  });

  it('should return market overview state', () => {
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const wrapper = mountUseMarketHarness()
    const vm = wrapper.vm as unknown as {
      marketOverview: unknown
      loading: boolean
      error: string | null
    }

    expect(vm.marketOverview).toBeNull();
    expect(vm.loading).toBe(false);
    expect(vm.error).toBeNull();
    expect(warnSpy).not.toHaveBeenCalled()
    expect(errorSpy).not.toHaveBeenCalled()
    wrapper.unmount()
    warnSpy.mockRestore()
    errorSpy.mockRestore()
  });

  it('should return fund flow data state', () => {
    const wrapper = mountUseMarketHarness()
    const vm = wrapper.vm as unknown as {
      fundFlowData: unknown[]
    }

    expect(vm.fundFlowData).toEqual([]);
    wrapper.unmount()
  });

  it('should return kline data state', () => {
    const wrapper = mountUseMarketHarness()
    const vm = wrapper.vm as unknown as {
      klineData: unknown
    }

    expect(vm.klineData).toBeNull();
    wrapper.unmount()
  });

  it('should provide fetch methods', () => {
    const wrapper = mountUseMarketHarness()
    const { fetchMarketOverview, fetchFundFlow, fetchKLineData } = wrapper.vm as unknown as ReturnType<typeof useMarket>

    expect(fetchMarketOverview).toBeInstanceOf(Function);
    expect(fetchFundFlow).toBeInstanceOf(Function);
    expect(fetchKLineData).toBeInstanceOf(Function);
    wrapper.unmount()
  });

  it('should provide cache management methods', () => {
    const wrapper = mountUseMarketHarness()
    const { clearCache, getCacheStats } = wrapper.vm as unknown as ReturnType<typeof useMarket>

    expect(clearCache).toBeInstanceOf(Function);
    expect(getCacheStats).toBeInstanceOf(Function);
    wrapper.unmount()
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
