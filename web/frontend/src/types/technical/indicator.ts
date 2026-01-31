/**
 * @fileoverview 技术指标模块类型定义
 * @description 提供技术指标相关的类型定义
 * @module types/technical
 * @version 1.0.0
 */

import type { UnifiedResponse } from '../common/response';

/**
 * 指标参数类型
 */
export interface IndicatorParameter {
  name: string;
  type: 'int' | 'float' | 'string' | 'bool';
  default: number | string | boolean;
  min?: number;
  max?: number;
  step?: number;
  description?: string;
}

/**
 * 叠加指标响应
 */
export interface OverlayIndicatorResponse extends UnifiedResponse<{
  indicatorType: string;
  params: IndicatorParameter;
  values: number[];
  timestamps: string[];
  metadata?: {
    period?: number;
    deviation?: number;
  maPeriod?: number;
  };
}> {}

/**
 * 振荡指标响应
 */
export interface OscillatorIndicatorResponse extends UnifiedResponse<{
  indicatorType: string;
  params: IndicatorParameter;
  values: number[];
  timestamps: string[];
  metadata?: {
    period?: number;
    signalPeriod?: number;
    overbought?: number;
    oversold?: number;
  };
}> {}

/**
 * 指标计算请求
 */
export interface IndicatorCalculationRequest {
  symbol: string;
  indicatorType: string;
  params: IndicatorParameter;
  period?: string;
  start_date?: string;
  end_date?: string;
}

/**
 * 指标计算响应
 */
export interface IndicatorCalculationResponse extends UnifiedResponse<{
  result: number[];
  timestamps: string[];
  params?: IndicatorParameter;
}> {}
