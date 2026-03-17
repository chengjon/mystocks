import type { SectorFundFlowItem } from '@/api/services/marketService'

export type ConceptFlowRecord = SectorFundFlowItem

export function extractConceptFlowRows(payload: unknown): ConceptFlowRecord[] {
  if (Array.isArray(payload)) {
    return payload as ConceptFlowRecord[]
  }

  if (payload && typeof payload === 'object') {
    const candidate = payload as Record<string, unknown>
    const collections = [candidate.items, candidate.data, candidate.records]
    for (const collection of collections) {
      if (Array.isArray(collection)) {
        return collection as ConceptFlowRecord[]
      }
    }
  }

  return []
}
