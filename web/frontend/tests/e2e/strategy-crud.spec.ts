/**
 * Strategy Management - CRUD Operations
 * 
 * End-to-end tests for creating, viewing, and deleting strategies.
 */

import { test, expect } from '@playwright/test';
import { loginAndSetupAuth } from './helpers/auth';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3020';

test.describe('Strategy Management - CRUD', () => {
  test.beforeEach(async ({ page, request }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await loginAndSetupAuth(request, page);
  });

  test.describe('Strategy List & Details', () => {
    test('should load strategy management page successfully', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy-hub/management`);
      await expect(page).toHaveTitle(/MyStocks/);
      const heading = page.locator('h1').filter({ hasText: /STRATEGY MANAGEMENT/ });
      await expect(heading).toBeVisible();
    });

    test('should display strategy cards', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      await page.waitForTimeout(2000);
      const strategyCards = page.locator('.strategy-card, [data-testid="strategy-card"]');
      const count = await strategyCards.count();
      expect(count).toBeGreaterThan(0);
    });

    test('should display strategy details correctly', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      await page.waitForTimeout(2000);
      const firstCard = page.locator('.strategy-card, [data-testid="strategy-card"]').first();
      const strategyName = firstCard.locator('.strategy-name, .name, [data-testid="strategy-name"]');
      await expect(strategyName).toBeVisible();
      const strategyType = firstCard.locator('.strategy-type, .type, [data-testid="strategy-type"]');
      await expect(strategyType).toBeVisible();
      const strategyStatus = firstCard.locator('.strategy-status, .status, [data-testid="strategy-status"]');
      await expect(strategyStatus).toBeVisible();
    });

    test('should navigate to strategy detail page', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      await page.waitForTimeout(2000);
      const firstCard = page.locator('.strategy-card, [data-testid="strategy-card"]').first();
      await firstCard.click();
      await page.waitForTimeout(1000);
      expect(page.url()).toContain('/strategy/');
    });

    test('should display strategy performance metrics', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      await page.waitForTimeout(2000);
      const firstCard = page.locator('.strategy-card, [data-testid="strategy-card"]').first();
      await firstCard.click();
      await page.waitForTimeout(1000);
      const performanceSection = page.locator('.performance-metrics, [data-testid="performance-metrics"]');
      if (await performanceSection.count() > 0) {
        await expect(performanceSection.first()).toBeVisible();
        await expect(page.locator('.total-return, [data-testid="total-return"]').first()).toBeVisible();
        await expect(page.locator('.sharpe-ratio, [data-testid="sharpe-ratio"]').first()).toBeVisible();
      }
    });
  });

  test.describe('Create Strategy', () => {
    test('should open create strategy dialog', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      await page.waitForTimeout(1000);
      const createButton = page.locator('button:has-text("创建策略"), button:has-text("新建"), [data-testid="create-strategy-button"]');
      if (await createButton.count() > 0) {
        await createButton.first().click();
        await page.waitForTimeout(500);
        await expect(page.locator('.dialog, .modal, [role="dialog"]').first()).toBeVisible();
      }
    });

    test('should validate strategy form fields', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      await page.waitForTimeout(1000);
      const createButton = page.locator('button:has-text("创建策略"), button:has-text("新建")');
      if (await createButton.count() > 0) {
        await createButton.first().click();
        await page.waitForTimeout(500);
        const submitButton = page.locator('button:has-text("提交"), button:has-text("创建"), button[type="submit"]');
        if (await submitButton.count() > 0) {
          await submitButton.first().click();
          const errorMessages = page.locator('.error-message, .validation-error, [data-testid="validation-error"]');
          if (await errorMessages.count() > 0) {
            await expect(errorMessages.first()).toBeVisible();
          }
        }
      }
    });

    test('should fill and submit create strategy form', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      await page.waitForTimeout(1000);
      const createButton = page.locator('button:has-text("创建策略"), button:has-text("新建")');
      if (await createButton.count() > 0) {
        await createButton.first().click();
        await page.waitForTimeout(500);
        const nameInput = page.locator('input[name="name"], [data-testid="strategy-name-input"]');
        if (await nameInput.count() > 0) {
          await nameInput.first().fill('测试策略');
          const typeSelect = page.locator('select[name="type"], [data-testid="strategy-type-select"]');
          if (await typeSelect.count() > 0) {
            await typeSelect.first().selectOption('trend_following');
            await page.locator('button:has-text("提交"), button[type="submit"]').first().click();
            await page.waitForTimeout(2000);
            const dialog = page.locator('.dialog, .modal, [role="dialog"]');
            if (await dialog.count() > 0) {
              expect(await dialog.first().isVisible()).toBeFalsy();
            }
          }
        }
      }
    });

    test('should display strategy type selector and options', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      const createButton = page.locator('button', { hasText: /CREATE|ADD/ }).first();
      await createButton.click();
      await page.waitForTimeout(500);
      await expect(page.locator('label', { hasText: /STRATEGY TYPE/ })).toBeVisible();
      const typeDropdown = page.locator('.el-select').filter({ has: page.locator('label', { hasText: /STRATEGY TYPE/ }) });
      await typeDropdown.click();
      await page.waitForTimeout(300);
      await expect(page.locator('.el-select-dropdown__item').filter({ hasText: 'TREND FOLLOWING' })).toBeVisible();
      await expect(page.locator('.el-select-dropdown__item').filter({ hasText: 'MEAN REVERSION' })).toBeVisible();
      await expect(page.locator('.el-select-dropdown__item').filter({ hasText: 'MOMENTUM' })).toBeVisible();
    });

    test('should create strategy with type and parameters', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      await page.locator('button', { hasText: /CREATE|ADD/ }).first().click();
      await page.waitForTimeout(500);
      await page.locator('input[name*="name"], input[placeholder*="NAME"]').first().fill('E2E Test Strategy');
      const typeDropdown = page.locator('.el-select').filter({ has: page.locator('label', { hasText: /STRATEGY TYPE/ }) });
      await typeDropdown.click();
      await page.waitForTimeout(300);
      await page.locator('.el-select-dropdown__item').filter({ hasText: 'TREND FOLLOWING' }).first().click();
      const addButton = page.locator('button', { hasText: /ADD PARAMETER/ });
      if (await addButton.count() > 0) {
        await addButton.first().click();
        await page.waitForTimeout(300);
        const paramInputs = page.locator('.parameter-row input');
        if (await paramInputs.count() >= 2) {
          await paramInputs.nth(0).fill('period');
          await paramInputs.nth(1).fill('20');
        }
      }
      await page.locator('button[type="submit"], button', { hasText: /CREATE|SUBMIT/ }).last().click();
      await page.waitForTimeout(1000);
      expect(await page.locator('.el-message').count()).toBeGreaterThan(0);
    });
  });

  test.describe('Delete Strategy', () => {
    test('should show delete confirmation dialog and cancel', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      await page.waitForTimeout(2000);
      const firstCard = page.locator('.strategy-card').first();
      const deleteButton = firstCard.locator('button', { hasText: /DELETE|REMOVE/ }).or(firstCard.locator('.el-icon[delete-icon]'));
      if (await deleteButton.count() > 0) {
        await deleteButton.first().click();
        await page.waitForTimeout(300);
        const confirmDialog = page.locator('.el-message-box').or(page.locator('.el-dialog'));
        if (await confirmDialog.count() > 0) {
          await expect(confirmDialog.locator('.el-message-box__title, .el-dialog__title')).toBeVisible();
          await confirmDialog.locator('button', { hasText: /CANCEL/ }).first().click();
        }
      }
    });

    test('should confirm and delete strategy', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      await page.waitForTimeout(2000);
      const firstCard = page.locator('.strategy-card').first();
      const deleteButton = firstCard.locator('button', { hasText: /DELETE|REMOVE/ });
      if (await deleteButton.count() > 0) {
        await deleteButton.first().click();
        await page.waitForTimeout(300);
        const confirmButton = page.locator('.el-message-box').locator('button', { hasText: /DELETE|CONFIRM/ }).or(page.locator('.el-message-box').locator('.el-button--danger'));
        if (await confirmButton.count() > 0) {
          await confirmButton.first().click();
          await page.waitForTimeout(1000);
          expect(await page.locator('.el-message--success').count()).toBeGreaterThan(0);
        }
      }
    });
  });
});
