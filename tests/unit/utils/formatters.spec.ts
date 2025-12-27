// tests/unit/utils/formatters.spec.ts
import { describe, it, expect } from 'vitest';

// Example utility function to test (normally this would be imported from your src)
const formatCurrency = (value: number, currency = 'CNY') => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: currency,
  }).format(value);
};

const formatPercent = (value: number) => {
  return `${(value * 100).toFixed(2)}%`;
};

describe('Utility Formatters', () => {
  describe('formatCurrency', () => {
    it('should format CNY correctly', () => {
      expect(formatCurrency(1000)).toContain('¥1,000.00');
    });

    it('should handle zero', () => {
      expect(formatCurrency(0)).toContain('¥0.00');
    });

    it('should support USD', () => {
      const result = formatCurrency(1000, 'USD');
      // output might vary slightly by locale environment (US$ or $)
      expect(result).toMatch(/(\$|US\$)/);
      expect(result).toContain('1,000.00');
    });
  });

  describe('formatPercent', () => {
    it('should format decimals as percentage', () => {
      expect(formatPercent(0.1234)).toBe('12.34%');
    });

    it('should handle negative numbers', () => {
      expect(formatPercent(-0.05)).toBe('-5.00%');
    });
  });
});
