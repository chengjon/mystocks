/**
 * Strategy Module Unit Tests
 *
 * Tests for StrategyAdapter and data transformation logic
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { StrategyAdapter } from '@/api/adapters/strategyAdapter';
import { mockStrategyList, mockStrategyDetail, mockBacktestTask } from '@/mock/strategyMock';
import type { UnifiedResponse } from '@/api/apiClient';

// Mock console methods
global.console = {
  ...global.console,
  warn: vi.fn(),
  error: vi.fn(),
};

describe('StrategyAdapter', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('adaptStrategyList', () => {
    it('should adapt successful API response', () => {
      const apiResponse: UnifiedResponse<any> = {
        success: true,
        code: 200,
        message: 'OK',
        data: mockStrategyList,
        timestamp: '2025-12-25T16:30:00Z',
        request_id: 'test-id',
        errors: null,
      };

      const result = StrategyAdapter.adaptStrategyList(apiResponse);

      expect(result).toHaveLength(4);
      expect(result[0].id).toBe('1');
      expect(result[0].name).toBe('双均线趋势跟踪');
      expect(result[0].type).toBe('trend_following');
      expect(result[0].performance?.totalReturn).toBe(0.256);
    });

    it('should fallback to mock data on API failure', () => {
      const apiResponse: UnifiedResponse<any> = {
        success: false,
        code: 500,
        message: 'Internal Server Error',
        data: null,
        timestamp: '2025-12-25T16:30:00Z',
        request_id: 'test-id',
        errors: null,
      };

      const result = StrategyAdapter.adaptStrategyList(apiResponse);

      expect(result).toHaveLength(4);
      expect(result[0].id).toBe('1');
      expect(console.warn).toHaveBeenCalledWith(
        '[StrategyAdapter] API failed, using mock data:',
        'Internal Server Error'
      );
    });

    it('should handle missing data gracefully', () => {
      const apiResponse: UnifiedResponse<any> = {
        success: true,
        code: 200,
        message: 'OK',
        data: null,
        timestamp: '2025-12-25T16:30:00Z',
        request_id: 'test-id',
        errors: null,
      };

      const result = StrategyAdapter.adaptStrategyList(apiResponse);

      expect(result).toHaveLength(4); // Falls back to mock
    });
  });

  describe('adaptStrategyDetail', () => {
    it('should adapt single strategy from API response', () => {
      const apiResponse: UnifiedResponse<any> = {
        success: true,
        code: 200,
        message: 'OK',
        data: mockStrategyDetail,
        timestamp: '2025-12-25T16:30:00Z',
        request_id: 'test-id',
        errors: null,
      };

      const result = StrategyAdapter.adaptStrategyDetail(apiResponse);

      expect(result.id).toBe('1');
      expect(result.name).toBe('双均线趋势跟踪');
      expect(result.performance).toBeDefined();
      expect(result.performance?.totalReturn).toBe(0.256);
    });

    it('should fallback to mock on error', () => {
      const apiResponse: UnifiedResponse<any> = {
        success: false,
        code: 404,
        message: 'Not Found',
        data: null,
        timestamp: '2025-12-25T16:30:00Z',
        request_id: 'test-id',
        errors: null,
      };

      const result = StrategyAdapter.adaptStrategyDetail(apiResponse);

      expect(result.id).toBe('1');
      expect(console.warn).toHaveBeenCalledWith(
        '[StrategyAdapter] Strategy detail API failed, using mock:',
        'Not Found'
      );
    });
  });

  describe('adaptPerformance', () => {
    it('should adapt performance metrics correctly', () => {
      const apiPerf = {
        total_return: 0.256,
        annual_return: 0.312,
        sharpe_ratio: 1.85,
        max_drawdown: -0.124,
        win_rate: 0.68,
        profit_loss_ratio: 2.15,
      };

      const result = StrategyAdapter.adaptPerformance(apiPerf);

      expect(result.totalReturn).toBe(0.256);
      expect(result.annualReturn).toBe(0.312);
      expect(result.sharpeRatio).toBe(1.85);
      expect(result.maxDrawdown).toBe(-0.124);
      expect(result.winRate).toBe(0.68);
      expect(result.profitLossRatio).toBe(2.15);
    });

    it('should handle camelCase and snake_case variants', () => {
      const apiPerf = {
        totalReturn: 0.3,
        annualReturn: 0.4,
        sharpeRatio: 2.0,
        maxDrawdown: -0.1,
        winRate: 0.75,
        profitLossRatio: 2.5,
      };

      const result = StrategyAdapter.adaptPerformance(apiPerf);

      expect(result.totalReturn).toBe(0.3);
      expect(result.sharpeRatio).toBe(2.0);
    });
  });

  describe('adaptBacktestTask', () => {
    it('should adapt backtest task successfully', () => {
      const apiResponse: UnifiedResponse<any> = {
        success: true,
        code: 200,
        message: 'OK',
        data: mockBacktestTask,
        timestamp: '2025-12-25T16:30:00Z',
        request_id: 'test-id',
        errors: null,
      };

      const result = StrategyAdapter.adaptBacktestTask(apiResponse);

      expect(result).not.toBeNull();
      expect(result?.taskId).toBe('bt_20250125_001');
      expect(result?.strategyId).toBe('1');
      expect(result?.status).toBe('completed');
    });

    it('should return null on API failure', () => {
      const apiResponse: UnifiedResponse<any> = {
        success: false,
        code: 500,
        message: 'Internal Server Error',
        data: null,
        timestamp: '2025-12-25T16:30:00Z',
        request_id: 'test-id',
        errors: null,
      };

      const result = StrategyAdapter.adaptBacktestTask(apiResponse);

      expect(result).toBeNull();
    });
  });

  describe('validateStrategy', () => {
    it('should validate valid strategy', () => {
      const validStrategy = {
        id: '1',
        name: 'Test Strategy',
        description: 'Test',
        type: 'trend_following' as const,
        status: 'active' as const,
        createdAt: new Date(),
        updatedAt: new Date(),
        parameters: {},
      };

      const result = StrategyAdapter.validateStrategy(validStrategy);
      expect(result).toBe(true);
    });

    it('should reject strategy without id', () => {
      const invalidStrategy = {
        id: '',
        name: 'Test',
        description: 'Test',
        type: 'trend_following' as const,
        status: 'active' as const,
        createdAt: new Date(),
        updatedAt: new Date(),
        parameters: {},
      };

      const result = StrategyAdapter.validateStrategy(invalidStrategy);
      expect(result).toBe(false);
    });

    it('should reject strategy with invalid type', () => {
      const invalidStrategy = {
        id: '1',
        name: 'Test',
        description: 'Test',
        type: 'invalid_type' as any,
        status: 'active' as const,
        createdAt: new Date(),
        updatedAt: new Date(),
        parameters: {},
      };

      const result = StrategyAdapter.validateStrategy(invalidStrategy);
      expect(result).toBe(false);
    });
  });

  describe('validateBacktestParams', () => {
    it('should validate valid backtest params', () => {
      const validParams = {
        startDate: '2025-01-01',
        endDate: '2025-01-31',
        initialCapital: 100000,
      };

      const result = StrategyAdapter.validateBacktestParams(validParams);
      expect(result).toBe(true);
    });

    it('should reject params without dates', () => {
      const invalidParams = {
        startDate: '',
        endDate: '',
        initialCapital: 100000,
      };

      const result = StrategyAdapter.validateBacktestParams(invalidParams);
      expect(result).toBe(false);
    });

    it('should reject params with invalid capital', () => {
      const invalidParams = {
        startDate: '2025-01-01',
        endDate: '2025-01-31',
        initialCapital: -1000,
      };

      const result = StrategyAdapter.validateBacktestParams(invalidParams);
      expect(result).toBe(false);
    });
  });
});
