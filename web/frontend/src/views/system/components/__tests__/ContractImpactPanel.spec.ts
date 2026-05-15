import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { assessContractImpact } from '@/api/contractImpact'
import ContractImpactPanel from '../ContractImpactPanel.vue'

vi.mock('@/api/contractImpact', () => ({
  assessContractImpact: vi.fn(),
}))

const impactResponse = {
  success: true,
  code: 200,
  message: 'ok',
  timestamp: '2026-05-15T00:00:00Z',
  request_id: 'req_contract_impact',
  data: {
    from_version: '1.0.0',
    to_version: '2.0.0',
    risk_level: 'critical',
    summary: {
      total_impacts: 2,
      breaking_impacts: 1,
      non_breaking_impacts: 1,
      by_category: { endpoint: 1, schema: 1 },
    },
    impacts: [
      {
        category: 'endpoint',
        name: 'GET /api/v1/market/quotes',
        path: '/api/v1/market/quotes',
        change_type: 'removed',
        severity: 'critical',
        is_breaking: true,
        reason: 'Endpoint was removed',
      },
    ],
    affected_endpoints: ['/api/v1/market/quotes'],
    affected_schemas: ['QuoteResponse'],
    affected_clients: ['market'],
    recommendations: ['Provide migration guide before rollout'],
    migration_effort: {
      level: 'high',
      score: 11,
      estimated_hours_min: 8,
      estimated_hours_max: 16,
      drivers: ['1 breaking endpoint change'],
    },
  },
}

describe('ContractImpactPanel', () => {
  beforeEach(() => {
    vi.mocked(assessContractImpact).mockReset()
    vi.mocked(assessContractImpact).mockResolvedValue({
      ...impactResponse,
      data: {
        analysis: impactResponse.data,
        hasBreakingChanges: true,
        requiresMigration: true,
        riskRank: 5,
        criticalImpactCount: 1,
        affectedSurfaceCount: 3,
        topImpacts: impactResponse.data.impacts,
      },
    })
  })

  it('requests impact analysis with selected version ids and renders governance summary', async () => {
    const wrapper = mount(ContractImpactPanel)

    await wrapper.find('[data-test="from-version-input"]').setValue('3')
    await wrapper.find('[data-test="to-version-input"]').setValue('7')
    expect(wrapper.find('[data-test="analyze-impact-button"]').attributes('disabled')).toBeUndefined()

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(assessContractImpact).toHaveBeenCalledWith({ fromVersionId: 3, toVersionId: 7 })
    expect(wrapper.text()).toContain('critical')
    expect(wrapper.text()).toContain('2')
    expect(wrapper.text()).toContain('/api/v1/market/quotes')
    expect(wrapper.text()).toContain('Provide migration guide before rollout')
  })
})
