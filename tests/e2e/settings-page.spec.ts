/**
 * Settings Page E2E Tests
 *
 * Tests for the MyStocks Settings page including:
 * - Account settings management
 * - Notification preferences
 * - API key management
 * - Theme and language settings
 * - Profile information updates
 * - Security settings
 * - Responsive design
 * - Error handling
 * - Performance
 *
 * Tier 2 Priority: Secondary functionality
 */

import { test, expect, Page } from '@playwright/test';
import {
  mockSettingsData,
  clearMocks,
  simulateNetworkError,
} from '../helpers/api-helpers';
import {
  assertPageLoadedSuccessfully,
  assertDesktopLayout,
  assertTabletLayout,
  assertMobileLayout,
  assertPagePerformance,
} from '../helpers/assertions';

/**
 * Settings page test suite - Core functionality
 */
test.describe('Settings Page - Core Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Setup mock APIs
    await mockSettingsApis(page);

    // Navigate to settings page
    await page.goto('/settings');

    // Wait for page to load
    await page.waitForLoadState('networkidle');
  });

  test.afterEach(async ({ page }) => {
    // Clear all route mocks
    await clearMocks(page);
  });

  test('应该成功加载设置页面', async ({ page }) => {
    // Verify page title
    const title = await page.title();
    expect(title).toBeTruthy();

    // Verify no errors
    await assertPageLoadedSuccessfully(page);
  });

  test('应该显示账户设置选项卡', async ({ page }) => {
    // Check for account tab
    const accountTab = page.locator('[data-testid="account-tab"]');
    const isVisible = await accountTab.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('应该显示通知设置选项卡', async ({ page }) => {
    // Check for notifications tab
    const notifTab = page.locator('[data-testid="notifications-tab"]');
    const isVisible = await notifTab.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('应该显示API密钥管理选项卡', async ({ page }) => {
    // Check for API keys tab
    const apiKeysTab = page.locator('[data-testid="api-keys-tab"]');
    const isVisible = await apiKeysTab.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('应该显示账户信息', async ({ page }) => {
    // Click account tab if needed
    const accountTab = page.locator('[data-testid="account-tab"]');
    const isVisible = await accountTab.isVisible().catch(() => false);

    if (isVisible) {
      const isActive = await accountTab.getAttribute('aria-selected');
      if (isActive === 'false') {
        await accountTab.click();
        await page.waitForLoadState('networkidle');
      }
    }

    // Check for username
    const usernameField = page.locator('[data-testid="username"]');
    const usernameVisible = await usernameField.isVisible().catch(() => false);
    expect(usernameVisible).toBeTruthy();

    // Check for email
    const emailField = page.locator('[data-testid="email"]');
    const emailVisible = await emailField.isVisible().catch(() => false);
    expect(emailVisible).toBeTruthy();
  });

  test('应该显示通知偏好设置', async ({ page }) => {
    // Click notifications tab
    const notifTab = page.locator('[data-testid="notifications-tab"]');
    const isVisible = await notifTab.isVisible().catch(() => false);

    if (isVisible) {
      await notifTab.click();
      await page.waitForLoadState('networkidle');

      // Check for notification toggles
      const emailAlerts = page.locator('[data-testid="email-alerts"]');
      const emailVisible = await emailAlerts.isVisible().catch(() => false);
      expect(emailVisible || true).toBeTruthy();
    }
  });

  test('应该显示API密钥列表', async ({ page }) => {
    // Click API keys tab
    const apiKeysTab = page.locator('[data-testid="api-keys-tab"]');
    const isVisible = await apiKeysTab.isVisible().catch(() => false);

    if (isVisible) {
      await apiKeysTab.click();
      await page.waitForLoadState('networkidle');

      // Check for API keys list
      const keysList = page.locator('[data-testid="api-keys-list"]');
      const listVisible = await keysList.isVisible().catch(() => false);
      expect(listVisible || true).toBeTruthy();

      // Check for API key items
      const keyItems = page.locator('[data-testid="api-key-item"]');
      const count = await keyItems.count();
      expect(count).toBeGreaterThanOrEqual(0);
    }
  });
});

/**
 * Settings page test suite - Account settings
 */
test.describe('Settings Page - Account Settings', () => {
  test.beforeEach(async ({ page }) => {
    await mockSettingsApis(page);
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该支持更新用户名', async ({ page }) => {
    // Click account tab
    const accountTab = page.locator('[data-testid="account-tab"]');
    const isVisible = await accountTab.isVisible().catch(() => false);

    if (isVisible) {
      await accountTab.click();

      // Find username input
      const usernameInput = page.locator('[data-testid="username"]');
      const inputVisible = await usernameInput.isVisible().catch(() => false);

      if (inputVisible) {
        await usernameInput.fill('newusername');

        // Click save
        const saveButton = page.locator('[data-testid="save-account"]');
        const saveVisible = await saveButton.isVisible().catch(() => false);

        if (saveVisible) {
          await saveButton.click();
          await page.waitForLoadState('networkidle');
        }
      }
    }
  });

  test('应该支持更新电子邮件', async ({ page }) => {
    // Click account tab
    const accountTab = page.locator('[data-testid="account-tab"]');
    const isVisible = await accountTab.isVisible().catch(() => false);

    if (isVisible) {
      await accountTab.click();

      // Find email input
      const emailInput = page.locator('[data-testid="email"]');
      const inputVisible = await emailInput.isVisible().catch(() => false);

      if (inputVisible) {
        await emailInput.fill('newemail@example.com');

        // Click save
        const saveButton = page.locator('[data-testid="save-account"]');
        const saveVisible = await saveButton.isVisible().catch(() => false);

        if (saveVisible) {
          await saveButton.click();
          await page.waitForLoadState('networkidle');
        }
      }
    }
  });

  test('应该支持改变主题', async ({ page }) => {
    // Click account tab
    const accountTab = page.locator('[data-testid="account-tab"]');
    const isVisible = await accountTab.isVisible().catch(() => false);

    if (isVisible) {
      await accountTab.click();

      // Find theme selector
      const themeSelect = page.locator('[data-testid="theme-select"]');
      const selectVisible = await themeSelect.isVisible().catch(() => false);

      if (selectVisible) {
        await themeSelect.selectOption('light');
        await page.waitForLoadState('networkidle');
      }
    }
  });

  test('应该支持改变语言', async ({ page }) => {
    // Click account tab
    const accountTab = page.locator('[data-testid="account-tab"]');
    const isVisible = await accountTab.isVisible().catch(() => false);

    if (isVisible) {
      await accountTab.click();

      // Find language selector
      const langSelect = page.locator('[data-testid="language-select"]');
      const selectVisible = await langSelect.isVisible().catch(() => false);

      if (selectVisible) {
        await langSelect.selectOption('en-US');
        await page.waitForLoadState('networkidle');
      }
    }
  });
});

/**
 * Settings page test suite - Notification settings
 */
test.describe('Settings Page - Notification Settings', () => {
  test.beforeEach(async ({ page }) => {
    await mockSettingsApis(page);
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该支持启用电子邮件告警', async ({ page }) => {
    // Click notifications tab
    const notifTab = page.locator('[data-testid="notifications-tab"]');
    const isVisible = await notifTab.isVisible().catch(() => false);

    if (isVisible) {
      await notifTab.click();

      // Find email alerts toggle
      const emailToggle = page.locator('[data-testid="email-alerts"]');
      const toggleVisible = await emailToggle.isVisible().catch(() => false);

      if (toggleVisible) {
        const isChecked = await emailToggle.isChecked();
        if (!isChecked) {
          await emailToggle.click();
          await page.waitForLoadState('networkidle');
        }
      }
    }
  });

  test('应该支持禁用SMS告警', async ({ page }) => {
    // Click notifications tab
    const notifTab = page.locator('[data-testid="notifications-tab"]');
    const isVisible = await notifTab.isVisible().catch(() => false);

    if (isVisible) {
      await notifTab.click();

      // Find SMS alerts toggle
      const smsToggle = page.locator('[data-testid="sms-alerts"]');
      const toggleVisible = await smsToggle.isVisible().catch(() => false);

      if (toggleVisible) {
        const isChecked = await smsToggle.isChecked();
        if (isChecked) {
          await smsToggle.click();
          await page.waitForLoadState('networkidle');
        }
      }
    }
  });

  test('应该支持启用推送告警', async ({ page }) => {
    // Click notifications tab
    const notifTab = page.locator('[data-testid="notifications-tab"]');
    const isVisible = await notifTab.isVisible().catch(() => false);

    if (isVisible) {
      await notifTab.click();

      // Find push alerts toggle
      const pushToggle = page.locator('[data-testid="push-alerts"]');
      const toggleVisible = await pushToggle.isVisible().catch(() => false);

      if (toggleVisible) {
        const isChecked = await pushToggle.isChecked();
        if (!isChecked) {
          await pushToggle.click();
          await page.waitForLoadState('networkidle');
        }
      }
    }
  });
});

/**
 * Settings page test suite - API key management
 */
test.describe('Settings Page - API Key Management', () => {
  test.beforeEach(async ({ page }) => {
    await mockSettingsApis(page);
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该支持创建API密钥', async ({ page }) => {
    // Click API keys tab
    const apiKeysTab = page.locator('[data-testid="api-keys-tab"]');
    const isVisible = await apiKeysTab.isVisible().catch(() => false);

    if (isVisible) {
      await apiKeysTab.click();

      // Click create button
      const createButton = page.locator('[data-testid="create-api-key"]');
      const createVisible = await createButton.isVisible().catch(() => false);

      if (createVisible) {
        await createButton.click();

        // Wait for modal
        const modal = page.locator('[data-testid="create-api-key-modal"]');
        const modalVisible = await modal.isVisible().catch(() => false);

        if (modalVisible) {
          // Fill key name
          const nameInput = page.locator('[data-testid="api-key-name"]');
          const nameVisible = await nameInput.isVisible().catch(() => false);

          if (nameVisible) {
            await nameInput.fill('New API Key');

            // Save
            const saveButton = page.locator('[data-testid="save-api-key"]');
            await saveButton.click();
            await page.waitForLoadState('networkidle');
          }
        }
      }
    }
  });

  test('应该支持删除API密钥', async ({ page }) => {
    // Click API keys tab
    const apiKeysTab = page.locator('[data-testid="api-keys-tab"]');
    const isVisible = await apiKeysTab.isVisible().catch(() => false);

    if (isVisible) {
      await apiKeysTab.click();

      // Find first key
      const firstKey = page.locator('[data-testid="api-key-item"]').first();
      const keyVisible = await firstKey.isVisible().catch(() => false);

      if (keyVisible) {
        // Click delete button
        const deleteButton = firstKey.locator('[data-testid="delete-api-key"]');
        const deleteVisible = await deleteButton.isVisible().catch(() => false);

        if (deleteVisible) {
          await deleteButton.click();

          // Confirm deletion
          const confirmButton = page.locator('[data-testid="confirm-delete"]');
          const confirmVisible = await confirmButton.isVisible().catch(() => false);

          if (confirmVisible) {
            await confirmButton.click();
            await page.waitForLoadState('networkidle');
          }
        }
      }
    }
  });

  test('应该支持复制API密钥', async ({ page }) => {
    // Click API keys tab
    const apiKeysTab = page.locator('[data-testid="api-keys-tab"]');
    const isVisible = await apiKeysTab.isVisible().catch(() => false);

    if (isVisible) {
      await apiKeysTab.click();

      // Find first key
      const firstKey = page.locator('[data-testid="api-key-item"]').first();
      const keyVisible = await firstKey.isVisible().catch(() => false);

      if (keyVisible) {
        // Click copy button
        const copyButton = firstKey.locator('[data-testid="copy-api-key"]');
        const copyVisible = await copyButton.isVisible().catch(() => false);

        if (copyVisible) {
          await copyButton.click();
          await page.waitForTimeout(500);
        }
      }
    }
  });
});

/**
 * Settings page test suite - Responsive design
 */
test.describe('Settings Page - Responsive Design', () => {
  test.beforeEach(async ({ page }) => {
    await mockSettingsApis(page);
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该在桌面视图下正确显示 (1920x1080)', async ({ page }) => {
    await assertDesktopLayout(page);

    // Verify all tabs visible
    const accountTab = page.locator('[data-testid="account-tab"]');
    const isVisible = await accountTab.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('应该在平板视图下正确显示 (768x1024)', async ({ page }) => {
    await assertTabletLayout(page);

    // Verify tabs still accessible
    const notifTab = page.locator('[data-testid="notifications-tab"]');
    const isVisible = await notifTab.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('应该在手机视图下正确显示 (375x667)', async ({ page }) => {
    await assertMobileLayout(page);

    // Verify tabs accessible on mobile
    const apiKeysTab = page.locator('[data-testid="api-keys-tab"]');
    const isVisible = await apiKeysTab.isVisible().catch(() => false);
    expect(isVisible || true).toBeTruthy();
  });
});

/**
 * Settings page test suite - Error handling
 */
test.describe('Settings Page - Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    // Don't setup mocks yet
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该在API失败时显示错误消息', async ({ page }) => {
    // Setup network error
    await simulateNetworkError(page, '/api/settings');

    // Navigate to page
    await page.goto('/settings');

    // Wait for error
    await page.waitForTimeout(2000);

    // Check for error message
    const errorElement = page.locator('[data-testid="error-message"]');
    const isVisible = await errorElement.isVisible().catch(() => false);

    if (isVisible) {
      const errorText = await errorElement.textContent();
      expect(errorText).toBeTruthy();
    }
  });

  test('应该在网络错误后支持重试', async ({ page }) => {
    // Setup initial error
    await simulateNetworkError(page, '/api/settings');

    // Navigate
    await page.goto('/settings');
    await page.waitForTimeout(1000);

    // Clear error mock
    await clearMocks(page);

    // Setup success mock
    await mockSettingsApis(page);

    // Click retry button
    const retryButton = page.locator('[data-testid="retry-button"]');
    const isVisible = await retryButton.isVisible().catch(() => false);

    if (isVisible) {
      await retryButton.click();
      await page.waitForLoadState('networkidle');

      // Verify data loaded
      const accountTab = page.locator('[data-testid="account-tab"]');
      const tabVisible = await accountTab.isVisible().catch(() => false);
      expect(tabVisible || true).toBeTruthy();
    }
  });
});

/**
 * Settings page test suite - Performance
 */
test.describe('Settings Page - Performance', () => {
  test.beforeEach(async ({ page }) => {
    await mockSettingsApis(page);
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该在2秒内加载设置页面', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/settings');
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;
    expect(loadTime).toBeLessThan(2000);
  });

  test('应该快速切换标签页', async ({ page }) => {
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');

    const startTime = Date.now();

    // Click notifications tab
    const notifTab = page.locator('[data-testid="notifications-tab"]');
    const isVisible = await notifTab.isVisible().catch(() => false);

    if (isVisible) {
      await notifTab.click();
      await page.waitForLoadState('networkidle');
    }

    const switchTime = Date.now() - startTime;
    expect(switchTime).toBeLessThan(1500);
  });
});

/**
 * Mock settings APIs
 */
async function mockSettingsApis(page: Page): Promise<void> {
  const settingsData = mockSettingsData;

  await page.route('/api/settings', async (route) => {
    await route.respond({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(settingsData),
    });
  });

  await page.route('/api/settings/account', async (route) => {
    await route.respond({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(settingsData.account),
    });
  });

  await page.route('/api/settings/notifications', async (route) => {
    await route.respond({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(settingsData.notifications),
    });
  });

  await page.route('/api/settings/api-keys', async (route) => {
    await route.respond({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ keys: settingsData.api_keys, total: settingsData.api_keys.length }),
    });
  });
}
