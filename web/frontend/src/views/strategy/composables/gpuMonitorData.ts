type RecordLike = Record<string, unknown>

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

export function mapGpuStatusPayload(payload: unknown) {
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
  const temperature = Math.round(parseNumber(row.temperature))

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
    coreClock: Math.round(parseNumber(row.sm_clock)),
    memoryClock: Math.round(parseNumber(row.memory_clock)),
    fanSpeed: Math.round(parseNumber(row.fan_speed)),
    powerUsage: parseNumber(row.power_usage),
  }
}

export function deriveGpuDashboardSummary(payload: unknown) {
  const row = extractFirstItem(payload, 'metrics')
  if (!row) {
    return null
  }

  const rawSpeedup = parseNumber(row.matrix_speedup)
  const accelerationRatio = Math.round(rawSpeedup)
  const performanceGain = Math.round((rawSpeedup - 1) * 100)
  const energyEfficiency = Number((parseNumber(row.matrix_gflops) / 42.2).toFixed(1))

  return {
    accelerationRatio,
    performanceGain,
    energyEfficiency,
  }
}
