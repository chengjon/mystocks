import { test, expect } from '@playwright/test';

/**
 * MyStocks Frontend - China Stock Market Color Adaptation Tests
 * Phase 3: ArtDeco Style Verification
 *
 * Tests for verifying China A-Share stock color conventions:
 * - Red for up (上涨 - 红涨)
 * - Green for down (下跌 - 绿跌)
 * - Proper application in stock displays and charts
 */

const STOCK_RED_RGB_PATTERNS = ['255, 71, 87', '235, 68, 54', '220, 38, 38', '239, 68, 68'];
const STOCK_GREEN_RGB_PATTERNS = ['0, 217, 36', '16, 185, 129', '34, 197, 94', '76, 175, 80'];

const hasAnyRgbPattern = (color: string, patterns: string[]) => {
  const normalized = color.toLowerCase();
  return patterns.some(pattern => normalized.includes(pattern));
};

const isStockUpColor = (color: string) => hasAnyRgbPattern(color, STOCK_RED_RGB_PATTERNS);
const isStockDownColor = (color: string) => hasAnyRgbPattern(color, STOCK_GREEN_RGB_PATTERNS);
const isAnyStockColor = (color: string) => isStockUpColor(color) || isStockDownColor(color);

test.describe('China Stock Colors: Token Definitions', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should define --color-stock-up as red', async ({ page }) => {
    const stockUpColor = await page.evaluate(() => {
      const test = document.createElement('div');
      test.style.color = 'var(--color-stock-up)';
      document.body.appendChild(test);
      const color = getComputedStyle(test).color;
      document.body.removeChild(test);
      return color;
    });

    // Should be RED for up (红涨)
    const isRed = hasAnyRgbPattern(stockUpColor, STOCK_RED_RGB_PATTERNS);

    expect(isRed, `stock-up should be red for China market, got ${stockUpColor}`).toBeTruthy();
  });

  test('should define --color-stock-down as green', async ({ page }) => {
    const stockDownColor = await page.evaluate(() => {
      const test = document.createElement('div');
      test.style.color = 'var(--color-stock-down)';
      document.body.appendChild(test);
      const color = getComputedStyle(test).color;
      document.body.removeChild(test);
      return color;
    });

    // Should be GREEN for down (绿跌) - #00d924 or similar green
    const isGreen = isStockDownColor(stockDownColor);

    expect(isGreen, `stock-down should be green for China market, got ${stockDownColor}`).toBeTruthy();
  });
});

test.describe('China Stock Colors: Stocks Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/stocks');
    await page.waitForLoadState('networkidle');
  });

  test('should display positive changes in red', async ({ page }) => {
    // Find elements with positive change class
    const positiveElements = await page.locator('.positive, [class*="up"], [class*="rise"]').all();

    for (const el of positiveElements.slice(0, 5)) {
      const color = await el.evaluate((element: Element) => {
        return getComputedStyle(element).color;
      });

      // Should be red (RGB: 235, 68, 54 or similar)
      const isRed = isStockUpColor(color);

      expect(isRed, `Positive change should be red, got ${color}`).toBeTruthy();
    }
  });

  test('should display negative changes in green', async ({ page }) => {
    // Find elements with negative change class
    const negativeElements = await page.locator('.negative, [class*="down"], [class*="fall"]').all();

    for (const el of negativeElements.slice(0, 5)) {
      const color = await el.evaluate((element: Element) => {
        return getComputedStyle(element).color;
      });

      // Should be green (RGB: 16, 185, 129 or similar)
      const isGreen = isStockDownColor(color);

      expect(isGreen, `Negative change should be green, got ${color}`).toBeTruthy();
    }
  });

  test('should apply stock colors to percentage changes', async ({ page }) => {
    // Find percentage change elements
    const percentElements = await page.locator('[class*="change"], [class*="pct"]').all();

    for (const el of percentElements.slice(0, 5)) {
      const text = await el.textContent();
      if (!text || text === '--') continue;

      // Check if color matches the sign
      const color = await el.evaluate((element: Element) => {
        return getComputedStyle(element).color;
      });

      const hasSign = (text.includes('+') || text.match(/\d/));

      if (hasSign) {
        // Should have stock color (either red or green)
        const hasColor = isAnyStockColor(color);

        expect(hasColor, `Percentage change should have stock color, got ${color}`).toBeTruthy();
      }
    }
  });
});

