// MyStocks ArtDeco v3.1 Common Types Entry
// Generated at: 2026-03-02T18:01:04.614672

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

// 重定向导出所有业务类型
export * from './common/all';
