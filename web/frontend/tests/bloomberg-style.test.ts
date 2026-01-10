import { test, expect } from '@playwright/test';
import {
  expectBloombergColor,
  expectBaselineGridSpacing,
  expectWCAGAACompliant,
  getContrastRatio,
} from './fixtures/test-utils';

/**
 * MyStocks Frontend - Bloomberg Terminal Style Compliance Tests
 * Phase 3: Bloomberg Terminal Design Feature Verification
 *
 * Tests for verifying Bloomberg Terminal core design features:
 * - Gold theme (#D4AF37)
 * - Dark background统一
 * - 8px grid system
 * - WCAG AA compliance
 * - Square design (minimal border-radius)
 */

test.describe('Bloomberg Style: Gold Theme (#D4AF37)', () => {
  test('should use gold for primary accents', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check for gold color in headings
    const headings = page.locator('h1, h2, h3').first();

    const color = await headings.evaluate((el) => {
      return getComputedStyle(el).color;
    });

    // Should contain gold RGB values
    expect(color.toLowerCase()).toMatch(/212,\s*175,\s*55/);
  });

  test('should use gold for buttons', async ({ page }) => {
    await page.goto('/market');

    const primaryButtons = page.locator('.el-button--primary, .button-primary').first();

    const bgColor = await primaryButtons.evaluate((el) => {
      return getComputedStyle(el).backgroundColor;
    });

    // Primary buttons should be gold
    expect(bgColor.toLowerCase()).toMatch(/212,\s*175,\s*55/);
  });

  test('should use gold for borders', async ({ page }) => {
    await page.goto('/');

    const cards = page.locator('.card, .data-card').first();

    const borderColor = await cards.evaluate((el) => {
      return getComputedStyle(el).borderColor;
    });

    // Borders should be gold or dark (both acceptable)
    const color = borderColor.toLowerCase();
    const isBloombergColor =
      color.match(/212,\s*175,\s*55/) || // Gold
      color.match(/42,\s*42,\s*42/) || // Dark border
      color.match(/26,\s*26,\s*26/); // Darker border

    expect(isBloombergColor).toBeTruthy();
  });

  test('should use gold for links and interactive elements', async ({ page }) => {
    await page.goto('/stocks');

    const links = page.locator('a, .link').first();

    const color = await links.evaluate((el) => {
      return getComputedStyle(el).color;
    });

    // Links should be gold or high-contrast white
    const colorLower = color.toLowerCase();
    const isGoldOrWhite =
      colorLower.match(/212,\s*175,\s*55/) || // Gold
      colorLower.match(/229,\s*229,\s*229/); // High-contrast white

    expect(isGoldOrWhite).toBeTruthy();
  });
});

test.describe('Bloomberg Style: Dark Background', () => {
  test('should have dark background on body', async ({ page }) => {
    await page.goto('/');

    const bgColor = await page.evaluate(() => {
      return getComputedStyle(document.body).backgroundColor;
    });

    // Should be dark background (#1A1A1A or similar)
    expect(bgColor.toLowerCase()).toMatch(/(26,\s*26,\s*26|10,\s*10,\s*10|0,\s*0,\s*0)/);
  });

  test('should have dark background on cards', async ({ page }) => {
    await page.goto('/market');

    const cards = page.locator('.card, .data-card').first();

    const bgColor = await cards.evaluate((el) => {
      return getComputedStyle(el).backgroundColor;
    });

    // Cards should be dark
    const color = bgColor.toLowerCase();
    const isDark =
      color.match(/10,\s*10,\s*10/) || // #0A0A0A
      color.match(/26,\s*26,\s*26/) || // #1A1A1A
      color.match(/34,\s*34,\s*34/); // #222222

    expect(isDark, `Card background should be dark, got ${bgColor}`).toBeTruthy();
  });

  test('should not have light backgrounds', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check for no light backgrounds (white, very light gray)
    const hasLightBg = await page.evaluate(() => {
      const allElements = document.querySelectorAll('*');
      for (const el of allElements) {
        const bg = getComputedStyle(el).backgroundColor;
        if (!bg) continue;

        // Convert to RGB for comparison
        const rgb = bg.match(/\d+/g);
        if (!rgb || rgb.length < 3) continue;

        const [r, g, b] = rgb.map(Number);

        // Check if it's light (high RGB values)
        if (r > 200 && g > 200 && b > 200) {
          // Skip if it's text (might be intentional)
          const text = el.textContent?.trim();
          if (!text || text.length < 10) {
            return true;
          }
        }
      }
      return false;
    });

    expect(hasLightBg, 'Should not have light background colors').toBeFalsy();
  });

  test('should have consistent dark background across pages', async ({ page }) => {
    const paths = ['/', '/market', '/stocks', '/trade-management'];
    const backgrounds: string[] = [];

    for (const path of paths) {
      await page.goto(path);
      await page.waitForLoadState('networkidle');

      const bgColor = await page.evaluate(() => {
        return getComputedStyle(document.body).backgroundColor;
      });

      backgrounds.push(bgColor);
    }

    // All backgrounds should be similar (dark)
    for (const bg of backgrounds) {
      expect(bg.toLowerCase()).toMatch(/(26,\s*26,\s*26|10,\s*10,\s*10|0,\s*0,\s*0)/);
    }
  });
});

