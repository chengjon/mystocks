/**
 * @fileoverview 测试模块类型定义
 * @description 提供测试相关的类型定义
 * @module types/test
 * @version 1.0.0
 */

import type { UnifiedResponse } from '../common/response';

/**
 * 测试用例
 */
export interface TestCase {
  id: string;
  name: string;
  description?: string;
  status?: 'pending' | 'running' | 'passed' | 'failed';
  duration?: number;
  createdAt?: string;
  updatedAt?: string;
}

/**
 * 测试结果
 */
export interface TestResult {
  testCaseId: string;
  success: boolean;
  output?: any;
  error?: string;
  duration?: number;
  timestamp?: string;
}

/**
 * 测试套件
 */
export interface TestSuite {
  id: string;
  name: string;
  description?: string;
  testCases: TestCase[];
  createdAt?: string;
}

/**
 * 测试套件列表响应
 */
export interface TestSuiteListResponse extends UnifiedResponse<TestSuite[]> {}

/**
 * 测试结果响应
 */
export interface TestResultResponse extends UnifiedResponse<TestResult[]> {}
