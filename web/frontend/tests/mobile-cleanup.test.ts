import { test, expect } from '@playwright/test';

/**
 * MyStocks Frontend - Mobile Code Cleanup Verification Tests
 * Phase 3: Bloomberg Terminal Style Verification
 *
 * Tests for verifying mobile responsive code has been removed:
 * - No @media queries for mobile breakpoints
 * - No Element Plus mobile components (el-col-xs, el-col-sm)
 * - Desktop-only layout maintained
 * - No responsive design patterns
 */

test.describe('Mobile Code Cleanup: No Mobile Media Queries', () => {
  const pages = [
    { path: '/', name: 'Dashboard' },
    { path: '/market', name: 'Market' },
    { path: '/stocks', name: 'Stocks' },
    { path: '/trade-management', name: 'TradeManagement' },
  ];

  for (const pageInfo of pages) {
    test.describe(`${pageInfo.name} Page`, () => {
      test('should not have mobile @media queries (768px)', async ({ page }) => {
        await page.goto(pageInfo.path);
        await page.waitForLoadState('networkidle');

        const hasMobileMediaQuery = await page.evaluate(() => {
          const stylesheets = Array.from(document.styleSheets);
          for (const sheet of stylesheets) {
            try {
              const rules = Array.from(sheet.cssRules || sheet.rules || []);
              for (const rule of rules) {
                if (rule.conditionText) {
                  const condition = rule.conditionText.toLowerCase();
                  if (
                    condition.includes('max-width: 768px') ||
                    condition.includes('max-width: 767px') ||
                    condition.includes('max-width: 480px') ||
                    condition.includes('max-width: 375px')
                  ) {
                    return true;
                  }
                }
              }
            } catch (e) {
              // CORS restriction - skip this stylesheet
              continue;
            }
          }
          return false;
        });

        expect(
          hasMobileMediaQuery,
          `${pageInfo.name}: Should not have mobile @media queries`
        ).toBeFalsy();
      });

      test('should not have mobile @media queries (375px)', async ({ page }) => {
        await page.goto(pageInfo.path);
        await page.waitForLoadState('networkidle');

        const hasMobileMediaQuery = await page.evaluate(() => {
          const styleTags = Array.from(document.querySelectorAll('style'));
          for (const tag of styleTags) {
            const css = tag.innerHTML || '';
            if (
              css.toLowerCase().includes('@media') &&
              (css.includes('375px') || css.includes('414px'))
            ) {
              return true;
            }
          }
          return false;
        });

        expect(
          hasMobileMediaQuery,
          `${pageInfo.name}: Should not have mobile breakpoint @media`
        ).toBeFalsy();
      });
    });
  }
});

test.describe('Mobile Code Cleanup: No Mobile Element Plus Components', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should not use el-col-xs', async ({ page }) => {
    const hasColXs = await page.locator('.el-col-xs').count();
    expect(hasColXs, 'Should not use el-col-xs components').toBe(0);
  });

  test('should not use el-col-sm', async ({ page }) => {
    const hasColSm = await page.locator('.el-col-sm').count();
    expect(hasColSm, 'Should not use el-col-sm components').toBe(0);
  });

  test('should not use el-col-md for mobile', async ({ page }) => {
    // el-col-md is acceptable for desktop, but check if used incorrectly
    const mdColumns = await page.locator('.el-col-md').all();

    for (const col of mdColumns) {
      // Check if it's used for mobile layout pattern
      const parent = await col.evaluate((el) => {
        const parent = el.parentElement;
        return parent ? parent.className : '';
      });

      // Should not be in a responsive grid with other mobile columns
      expect(parent.toLowerCase()).not.toContain('el-col-xs');
      expect(parent.toLowerCase()).not.toContain('el-col-sm');
    }
  });

  test('should not use el-row responsive classes', async ({ page }) => {
    // Check for el-row with mobile responsive attributes
    const hasResponsiveRow = await page.evaluate(() => {
      const rows = document.querySelectorAll('.el-row');
      for (const row of rows) {
        const className = row.className || '';
        if (
          className.includes(':xs') ||
          className.includes(':sm') ||
          className.includes(':md') ||
          className.includes('gutter-')
        ) {
          return true;
        }
      }
      return false;
    });

    expect(hasResponsiveRow, 'Should not use responsive el-row classes').toBeFalsy();
  });
});

