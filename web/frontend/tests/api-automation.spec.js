/**
 * Playwright API 自动化测试脚本
 * 用于自动化测试 FastAPI 后端的所有接口
 *
 * 功能：
 * 1. 从 OpenAPI 规范自动发现所有 API 端点
 * 2. 对每个端点进行自动化测试
 * 3. 验证响应状态、数据格式和性能
 * 4. 生成详细的测试报告
 */

const { test, expect } = require('@playwright/test');

const fs = require('fs');

const path = require('path');



// 测试配置



const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';



const API_PREFIX = '/api/v1';



const API_TOKEN = process.env.API_TOKEN || ''; // 默认不提供令牌，由环境驱动



const REPORT_DIR = '/opt/claude/mystocks_spec/docs/reports/test-results';









// 测试结果收集

const testResults = {

  total: 0,

  passed: 0,

  failed: 0,

  skipped: 0,

  endpoints: []

};



/**

 * 从 OpenAPI 规范获取所有 API 端点

 */

async function getOpenApiSpec() {

  const response = await fetch(`${BASE_URL}/openapi.json`);

  if (!response.ok) {

    throw new Error(`获取 OpenAPI 规范失败: ${response.status}`);

  }

  return await response.json();

}



/**

 * 提取所有需要测试的端点

 */

function extractEndpoints(openApiSpec) {

  const endpoints = [];

  const paths = openApiSpec.paths || {};



  for (const [path, methods] of Object.entries(paths)) {

    for (const [method, details] of Object.entries(methods)) {

      // 跳过非 HTTP 方法

      if (!['get', 'post', 'put', 'delete', 'patch'].includes(method.toLowerCase())) {

        continue;

      }



      endpoints.push({

        path,

        method: method.toUpperCase(),

        summary: details.summary || details.operationId || `${method} ${path}`,

        tags: details.tags || [],

        parameters: details.parameters || [],

        requestBody: details.requestBody,

        responses: details.responses

      });

    }

  }



  return endpoints;

}



/**



 * 生成测试数据（根据参数定义）



 */



function generateTestData(parameters) {



  const testData = {};







  parameters.forEach(param => {



    if (param.in === 'path' || param.in === 'query') {



      const schema = param.schema;



      const name = param.name.toLowerCase();







      // 智能默认值



      if (name.includes('symbol') || name.includes('code')) {



        testData[param.name] = '600000';



      } else if (name === 'market') {



        testData[param.name] = 'SH';



      } else if (name === 'period') {



        testData[param.name] = 'daily';



      } else if (name === 'limit') {



        testData[param.name] = 10;



      } else if (name.includes('start_date') || name === 'start') {



        testData[param.name] = '2024-01-01';



      } else if (name.includes('end_date') || name === 'end') {



        testData[param.name] = '2024-01-31';



      } else {



        // 根据类型生成默认值



        if (schema?.type === 'string') {



          testData[param.name] = schema.example || 'test';



        } else if (schema?.type === 'integer' || schema?.type === 'number') {



          testData[param.name] = schema.example || 1;



        } else if (schema?.type === 'boolean') {



          testData[param.name] = schema.example || true;



        } else if (schema?.enum) {



          testData[param.name] = schema.enum[0];



        }



      }



    }



  });







  return testData;



}







/**



 * 替换路径参数



 */



function replacePathParams(path, params) {



  let result = path;



  for (const [key, value] of Object.entries(params)) {



    result = result.replace(`{${key}}`, value);



  }



  return result;



}







/**



 * 测试单个 API 端点



 */