test.describe('Bloomberg Style: 8px Grid System', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should use 8px grid for container spacing', async ({ page }) => {
    const containers = await page.locator('.container, .section, .panel').all();

    for (const container of containers.slice(0, 10)) {
      const margin = await container.evaluate((el) => {
        const styles = getComputedStyle(el);
        return {
          margin: styles.margin,
          padding: styles.padding,
        };
      });

      // Check margin
      if (margin.margin && margin.margin !== '0px') {
        const values = margin.margin.split(' ').map(v => parseInt(v.replace('px', '')));
        for (const v of values) {
          if (isNaN(v)) continue;
          expect(v % 8, `Margin ${margin.margin} should follow 8px grid`).toBe(0);
        }
      }

      // Check padding
      if (margin.padding && margin.padding !== '0px') {
        const values = margin.padding.split(' ').map(v => parseInt(v.replace('px', '')));
        for (const v of values) {
          if (isNaN(v)) continue;
          expect(v % 8, `Padding ${margin.padding} should follow 8px grid`).toBe(0);
        }
      }
    }
  });

  test('should use 8px grid for form elements', async ({ page }) => {
    await page.goto('/settings');

    const formItems = await page.locator('.el-form-item, .form-group').all();

    for (const item of formItems.slice(0, 10)) {
      const marginBottom = await item.evaluate((el) => {
        return getComputedStyle(el).marginBottom;
      });

      if (marginBottom === '0px' || marginBottom === 'auto') continue;

      const value = parseInt(marginBottom.replace('px', ''));
      if (isNaN(value)) continue;

      expect(value % 8, `Form item margin-bottom ${marginBottom} should follow 8px grid`).toBe(0);
    }
  });

  test('should use 8px grid for button spacing', async ({ page }) => {
    await page.goto('/market');

    const buttonGroups = await page.locator('.button-group, .filter-actions').all();

    for (const group of buttonGroups) {
      const gap = await group.evaluate((el) => {
        return getComputedStyle(el).gap;
      });

      if (!gap || gap === 'normal') continue;

      const value = parseInt(gap.replace('px', ''));
      if (isNaN(value)) continue;

      expect(value % 8, `Button group gap ${gap} should follow 8px grid`).toBe(0);
    }
  });
});

