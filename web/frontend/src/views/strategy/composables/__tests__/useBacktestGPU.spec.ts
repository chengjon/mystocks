import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  axiosGetMock,
  messageErrorMock,
  messageInfoMock,
  messageSuccessMock,
} = vi.hoisted(() => ({
  axiosGetMock: vi.fn(),
  messageErrorMock: vi.fn(),
  messageInfoMock: vi.fn(),
  messageSuccessMock: vi.fn(),
}))

vi.mock('axios', () => ({
  default: {
    get: axiosGetMock,
  },
}))

vi.mock('element-plus', () => ({
  ElMessage: {
    success: messageSuccessMock,
    error: messageErrorMock,
    info: messageInfoMock,
  },
}))

vi.mock('vue', async () => {
  const actual = await vi.importActual<typeof import('vue')>('vue')
  return {
    ...actual,
    onMounted: vi.fn(),
    onUnmounted: vi.fn(),
  }
})

import { useBacktestGPU } from '../useBacktestGPU'

describe('useBacktestGPU', () => {
  beforeEach(() => {
    axiosGetMock.mockReset()
    messageSuccessMock.mockReset()
    messageErrorMock.mockReset()
    messageInfoMock.mockReset()
    vi.restoreAllMocks()
  })

  it('does not present a performance-only first load as a full recent-sync runtime banner', async () => {
    axiosGetMock.mockImplementation(async (url: string) => {
      if (url === '/api/gpu/status') {
        return {
          data: {
            success: true,
            data: {
              note: 'missing runtime snapshot',
            },
          },
        }
      }

      if (url === '/api/gpu/performance') {
        return {
          data: {
            success: true,
            data: {
              metrics: [
                {
                  matrix_speedup: 64,
                  matrix_gflops: 1350,
                },
              ],
            },
          },
        }
      }

      throw new Error(`Unexpected url: ${url}`)
    })

    const dashboard = useBacktestGPU()

    await dashboard.refreshGPUStatus()

    expect(dashboard.hasStatusSnapshot.value).toBe(false)
    expect(dashboard.hasPerformanceSnapshot.value).toBe(true)
    expect(dashboard.lastUpdatedAt.value).not.toBeNull()
    expect(dashboard.runtimeStatusMessage.value).toContain('部分同步')
    expect(dashboard.runtimeStatusMessage.value).toContain('GPU 状态待同步')
    expect(dashboard.runtimeStatusMessage.value).not.toMatch(/^最近同步\s/)
  })

  it('does not present a status-only first load as a full recent-sync runtime banner', async () => {
    axiosGetMock.mockImplementation(async (url: string) => {
      if (url === '/api/gpu/status') {
        return {
          data: {
            success: true,
            data: {
              gpus: [
                {
                  name: 'NVIDIA RTX 6000 Ada',
                  driver_version: '550.54.15',
                  gpu_utilization: 64,
                  memory_total: 49140,
                  memory_used: 12288,
                  memory_utilization: 25,
                  temperature: 58,
                  sm_clock: 2520,
                  memory_clock: 1313,
                  fan_speed: 44,
                  power_usage: 212,
                },
              ],
            },
          },
        }
      }

      if (url === '/api/gpu/performance') {
        return {
          data: {
            success: true,
            data: {
              note: 'missing benchmark snapshot',
            },
          },
        }
      }

      throw new Error(`Unexpected url: ${url}`)
    })

    const dashboard = useBacktestGPU()

    await dashboard.refreshGPUStatus()

    expect(dashboard.hasStatusSnapshot.value).toBe(true)
    expect(dashboard.hasPerformanceSnapshot.value).toBe(false)
    expect(dashboard.lastUpdatedAt.value).not.toBeNull()
    expect(dashboard.runtimeStatusMessage.value).toContain('部分同步')
    expect(dashboard.runtimeStatusMessage.value).toContain('性能快照待同步')
    expect(dashboard.runtimeStatusMessage.value).not.toMatch(/^最近同步\s/)
  })
})
