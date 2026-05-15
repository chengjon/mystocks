import { beforeEach, describe, expect, it, vi } from 'vitest'

import { apiClient } from '../apiClient'
import {
  analyzeContractImpact,
  assessContractImpact,
  buildContractImpactAssessment,
  requestContractImpactAnalysis,
  type ContractImpactAnalysis,
} from '../contractImpact'

vi.mock('../apiClient', () => ({
  apiClient: {
    post: vi.fn(),
  },
}))

const analysis: ContractImpactAnalysis = {
  from_version: '1.0.0',
  to_version: '2.0.0',
  risk_level: 'critical',
  summary: {
    total_impacts: 3,
    breaking_impacts: 2,
    non_breaking_impacts: 1,
    by_category: {
      endpoint: 2,
      schema: 1,
    },
  },
  impacts: [
    {
      category: 'schema',
      name: 'QuoteResponse',
      path: 'components.schemas.QuoteResponse',
      change_type: 'property_removed',
      severity: 'high',
      is_breaking: true,
      reason: 'Required response property was removed',
    },
    {
      category: 'endpoint',
      name: 'GET /api/v1/quotes',
      path: '/api/v1/quotes',
      change_type: 'endpoint_removed',
      severity: 'critical',
      is_breaking: true,
      reason: 'Endpoint was removed',
    },
    {
      category: 'endpoint',
      name: 'GET /api/v1/status',
      path: '/api/v1/status',
      change_type: 'description_changed',
      severity: 'low',
      is_breaking: false,
      reason: 'Description changed',
    },
  ],
  affected_endpoints: ['/api/v1/quotes'],
  affected_schemas: ['QuoteResponse'],
  affected_clients: ['market'],
  recommendations: ['Create a migration plan before release'],
  migration_effort: {
    level: 'high',
    score: 80,
    estimated_hours_min: 8,
    estimated_hours_max: 16,
    drivers: ['Removed endpoint'],
  },
}

const analysisWithNotifications = {
  ...analysis,
  notifications: [
    {
      kind: 'contract_impact',
      priority: 'urgent',
      title: 'Contract impact 1.0.0 -> 2.0.0: critical risk',
      message: '3 impact(s), 2 breaking; migration effort high (8-16h).',
      targets: ['api-governance', 'market'],
      action_required: true,
      action_url: '/system/api',
      metadata: {
        risk_level: 'critical',
      },
    },
    {
      kind: 'contract_impact',
      priority: 'low',
      title: 'Contract impact observed',
      message: 'Non-breaking change detected.',
      targets: ['api-governance'],
      action_required: false,
      action_url: null,
      metadata: {},
    },
  ],
} satisfies ContractImpactAnalysis

describe('contractImpact API client', () => {
  beforeEach(() => {
    vi.mocked(apiClient.post).mockReset()
  })

  it('posts version ids to the canonical contract impact endpoint', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({ success: true, code: 200, data: analysis } as never)

    await analyzeContractImpact({ fromVersionId: 3, toVersionId: 7 })
    await requestContractImpactAnalysis({ from_version_id: 3, to_version_id: 7 })

    expect(apiClient.post).toHaveBeenCalledWith('/contracts/impact', {
      from_version_id: 3,
      to_version_id: 7,
    })
    expect(apiClient.post).toHaveBeenCalledTimes(2)
  })

  it('builds a UI-ready assessment from backend impact analysis', () => {
    const assessment = buildContractImpactAssessment(analysis)

    expect(assessment.hasBreakingChanges).toBe(true)
    expect(assessment.requiresMigration).toBe(true)
    expect(assessment.riskRank).toBe(5)
    expect(assessment.criticalImpactCount).toBe(1)
    expect(assessment.affectedSurfaceCount).toBe(3)
    expect(assessment.topImpacts.map((impact) => impact.severity)).toEqual(['critical', 'high', 'low'])
  })

  it('keeps automated impact notifications available for UI surfaces', () => {
    const assessment = buildContractImpactAssessment(analysisWithNotifications)

    expect(assessment.notifications.map((notification) => notification.priority)).toEqual(['urgent', 'low'])
    expect(assessment.actionableNotificationCount).toBe(1)
  })

  it('returns assessed impact data while preserving the unified response envelope', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      success: true,
      code: 200,
      message: 'ok',
      data: analysis,
      timestamp: '2026-05-15T00:00:00Z',
      request_id: 'req-2',
    } as never)

    const response = await assessContractImpact({ fromVersionId: 1, toVersionId: 2 })

    expect(response.success).toBe(true)
    expect(response.data.analysis).toBe(analysis)
    expect(response.data.hasBreakingChanges).toBe(true)
    expect(response.data.topImpacts[0]?.path).toBe('/api/v1/quotes')
  })
})
