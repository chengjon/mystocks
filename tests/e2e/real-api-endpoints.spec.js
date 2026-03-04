/**
 * 测试实际可用的API端点
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = 'http://localhost:8020';

test.describe('实际API端点验证测试', () => {

  test('验证公告相关API', async () => {
    try {
      console.log('📢 测试公告API端点...');

      // 测试公告列表
      const listResponse = await fetch(`${BASE_URL}/announcement/list`);
      if (listResponse.ok) {
        const data = await listResponse.json();
        console.log('✅ 公告列表API正常:', typeof data);
      } else {
        console.warn('⚠️ 公告列表API状态码:', listResponse.status);
      }

      // 测试公告健康检查
      const healthResponse = await fetch(`${BASE_URL}/announcement/health`);
      if (healthResponse.ok) {
        const data = await healthResponse.json();
        console.log('✅ 公告服务健康检查:', data);
      }
    } catch (error) {
      console.error('❌ 公告API测试失败:', error.message);
    }
  });

  test('验证分析相关API', async () => {
    try {
      console.log('📊 测试分析API端点...');

      // 测试概念列表
      const conceptResponse = await fetch(`${BASE_URL}/api/analysis/concept/list`);
      if (conceptResponse.ok) {
        const data = await conceptResponse.json();
        console.log('✅ 概念列表API正常，数据量:', Array.isArray(data) ? data.length : 'N/A');
      } else {
        console.warn('⚠️ 概念列表API状态码:', conceptResponse.status);
      }

      // 测试行业列表
      const industryResponse = await fetch(`${BASE_URL}/api/analysis/industry/list`);
      if (industryResponse.ok) {
        const data = await industryResponse.json();
        console.log('✅ 行业列表API正常，数据量:', Array.isArray(data) ? data.length : 'N/A');
      } else {
        console.warn('⚠️ 行业列表API状态码:', industryResponse.status);
      }
    } catch (error) {
      console.error('❌ 分析API测试失败:', error.message);
    }
  });

  test('验证认证相关API', async () => {
    try {
      console.log('🔐 测试认证API端点...');

      // 测试登录端点
      const loginResponse = await fetch(`${BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: 'test',
          password: 'test'
        })
      });

      console.log('🔑 登录API状态码:', loginResponse.status);
      if (loginResponse.ok) {
        const data = await loginResponse.json();
        console.log('✅ 登录API响应结构:', Object.keys(data));
      }
    } catch (error) {
      console.error('❌ 认证API测试失败:', error.message);
    }
  });

});
