// MyStocks ArtDeco v3.1 Common Types Entry

/**
 * ⚠️ 警告: 本文件已通过工程红线瘦身。
 * 实际类型定义已迁移至 ./common/all.ts
 */

// 核心响应契约 (保留在入口方便查阅)
export interface UnifiedResponse<T = unknown> {
  success: boolean;
  code: number;
  message: string;
  data: T;
  timestamp: string;
  request_id: string;
  process_time?: string;
  errors?: unknown;
}

export interface ServiceResult<T> {
  ok: boolean;
  data: T;
  error?: string;
}

export function serviceOk<T>(data: T): ServiceResult<T> {
  return {
    ok: true,
    data,
  };
}

export function serviceErr<T>(data: T, error: string): ServiceResult<T> {
  return {
    ok: false,
    data,
    error,
  };
}

// 重定向导出所有业务类型
export * from './common/all';
