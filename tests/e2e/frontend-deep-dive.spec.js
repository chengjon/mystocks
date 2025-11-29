/**
 * 深度前端测试
 */

const { test, expect } = require('@playwright/test');
const FRONTEND_URL = 'http://localhost:3006';

test.describe('MyStocks前端深度测试', () => {

  test('完整页面结构和内容分析', async ({ page }) => {
    try {
      console.log('🔍 开始深度前端分析...');

      // 访问页面
      const response = await page.goto(FRONTEND_URL);
      expect(response.status()).toBe(200);

      // 等待页面完全加载
      await page.waitForLoadState('networkidle');

      // 获取页面标题
      const title = await page.title();
      console.log('📄 页面标题:', title);

      // 分析页面结构
      const pageStructure = {
        headings: [],
        buttons: [],
        inputs: [],
        links: [],
        tables: 0,
        charts: 0,
        forms: 0
      };

      // 获取所有标题
      const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
      for (const heading of headings) {
        const text = await heading.textContent();
        const tag = await heading.evaluate(el => el.tagName);
        if (text && text.trim()) {
          pageStructure.headings.push({ tag, text: text.trim() });
        }
      }

      // 获取所有按钮
      const buttons = await page.locator('button, [role="button"], .btn, .el-button').all();
      for (const button of buttons) {
        const text = await button.textContent();
        if (text && text.trim()) {
          pageStructure.buttons.push(text.trim());
        }
      }

      // 获取所有输入框
      const inputs = await page.locator('input, textarea, select').all();
      for (const input of inputs) {
        const placeholder = await input.getAttribute('placeholder');
        const type = await input.getAttribute('type');
        pageStructure.inputs.push({ type, placeholder });
      }

      // 获取表格数量
      pageStructure.tables = await page.locator('table').count();

      // 获取图表相关元素
      const chartElements = await page.locator('canvas, svg, .chart, [id*="chart"]').count();
      pageStructure.charts = chartElements;

      // 获取表单数量
      pageStructure.forms = await page.locator('form').count();

      console.log('📊 页面结构分析结果:');
      console.log('   标题:', pageStructure.headings);
      console.log('   按钮:', pageStructure.buttons.slice(0, 5)); // 只显示前5个
      console.log('   输入框:', pageStructure.inputs);
      console.log('   表格数量:', pageStructure.tables);
      console.log('   图表元素:', pageStructure.charts);
      console.log('   表单数量:', pageStructure.forms);

      // 检查是否有Vue开发者工具
      const vueDevtools = await page.locator('[data-v-]').count();
      if (vueDevtools > 0) {
        console.log('✅ 检测到Vue.js应用 (' + vueDevtools + ' 个Vue元素)');
      }

      // 尝试查找搜索相关元素
      const searchElements = await page.locator('[placeholder*="搜索"], [placeholder*="search"], #search, .search').all();
      console.log('🔍 搜索相关元素数量:', searchElements.length);

      // 查找股票相关内容
      const stockContent = await page.locator('text=/股票|stock|Stock/').count();
      console.log('📈 股票相关内容数量:', stockContent);

      // 获取所有链接
      const links = await page.locator('a[href]').all();
      console.log('🔗 链接数量:', links.length);

      // 检查Element Plus组件
      const elementPlusComponents = await page.locator('[class*="el-"]').count();
      if (elementPlusComponents > 0) {
        console.log('✅ 检测到Element Plus组件 (' + elementPlusComponents + ' 个)');
      }

    } catch (error) {
      console.error('❌ 前端深度测试失败:', error.message);
      throw error;
    }
  });

  test('交互功能测试', async ({ page }) => {
    try {
      console.log('🎮 开始交互功能测试...');

      await page.goto(FRONTEND_URL);
      await page.waitForLoadState('networkidle');

      // 尝试找到并点击各种可交互元素
      const clickableElements = [
        'button',
        'a[href]',
        '[role="button"]',
        '.btn',
        '.el-button',
        '.clickable'
      ];

      let clickCount = 0;
      let maxClicks = 5; // 限制点击次数避免过度交互

      for (const selector of clickableElements) {
        const elements = await page.locator(selector).all();
        for (const element of elements) {
          if (clickCount >= maxClicks) break;

          try {
            // 检查元素是否可见
            const isVisible = await element.isVisible();
            if (!isVisible) continue;

            // 获取元素文本或属性
            const text = await element.textContent();
            const href = await element.getAttribute('href');

            console.log(`🖱️ 点击元素: ${selector} - 文本: ${text?.trim() || href || 'N/A'}`);

            // 点击元素
            await element.click();

            // 等待页面响应
            await page.waitForTimeout(1000);

            // 检查是否有导航或页面变化
            const currentUrl = page.url();
            if (currentUrl !== FRONTEND_URL) {
              console.log(`🔄 页面导航到: ${currentUrl}`);
              // 如果导航了，返回原页面
              await page.goto(FRONTEND_URL);
              await page.waitForLoadState('networkidle');
            }

            clickCount++;
          } catch (error) {
            console.warn(`⚠️ 点击元素失败: ${error.message}`);
          }
        }
        if (clickCount >= maxClicks) break;
      }

      console.log(`🎯 完成了 ${clickCount} 次交互测试`);

    } catch (error) {
      console.error('❌ 交互功能测试失败:', error.message);
      throw error;
    }
  });

  test('性能和资源分析', async ({ page }) => {
    try {
      console.log('⚡ 开始性能分析...');

      // 监控网络请求
      const requests = [];
      page.on('request', request => {
        requests.push({
          url: request.url(),
          method: request.method(),
          type: request.resourceType()
        });
      });

      await page.goto(FRONTEND_URL);
      await page.waitForLoadState('networkidle');

      console.log('📊 网络请求统计:');
      console.log('   总请求数:', requests.length);

      // 分析请求类型
      const requestTypes = {};
      requests.forEach(req => {
        requestTypes[req.type] = (requestTypes[req.type] || 0) + 1;
      });
      console.log('   请求类型分布:', requestTypes);

      // 分析API请求
      const apiRequests = requests.filter(req => req.url.includes('/api/'));
      console.log('   API请求数:', apiRequests.length);

      if (apiRequests.length > 0) {
        console.log('   API端点:', [...new Set(apiRequests.map(req => req.url.split('?')[0]))]);
      }

      // 检查资源加载情况
      const resources = await page.evaluate(() => {
        return performance.getEntriesByType('resource').map(entry => ({
          name: entry.name,
          type: entry.initiatorType,
          duration: entry.duration
        }));
      });

      // 按加载时间排序
      const slowResources = resources
        .sort((a, b) => b.duration - a.duration)
        .slice(0, 5);

      console.log('⏱️ 最慢的5个资源:');
      slowResources.forEach((resource, index) => {
        console.log(`   ${index + 1}. ${resource.name} (${resource.duration.toFixed(2)}ms)`);
      });

      // 检查JavaScript错误
      const jsErrors = [];
      page.on('pageerror', error => {
        jsErrors.push(error.message);
      });

      await page.reload();
      await page.waitForLoadState('networkidle');

      if (jsErrors.length > 0) {
        console.log('❌ JavaScript错误:', jsErrors.length);
        jsErrors.forEach((error, index) => {
          console.log(`   ${index + 1}. ${error.substring(0, 100)}...`);
        });
      } else {
        console.log('✅ 没有JavaScript错误');
      }

    } catch (error) {
      console.error('❌ 性能分析失败:', error.message);
      throw error;
    }
  });

});
