import { expect, Page } from '@playwright/test';

/**
 * MyStocks Frontend - Playwright Test Utilities
 * Phase 3: Bloomberg Terminal Style Verification
 *
 * Reusable helper functions for Design Token validation,
 * style assertions, and Bloomberg compliance checks.
 */

/**
 * Bloomberg Design Token Constants
 * Expected values from theme-tokens.scss
 */
export const BLOOMBERG_TOKENS = {
  // Color tokens
  colorAccent: '#D4AF37', // Gold
  colorBgPrimary: '#1A1A1A', // Main dark background
  colorBgElevated: '#0A0A0A', // Emphasized background
  colorBgSecondary: '#222222', // Secondary background
  colorTextPrimary: '#E5E5E5', // High contrast text
  colorTextSecondary: '#A0A0A0', // Secondary text
  colorBorder: '#2A2A2A', // Border color
  colorStockDown: '#EB4436', // Red (up in China market)
  colorStockUp: '#10B981', // Green (down in China market)

  // Spacing tokens (8px baseline grid)
  spacingXs: '4px',
  spacingSm: '8px',
  spacingMd: '12px',
  spacingLg: '16px',
  spacingXl: '20px',
  spacing2xl: '24px',
  spacing3xl: '32px',

  // Font tokens
  fontFamilySans: 'Inter, system-ui, sans-serif',
  fontFamilyMono: 'JetBrains Mono, Consolas, monospace',
  fontSizeXs: '12px',
  fontSizeSm: '14px',
  fontSizeMd: '16px',
  fontSizeLg: '18px',
  fontSizeXl: '24px',
  fontSize2xl: '32px',

  // Border radius tokens
  borderRadiusSm: '4px',
  borderRadiusMd: '8px',

  // Shadow tokens
  shadowMd: '0 2px 4px rgba(0, 0, 0, 0.1)',
  shadowLg: '0 6px 12px rgba(0, 0, 0, 0.15)',
};

/**
 * Old system colors that should NOT exist
 */
export const OLD_SYSTEM_COLORS = [
  '#409eff', // Element Plus default blue
  '#f5f7fa', // Light gray background
  '#909399', // Secondary gray text
  '#67C23A', // Success green
  '#E6A23C', // Warning orange
  '#F56C6C', // Error red
];

/**
 * Assert computed CSS variable matches expected value
 */
export async function expectCSSVariable(
  page: Page,
  selector: string,
  variableName: string,
  expectedValue: string
) {
  const actualValue = await page.locator(selector).evaluate((el, name) => {
    return getComputedStyle(el).getPropertyValue(name).trim();
  }, variableName);

  expect(actualValue.toLowerCase()).toBe(expectedValue.toLowerCase());
}

/**
 * Get computed CSS variable value
 */
export async function getCSSVariable(
  page: Page,
  selector: string,
  variableName: string
): Promise<string> {
  return await page.locator(selector).evaluate((el, name) => {
    return getComputedStyle(el).getPropertyValue(name).trim();
  }, variableName);
}

/**
 * Assert element has no hardcoded colors (inline styles)
 */
export async function expectNoHardcodedColors(
  page: Page,
  selector: string
) {
  const element = page.locator(selector).first();

  // Check for inline style attribute
  const styleAttr = await element.getAttribute('style');
  if (styleAttr) {
    // Check for color properties in inline style
    const colorRegex = /(color|background|border):\s*[^;]+;/gi;
    const hasColor = colorRegex.test(styleAttr);
    expect(hasColor, `${selector} should not have inline colors`).toBeFalsy();
  }
}

/**
 * Assert computed style matches Design Token
 */
export async function expectComputedStyle(
  page: Page,
  selector: string,
  property: string,
  expectedValue: string
) {
  const actualValue = await page.locator(selector).evaluate((el, prop) => {
    const computed = getComputedStyle(el);
    return computed.getPropertyValue(prop).trim();
  }, property);

  expect(actualValue.toLowerCase()).toBe(expectedValue.toLowerCase());
}

/**
 * Assert element uses Bloomberg color palette
 */
export async function expectBloombergColor(
  page: Page,
  selector: string,
  property: 'color' | 'backgroundColor' | 'borderColor' | 'borderTopColor'
) {
  const actualValue = await page.locator(selector).evaluate((el, prop) => {
    return getComputedStyle(el).getPropertyValue(prop).trim();
  }, property);

  // Convert to lowercase for comparison
  const color = actualValue.toLowerCase();

  // Check if it's one of the Bloomberg colors (hex or rgb)
  const isBloombergColor =
    color.includes('212, 175, 55') || // Gold #D4AF37
    color.includes('26, 26, 26') || // #1A1A1A
    color.includes('10, 10, 10') || // #0A0A0A
    color.includes('229, 229, 229') || // #E5E5E5
    color.includes('160, 160, 160') || // #A0A0A0
    color.includes('42, 42, 42') || // #2A2A2A
    color.includes('235, 68, 54') || // Stock down (red)
    color.includes('16, 185, 129'); // Stock up (green)

  expect(isBloombergColor, `${selector} ${property}=${actualValue} should use Bloomberg color palette`).toBeTruthy();
}

/**
 * Assert spacing follows 8px baseline grid
 */