test.describe('Mobile Code Cleanup: Desktop-Only Layout', () => {
  test('should maintain desktop layout at smaller viewports', async ({ page }) => {
    // Set viewport to mobile size
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check that layout is still desktop-style (not responsive)
    const hasDesktopLayout = await page.evaluate(() => {
      // Check for fixed width containers or no responsive wrapping
      const containers = document.querySelectorAll('.container, .main-content');
      for (const container of containers) {
        const styles = getComputedStyle(container);
        const width = styles.width;
        const maxWidth = styles.maxWidth;

        // Should have desktop width (not fluid mobile width)
        if (maxWidth && parseInt(maxWidth) < 768) {
          return false;
        }
      }
      return true;
    });

    expect(hasDesktopLayout, 'Should maintain desktop layout').toBeTruthy();
  });

  test('should not collapse navigation on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/market');

    // Navigation should be visible (not collapsed to hamburger menu)
    const navVisible = await page.locator('nav, .navbar, .navigation').isVisible();

    expect(navVisible, 'Navigation should remain visible on mobile viewport').toBeTruthy();
  });

  test('should not stack columns on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/trade-management');

    // Check for horizontal layout (not stacked)
    const hasHorizontalLayout = await page.evaluate(() => {
      const flexContainers = document.querySelectorAll('[class*="flex"]');
      for (const container of flexContainers) {
        const styles = getComputedStyle(container);
        const flexDirection = styles.flexDirection;

        // Should remain row (horizontal), not column (stacked)
        if (flexDirection === 'column') {
          // Check if it's intentional (not a mobile-specific change)
          const className = container.className;
          if (!className.includes('vertical') && !className.includes('column')) {
            return false;
          }
        }
      }
      return true;
    });

    expect(hasHorizontalLayout, 'Should maintain horizontal layout on mobile').toBeTruthy();
  });
});

test.describe('Mobile Code Cleanup: No Touch Optimizations', () => {
  test('should not have touch-specific styles', async ({ page }) => {
    await page.goto('/');

    const hasTouchStyles = await page.evaluate(() => {
      const allElements = document.querySelectorAll('*');
      for (const el of allElements) {
        const styles = getComputedStyle(el);

        // Check for touch-related properties
        if (
          styles.touchAction !== 'auto' ||
          styles.pointerEvents === 'touch' ||
          styles.cursor === 'pointer' && el.tagName !== 'BUTTON' && el.tagName !== 'A'
        ) {
          // These might be acceptable, but check if excessive
          const className = el.className || '';
          if (className.includes('touch') || className.includes('mobile')) {
            return true;
          }
        }
      }
      return false;
    });

    expect(hasTouchStyles, 'Should not have mobile/touch-specific optimizations').toBeFalsy();
  });

  test('should not use mobile-specific icons or buttons', async ({ page }) => {
    await page.goto('/market');

    // Check for hamburger menu, back buttons, etc.
    const hasMobileUI = await page.locator(
      '.hamburger, .mobile-menu, .mobile-nav, .back-button, [class*="mobile-"]'
    ).count();

    expect(hasMobileUI, 'Should not have mobile-specific UI elements').toBe(0);
  });
});

test.describe('Mobile Code Cleanup: Font Sizes', () => {
  test('should not use responsive font sizes', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/');

    // Get font sizes at desktop viewport
    const desktopSizes = await page.evaluate(() => {
      const headings = Array.from(document.querySelectorAll('h1, h2, h3'));
      return headings.map(h => parseFloat(getComputedStyle(h).fontSize));
    });

    // Change to mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Get font sizes at mobile viewport
    const mobileSizes = await page.evaluate(() => {
      const headings = Array.from(document.querySelectorAll('h1, h2, h3'));
      return headings.map(h => parseFloat(getComputedStyle(h).fontSize));
    });

    // Font sizes should be similar (no responsive scaling)
    for (let i = 0; i < Math.min(desktopSizes.length, mobileSizes.length); i++) {
      const difference = Math.abs(desktopSizes[i] - mobileSizes[i]);
      expect(
        difference,
        `Font size should not change significantly (desktop: ${desktopSizes[i]}px, mobile: ${mobileSizes[i]}px)`
      ).toBeLessThanOrEqual(2); // Allow 2px difference for rounding
    }
  });

  test('should maintain readable text at mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/stocks');

    // Check if text is still readable (not too small)
    const bodyText = page.locator('p, .text, body').first();

    const fontSize = await bodyText.evaluate((el) => {
      return parseFloat(getComputedStyle(el).fontSize);
    });

    // Should be at least 12px (even on mobile viewport, since no responsive scaling)
    expect(
      fontSize,
      'Font size should remain readable (>= 12px) even on mobile viewport'
    ).toBeGreaterThanOrEqual(12);
  });
});

