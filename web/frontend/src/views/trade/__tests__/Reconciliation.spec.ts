import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const {
  getReconciliationAccountsMock,
  getReconciliationStatementsMock,
  importReconciliationCsvMock,
  getReconciliationResultsMock,
  exportReconciliationResultsMock,
} = vi.hoisted(() => ({
  getReconciliationAccountsMock: vi.fn(),
  getReconciliationStatementsMock: vi.fn(),
  importReconciliationCsvMock: vi.fn(),
  getReconciliationResultsMock: vi.fn(),
  exportReconciliationResultsMock: vi.fn(),
}))

vi.mock('@/api/trade', () => ({
  tradeApi: {
    getReconciliationAccounts: getReconciliationAccountsMock,
    getReconciliationStatements: getReconciliationStatementsMock,
    importReconciliationCsv: importReconciliationCsvMock,
    getReconciliationResults: getReconciliationResultsMock,
    exportReconciliationResults: exportReconciliationResultsMock,
  },
}))

vi.mock('@/components/artdeco', async () => {
  const { default: ArtDecoStatCard } = await import('@/components/artdeco/base/ArtDecoStatCard.vue')

  return {
    ArtDecoButton: {
      props: ['loading', 'disabled'],
      emits: ['click'],
      template: '<button :disabled="disabled" @click="$emit(\'click\')"><slot /><slot name="icon" /></button>',
    },
    ArtDecoCard: {
      props: ['title'],
      template: '<section><h2 v-if="title">{{ title }}</h2><slot /></section>',
    },
    ArtDecoHeader: {
      props: ['title', 'subtitle', 'statusText'],
      template: '<header><h1>{{ title }}</h1><p>{{ subtitle }}</p><span>{{ statusText }}</span><slot name="actions" /></header>',
    },
    ArtDecoIcon: {
      template: '<span />',
    },
    ArtDecoStatCard,
  }
})

import TradeReconciliationPage from '../Reconciliation.vue'

const reconciliationAccounts = [
  { accountId: 'backtest:7', label: 'Backtest #7', accountType: 'backtest' },
  { accountId: 'backtest:8', label: 'Backtest #8', accountType: 'backtest' },
]

const statementsPayloadByAccount = {
  'backtest:7': {
    status: 'available',
    endpoint: 'trade',
    resource: 'reconciliation_statements',
    accountId: 'backtest:7',
    items: [
      {
        accountId: 'backtest:7',
        tradeId: '101',
        orderId: 'backtest-7-101',
        symbol: '600519.SH',
        direction: 'buy',
        tradeTime: '2026-05-06T09:31:00',
        price: 1750,
        quantity: 100,
        amount: 175000,
        commission: 52.5,
      },
    ],
    summary: {
      totalCount: 1,
      totalAmount: 175000,
      totalCommission: 52.5,
    },
    totalCount: 1,
    page: 1,
    pageSize: 20,
    source: 'backtest_trades',
  },
  'backtest:8': {
    status: 'available',
    endpoint: 'trade',
    resource: 'reconciliation_statements',
    accountId: 'backtest:8',
    items: [
      {
        accountId: 'backtest:8',
        tradeId: '202',
        orderId: 'backtest-8-202',
        symbol: '300750.SZ',
        direction: 'sell',
        tradeTime: '2026-05-06T10:15:00',
        price: 212.5,
        quantity: 50,
        amount: 10625,
        commission: 6.2,
      },
    ],
    summary: {
      totalCount: 1,
      totalAmount: 10625,
      totalCommission: 6.2,
    },
    totalCount: 1,
    page: 1,
    pageSize: 20,
    source: 'backtest_trades',
  },
} as const

const resultsPayload = {
  status: 'available',
  endpoint: 'trade',
  resource: 'reconciliation_results',
  accountId: 'backtest:7',
  importBatchId: 'batch-7',
  items: [
    {
      matchStatus: 'matched',
      internalRow: statementsPayloadByAccount['backtest:7'].items[0],
      brokerRow: {
        accountId: 'backtest:7',
        tradeId: '101',
        orderId: 'backtest-7-101',
        symbol: '600519.SH',
        direction: 'buy',
        tradeTime: '2026-05-06T09:31:00',
        price: 1750,
        quantity: 100,
        amount: 175000,
        commission: 52.5,
        sourceType: 'miniqmt',
        rawRowNumber: 2,
      },
      mismatchFields: [],
    },
    {
      matchStatus: 'mismatched',
      internalRow: {
        accountId: 'backtest:7',
        tradeId: '102',
        orderId: 'backtest-7-102',
        symbol: '601318.SH',
        direction: 'sell',
        tradeTime: '2026-05-06T10:01:00',
        price: 55.5,
        quantity: 300,
        amount: 16650,
        commission: 5.1,
      },
      brokerRow: {
        accountId: 'backtest:7',
        tradeId: '102-broker',
        orderId: 'backtest-7-102',
        symbol: '601318.SH',
        direction: 'sell',
        tradeTime: '2026-05-06T10:01:00',
        price: 55.5,
        quantity: 300,
        amount: 16660,
        commission: 5.5,
        sourceType: 'miniqmt',
        rawRowNumber: 3,
      },
      mismatchFields: ['amount', 'commission'],
    },
    {
      matchStatus: 'missing_broker_record',
      internalRow: {
        accountId: 'backtest:7',
        tradeId: '103',
        orderId: 'backtest-7-103',
        symbol: '000001.SZ',
        direction: 'buy',
        tradeTime: '2026-05-06T10:21:00',
        price: 12.5,
        quantity: 1000,
        amount: 12500,
        commission: 4.1,
      },
      brokerRow: null,
      mismatchFields: [],
    },
  ],
  totalCount: 3,
  page: 1,
  pageSize: 20,
  source: 'backtest_trades',
  matchStatus: null,
} as const