async function testEndpoint(endpoint) {



  const startTime = Date.now();



  const result = {



    ...endpoint,



    status: 'pending',



    statusCode: null,



    responseTime: null,



    error: null,



    validation: null



  };







  try {



    // 生成测试数据



    const generatedData = generateTestData(endpoint.parameters);



    const pathParams = {};



    const queryParams = {};







    // 分离路径参数和查询参数



    endpoint.parameters.forEach(param => {



      if (param.in === 'path') {



        pathParams[param.name] = generatedData[param.name];



      } else if (param.in === 'query') {



        queryParams[param.name] = generatedData[param.name];



      } else if (param.in === 'header') {



        // 添加认证头



        if (param.name.toLowerCase() === 'authorization') {



          queryParams[param.name] = API_TOKEN;



        }



      }



    });







    // 构建请求 URL



    let url = `${BASE_URL}${replacePathParams(endpoint.path, pathParams)}`;







    // 添加查询参数



    if (Object.keys(queryParams).length > 0) {



      const searchParams = new URLSearchParams();



      for (const [key, value] of Object.entries(queryParams)) {



        if (key !== 'authorization') {



          searchParams.append(key, String(value));



        }



      }



      if (searchParams.toString()) {



        url += `?${searchParams.toString()}`;



      }



    }







    // 构建请求选项



    const options = {



      method: endpoint.method,



      headers: {



        'Content-Type': 'application/json',



        ...(queryParams.authorization && { 'Authorization': queryParams.authorization })



      }



    };







    // 添加请求体（如果有）



    if (endpoint.requestBody && endpoint.method !== 'GET') {



      options.body = JSON.stringify({ test: true });



    }







    // 发送请求



    const response = await fetch(url, options);



    const responseTime = Date.now() - startTime;







    result.statusCode = response.status;



    result.responseTime = responseTime;







    // 验证响应



    if (response.ok) {



      result.status = 'passed';



      testResults.passed++;







      // 尝试解析 JSON 响应



      try {



        const data = await response.json();



        result.validation = {



          hasData: !!data,



          isSuccess: data.success !== false,



          dataType: typeof data



        };



      } catch (e) {



        result.validation = {



          hasData: false,



          note: 'Non-JSON response'



        };



      }



    } else {



      result.status = 'failed';



      result.error = `HTTP ${response.status}`;



      testResults.failed++;



    }







  } catch (error) {



    result.status = 'failed';



    result.error = error.message;



    result.responseTime = Date.now() - startTime;



    testResults.failed++;



  }







  testResults.endpoints.push(result);



  testResults.total++;







  return result;



}







/**



 * 生成测试报告



 */



function generateReport() {



  const report = {



    summary: {



      total: testResults.total,



      passed: testResults.passed,



      failed: testResults.failed,



      skipped: testResults.skipped,



      passRate: ((testResults.passed / testResults.total) * 100).toFixed(2) + '%',



      avgResponseTime: testResults.endpoints.length > 0



        ? Math.round(testResults.endpoints.reduce((sum, e) => sum + (e.responseTime || 0), 0) / testResults.endpoints.length)



        : 0



    },



    endpoints: testResults.endpoints



  };







  return report;



}







/**



 * 主测试套件



 */



test.describe('FastAPI API 自动化测试', () => {



  let openApiSpec;



  let endpoints;







  test.beforeAll('获取 OpenAPI 规范', async () => {



    try {



      openApiSpec = await getOpenApiSpec();



      endpoints = extractEndpoints(openApiSpec);







      console.log(`\n✓ 发现 ${endpoints.length} 个 API 端点`);



      console.log(`✓ API 版本: ${openApiSpec.info.version}`);



      console.log(`✓ API 标题: ${openApiSpec.info.title}\n`);



    } catch (error) {



      console.error('❌ 获取 OpenAPI 规范失败:', error.message);



      throw error;



    }



  });







  test('完整 API 端点测试', async () => {



    // 设置超时时间为 300 秒 (5分钟)，因为端点数量较多且涉及真实数据



    test.setTimeout(300000);







    if (!endpoints || endpoints.length === 0) {



      test.skip(true, '没有发现可测试的端点');



      return;



    }

    console.log('\n📋 开始测试所有端点...\n');

    // 批量测试所有端点
    for (const endpoint of endpoints) {
      console.log(`  测试: ${endpoint.method} ${endpoint.path}`);
      const result = await testEndpoint(endpoint);

      if (result.status === 'passed') {
        console.log(`    ✓ 通过 (${result.responseTime}ms)`);
      } else {
        console.log(`    ✗ 失败: ${result.error || 'Unknown error'}`);
      }
    }

    // 生成报告
    const report = generateReport();

    console.log('\n📊 测试摘要:');
    console.log(`  总计: ${report.summary.total}`);
    console.log(`  通过: ${report.summary.passed} ✅`);
    console.log(`  失败: ${report.summary.failed} ❌`);
    console.log(`  跳过: ${report.summary.skipped} ⏭️`);
    console.log(`  通过率: ${report.summary.passRate}`);
    console.log(`  平均响应时间: ${report.summary.avgResponseTime}ms\n`);

    // 断言：至少有部分端点应该测试通过
    expect(report.summary.passed).toBeGreaterThan(0);

    // 如果所有端点都失败，抛出错误
    if (report.summary.failed === report.summary.total) {
      throw new Error('所有 API 端点测试失败');
    }
  });

  test('健康检查端点测试', async () => {
    const response = await fetch(`${BASE_URL}/health`);
    expect(response.ok).toBeTruthy();

    const data = await response.json();
    expect(data).toHaveProperty('status');
  });

  test('OpenAPI 规范验证', async () => {
    expect(openApiSpec).toBeDefined();
    expect(openApiSpec.openapi).toMatch(/^3\.\d+\.\d+$/);
    expect(openApiSpec.info).toHaveProperty('title');
    expect(openApiSpec.info).toHaveProperty('version');
    expect(openApiSpec.paths).toBeDefined();
  });
});