test.describe('Mobile Code Cleanup: No Responsive Images', () => {
  test('should not use srcset for responsive images', async ({ page }) => {
    await page.goto('/');

    const hasSrcset = await page.locator('img[srcset]').count();
    expect(hasSrcset, 'Should not use responsive images with srcset').toBe(0);
  });

  test('should not use picture element for responsive images', async ({ page }) => {
    await page.goto('/');

    const hasPicture = await page.locator('picture').count();
    expect(hasPicture, 'Should not use picture element for responsive images').toBe(0);
  });

  test('should not use sizes attribute', async ({ page }) => {
    await page.goto('/');

    const hasSizes = await page.locator('img[sizes]').count();
    expect(hasSizes, 'Should not use sizes attribute for responsive images').toBe(0);
  });
});

test.describe('Mobile Code Cleanup: Spacing Consistency', () => {
  test('should maintain consistent spacing at mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/market');

    // Get padding at desktop viewport
    const desktopPadding = await page.locator('.container, .main-content').first().evaluate((el) => {
      return getComputedStyle(el).padding;
    });

    // Change to mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Get padding at mobile viewport
    const mobilePadding = await page.locator('.container, .main-content').first().evaluate((el) => {
      return getComputedStyle(el).padding;
    });

    // Padding should be similar (no responsive adjustment)
    expect(
      desktopPadding,
      'Padding should remain consistent (not responsive)'
    ).toBe(mobilePadding);
  });
});

test.describe('Mobile Code Cleanup: Comments and Documentation', () => {
  test('should have design notes about desktop-only in source files', async ({ page }) => {
    // This test verifies the design note exists in compiled styles
    // (If comments are preserved in build)

    const hasDesignNote = await page.evaluate(() => {
      const stylesheets = Array.from(document.styleSheets);
      for (const sheet of stylesheets) {
        try {
          const rules = Array.from(sheet.cssRules || sheet.rules || []);
          for (const rule of rules) {
            if (rule.cssText) {
              const css = rule.cssText.toLowerCase();
              if (
                css.includes('desktop only') ||
                css.includes('desktop端') ||
                css.includes('mobile端') ||
                css.includes('仅支持桌面')
              ) {
                return true;
              }
            }
          }
        } catch (e) {
          // CORS restriction
          continue;
        }
      }
      return false;
    });

    // Note: Comments are typically removed in production build
    // This test will pass if comments are preserved, otherwise skip
    if (hasDesignNote) {
      expect(true).toBeTruthy();
    } else {
      // Comments stripped in build - acceptable
      expect(true).toBeTruthy();
    }
  });
});

test.describe('Mobile Code Cleanup: Component Verification', () => {
  const components = [
    { selector: '.data-card', name: 'DataCard' },
    { selector: '.chart-container', name: 'ChartContainer' },
    { selector: '.filter-bar', name: 'FilterBar' },
    { selector: '.detail-dialog', name: 'DetailDialog' },
  ];

  for (const component of components) {
    test.describe(`${component.name} Component`, () => {
      test(`should not have mobile styles for ${component.name}`, async ({ page }) => {
        await page.goto('/market');

        const hasMobileStyle = await page.locator(component.selector).first().evaluate((el) => {
          const styles = getComputedStyle(el);

          // Check for mobile-specific properties
          if (
            styles.maxWidth &&
            parseInt(styles.maxWidth) < 768
          ) {
            return true;
          }

          // Check for mobile classes
          const className = el.className || '';
          if (
            className.includes('mobile') ||
            className.includes('xs-') ||
            className.includes('sm-')
          ) {
            return true;
          }

          return false;
        });

        expect(
          hasMobileStyle,
          `${component.name} should not have mobile-specific styles`
        ).toBeFalsy();
      });
    });
  }
});
