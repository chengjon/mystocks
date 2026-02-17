// MyStocks ArtDeco v3.1 Common Types Entry
// Generated at: 2026-02-17T09:47:17.537775

/**
 * ⚠️ 警告: 本文件已通过工程红线瘦身。
 * 实际类型定义已迁移至 ./common/all.ts
 */

// 核心响应契约 (保留在入口方便查阅)
export interface UnifiedResponse<T = any> {
  success: boolean;
  code: number;
  message: string;
  data: T;
  timestamp: string;
  request_id: string;
  errors?: any;
}

// 重定向导出所有业务类型
export * from './common/all';
