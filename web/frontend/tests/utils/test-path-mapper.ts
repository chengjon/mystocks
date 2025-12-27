/**
 * 测试路径映射工具
 *
 * 由于测试文件在 /tests/ 目录下，但源码在 /src/ 目录下，
 * 需要正确配置模块解析路径
 */

import path from 'path'

// 定义路径映射
const pathMappings = {
  '@': path.resolve(__dirname, '../../src'),
  '@/tests': path.resolve(__dirname, '../'),
  '@/utils': path.resolve(__dirname, '../utils'),
  '@/fixtures': path.resolve(__dirname, '../fixtures'),
  '@/pages': path.resolve(__dirname, '../e2e/pages'),
  '@/api': path.resolve(__dirname, '../mocks/api'),
}

// 导出路径配置供其他文件使用
export const testPaths = {
  src: pathMappings['@'],
  tests: pathMappings['@/tests'],
  utils: pathMappings['@/utils'],
  fixtures: pathMappings['@/fixtures'],
  mockData: pathMappings['@/fixtures'],
}

// 生成相对路径的辅助函数
export function getRelativePath(from: string, to: string): string {
  return path.relative(from, to)
}

// 导出常用的测试文件路径
export const testFiles = {
  apiMocks: path.resolve(testPaths.utils, 'api-mock-manager.ts'),
  testHelpers: path.resolve(testPaths.utils, 'test-helpers.ts'),
  fixtures: {
    users: path.resolve(testPaths.fixtures, 'users.json'),
    stocks: path.resolve(testPaths.fixtures, 'stocks.json'),
    markets: path.resolve(testPaths.fixtures, 'markets.json'),
  }
}
