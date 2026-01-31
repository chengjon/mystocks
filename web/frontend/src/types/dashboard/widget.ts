/**
 * @fileoverview 仪表板Widget组件类型定义
 * @description 提供仪表板Widget组件相关的类型定义
 * @module types/dashboard
 * @version 1.0.0
 */

import type { UnifiedResponse } from '../common/response';

/**
 * Widget数据源
 */
export type WidgetDataSource = 'api' | 'websocket' | 'mock';

/**
 * Widget配置
 */
export interface WidgetConfig {
  id: string;
  type: string;
  title: string;
  dataSource: WidgetDataSource;
  endpoint?: string;
  refreshInterval?: number;
  query?: Record<string, any>;
  filters?: Record<string, any>;
}

/**
 * Widget配置响应
 */
export interface WidgetConfigResponse extends UnifiedResponse<WidgetConfig[]> {}

/**
 * Widget实例
 */
export interface WidgetInstance {
  id: string;
  config: WidgetConfig;
  state?: Record<string, any>;
  lastUpdate?: string;
}

/**
 * Widget实例列表
 */
export interface WidgetInstancesResponse extends UnifiedResponse<WidgetInstance[]> {}
