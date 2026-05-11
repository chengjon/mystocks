import { apiClient } from './apiClient.ts'

import type { UnifiedResponse } from './types/common.ts'

export type MlWorkbenchModelFamily = 'svm' | 'lightgbm'

export interface MlDependencyStatus {
  available: boolean
  package: string
}

export interface MlRuntimeStatus {
  service_available: boolean
  model_backend: string
  optional_dependencies: Record<string, MlDependencyStatus>
  model_dir?: string
  model_dir_writable?: boolean
  legacy_api_available: boolean
  supported_operations: string[]
  warnings: string[]
  safety?: MlSafety
}

export interface MlSafety {
  analytical_output_only?: boolean
  disclaimer?: string
}

export interface MlFeatureContext {
  feature_window?: number
  prediction_horizon?: number
  feature_columns?: string[]
  target_name?: string
  sample_count?: number
  date_range?: Record<string, string>
}

export interface MlWorkbenchModel {
  model_id: string
  model_family: MlWorkbenchModelFamily | string
  symbol: string
  artifact_status: string
  feature_context: MlFeatureContext
  metrics: Record<string, number>
  feature_importance?: Record<string, number>
  created_at?: string
  updated_at?: string
  safety?: MlSafety
}

export interface MlTrainingRequest {
  model_family: MlWorkbenchModelFamily
  symbol: string
  start_date: string
  end_date: string
  feature_window: number
  prediction_horizon: number
  parameters: Record<string, unknown>
}

export interface MlTrainingResult extends MlWorkbenchModel {
  trained_at?: string
  warnings?: string[]
}

export interface MlPredictionRequest {
  model_id: string
  symbol: string
  prediction_horizon: number
}

export interface MlPredictionResult {
  model_id: string
  model_family: string
  symbol: string
  prediction_horizon: number
  generated_at?: string
  feature_context: MlFeatureContext
  prediction: {
    signal?: 'buy' | 'sell' | 'hold'
    expected_return?: number
    prediction_horizon?: number
  }
  confidence?: number
  warnings?: string[]
  safety?: MlSafety
}

export interface MlModelListPayload {
  models: MlWorkbenchModel[]
  total: number
}

export const getMlRuntimeStatus = (): Promise<UnifiedResponse<MlRuntimeStatus>> =>
  apiClient.get<UnifiedResponse<MlRuntimeStatus>>('/v1/strategies/ml/runtime-status')

export const trainMlWorkbenchModel = (
  payload: MlTrainingRequest,
): Promise<UnifiedResponse<MlTrainingResult>> =>
  apiClient.post<UnifiedResponse<MlTrainingResult>>('/v1/strategies/ml/train', payload)

export const predictMlWorkbenchModel = (
  payload: MlPredictionRequest,
): Promise<UnifiedResponse<MlPredictionResult>> =>
  apiClient.post<UnifiedResponse<MlPredictionResult>>('/v1/strategies/ml/predict', payload)

export const listMlWorkbenchModels = (): Promise<UnifiedResponse<MlModelListPayload>> =>
  apiClient.get<UnifiedResponse<MlModelListPayload>>('/v1/strategies/ml/models')

export const getMlWorkbenchModelDetail = (
  modelId: string,
): Promise<UnifiedResponse<MlWorkbenchModel>> => {
  const resolvedModelId = modelId.trim()
  if (!resolvedModelId) {
    return Promise.reject(new Error('Model ID is required'))
  }
  return apiClient.get<UnifiedResponse<MlWorkbenchModel>>(
    `/v1/strategies/ml/models/${encodeURIComponent(resolvedModelId)}`,
  )
}

export const mlWorkbenchApi = {
  getMlRuntimeStatus,
  getMlWorkbenchModelDetail,
  listMlWorkbenchModels,
  predictMlWorkbenchModel,
  trainMlWorkbenchModel,
}
