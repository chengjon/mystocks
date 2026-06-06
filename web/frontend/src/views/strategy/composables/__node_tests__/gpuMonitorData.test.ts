import test from "node:test"
import assert from "node:assert/strict"

import {
  createUnknownGpuDashboardSummary,
  createUnknownGpuStatus,
  deriveGpuDashboardSummary,
  mapGpuStatusPayload,
} from "../gpuMonitorData.ts"

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
    fanSpeed: null,
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

test("mapGpuStatusPayload does not treat zero thermals and power as verified runtime sensors", () => {
  const mapped = mapGpuStatusPayload({
    data: {
      gpus: [
        {
          name: "NVIDIA GeForce RTX 2080",
          driver_version: "555.10",
          gpu_utilization: 6,
          memory_used: 3194,
          memory_total: 8192,
          memory_utilization: 39,
          temperature: 0,
          power_usage: 0,
        },
      ],
    },
  })

  assert.equal(mapped?.available, true)
  assert.equal(mapped?.temperature, null)
  assert.equal(mapped?.maxTemperature, null)
  assert.equal(mapped?.minTemperature, null)
  assert.equal(mapped?.averageTemperature, null)
  assert.equal(mapped?.coreClock, null)
  assert.equal(mapped?.memoryClock, null)
  assert.equal(mapped?.fanSpeed, null)
  assert.equal(mapped?.powerUsage, null)
})

test("deriveGpuDashboardSummary leaves benchmark metrics unsynced when runtime payload has no benchmark fields", () => {
  const summary = deriveGpuDashboardSummary({
    data: {
      metrics: [
        {
          gpu_utilization: 6,
          memory_utilization: 39,
          temperature: 0,
          power_usage: 0,
          health_status: "healthy",
        },
      ],
    },
  })

  assert.deepEqual(summary, {
    accelerationRatio: null,
    performanceGain: null,
    energyEfficiency: null,
  })
})

test("createUnknownGpuStatus returns a non-misleading empty monitor state", () => {
  assert.deepEqual(createUnknownGpuStatus(), {
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
  })
})

test("createUnknownGpuDashboardSummary leaves performance fields unsynced", () => {
  assert.deepEqual(createUnknownGpuDashboardSummary(), {
    accelerationRatio: null,
    performanceGain: null,
    energyEfficiency: null,
  })
})
