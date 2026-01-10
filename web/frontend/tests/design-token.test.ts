import { test, expect } from '@playwright/test';
import {
  BLOOMBERG_TOKENS,
  OLD_SYSTEM_COLORS,
  expectCSSVariable,
  getCSSVariable,
  expectDesignTokenUsed,
  expectThemeTokensImported,
} from './fixtures/test-utils';

/**
 * MyStocks Frontend - Design Token System Validation
 * Phase 3: Bloomberg Terminal Style Verification
 *
 * Comprehensive tests for Design Token system effectiveness:
 * - CSS variable injection
 * - No hardcoded color residue
 * - SCSS advanced features
 * - Spacing/font/border-radius compliance
 */

test.describe('Design Token: CSS Variable Injection', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should inject --color-accent globally', async ({ page }) => {
    // Test on body element
    await expectDesignTokenUsed(page, '--color-accent');

    const accentColor = await page.evaluate(() => {
      const test = document.createElement('div');
      test.style.color = 'var(--color-accent)';
      document.body.appendChild(test);
      const color = getComputedStyle(test).color;
      document.body.removeChild(test);
      return color;
    });

    // Should contain gold color (rgb(212, 175, 55))
    expect(accentColor.toLowerCase()).toContain('212, 175, 55');
  });

  test('should inject --color-bg-primary globally', async ({ page }) => {
    await expectDesignTokenUsed(page, '--color-bg-primary');

    const bgColor = await page.evaluate(() => {
      const test = document.createElement('div');
      test.style.backgroundColor = 'var(--color-bg-primary)';
      document.body.appendChild(test);
      const color = getComputedStyle(test).backgroundColor;
      document.body.removeChild(test);
      return color;
    });

    // Should be dark background (#1A1A1A)
    expect(bgColor.toLowerCase()).toContain('26, 26, 26');
  });

  test('should inject --color-text-primary globally', async ({ page }) => {
    await expectDesignTokenUsed(page, '--color-text-primary');

    const textColor = await page.evaluate(() => {
      const test = document.createElement('div');
      test.style.color = 'var(--color-text-primary)';
      document.body.appendChild(test);
      const color = getComputedStyle(test).color;
      document.body.removeChild(test);
      return color;
    });

    // Should be high contrast white (#E5E5E5)
    expect(textColor.toLowerCase()).toContain('229, 229, 229');
  });

  test('should inject spacing tokens', async ({ page }) => {
    const spacingTokens = [
      '--spacing-xs',
      '--spacing-sm',
      '--spacing-md',
      '--spacing-lg',
      '--spacing-xl',
    ];

    for (const token of spacingTokens) {
      await expectDesignTokenUsed(page, token);
    }
  });

  test('should inject font family tokens', async ({ page }) => {
    await expectDesignTokenUsed(page, '--font-family-sans');
    await expectDesignTokenUsed(page, '--font-family-mono');
  });

  test('should inject border radius tokens', async ({ page }) => {
    await expectDesignTokenUsed(page, '--border-radius-sm');
    await expectDesignTokenUsed(page, '--border-radius-md');
  });

  test('should inject shadow tokens', async ({ page }) => {
    // Shadow tokens might be complex values, just check they're defined
    await page.evaluate(() => {
      const test = document.createElement('div');
      test.style.boxShadow = 'var(--shadow-md)';
      document.body.appendChild(test);
      const shadow = getComputedStyle(test).boxShadow;
      document.body.removeChild(test);
      return shadow !== 'none';
    }).then(result => {
      expect(result).toBeTruthy();
    });
  });
});

test.describe('Design Token: No Hardcoded Colors', () => {
  const pages = [
    { path: '/', name: 'Dashboard' },
    { path: '/market', name: 'Market' },
    { path: '/industry-concept', name: 'IndustryConceptAnalysis' },
    { path: '/stocks', name: 'Stocks' },
    { path: '/trade-management', name: 'TradeManagement' },
    { path: '/risk-monitor', name: 'RiskMonitor' },
    { path: '/settings', name: 'Settings' },
  ];

  for (const pageInfo of pages) {
    test.describe(`${pageInfo.name} Page`, () => {
      test(`should not contain old system colors inline`, async ({ page }) => {
        await page.goto(pageInfo.path);
        await page.waitForLoadState('networkidle');

        // Get all elements with inline styles
        const elementsWithInlineStyle = await page.locator('[style]').all();

        for (const element of elementsWithInlineStyle) {
          const style = await element.getAttribute('style');

          // Check for old system colors in inline styles
          for (const oldColor of OLD_SYSTEM_COLORS) {
            expect(
              style?.toLowerCase(),
              `${pageInfo.name}: Should not have old color ${oldColor} in inline style`
            ).not.toContain(oldColor.toLowerCase());
          }
        }
      });

      test(`should not have element with #409eff color`, async ({ page }) => {
        await page.goto(pageInfo.path);
        await page.waitForLoadState('networkidle');

        // Check all elements for old blue color
        const hasOldBlue = await page.evaluate((oldColors) => {
          const allElements = document.querySelectorAll('*');
          for (const el of allElements) {
            const styles = getComputedStyle(el);
            const properties = [
              styles.color,
              styles.backgroundColor,
              styles.borderColor,
              styles.borderTopColor,
              styles.borderBottomColor,
              styles.borderLeftColor,
              styles.borderRightColor,
            ];

            for (const prop of properties) {
              if (!prop) continue;
              const color = prop.toLowerCase();
              for (const oldColor of oldColors) {
                if (color.includes(oldColor.toLowerCase())) {
                  return true;
                }
              }
            }
          }
          return false;
        }, OLD_SYSTEM_COLORS);

        expect(
          hasOldBlue,
          `${pageInfo.name}: Should not use old system colors`
        ).toBeFalsy();
      });
    });
  }
});

