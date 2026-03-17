import type { ConceptFlowRecord } from './marketConceptContract'

export interface ConceptRow {
  rank: number
  name: string
  changePct: number
  mainInflow: string
  leader: string
  mainInflowAmount: number
}

export interface ConceptSummary {
  activeConcepts: number
  risingConcepts: number
  fallingConcepts: number
  strongestChange: number
  strongestInflow: number
}

function parseNumeric(value: unknown): number {
  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : 0
  }

  return Number.parseFloat(String(value ?? '0')) || 0
}

function formatSigned(value: number, digits = 2): string {
  const normalized = Number.isFinite(value) ? value : 0
  const prefix = normalized > 0 ? '+' : ''
  return `${prefix}${normalized.toFixed(digits)}`
}

function formatInflow(value: number): string {
  const normalized = Number.isFinite(value) ? value : 0
  return `${formatSigned(normalized, 1)}亿`
}

export function toConceptRows(rows: ConceptFlowRecord[]): ConceptRow[] {
  return rows.map((row, index) => {
    const mainInflowAmount = parseNumeric(row.main_net_inflow) / 100000000

    return {
      rank: index + 1,
      name:
        typeof row.sector_name === 'string' && row.sector_name.trim().length > 0
          ? row.sector_name
          : `概念-${index + 1}`,
      changePct: parseNumeric(row.change_percent),
      mainInflow: formatInflow(mainInflowAmount),
      leader:
        typeof row.leading_stock === 'string' && row.leading_stock.trim().length > 0
          ? row.leading_stock
          : '--',
      mainInflowAmount: Number(mainInflowAmount.toFixed(1))
    }
  })
}

export function summarizeConceptRows(rows: ConceptRow[]): ConceptSummary {
  if (rows.length === 0) {
    return {
      activeConcepts: 0,
      risingConcepts: 0,
      fallingConcepts: 0,
      strongestChange: 0,
      strongestInflow: 0
    }
  }

  return {
    activeConcepts: rows.length,
    risingConcepts: rows.filter((row) => row.changePct > 0).length,
    fallingConcepts: rows.filter((row) => row.changePct < 0).length,
    strongestChange: Number(Math.max(...rows.map((row) => row.changePct)).toFixed(2)),
    strongestInflow: Number(Math.max(...rows.map((row) => row.mainInflowAmount)).toFixed(1))
  }
}