test.describe('China Stock Colors: Market Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/market');
    await page.waitForLoadState('networkidle');
  });

  test('should use red for stock price increases', async ({ page }) => {
    const priceElements = await page.locator('.price, .stock-price').all();

    for (const el of priceElements.slice(0, 5)) {
      const text = await el.textContent();

      // If price has upward indicator or is in positive context
      if (text && (text.includes('↑') || text.includes('+'))) {
        const color = await el.evaluate((element: Element) => {
          return getComputedStyle(element).color;
        });

        // Should be red for up
        const isRed = isStockUpColor(color);
        expect(isRed, `Upward price should be red, got ${color}`).toBeTruthy();
      }
    }
  });

  test('should use green for stock price decreases', async ({ page }) => {
    const priceElements = await page.locator('.price, .stock-price').all();

    for (const el of priceElements.slice(0, 5)) {
      const text = await el.textContent();

      // If price has downward indicator or is in negative context
      if (text && (text.includes('↓') || text.includes('-'))) {
        const color = await el.evaluate((element: Element) => {
          return getComputedStyle(element).color;
        });

        // Should be green for down
        const isGreen = isStockDownColor(color);
        expect(isGreen, `Downward price should be green, got ${color}`).toBeTruthy();
      }
    }
  });
});

test.describe('China Stock Colors: Trade Management Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/trade-management');
    await page.waitForLoadState('networkidle');
  });

  test('should apply stock colors to profit/loss display', async ({ page }) => {
    // Find profit/loss elements
    const pnlElements = await page.locator('[class*="profit"], [class*="loss"], [class*="pnl"]').all();

    for (const el of pnlElements.slice(0, 5)) {
      const color = await el.evaluate((element: Element) => {
        return getComputedStyle(element).color;
      });

      // Should be either red (profit) or green (loss)
      const isStockColor = isAnyStockColor(color);

      expect(isStockColor, `Profit/Loss should use stock color, got ${color}`).toBeTruthy();
    }
  });

  test('should display portfolio summary with correct colors', async ({ page }) => {
    const portfolioCards = await page.locator('.portfolio-overview, .account-summary').all();

    for (const card of portfolioCards) {
      const hasStockColors = await card.evaluate((element: Element) => {
        const hasAnyPattern = (value: string, patterns: string[]) =>
          patterns.some((pattern) => value.includes(pattern));

        const allElements = element.querySelectorAll('*');
        let hasRed = false;
        let hasGreen = false;

        for (const el of allElements) {
          const color = getComputedStyle(el).color.toLowerCase();
          if (hasAnyPattern(color, STOCK_RED_RGB_PATTERNS)) hasRed = true;
          if (hasAnyPattern(color, STOCK_GREEN_RGB_PATTERNS)) hasGreen = true;
        }

        return hasRed && hasGreen;
      });

      expect(hasStockColors, 'Portfolio overview should use both red and green').toBeTruthy();
    }
  });
});

test.describe('China Stock Colors: Dashboard Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should display watchlist with stock colors', async ({ page }) => {
    const watchlistItems = await page.locator('.watchlist-item, .stock-item').all();

    for (const item of watchlistItems.slice(0, 3)) {
      const hasStockColor = await item.evaluate((element: Element) => {
        const allElements = element.querySelectorAll('*');
        for (const el of allElements) {
          const color = getComputedStyle(el).color;
          if (isAnyStockColor(color)) {
            return true;
          }
        }
        return false;
      });

      expect(hasStockColor, 'Watchlist items should use stock colors').toBeTruthy();
    }
  });

  test('should apply colors to market indices', async ({ page }) => {
    const indexElements = await page.locator('.market-index, .index-value').all();

    for (const el of indexElements.slice(0, 3)) {
      const color = await el.evaluate((element: Element) => {
        return getComputedStyle(element).color;
      });

      // Should have stock color (red or green)
      const hasColor = isAnyStockColor(color);

      expect(hasColor, 'Market indices should use stock colors').toBeTruthy();
    }
  });
});