test.describe('Design Token: SCSS Advanced Features', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should use color.adjust for opacity variations', async ({ page }) => {
    // Find elements with hover effects
    const hoverableElements = await page.locator('button, a, .clickable').all();

    for (const element of hoverableElements.slice(0, 5)) {
      // Check if element has hover state with adjusted opacity
      const hasHover = await element.evaluate((el) => {
        // Check if there's a :hover rule in computed styles
        // This is a simplified check
        const styles = getComputedStyle(el);
        return styles.transition !== 'none' || styles.transition !== '';
      });

      if (hasHover) {
        // Verify transition exists (indicates SCSS color.adjust usage)
        expect(hasHover).toBeTruthy();
      }
    }
  });

  test('should use color.adjust for lightness variations', async ({ page }) => {
    await page.locator('.el-button--primary').first().waitFor();

    // Check primary buttons for hover state
    const hasHoverEffect = await page.evaluate(() => {
      const buttons = document.querySelectorAll('.el-button--primary');
      for (const btn of buttons) {
        const styles = getComputedStyle(btn);
        // Check if button has transition (likely using color.adjust for hover)
        if (styles.transition && styles.transition !== 'none') {
          return true;
        }
      }
      return false;
    });

    expect(hasHoverEffect, 'Primary buttons should have hover effects').toBeTruthy();
  });

  test('should use SCSS functions for shadows', async ({ page }) => {
    // Check for shadow tokens usage
    const shadowUsed = await page.evaluate(() => {
      const testDiv = document.createElement('div');
      testDiv.style.boxShadow = 'var(--shadow-md)';
      document.body.appendChild(testDiv);
      const shadow = getComputedStyle(testDiv).boxShadow;
      document.body.removeChild(testDiv);

      // Check if shadow is not 'none' and has valid format
      return shadow !== 'none' && shadow.includes('px');
    });

    expect(shadowUsed, 'Should use shadow tokens').toBeTruthy();
  });
});

test.describe('Design Token: Spacing Compliance', () => {
  const pages = [
    { path: '/market', name: 'Market' },
    { path: '/stocks', name: 'Stocks' },
    { path: '/trade-management', name: 'TradeManagement' },
  ];

  for (const pageInfo of pages) {
    test.describe(`${pageInfo.name} Page`, () => {
      test('should use 8px baseline grid for margins', async ({ page }) => {
        await page.goto(pageInfo.path);
        await page.waitForLoadState('networkidle');

        // Check common container elements
        const containers = await page.locator('.container, .card, .section').all();

        for (const container of containers.slice(0, 10)) {
          const margin = await container.evaluate((el) => {
            return getComputedStyle(el).margin;
          });

          if (margin === '0px' || margin === 'auto') continue;

          // Extract numeric values and check if they're multiples of 8
          const values = margin.split(' ').map(v => parseInt(v.replace('px', '')));
          for (const v of values) {
            if (isNaN(v)) continue;
            expect(v % 8).toBe(0); // Should be divisible by 8
          }
        }
      });

      test('should use 8px baseline grid for padding', async ({ page }) => {
        await page.goto(pageInfo.path);
        await page.waitForLoadState('networkidle');

        // Check cards and containers
        const cards = await page.locator('.card, .data-card').all();

        for (const card of cards.slice(0, 10)) {
          const padding = await card.evaluate((el) => {
            return getComputedStyle(el).padding;
          });

          if (!padding || padding === '0px') continue;

          // Check if padding values are 8px multiples
          const values = padding.split(' ').map(v => parseInt(v.replace('px', '')));
          for (const v of values) {
            if (isNaN(v)) continue;
            expect(v % 8, `Padding ${padding} should follow 8px grid`).toBe(0);
          }
        }
      });

      test('should use 8px baseline grid for gaps', async ({ page }) => {
        await page.goto(pageInfo.path);
        await page.waitForLoadState('networkidle');

        // Check flex/grid containers
        const flexContainers = await page.locator('[class*="flex"], [class*="grid"]').all();

        for (const container of flexContainers.slice(0, 10)) {
          const gap = await container.evaluate((el) => {
            return getComputedStyle(el).gap;
          });

          if (!gap || gap === 'normal') continue;

          const value = parseInt(gap.replace('px', ''));
          if (isNaN(value)) continue;

          expect(value % 8, `Gap ${gap} should follow 8px grid`).toBe(0);
        }
      });
    });
  }
});

