/**
 * ArtDeco Visual Regression Tests
 *
 * 用途：验证ArtDeco设计系统CSS属性和视觉一致性
 * 覆盖：字体、颜色、间距、装饰元素
 */

import { test, expect } from '@playwright/test';

test.describe('ArtDeco设计系统视觉回归测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
  });

  test('ArtDeco颜色变量应该正确定义', async ({ page }) => {
    // 获取CSS变量值
    const colors = await page.evaluate(() => {
      const styles = getComputedStyle(document.documentElement);
      return {
        goldPrimary: styles.getPropertyValue('--artdeco-gold-primary').trim(),
        goldHover: styles.getPropertyValue('--artdeco-gold-hover').trim(),
        bgGlobal: styles.getPropertyValue('--artdeco-bg-global').trim(),
        borderDefault: styles.getPropertyValue('--artdeco-border-default').trim()
      };
    });

    // 验证金色主色
    expect(colors.goldPrimary).toBe('#D4AF37');

    // 验证金色悬停色
    expect(colors.goldHover).toBe('#F2E8C4');

    // 验证背景色（黑曜石黑）
    expect(colors.bgGlobal).toBe('#0A0A0A');

    // 验证边框色（半透明金色）
    expect(colors.borderDefault).toBe('rgba(212, 175, 55, 0.2)');
  });

  test('ArtDeco字体应该正确应用', async ({ page }) => {
    // 检查标题字体
    const headingFont = await page.evaluate(() => {
      const heading = document.querySelector('.artdeco-heading, h1, h2, h3');
      if (!heading) return null;
      const styles = getComputedStyle(heading);
      return {
        fontFamily: styles.fontFamily,
        fontWeight: styles.fontWeight,
        fontSize: styles.fontSize
      };
    });

    if (headingFont) {
      // 验证标题使用Marcellus字体（如果已加载）
      expect(headingFont.fontFamily).toMatch(/Marcellus|serif/i);
      expect(headingFont.fontWeight).toMatch(/^(400|500|600|700)$/);
    }

    // 检查正文字体
    const bodyFont = await page.evaluate(() => {
      const body = document.querySelector('.artdeco-body, p, span, div');
      if (!body) return null;
      const styles = getComputedStyle(body);
      return {
        fontFamily: styles.fontFamily,
        fontWeight: styles.fontWeight,
        fontSize: styles.fontSize
      };
    });

    if (bodyFont) {
      // 验证正文使用Josefin Sans字体（如果已加载）
      expect(bodyFont.fontFamily).toMatch(/Josefin Sans|sans-serif/i);
    }
  });

  test('菜单项应该有ArtDeco风格样式', async ({ page }) => {
    const navItem = page.locator('.nav-item').first();

    // 获取计算样式
    const styles = await navItem.evaluate((el) => {
      const styles = getComputedStyle(el);
      return {
        borderLeft: styles.borderLeft,
        borderLeftColor: styles.borderLeftColor,
        paddingLeft: styles.paddingLeft,
        color: styles.color,
        transition: styles.transition
      };
    });

    // 验证左侧金色边框
    expect(styles.borderLeft).toMatch(/\d+px/);

    // 验证颜色包含金色RGB值
    expect(styles.borderLeftColor).toBe('rgb(212, 175, 55)');

    // 验证内边距
    expect(parseInt(styles.paddingLeft)).toBeGreaterThan(10);

    // 验证过渡动画
    expect(styles.transition).toContain('all');
  });

  test('菜单项悬停状态应该正确应用', async ({ page }) => {
    const navItem = page.locator('.nav-item').first();

    // 悬停前状态
    const beforeHover = await navItem.evaluate((el) => {
      const styles = getComputedStyle(el);
      return {
        backgroundColor: styles.backgroundColor,
        color: styles.color
      };
    });

    // 悬停
    await navItem.hover();
    await page.waitForTimeout(300); // 等待过渡动画

    // 悬停后状态
    const afterHover = await navItem.evaluate((el) => {
      const styles = getComputedStyle(el);
      return {
        backgroundColor: styles.backgroundColor,
        color: styles.color
      };
    });

    // 验证背景色变化
    expect(afterHover.backgroundColor).not.toBe(beforeHover.backgroundColor);

    // 验证文字颜色变化
    expect(afterHover.color).toContain('255'); // 亮金色
  });

  test('ArtDeco卡片组件应该有几何装饰', async ({ page }) => {
    const card = page.locator('.artdeco-card, .artdeco-stat-card').first();

    if (await card.count() === 0) {
      test.skip();
      return;
    }

    // 验证装饰元素存在
    const decorations = await card.evaluate((el) => {
      // 检查伪元素
      const styles = getComputedStyle(el, '::before');
      const afterStyles = getComputedStyle(el, '::after');
      return {
        hasBeforeDecoration: styles.content !== 'none',
        hasAfterDecoration: afterStyles.content !== 'none',
        beforeBorder: styles.border,
        afterBorder: afterStyles.border
      };
    });

    // 验证至少有一个装饰元素
    expect(
      decorations.hasBeforeDecoration || decorations.hasAfterDecoration
    ).toBeTruthy();
  });

  test('Toast通知应该有ArtDeco样式', async ({ page }) => {
    // 触发Toast通知（如果存在错误Badge）
    const errorBadge = page.locator('.artdeco-badge--error, .api-error-badge').first();

    if (await errorBadge.count() > 0) {
      // 点击错误Badge触发Toast
      await errorBadge.click();
      await page.waitForTimeout(500);

      // 验证Toast存在
      const toast = page.locator('.artdeco-toast').first();
      await expect(toast).toBeVisible();

      // 验证Toast样式
      const toastStyles = await toast.evaluate((el) => {
        const styles = getComputedStyle(el);
        return {
          backgroundColor: styles.backgroundColor,
          borderRadius: styles.borderRadius,
          boxShadow: styles.boxShadow
        };
      });

      // 验证圆角（ArtDeco不使用圆角）
      expect(parseInt(toastStyles.borderRadius)).toBeLessThan(8);

      // 验证阴影（金色发光效果）
      expect(toastStyles.boxShadow).toContain('212, 175, 55');
    } else {
      test.skip();
    }
  });

  test('侧边栏应该有ArtDeco折叠效果', async ({ page }) => {
    const sidebar = page.locator('.layout-sidebar');
    const toggleButton = page.locator('.sidebar-toggle');

    if (await toggleButton.count() === 0) {
      test.skip();
      return;
    }

    // 初始状态
    const beforeCollapse = await sidebar.evaluate((el) => {
      const styles = getComputedStyle(el);
      return {
        width: styles.width,
        transition: styles.transition
      };
    });

    // 点击折叠
    await toggleButton.click();
    await page.waitForTimeout(300);

    // 折叠状态
    const afterCollapse = await sidebar.evaluate((el) => {
      const styles = getComputedStyle(el);
      return {
        width: styles.width
      };
    });

    // 验证宽度变化
    expect(parseInt(afterCollapse.width)).toBeLessThan(parseInt(beforeCollapse.width));

    // 验证过渡动画
    expect(beforeCollapse.transition).toContain('width');
  });

  test('响应式布局应该符合ArtDeco设计规范', async ({ page }) => {
    // 桌面端（1920x1080）
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForTimeout(300);

    const sidebarWidthDesktop = await page.locator('.layout-sidebar').evaluate((el) => {
      return getComputedStyle(el).width;
    });

    // 验证侧边栏宽度（桌面端应该较宽）
    expect(parseInt(sidebarWidthDesktop)).toBeGreaterThan(200);

    // 小屏幕（1280x720）
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.waitForTimeout(300);

    const sidebarWidthSmall = await page.locator('.layout-sidebar').evaluate((el) => {
      return getComputedStyle(el).width;
    });

    // 小屏幕侧边栏应该更窄（但不应该消失，因为不支持移动端）
    expect(parseInt(sidebarWidthSmall)).toBeLessThanOrEqual(parseInt(sidebarWidthDesktop));
  });

  test('颜色对比度应该符合WCAG AA标准', async ({ page }) => {
    const navItem = page.locator('.nav-item').first();

    const contrast = await navItem.evaluate((el) => {
      const styles = getComputedStyle(el);
      const textColor = styles.color;
      const bgColor = styles.backgroundColor;

      // 转换RGB到相对亮度（简化版）
      const getLuminance = (rgb: string) => {
        const match = rgb.match(/\d+/g);
        if (!match) return 0;
        const [r, g, b] = match.map(Number);
        const [rs, gs, bs] = [r, g, b].map(v => {
          v = v / 255;
          return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
        });
        return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
      };

      const l1 = getLuminance(textColor);
      const l2 = getLuminance(bgColor);
      const lighter = Math.max(l1, l2);
      const darker = Math.min(l1, l2);

      return (lighter + 0.05) / (darker + 0.05);
    });

    // WCAG AA标准：对比度至少4.5:1
    expect(contrast).toBeGreaterThanOrEqual(4.5);
  });

  test('截图对比：完整ArtDeco布局', async ({ page }) => {
    // 等待页面完全加载
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // 截图（用于视觉回归）
    await page.screenshot({
      path: 'test-results/artdeco-layout-full.png',
      fullPage: true
    });

    // 验证关键元素可见
    await expect(page.locator('.layout-header')).toBeVisible();
    await expect(page.locator('.layout-sidebar')).toBeVisible();
    await expect(page.locator('.layout-main')).toBeVisible();
  });

  test('截图对比：菜单项悬停状态', async ({ page }) => {
    const navItem = page.locator('.nav-item').first();
    await navItem.hover();
    await page.waitForTimeout(300);

    await page.screenshot({
      path: 'test-results/artdeco-menu-hover.png'
    });
  });
});

test.describe('ArtDeco组件快照测试', () => {
  test('菜单导航快照', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    // 等待菜单加载
    await page.waitForSelector('.nav-item');

    // 快照测试（仅包含菜单区域）
    const sidebar = page.locator('.layout-sidebar');
    await expect(sidebar).toHaveScreenshot('artdeco-menu-sidebar.png', {
      maxDiffPixels: 100
    });
  });

  test('ArtDeco卡片组件快照', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const cards = page.locator('.artdeco-card, .artdeco-stat-card');

    if (await cards.count() > 0) {
      await cards.first().screenshot({
        path: 'test-results/artdeco-card-component.png'
      });
    } else {
      test.skip();
    }
  });
});
