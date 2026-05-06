import { test, expect } from '@playwright/test'

test.use({ serviceWorkers: 'block' })

test('trade reconciliation page imports and exports statement results', async ({ page }) => {
  let exportRequested = false

  await page.addInitScript(() => {
    localStorage.setItem('auth_token', 'e2e-auth-token')
    localStorage.setItem('auth_user', JSON.stringify({
      id: 1,
      username: 'e2e-admin',
      email: 'e2e-admin@example.com',
      role: 'admin',
      permissions: ['*'],
    }))
  })

  await page.route('**/api/auth/csrf', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ token: 'csrf-token' }),
    })
  })

  await page.route('**/*reconciliation/*', async (route) => {
    const url = route.request().url()

    if (url.includes('/accounts')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            status: 'available',
            endpoint: 'trade',
            resource: 'reconciliation_accounts',
            items: [
              {
                account_id: 'backtest:7',
                label: 'Backtest #7',
                account_type: 'backtest',
              },
            ],
            total_count: 1,
          },
        }),
      })
      return
    }

    if (url.includes('/statements')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            status: 'available',
            endpoint: 'trade',
            resource: 'reconciliation_statements',
            account_id: 'backtest:7',
            items: [
              {
                account_id: 'backtest:7',
                trade_id: '101',
                order_id: 'backtest-7-101',
                symbol: '600519.SH',
                direction: 'buy',
                trade_time: '2026-05-06T09:31:00',
                price: 1750,
                quantity: 100,
                amount: 175000,
                commission: 52.5,
              },
            ],
            summary: {
              total_count: 1,
              total_amount: 175000,
              total_commission: 52.5,
            },
            total_count: 1,
            page: 1,
            page_size: 20,
            source: 'backtest_trades',
          },
        }),
      })
      return
    }

    if (url.includes('/import')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            status: 'available',
            endpoint: 'trade',
            resource: 'reconciliation_import_batch',
            import_batch_id: 'batch-001',
            account_id: 'backtest:7',
            source_type: 'miniqmt',
            row_count: 3,
          },
        }),
      })
      return
    }

    if (url.includes('/results')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            status: 'available',
            endpoint: 'trade',
            resource: 'reconciliation_results',
            account_id: 'backtest:7',
            import_batch_id: 'batch-001',
            items: [
              {
                match_status: 'matched',
                internal_row: {
                  account_id: 'backtest:7',
                  trade_id: '101',
                  order_id: 'backtest-7-101',
                  symbol: '600519.SH',
                  direction: 'buy',
                  trade_time: '2026-05-06T09:31:00',
                  price: 1750,
                  quantity: 100,
                  amount: 175000,
                  commission: 52.5,
                },
                broker_row: {
                  account_id: 'backtest:7',
                  trade_id: '101',
                  order_id: 'backtest-7-101',
                  symbol: '600519.SH',
                  direction: 'buy',
                  trade_time: '2026-05-06T09:31:00',
                  price: 1750,
                  quantity: 100,
                  amount: 175000,
                  commission: 52.5,
                  source_type: 'miniqmt',
                  raw_row_number: 2,
                },
                mismatch_fields: [],
              },
            ],
            total_count: 1,
            page: 1,
            page_size: 20,
            source: 'backtest_trades',
            match_status: null,
          },
        }),
      })
      return
    }

    if (url.includes('/export')) {
      exportRequested = true
      await route.fulfill({
        status: 200,
        contentType: 'text/csv; charset=utf-8',
        body: 'match_status,symbol\nmatched,600519.SH\n',
      })
      return
    }

    await route.continue()
  })

  await page.goto('/trade/reconciliation')
  await page.waitForLoadState('networkidle')

  await expect(page.getByRole('heading', { name: '对账单工作台' })).toBeVisible()
  await expect(page.locator('[data-testid="reconciliation-account-select"]')).toHaveValue('backtest:7')
  await expect(page.getByText('600519.SH')).toBeVisible()

  await page.locator('[data-testid="reconciliation-source-select"]').selectOption('miniqmt')
  await page.locator('[data-testid="reconciliation-file-input"]').setInputFiles({
    name: 'miniqmt.csv',
    mimeType: 'text/csv',
    buffer: Buffer.from('csv'),
  })
  await page.getByRole('button', { name: '导入并对账' }).click()

  await expect(page.getByText('已匹配')).toBeVisible()

  await page.getByRole('button', { name: '导出 CSV' }).click()

  await expect.poll(() => exportRequested).toBe(true)
})
