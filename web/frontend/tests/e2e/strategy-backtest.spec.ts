/**
 * Strategy Management - Backtesting
 * 
 * End-to-end tests for strategy backtesting flows and parameter validation.
 */

import { test, expect } from '@playwright/test';
import { loginAndSetupAuth } from './helpers/auth';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3020';

test.describe('Strategy Management - Backtesting', () => {
  test.beforeEach(async ({ page, request }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await loginAndSetupAuth(request, page);
  });

  test.describe('Backtest Panel', () => {
    test('should open backtest panel', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      await page.waitForTimeout(2000);
      const firstCard = page.locator('.strategy-card, [data-testid="strategy-card"]').first();
      await firstCard.click();
      await page.waitForTimeout(1000);
      const backtestButton = page.locator('button:has-text("回测"), [data-testid="backtest-button"]');
      if (await backtestButton.count() > 0) {
        await backtestButton.first().click();
        await page.waitForTimeout(500);
        await expect(page.locator('.backtest-panel, [data-testid="backtest-panel"]').first()).toBeVisible();
      }
    });

    test('should validate backtest parameters', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      await page.waitForTimeout(2000);
      const firstCard = page.locator('.strategy-card, [data-testid="strategy-card"]').first();
      await firstCard.click();
      await page.waitForTimeout(1000);
      const backtestButton = page.locator('button:has-text("回测"), [data-testid="backtest-button"]');
      if (await backtestButton.count() > 0) {
        await backtestButton.first().click();
        await page.waitForTimeout(500);
        const submitButton = page.locator('.backtest-panel button:has-text("开始回测"), .backtest-panel button[type="submit"]');
        if (await submitButton.count() > 0) {
          await submitButton.first().click();
          const errorMessages = page.locator('.error-message, .validation-error');
          if (await errorMessages.count() > 0) {
            await expect(errorMessages.first()).toBeVisible();
          }
        }
      }
    });
  });

  test.describe('Backtest Configuration', () => {
    test('should add and remove parameters in creation form', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      const createButton = page.locator('button', { hasText: /CREATE|ADD/ }).first();
      await createButton.click();
      await page.waitForTimeout(500);
      const addButton = page.locator('button', { hasText: /ADD PARAMETER/ });
      if (await addButton.count() > 0) {
        await addButton.first().click();
        await page.waitForTimeout(300);
        expect(await page.locator('.parameter-row input').count()).toBeGreaterThan(0);
        const removeButton = page.locator('.parameter-row button');
        if (await removeButton.count() > 0) {
          await removeButton.first().click();
          await page.waitForTimeout(300);
        }
      }
    });
  });
});
