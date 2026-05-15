import { apiClient } from './apiClient.ts'

import type { UnifiedResponse } from './types/common.ts'

export type ContractImpactRiskLevel = 'none' | 'low' | 'medium' | 'high' | 'critical' | string
export type ContractImpactSeverity = 'info' | 'low' | 'medium' | 'high' | 'critical' | string

export interface ContractImpactRequest {
  from_version_id: number
  to_version_id: number
}

export interface ContractImpactItem {
  category: string
  name: string
  path: string
  change_type: string
  severity: ContractImpactSeverity
  is_breaking: boolean
  reason: string
}

export interface ContractImpactSummary {
  total_impacts: number
  breaking_impacts: number
  non_breaking_impacts: number
  by_category: Record<string, number>
}

export interface ContractMigrationEffort {
  level: ContractImpactRiskLevel
  score: number
  estimated_hours_min: number
  estimated_hours_max: number
  drivers: string[]
}

export interface ContractImpactAnalysis {
  from_version: string
  to_version: string
  risk_level: ContractImpactRiskLevel
  summary: ContractImpactSummary
  impacts: ContractImpactItem[]
  affected_endpoints: string[]
  affected_schemas: string[]
  affected_clients: string[]
  recommendations: string[]
  migration_effort: ContractMigrationEffort
}

export interface ContractImpactAssessment {
  analysis: ContractImpactAnalysis
  hasBreakingChanges: boolean
  requiresMigration: boolean
  riskRank: number
  criticalImpactCount: number
  affectedSurfaceCount: number
  topImpacts: ContractImpactItem[]
}

const severityRank: Record<string, number> = {
  none: 0,
  info: 1,
  low: 2,
  medium: 3,
  high: 4,
  critical: 5,
}

export const rankContractImpactSeverity = (severity: ContractImpactSeverity): number => {
  return severityRank[String(severity).toLowerCase()] ?? severityRank.medium
}

export const requestContractImpactAnalysis = (
  payload: ContractImpactRequest,
): Promise<UnifiedResponse<ContractImpactAnalysis>> =>
  apiClient.post<UnifiedResponse<ContractImpactAnalysis>>('/contracts/impact', payload)

export const buildContractImpactAssessment = (analysis: ContractImpactAnalysis): ContractImpactAssessment => {
  const topImpacts = [...analysis.impacts].sort((left, right) => {
    const rankDiff = rankContractImpactSeverity(right.severity) - rankContractImpactSeverity(left.severity)
    if (rankDiff !== 0) {
      return rankDiff
    }
    return Number(right.is_breaking) - Number(left.is_breaking)
  })

  return {
    analysis,
    hasBreakingChanges: analysis.summary.breaking_impacts > 0,
    requiresMigration: analysis.migration_effort.level !== 'none' || analysis.migration_effort.score > 0,
    riskRank: rankContractImpactSeverity(analysis.risk_level),
    criticalImpactCount: analysis.impacts.filter((impact) => rankContractImpactSeverity(impact.severity) >= 5).length,
    affectedSurfaceCount:
      analysis.affected_endpoints.length + analysis.affected_schemas.length + analysis.affected_clients.length,
    topImpacts,
  }
}

export const assessContractImpact = async (
  payload: ContractImpactRequest,
): Promise<UnifiedResponse<ContractImpactAssessment>> => {
  const response = await requestContractImpactAnalysis(payload)
  return {
    ...response,
    data: buildContractImpactAssessment(response.data),
  }
}
