import { expect, type Page } from "@playwright/test"

export async function waitForAppReady(page: Page, timeout = 15000): Promise<void> {
  const readyLocator = page.locator('[data-readiness-state="ready"]')
  const errorLocator = page.locator('[data-testid="app-readiness-error"]')
  const retryButton = page.locator('.app-readiness-action')

  for (let attempt = 0; attempt < 2; attempt += 1) {
    try {
      await expect(readyLocator).toBeVisible({ timeout })
      return
    } catch (error) {
      const isErrorVisible = await errorLocator.isVisible().catch(() => false)
      const canRetry = attempt === 0 && isErrorVisible && await retryButton.isVisible().catch(() => false)

      if (canRetry) {
        await retryButton.click()
        continue
      }

      throw error
    }
  }
}
