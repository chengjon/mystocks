import test from "node:test"
import assert from "node:assert/strict"

import { deriveGpuDashboardSummary, mapGpuStatusPayload } from "../gpuMonitorData.ts"

test("mapGpuStatusPayload maps unified gpu status payload to dashboard status", () => {
  const mapped = mapGpuStatusPayload({
    data: {
      gpus: [
        {
          name: "NVIDIA GeForce RTX 3090",
          gpu_utilization: 75.5,
          memory_used: 18000,
          memory_total: 24576,
          memory_utilization: 73.2,
          temperature: 68,
          power_usage: 320.5,
          sm_clock: 1755,
          memory_clock: 9751,
        },
      ],
    },
  })

  assert.deepEqual(mapped, {
    available: true,
    model: "NVIDIA GeForce RTX 3090",
    driverVersion: "N/A",
    availability: 100,
    utilization: 76,
    peakUtilization: 76,
    averageUtilization: 76,
    memoryUsed: 18874368000,
    memoryTotal: 25769803776,
    memoryFree: 6895435776,
    memoryUsagePercent: 73,
    temperature: 68,
    maxTemperature: 68,
    minTemperature: 68,
    averageTemperature: 68,
    coreClock: 1755,
    memoryClock: 9751,
    fanSpeed: 0,
    powerUsage: 320.5,
  })
})

test("deriveGpuDashboardSummary maps performance metrics to speedup stats", () => {
  const summary = deriveGpuDashboardSummary({
    data: {
      metrics: [
        {
          matrix_gflops: 662.52,
          matrix_speedup: 187.35,
        },
      ],
    },
  })

  assert.deepEqual(summary, {
    accelerationRatio: 187,
    performanceGain: 18635,
    energyEfficiency: 15.7,
  })
})
