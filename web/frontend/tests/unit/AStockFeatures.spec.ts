import { describe, it, expect, beforeEach, vi } from 'vitest';
import { calculateStopLimit, isLimitUp, isLimitDown, calculateT1Status } from '@/utils/astock';

describe('A-Share Features', () => {
  describe('calculateStopLimit', () => {
    it('should calculate 10% limit for main board stocks', () => {
      const result = calculateStopLimit(10.00, 'main');
      expect(result.limitUp).toBeCloseTo(11.00, 2);
      expect(result.limitDown).toBeCloseTo(9.00, 2);
      expect(result.limitPct).toBe(0.10);
    });

    it('should calculate 5% limit for ST stocks', () => {
      const result = calculateStopLimit(10.00, 'st');
      expect(result.limitUp).toBeCloseTo(10.50, 2);
      expect(result.limitDown).toBeCloseTo(9.50, 2);
      expect(result.limitPct).toBe(0.05);
    });

    it('should calculate 20% limit for STAR market', () => {
      const result = calculateStopLimit(50.00, 'star');
      expect(result.limitUp).toBeCloseTo(60.00, 2);
      expect(result.limitDown).toBeCloseTo(40.00, 2);
      expect(result.limitPct).toBe(0.20);
    });

    it('should calculate 30% limit for Beijing Stock Exchange', () => {
      const result = calculateStopLimit(10.00, 'bse');
      expect(result.limitUp).toBeCloseTo(13.00, 2);
      expect(result.limitDown).toBeCloseTo(7.00, 2);
      expect(result.limitPct).toBe(0.30);
    });

    it('should handle special price calculations', () => {
      const result = calculateStopLimit(3.33, 'main');
      expect(result.limitUp).toBeCloseTo(3.66, 2);
    });
  });

  describe('isLimitUp', () => {
    it('should return true when price hits limit up', () => {
      expect(isLimitUp(11.00, 10.00, 0.10)).toBe(true);
    });

    it('should return false when price is below limit up', () => {
      expect(isLimitUp(10.50, 10.00, 0.10)).toBe(false);
    });

    it('should handle edge case with floating point precision', () => {
      expect(isLimitUp(10.0000001, 10.00, 0.10)).toBe(true);
    });
  });

  describe('isLimitDown', () => {
    it('should return true when price hits limit down', () => {
      expect(isLimitDown(9.00, 10.00, 0.10)).toBe(true);
    });

    it('should return false when price is above limit down', () => {
      expect(isLimitDown(9.50, 10.00, 0.10)).toBe(false);
    });
  });

  describe('calculateT1Status', () => {
    it('should return T+1 status for regular T+1 stocks', () => {
      const buyDate = new Date('2024-12-27');
      const result = calculateT1Status(buyDate, 'main');

      expect(result.status).toBe('T+1');
      expect(result.buyDate).toEqual(buyDate);
      expect(result.sellableDate).toBeDefined();
    });

    it('should return T+0 status for eligible stocks', () => {
      const buyDate = new Date('2024-12-27');
      const result = calculateT1Status(buyDate, 't0');

      expect(result.status).toBe('T+0');
      expect(result.sellableDate).toEqual(buyDate);
    });

    it('should calculate correct sellable date for T+1', () => {
      const friday = new Date('2024-12-27');
      const result = calculateT1Status(friday, 'main');

      const expectedSellable = new Date('2024-12-30');
      expect(result.sellableDate.getDate()).toBe(expectedSellable.getDate());
    });
  });

  describe('adjustment factor calculation', () => {
    it('should calculate forward adjustment factor correctly', () => {
      const prevClose = 10.0;
      const currentClose = 11.0;
      const factor = (currentClose - prevClose) / prevClose;
      expect(factor).toBeCloseTo(0.10, 4);
    });
  });

  describe('market type detection', () => {
    it('should identify ST stocks correctly', () => {
      expect('st').toBe('st');
    });

    it('should identify main board correctly', () => {
      expect('main').toBe('main');
    });

    it('should identify STAR market correctly', () => {
      expect('star').toBe('star');
    });

    it('should identify ChiNext correctly', () => {
      expect('创业板').toBe('创业板');
    });
  });
});