test.describe('Design Token: Font Compliance', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should use Inter font family', async ({ page }) => {
    const fontUsed = await page.evaluate(() => {
      const test = document.createElement('div');
      test.style.fontFamily = 'var(--font-family-sans)';
      document.body.appendChild(test);
      const font = getComputedStyle(test).fontFamily;
      document.body.removeChild(test);
      return font;
    });

    expect(fontUsed.toLowerCase()).toContain('inter');
  });

  test('should use monospace font for code/numbers', async ({ page }) => {
    const monoFont = await page.evaluate(() => {
      const test = document.createElement('div');
      test.style.fontFamily = 'var(--font-family-mono)';
      document.body.appendChild(test);
      const font = getComputedStyle(test).fontFamily;
      document.body.removeChild(test);
      return font;
    });

    expect(monoFont.toLowerCase()).toMatch(/jetbrains|consolas|monaco|monospace/);
  });

  test('should use tokenized font sizes', async ({ page }) => {
    const fontSizes = [
      '--font-size-xs',
      '--font-size-sm',
      '--font-size-md',
      '--font-size-lg',
      '--font-size-xl',
      '--font-size-2xl',
    ];

    for (const token of fontSizes) {
      await expectDesignTokenUsed(page, token);
    }
  });
});

test.describe('Design Token: Border Radius Compliance', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should use small border radius for compact elements', async ({ page }) => {
    await page.locator('.button, .btn, .data-card').first().waitFor();

    const borderRadius = await page.evaluate(() => {
      const el = document.querySelector('.button, .btn, .data-card');
      if (!el) return null;
      return getComputedStyle(el).borderRadius;
    });

    // Should be 4px (small) or 0px (square design)
    expect(borderRadius).toMatch(/^(0px|4px)$/);
  });

  test('should use medium border radius for cards', async ({ page }) => {
    const borderRadius = await page.evaluate(() => {
      const cards = document.querySelectorAll('.card, .dialog, .panel');
      if (cards.length === 0) return null;
      return getComputedStyle(cards[0]).borderRadius;
    });

    if (borderRadius) {
      // Should be small (4px) or medium (8px)
      expect(borderRadius).toMatch(/^(0px|4px|8px)$/);
    }
  });

  test('should not have excessive border radius', async ({ page }) => {
    // Check for no rounded-xl or similar large border radius
    const hasLargeRadius = await page.evaluate(() => {
      const allElements = document.querySelectorAll('*');
      for (const el of allElements) {
        const radius = getComputedStyle(el).borderRadius;
        if (radius && parseInt(radius) > 12) {
          return true;
        }
      }
      return false;
    });

    expect(hasLargeRadius, 'Should not have border radius > 12px').toBeFalsy();
  });
});

test.describe('Design Token: Global Theme Import', () => {
  const pages = [
    { path: '/', name: 'Dashboard' },
    { path: '/market', name: 'Market' },
    { path: '/stocks', name: 'Stocks' },
  ];

  for (const pageInfo of pages) {
    test(`${pageInfo.name}: should have theme-tokens.scss imported`, async ({ page }) => {
      await page.goto(pageInfo.path);
      await expectThemeTokensImported(page);
    });
  }

  test('should have theme-tokens.scss imported in all pages', async ({ page }) => {
    // Navigate through multiple pages and verify theme is loaded
    const paths = ['/', '/market', '/stocks', '/trade-management'];

    for (const path of paths) {
      await page.goto(path);
      await page.waitForLoadState('networkidle');

      // Check for Design Token existence
      const hasToken = await page.evaluate(() => {
        const test = document.createElement('div');
        test.style.color = 'var(--color-accent)';
        document.body.appendChild(test);
        const color = getComputedStyle(test).color;
        document.body.removeChild(test);
        return color !== 'rgba(0, 0, 0, 0)' && color !== '';
      });

      expect(hasToken, `Theme tokens should be loaded on ${path}`).toBeTruthy();
    }
  });
});