/**
 * 测试套件：按标签动态分组测试
 */
test.describe('API 端点分组详细测试', () => {
  let openApiSpec;
  let endpoints;
  let tags = new Set();

  test.beforeAll(async () => {
    try {
      openApiSpec = await getOpenApiSpec();
      endpoints = extractEndpoints(openApiSpec);

      // 提取所有唯一标签
      endpoints.forEach(e => {
        if (e.tags && e.tags.length > 0) {
          e.tags.forEach(tag => tags.add(tag));
        } else {
          tags.add('未分类');
        }
      });

      console.log(`\n🏷️  发现标签: ${Array.from(tags).join(', ')}`);
    } catch (error) {
      console.error('获取规范失败:', error);
    }
  });

  // 为每个标签运行测试
  // 注意：Playwright 的测试定义是静态的，所以我们在一个测试中遍历该标签的所有端点
  test('执行按标签分组的自动化测试', async () => {
    if (!endpoints || endpoints.length === 0) {
      test.skip(true, '未发现端点');
      return;
    }

    const tagList = Array.from(tags);

    for (const tag of tagList) {
      console.log(`\n📂 正在测试标签: ${tag}`);

      const taggedEndpoints = endpoints.filter(e =>
        (tag === '未分类' && (!e.tags || e.tags.length === 0)) ||
        (e.tags && e.tags.includes(tag))
      );

      console.log(`   端点数量: ${taggedEndpoints.length}`);

      for (const endpoint of taggedEndpoints) {
        process.stdout.write(`   ${endpoint.method.padEnd(6)} ${endpoint.path.padEnd(40)} `);
        const result = await testEndpoint(endpoint);

        if (result.status === 'passed') {
          console.log(`✅ [${result.statusCode}] ${result.responseTime}ms`);
        } else {
          console.log(`❌ [${result.statusCode || 'ERR'}] ${result.error}`);
        }
      }
    }

    // 汇总报告
    const report = generateReport();
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log(`🏆 最终统计: ${report.summary.passed}/${report.summary.total} 通过 (${report.summary.passRate})`);
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

    // 保存 JSON 报告
    try {
      if (!fs.existsSync(REPORT_DIR)) {
        fs.mkdirSync(REPORT_DIR, { recursive: true });
      }
      const summaryPath = path.join(REPORT_DIR, 'api-test-summary.json');
      fs.writeFileSync(summaryPath, JSON.stringify(report, null, 2));
      console.log(`💾 JSON 报告已保存至: ${summaryPath}`);
    } catch (err) {
      console.error('❌ 保存 JSON 报告失败:', err.message);
    }
  });
});

/**
 * 导出测试结果（用于外部工具）
 */
if (require.main === module) {
  // 直接运行此脚本时的行为
  getOpenApiSpec()
    .then(spec => {
      const endpoints = extractEndpoints(spec);
      console.log(`发现 ${endpoints.length} 个端点`);
      return Promise.all(endpoints.map(e => testEndpoint(e)));
    })
    .then(() => {
      const report = generateReport();
      console.log('\n测试完成！');
      console.log(JSON.stringify(report, null, 2));
    })
    .catch(error => {
      console.error('测试失败:', error);
      process.exit(1);
    });
}