test.describe('China Stock Colors: Color Consistency', () => {
  const pages = [
    { path: '/stocks', name: 'Stocks' },
    { path: '/market', name: 'Market' },
    { path: '/trade-management', name: 'TradeManagement' },
    { path: '/', name: 'Dashboard' },
  ];

  for (const pageInfo of pages) {
    test.describe(`${pageInfo.name} Page`, () => {
      test('should consistently use red for up', async ({ page }) => {
        await page.goto(pageInfo.path);
        await page.waitForLoadState('networkidle');

        const redElementsCount = await page.evaluate(() => {
          const allElements = Array.from(document.querySelectorAll('*'));
          return allElements.filter((element: Element) =>
            isStockUpColor(getComputedStyle(element).color)
          ).length;
        });

        // Should have at least some red elements for positive values
        expect(redElementsCount).toBeGreaterThan(0);
      });

      test('should consistently use green for down', async ({ page }) => {
        await page.goto(pageInfo.path);
        await page.waitForLoadState('networkidle');

        const greenElementsCount = await page.evaluate(() => {
          const allElements = Array.from(document.querySelectorAll('*'));
          return allElements.filter((element: Element) =>
            isStockDownColor(getComputedStyle(element).color)
          ).length;
        });

        // Should have at least some green elements for negative values
        expect(greenElementsCount).toBeGreaterThan(0);
      });
    });
  }
});

test.describe('China Stock Colors: Visual Clarity', () => {
  test('should have high contrast for stock colors', async ({ page }) => {
    await page.goto('/stocks');

    // Test red (up) contrast
    const redElement = page.locator('.positive').first();
    if (await redElement.count() > 0) {
      const redColor = await redElement.evaluate((el: Element) => getComputedStyle(el).color);
      const bgColor = await redElement.evaluate((el: Element) => {
        const parent = el.parentElement || document.body;
        return getComputedStyle(parent).backgroundColor;
      });

      // Convert to hex for contrast calculation
      const rgbToHex = (rgb: string) => {
        const match = rgb.match(/\d+/g);
        if (!match || match.length < 3) return '#000000';
        const [r, g, b] = match.map(Number);
        return '#' + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
      };

      const getContrastRatio = (fg: string, bg: string) => {
        const parse = (color: string) => {
          const hex = color.replace('#', '');
          return {
            r: parseInt(hex.substring(0, 2), 16),
            g: parseInt(hex.substring(2, 4), 16),
            b: parseInt(hex.substring(4, 6), 16),
          };
        };

        const fgRgb = parse(rgbToHex(fg));
        const bgRgb = parse(rgbToHex(bg));

        const lum = (c: { r: number; g: number; b: number }) => {
          const [r, g, b] = [c.r / 255, c.g / 255, c.b / 255].map((v) =>
            v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)
          );
          return 0.2126 * r + 0.7152 * g + 0.0722 * b;
        };

        const lum1 = lum(fgRgb);
        const lum2 = lum(bgRgb);
        return (Math.max(lum1, lum2) + 0.05) / (Math.min(lum1, lum2) + 0.05);
      };

      const ratio = getContrastRatio(redColor, bgColor);
      expect(ratio, `Red stock color should have sufficient contrast (ratio: ${ratio.toFixed(2)}:1)`).toBeGreaterThanOrEqual(3);
    }
  });

  test('should not use Western stock colors (green for up, red for down)', async ({ page }) => {
    await page.goto('/stocks');

    // Check for Western-style color usage (should NOT exist)
    const westernPattern = await page.evaluate(() => {
      const allElements = document.querySelectorAll('*');
      for (const el of allElements) {
        const text = el.textContent?.trim() || '';
        const color = getComputedStyle(el).color.toLowerCase();

        // Check if positive text has green color (Western style - WRONG)
        if (text.includes('+') || text.includes('↑') || text.includes('涨')) {
          if (isStockDownColor(color)) {
            return true; // Found Western style
          }
        }
      }
      return false;
    });

    expect(westernPattern, 'Should not use Western stock colors (green for up)').toBeFalsy();
  });
});