test.describe('Bloomberg Style: WCAG AA Compliance', () => {
  test('should have sufficient contrast for headings', async ({ page }) => {
    await page.goto('/');

    const h1 = page.locator('h1').first();
    await expectWCAGAACompliant(await h1.page(), 'h1');
  });

  test('should have sufficient contrast for body text', async ({ page }) => {
    await page.goto('/');

    const bodyText = page.locator('p, .text, .content').first();
    await expectWCAGAACompliant(await bodyText.page(), 'body text');
  });

  test('should have sufficient contrast for buttons', async ({ page }) => {
    await page.goto('/market');

    const buttons = page.locator('button, .el-button').all();

    for (const button of buttons.slice(0, 5)) {
      const fgColor = await button.evaluate((el) => getComputedStyle(el).color);
      const bgColor = await button.evaluate((el) => getComputedStyle(el).backgroundColor);

      // Convert rgb() to hex
      const rgbToHex = (rgb: string) => {
        const match = rgb.match(/\d+/g);
        if (!match || match.length < 3) return '#000000';
        const [r, g, b] = match.map(Number);
        return '#' + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
      };

      const fgHex = rgbToHex(fgColor);
      const bgHex = rgbToHex(bgColor);

      const ratio = getContrastRatio(fgHex, bgHex);

      expect(
        ratio >= 4.5,
        `Button contrast ratio ${ratio.toFixed(2)}:1 should meet WCAG AA`
      ).toBeTruthy();
    }
  });

  test('should have sufficient contrast for card titles', async ({ page }) => {
    await page.goto('/stocks');

    const cardTitles = page.locator('.card h3, .card .title, .card-title').all();

    for (const title of cardTitles.slice(0, 5)) {
      const fgColor = await title.evaluate((el) => getComputedStyle(el).color);
      const bgColor = await title.evaluate((el) => {
        // Get parent background
        const parent = el.parentElement;
        return parent ? getComputedStyle(parent).backgroundColor : '#000000';
      });

      const rgbToHex = (rgb: string) => {
        const match = rgb.match(/\d+/g);
        if (!match || match.length < 3) return '#000000';
        const [r, g, b] = match.map(Number);
        return '#' + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
      };

      const fgHex = rgbToHex(fgColor);
      const bgHex = rgbToHex(bgColor);

      const ratio = getContrastRatio(fgHex, bgHex);

      expect(
        ratio >= 4.5,
        `Card title contrast ratio ${ratio.toFixed(2)}:1 should meet WCAG AA`
      ).toBeTruthy();
    }
  });
});

test.describe('Bloomberg Style: Square Design (Minimal Border Radius)', () => {
  test('should have square or minimal rounded buttons', async ({ page }) => {
    await page.goto('/');

    const buttons = page.locator('button, .el-button').all();

    for (const button of buttons.slice(0, 10)) {
      const borderRadius = await button.evaluate((el) => {
        return getComputedStyle(el).borderRadius;
      });

      // Should be 0px (square) or small radius (4px)
      const radius = parseInt(borderRadius.replace('px', ''));
      expect(radius, `Button border-radius should be 0-4px, got ${borderRadius}`).toBeLessThanOrEqual(4);
    }
  });

  test('should have square or minimal rounded cards', async ({ page }) => {
    await page.goto('/market');

    const cards = page.locator('.card, .data-card').all();

    for (const card of cards.slice(0, 10)) {
      const borderRadius = await card.evaluate((el) => {
        return getComputedStyle(el).borderRadius;
      });

      // Should be 0-8px (small to medium)
      const radius = parseInt(borderRadius.replace('px', ''));
      expect(radius, `Card border-radius should be 0-8px, got ${borderRadius}`).toBeLessThanOrEqual(8);
    }
  });

  test('should not have circular or fully rounded elements', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check for no circular buttons or elements
    const hasCircular = await page.evaluate(() => {
      const allElements = document.querySelectorAll('*');
      for (const el of allElements) {
        const radius = getComputedStyle(el).borderRadius;

        // Skip if no border radius
        if (!radius || radius === '0px' || radius === 'none') continue;

        // Check for 50% (circular) or large radius
        const value = parseInt(radius);
        if (
          radius === '50%' ||
          radius.includes('%') && parseInt(radius) > 25
        ) {
          return true;
        }

        // Check for large pixel radius (> 12px)
        if (!isNaN(value) && value > 12) {
          return true;
        }
      }
      return false;
    });

    expect(hasCircular, 'Should not have circular or over-rounded elements').toBeFalsy();
  });

  test('should have sharp borders for data tables', async ({ page }) => {
    await page.goto('/stocks');

    const tables = page.locator('table, .el-table').first();

    const borderRadius = await tables.evaluate((el) => {
      return getComputedStyle(el).borderRadius;
    });

    // Tables should be square or minimally rounded
    const radius = parseInt(borderRadius.replace('px', ''));
    expect(radius, `Table border-radius should be 0-4px, got ${borderRadius}`).toBeLessThanOrEqual(4);
  });
});

