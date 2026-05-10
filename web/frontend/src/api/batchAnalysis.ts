import { apiClient } from './apiClient.ts'

import type { UnifiedResponse } from './types/common.ts'

export type BatchAnalysisOperation = 'batch_backtest' | 'batch_screening' | 'batch_monitoring'

export interface BatchAnalysisSafety {
  analytical_output_only?: boolean
  disclaimer?: string
}

export interface BatchAnalysisRuntimeStatus {
  service_available: boolean
  runtime_backend: string
  max_symbols: number
  supported_operations: BatchAnalysisOperation[]
  evidence_modules: string[]
  warnings: string[]
  safety: BatchAnalysisSafety
}

export interface BatchAnalysisRequest {
  operation: BatchAnalysisOperation
  symbols: string[]
  start_date: string
  end_date: string
  options: Record<string, unknown>
}

export interface BatchAnalysisResultRow {
  symbol: string
  status: string
  score: number
  signal: 'candidate' | 'watch' | 'neutral' | string
  metrics: Record<string, number>
  evidence?: Record<string, string>
}

export interface BatchAnalysisTask {
  task_id: string
  operation: BatchAnalysisOperation | string
  symbols: string[]
  status: string
  summary: {
    total_symbols: number
    completed_symbols: number
    failed_symbols: number
    candidate_count: number
    average_score: number
  }
  results?: BatchAnalysisResultRow[]
  warnings: string[]
  created_at?: string
  updated_at?: string
  safety: BatchAnalysisSafety
}

export interface BatchAnalysisTaskListPayload {
  tasks: BatchAnalysisTask[]
  total: number
}

export const getBatchAnalysisRuntimeStatus = (): Promise<UnifiedResponse<BatchAnalysisRuntimeStatus>> =>
  apiClient.get<UnifiedResponse<BatchAnalysisRuntimeStatus>>('/v1/strategies/batch-analysis/runtime-status')

export const submitBatchAnalysisTask = (
  payload: BatchAnalysisRequest,
): Promise<UnifiedResponse<BatchAnalysisTask>> =>
  apiClient.post<UnifiedResponse<BatchAnalysisTask>>('/v1/strategies/batch-analysis/submit', payload)

export const listBatchAnalysisTasks = (): Promise<UnifiedResponse<BatchAnalysisTaskListPayload>> =>
  apiClient.get<UnifiedResponse<BatchAnalysisTaskListPayload>>('/v1/strategies/batch-analysis/tasks')

export const getBatchAnalysisTaskDetail = (
  taskId: string,
): Promise<UnifiedResponse<BatchAnalysisTask>> =>
  apiClient.get<UnifiedResponse<BatchAnalysisTask>>(
    `/v1/strategies/batch-analysis/tasks/${encodeURIComponent(taskId)}`,
  )

export const batchAnalysisApi = {
  getBatchAnalysisRuntimeStatus,
  getBatchAnalysisTaskDetail,
  listBatchAnalysisTasks,
  submitBatchAnalysisTask,
}