export async function expectBaselineGridSpacing(
  page: Page,
  selector: string,
  property: 'padding' | 'margin' | 'gap'
) {
  const value = await page.locator(selector).evaluate((el, prop) => {
    return getComputedStyle(el).getPropertyValue(prop).trim();
  }, property);

  if (value === '0px' || value === '') {
    return; // 0px or auto is acceptable
  }

  // Extract numeric value(s)
  const values = value.split(' ').map(v => parseInt(v.replace('px', '')));

  for (const v of values) {
    if (isNaN(v)) continue; // Skip non-numeric values
    expect(v % 8, `${selector} ${property}=${value} should follow 8px grid`).toBe(0);
  }
}

/**
 * Assert no mobile responsive code exists
 * Checks for @media queries with mobile breakpoints
 */
export async function expectNoMobileResponsiveCode(page: Page) {
  // Check stylesheets for mobile media queries
  const hasMobileMediaQuery = await page.evaluate(() => {
    const stylesheets = Array.from(document.styleSheets);
    for (const sheet of stylesheets) {
      try {
        const rules = Array.from(sheet.cssRules || sheet.rules || []);
        for (const rule of rules) {
          if (rule.conditionText) {
            // Check for mobile breakpoints
            if (
              rule.conditionText.includes('max-width: 768px') ||
              rule.conditionText.includes('max-width: 767px') ||
              rule.conditionText.includes('max-width: 480px') ||
              rule.conditionText.includes('max-width: 375px')
            ) {
              return true;
            }
          }
        }
      } catch (e) {
        // CORS restrictions on stylesheet access
        console.warn('Cannot access stylesheet rules:', e);
      }
    }
    return false;
  });

  expect(hasMobileMediaQuery, 'Should not have mobile responsive media queries').toBeFalsy();
}

/**
 * Get contrast ratio between two colors
 * Returns WCAG contrast ratio
 */
export function getContrastRatio(foreground: string, background: string): number {
  // Parse hex/rgb colors to RGB
  const parseColor = (color: string) => {
    const hex = color.replace('#', '');
    if (hex.length === 3) {
      return {
        r: parseInt(hex[0] + hex[0], 16),
        g: parseInt(hex[1] + hex[1], 16),
        b: parseInt(hex[2] + hex[2], 16),
      };
    } else if (hex.length === 6) {
      return {
        r: parseInt(hex.substring(0, 2), 16),
        g: parseInt(hex.substring(2, 4), 16),
        b: parseInt(hex.substring(4, 6), 16),
      };
    }
    return { r: 0, g: 0, b: 0 };
  };

  const fg = parseColor(foreground);
  const bg = parseColor(background);

  // Calculate luminance
  const luminance = (color: { r: number; g: number; b: number }) => {
    const [r, g, b] = [color.r, color.g, color.b].map((v) => {
      v /= 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };

  const lum1 = luminance(fg);
  const lum2 = luminance(bg);
  const brightest = Math.max(lum1, lum2);
  const darkest = Math.min(lum1, lum2);

  return (brightest + 0.05) / (darkest + 0.05);
}

/**
 * Assert WCAG AA compliance (contrast ratio >= 4.5:1)
 */
export async function expectWCAGAACompliant(
  page: Page,
  selector: string
) {
  const [foreground, background] = await page.locator(selector).evaluate((el) => {
    const computed = getComputedStyle(el);
    return [
      computed.color.trim(),
      computed.backgroundColor.trim(),
    ];
  });

  // Convert rgb() to hex for contrast calculation
  const rgbToHex = (rgb: string) => {
    const match = rgb.match(/\d+/g);
    if (!match || match.length < 3) return '#000000';
    const [r, g, b] = match.map(Number);
    return '#' + [r, g, b].map((x) => x.toString(16).padStart(2, '0')).join('');
  };

  const fgHex = rgbToHex(foreground);
  const bgHex = rgbToHex(background);

  const ratio = getContrastRatio(fgHex, bgHex);

  expect(
    ratio,
    `${selector} contrast ratio ${ratio.toFixed(2)}:1 should meet WCAG AA (>= 4.5:1)`
  ).toBeGreaterThanOrEqual(4.5);
}

/**
 * Navigate to page and wait for network idle
 */
export async function navigateAndWait(page: Page, path: string) {
  await page.goto(path, { waitUntil: 'networkidle' });
  // Additional wait for any lazy-loaded content
  await page.waitForTimeout(500);
}

/**
 * Take screenshot with custom options
 */
export async function takeComponentScreenshot(
  page: Page,
  selector: string,
  name: string
) {
  await page.locator(selector).screenshot({
    path: `screenshots/${name}.png`,
  });
}

/**
 * Assert Design Token is used in stylesheet
 */
export async function expectDesignTokenUsed(
  page: Page,
  tokenName: string
) {
  const isUsed = await page.evaluate((name) => {
    // Check if CSS variable is defined
    const testElement = document.createElement('div');
    testElement.style.color = `var(${name})`;
    document.body.appendChild(testElement);

    const computedColor = getComputedStyle(testElement).color;
    document.body.removeChild(testElement);

    // If computed value is not empty, token is defined
    return computedColor !== '' && computedColor !== 'rgba(0, 0, 0, 0)';
  }, tokenName);

  expect(isUsed, `Design Token ${tokenName} should be defined and accessible`).toBeTruthy();
}

/**
 * Check if theme-tokens.scss is imported
 */
export async function expectThemeTokensImported(page: Page) {
  // Check for one of the key Design Token variables
  await expectDesignTokenUsed(page, '--color-accent');
  await expectDesignTokenUsed(page, '--color-bg-primary');
  await expectDesignTokenUsed(page, '--color-text-primary');
}