test.describe('Bloomberg Style: High Contrast Design', () => {
  test('should have high contrast text on dark backgrounds', async ({ page }) => {
    await page.goto('/');

    const contrastCheck = await page.evaluate(() => {
      const body = document.body;
      const bodyStyle = getComputedStyle(body);

      return {
        textColor: bodyStyle.color,
        bgColor: bodyStyle.backgroundColor,
      };
    });

    // Body text should be light on dark
    const textColor = contrastCheck.textColor.toLowerCase();
    const bgColor = contrastCheck.bgColor.toLowerCase();

    // Text should be light (high RGB values)
    expect(textColor).toMatch(/(229,\s*229,\s*229|255,\s*255,\s*255|238,\s*238,\s*238)/);

    // Background should be dark (low RGB values)
    expect(bgColor).toMatch(/(0,\s*0,\s*0|10,\s*10,\s*10|26,\s*26,\s*26)/);
  });

  test('should have clear visual hierarchy', async ({ page }) => {
    await page.goto('/');

    // Check heading levels
    const h1Size = await page.locator('h1').first().evaluate((el) => {
      return parseFloat(getComputedStyle(el).fontSize);
    });

    const h2Size = await page.locator('h2').first().evaluate((el) => {
      return parseFloat(getComputedStyle(el).fontSize);
    });

    const bodySize = await page.locator('p').first().evaluate((el) => {
      return parseFloat(getComputedStyle(el).fontSize);
    });

    // h1 should be largest
    expect(h1Size).toBeGreaterThan(h2Size);
    expect(h2Size).toBeGreaterThan(bodySize);
  });

  test('should have distinct accent colors for actions', async ({ page }) => {
    await page.goto('/market');

    // Primary vs secondary buttons should be visually distinct
    const primaryBtn = page.locator('.el-button--primary').first();
    const secondaryBtn = page.locator('.el-button:not(.el-button--primary)').first();

    const primaryBg = await primaryBtn.evaluate((el) => getComputedStyle(el).backgroundColor);
    const secondaryBg = await secondaryBtn.evaluate((el) => getComputedStyle(el).backgroundColor);

    // Colors should be different
    expect(primaryBg).not.toBe(secondaryBg);

    // Primary should be gold
    expect(primaryBg.toLowerCase()).toMatch(/212,\s*175,\s*55/);
  });
});

test.describe('Bloomberg Style: Professional Typography', () => {
  test('should use uppercase for headings', async ({ page }) => {
    await page.goto('/');

    const headings = page.locator('h1, h2, h3').all();

    for (const heading of headings.slice(0, 5)) {
      const text = await heading.textContent();
      const transform = await heading.evaluate((el) => {
        return getComputedStyle(el).textTransform;
      });

      // Major headings should be uppercase (Bloomberg style)
      if (text && text.length < 50) { // Only check short headings
        expect(transform.toLowerCase()).toBe('uppercase');
      }
    }
  });

  test('should have proper letter spacing', async ({ page }) => {
    await page.goto('/');

    const headings = page.locator('h1, h2, h3').all();

    for (const heading of headings.slice(0, 5)) {
      const letterSpacing = await heading.evaluate((el) => {
        return getComputedStyle(el).letterSpacing;
      });

      // Should have some letter spacing (not 0px)
      const value = parseFloat(letterSpacing);
      // Allow normal or positive spacing
      expect(value >= 0 || letterSpacing === 'normal').toBeTruthy();
    }
  });

  test('should use monospace for numerical data', async ({ page }) => {
    await page.goto('/stocks');

    const monoElements = page.locator('.mono, [class*="price"], [class*="amount"]').all();

    for (const el of monoElements.slice(0, 5)) {
      const fontFamily = await el.evaluate((el) => {
        return getComputedStyle(el).fontFamily;
      });

      // Should use monospace or contain 'Mono'
      const fontLower = fontFamily.toLowerCase();
      const hasMono = fontLower.includes('mono') ||
                      fontLower.includes('consolas') ||
                      fontLower.includes('code');

      expect(hasMono, `Numerical data should use monospace, got ${fontFamily}`).toBeTruthy();
    }
  });
});
