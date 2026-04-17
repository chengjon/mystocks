import { apiClient } from './apiClient.ts'
import type { UnifiedResponse } from './types/common.ts'
import type { KronosCandle, KronosEncodeRequest, KronosPredictRequest } from './types/analysis.ts'

export type { KronosCandle, KronosEncodeRequest, KronosPredictRequest }

export interface KronosRuntimeMeta {
  model?: string | null
  device?: string | null
  degraded?: boolean
  cached?: boolean
  latency_ms?: number | null
  queue_wait_ms?: number | null
  batch_size?: number | null
}

export interface KronosPredictedCandle extends KronosCandle {}

export interface KronosPredictResult {
  predictions?: KronosPredictedCandle[]
  confidence?: number
  meta?: KronosRuntimeMeta
}

export interface KronosEncodeResult {
  s1_tokens?: number[]
  s2_tokens?: number[]
  reconstruction_error?: number
  token_count?: number
  meta?: KronosRuntimeMeta
}

export interface KronosStatusResult {
  health?: string
  active_model?: string
  loaded_models?: string[]
  device?: string
  gpu_name?: string
  gpu_memory_used_mb?: number
  queue_depth?: number
  requests_inflight?: number
  inference_latency_ms_avg?: number
  version?: string
  meta?: KronosRuntimeMeta
}

class KronosApiService {
  private readonly baseUrl = '/v1/kronos'

  predict(payload: KronosPredictRequest): Promise<UnifiedResponse<KronosPredictResult>> {
    return apiClient.post<UnifiedResponse<KronosPredictResult>>(`${this.baseUrl}/predict`, payload)
  }

  encode(payload: KronosEncodeRequest): Promise<UnifiedResponse<KronosEncodeResult>> {
    return apiClient.post<UnifiedResponse<KronosEncodeResult>>(`${this.baseUrl}/encode`, payload)
  }

  getStatus(): Promise<UnifiedResponse<KronosStatusResult>> {
    return apiClient.get<UnifiedResponse<KronosStatusResult>>(`${this.baseUrl}/status`)
  }
}

export const kronosApi = new KronosApiService()

export default KronosApiService
