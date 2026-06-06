type RecordLike = Record<string, unknown>

export interface GpuDashboardStatus {
  available: boolean
  model: string
  driverVersion: string
  availability: number
  utilization: number
  peakUtilization: number
  averageUtilization: number
  memoryUsed: number
  memoryTotal: number
  memoryFree: number
  memoryUsagePercent: number
  temperature: number | null
  maxTemperature: number | null
  minTemperature: number | null
  averageTemperature: number | null
  coreClock: number | null
  memoryClock: number | null
  fanSpeed: number | null
  powerUsage: number | null
}

export interface GpuDashboardSummary {
  accelerationRatio: number | null
  performanceGain: number | null
  energyEfficiency: number | null
}

export function createUnknownGpuStatus(): GpuDashboardStatus {
  return {
    available: false,
    model: "",
    driverVersion: "",
    availability: 0,
    utilization: 0,
    peakUtilization: 0,
    averageUtilization: 0,
    memoryUsed: 0,
    memoryTotal: 0,
    memoryFree: 0,
    memoryUsagePercent: 0,
    temperature: null,
    maxTemperature: null,
    minTemperature: null,
    averageTemperature: null,
    coreClock: null,
    memoryClock: null,
    fanSpeed: null,
    powerUsage: null,
  }
}

export function createUnknownGpuDashboardSummary(): GpuDashboardSummary {
  return {
    accelerationRatio: null,
    performanceGain: null,
    energyEfficiency: null,
  }
}

function isRecord(value: unknown): value is RecordLike {
  return typeof value === 'object' && value !== null
}

function parseNumber(value: unknown): number {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value
  }

  if (typeof value === 'string' && value.trim().length > 0) {
    const parsed = Number.parseFloat(value)
    return Number.isFinite(parsed) ? parsed : 0
  }

  return 0
}

function parseOptionalNumber(value: unknown): number | null {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value
  }

  if (typeof value === 'string' && value.trim().length > 0) {
    const parsed = Number.parseFloat(value)
    return Number.isFinite(parsed) ? parsed : null
  }

  return null
}

function parseVerifiedMetric(value: unknown): number | null {
  const parsed = parseOptionalNumber(value)
  if (parsed === null || parsed <= 0) {
    return null
  }

  return parsed
}

function extractFirstItem(payload: unknown, key: string): RecordLike | null {
  if (!isRecord(payload)) {
    return null
  }

  const data = isRecord(payload.data) ? payload.data : payload
  const collection = data[key]
  if (Array.isArray(collection) && collection.length > 0 && isRecord(collection[0])) {
    return collection[0]
  }

  return null
}

export function mapGpuStatusPayload(payload: unknown): GpuDashboardStatus | null {
  const row = extractFirstItem(payload, 'gpus')
  if (!row) {
    return null
  }

  const memoryTotalMb = parseNumber(row.memory_total)
  const memoryUsedMb = parseNumber(row.memory_used)
  const memoryFreeMb = Math.max(0, memoryTotalMb - memoryUsedMb)
  const toBytes = (valueMb: number) => Math.round(valueMb * 1024 * 1024)
  const utilization = Math.round(parseNumber(row.gpu_utilization))
  const memoryUsagePercent = Math.round(parseNumber(row.memory_utilization))
  const rawTemperature = parseVerifiedMetric(row.temperature)
  const temperature = rawTemperature === null ? null : Math.round(rawTemperature)
  const powerUsage = parseVerifiedMetric(row.power_usage)

  return {
    available: true,
    model: String(row.name ?? 'Unknown GPU'),
    driverVersion: String(row.driver_version ?? 'N/A'),
    availability: 100,
    utilization,
    peakUtilization: utilization,
    averageUtilization: utilization,
    memoryUsed: toBytes(memoryUsedMb),
    memoryTotal: toBytes(memoryTotalMb),
    memoryFree: toBytes(memoryFreeMb),
    memoryUsagePercent,
    temperature,
    maxTemperature: temperature,
    minTemperature: temperature,
    averageTemperature: temperature,
    coreClock: (() => {
      const value = parseOptionalNumber(row.sm_clock)
      return value === null ? null : Math.round(value)
    })(),
    memoryClock: (() => {
      const value = parseOptionalNumber(row.memory_clock)
      return value === null ? null : Math.round(value)
    })(),
    fanSpeed: (() => {
      const value = parseOptionalNumber(row.fan_speed)
      return value === null ? null : Math.round(value)
    })(),
    powerUsage,
  }
}

export function deriveGpuDashboardSummary(payload: unknown): GpuDashboardSummary | null {
  const row = extractFirstItem(payload, 'metrics')
  if (!row) {
    return null
  }

  const rawSpeedup = parseVerifiedMetric(row.matrix_speedup)
  const rawGflops = parseVerifiedMetric(row.matrix_gflops)

  if (rawSpeedup === null || rawGflops === null) {
    return createUnknownGpuDashboardSummary()
  }

  const accelerationRatio = Math.round(rawSpeedup)
  const performanceGain = Math.round((rawSpeedup - 1) * 100)
  const energyEfficiency = Number((rawGflops / 42.2).toFixed(1))

  return {
    accelerationRatio,
    performanceGain,
    energyEfficiency,
  }
}