describe('Trade reconciliation statement page', () => {
  beforeEach(() => {
    getReconciliationAccountsMock.mockReset().mockResolvedValue(reconciliationAccounts)
    getReconciliationStatementsMock.mockReset().mockImplementation(({ accountId }: { accountId: 'backtest:7' | 'backtest:8' }) => {
      return Promise.resolve(statementsPayloadByAccount[accountId])
    })
    importReconciliationCsvMock.mockReset().mockResolvedValue({
      status: 'available',
      endpoint: 'trade',
      resource: 'reconciliation_import_batch',
      importBatchId: 'batch-7',
      accountId: 'backtest:7',
      sourceType: 'miniqmt',
      rowCount: 3,
    })
    getReconciliationResultsMock.mockReset().mockResolvedValue(resultsPayload)
    exportReconciliationResultsMock.mockReset().mockResolvedValue(new Blob(['csv']))

    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})

    Object.defineProperty(URL, 'createObjectURL', {
      configurable: true,
      writable: true,
      value: vi.fn(() => 'blob:test-reconciliation'),
    })
    Object.defineProperty(URL, 'revokeObjectURL', {
      configurable: true,
      writable: true,
      value: vi.fn(),
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('loads reconciliation accounts and the default statement snapshot on mount', async () => {
    const wrapper = mount(TradeReconciliationPage as never)

    await flushPromises()

    expect(getReconciliationAccountsMock).toHaveBeenCalledTimes(1)
    expect(getReconciliationStatementsMock).toHaveBeenCalledWith(
      expect.objectContaining({ accountId: 'backtest:7' }),
    )
    expect(wrapper.text()).toContain('对账单工作台')
    expect(wrapper.text()).toContain('Backtest #7')
    expect(wrapper.text()).toContain('600519.SH')
    expect(wrapper.text()).toContain('175,000.00')
  })

  it('switches account and refreshes the statement snapshot with the selected account truth', async () => {
    const wrapper = mount(TradeReconciliationPage as never)

    await flushPromises()

    await wrapper.get('[data-testid="reconciliation-account-select"]').setValue('backtest:8')
    await flushPromises()

    expect(getReconciliationStatementsMock).toHaveBeenLastCalledWith(
      expect.objectContaining({ accountId: 'backtest:8' }),
    )
    expect(wrapper.text()).toContain('300750.SZ')
    expect(wrapper.text()).toContain('10,625.00')
  })

  it('imports a broker csv and renders matched, mismatched, and missing broker statuses as read-only results', async () => {
    const wrapper = mount(TradeReconciliationPage as never)

    await flushPromises()

    const importFile = new File(['csv'], 'miniqmt.csv', { type: 'text/csv' })
    await wrapper.get('[data-testid="reconciliation-source-select"]').setValue('miniqmt')
    const fileInput = wrapper.get('[data-testid="reconciliation-file-input"]')
    Object.defineProperty(fileInput.element, 'files', {
      configurable: true,
      value: [importFile],
    })
    await fileInput.trigger('change')
    await wrapper.get('[data-testid="reconciliation-import-button"]').trigger('click')
    await flushPromises()

    expect(importReconciliationCsvMock).toHaveBeenCalledWith(
      expect.objectContaining({
        file: importFile,
        sourceType: 'miniqmt',
        accountId: 'backtest:7',
      }),
    )
    expect(getReconciliationResultsMock).toHaveBeenCalledWith(
      expect.objectContaining({
        accountId: 'backtest:7',
        importBatchId: 'batch-7',
      }),
    )
    expect(wrapper.text()).toContain('已匹配')
    expect(wrapper.text()).toContain('差异')
    expect(wrapper.text()).toContain('缺少券商记录')
    expect(wrapper.text()).toContain('601318.SH')
    expect(wrapper.text()).toContain('000001.SZ')
  })

  it('exports the current reconciliation result set after an import batch is available', async () => {
    const wrapper = mount(TradeReconciliationPage as never)

    await flushPromises()

    const importFile = new File(['csv'], 'miniqmt.csv', { type: 'text/csv' })
    await wrapper.get('[data-testid="reconciliation-source-select"]').setValue('miniqmt')
    const fileInput = wrapper.get('[data-testid="reconciliation-file-input"]')
    Object.defineProperty(fileInput.element, 'files', {
      configurable: true,
      value: [importFile],
    })
    await fileInput.trigger('change')
    await wrapper.get('[data-testid="reconciliation-import-button"]').trigger('click')
    await flushPromises()

    await wrapper.get('[data-testid="reconciliation-export-button"]').trigger('click')
    await flushPromises()

    expect(exportReconciliationResultsMock).toHaveBeenCalledWith(
      expect.objectContaining({
        accountId: 'backtest:7',
        importBatchId: 'batch-7',
      }),
    )
  })
})
