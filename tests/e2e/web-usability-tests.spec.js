/**
 * MyStocks Web端可用性测试套件
 * 包含功能性、性能、安全性、用户体验和数据质量的端到端测试
 */

const { test, expect } = require('@playwright/test');
const path = require('path');

// 测试配置
const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';
const API_URL = process.env.API_URL || 'http://localhost:8020';

// 测试数据
const TEST_STOCKS = ['000001', '000002', '600000'];
const TEST_USER = {
    username: 'admin',
    password: 'admin123'
};

// 工具函数
const helpers = {
    // 等待页面完全加载
    waitForPageLoad: async (page) => {
        await page.waitForLoadState('networkidle');
        await page.waitForLoadState('domcontentloaded');
    },

    // 模拟用户登录
    login: async (page, username = TEST_USER.username, password = TEST_USER.password) => {
        await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle' });
        await page.waitForSelector('[data-testid="username-input"]', { timeout: 10000 });
        await page.fill('[data-testid="username-input"]', username);
        await page.fill('[data-testid="password-input"]', password);
        await page.click('[data-testid="login-button"]');
        await page.waitForURL(`${BASE_URL}/dashboard`, { timeout: 15000 });
    },

    // 测量元素加载时间
    measureLoadTime: async (page, selector) => {
        const startTime = Date.now();
        await page.waitForSelector(selector, { timeout: 10000 });
        return Date.now() - startTime;
    },

    // 检查元素可见性
    isElementVisible: async (page, selector) => {
        try {
            const element = await page.$(selector);
            return element && await element.isVisible();
        } catch {
            return false;
        }
    },

    // 模拟网络慢速条件
    simulateSlowNetwork: async (page) => {
        const client = await page.context().newCDPSession(page);
        await client.send('Network.emulateNetworkConditions', {
            offline: false,
            downloadThroughput: 50 * 1024 / 8, // 50kb/s
            uploadThroughput: 20 * 1024 / 8,   // 20kb/s
            latency: 500
        });
    }
};

// 功能性测试组
test.describe('🧪 功能性测试', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto(BASE_URL);
    });

    test.describe('股票查询功能', () => {
        test('股票搜索功能正常', async ({ page }) => {
            await helpers.login(page);

            // 测试搜索功能
            await page.click('[data-testid="search-input"]');
            await page.fill('[data-testid="search-input"]', '平安银行');
            await page.press('[data-testid="search-input"]', 'Enter');

            // 验证搜索结果
            await expect(page.locator('[data-testid="search-results"]')).toBeVisible({ timeout: 5000 });
            await expect(page.locator('[data-testid="stock-000001"]')).toContainText('平安银行');

            // 测试股票详情页
            await page.click('[data-testid="stock-000001"]');
            await expect(page.locator('[data-testid="stock-detail"]')).toBeVisible();

            // 验证关键数据字段
            const currentPrice = await page.locator('[data-testid="current-price"]').textContent();
            const volume = await page.locator('[data-testid="volume"]').textContent();
            const change = await page.locator('[data-testid="price-change"]').textContent();

            expect(currentPrice).toMatch(/^\d+\.\d{2}$/); // 价格格式验证
            expect(volume).toMatch(/^\d+$/); // 成交量格式验证
        });

        test('多条件筛选功能', async ({ page }) => {
            await helpers.login(page);

            // 进入股票筛选页面
            await page.click('[data-testid="stock-filter-nav"]');
            await expect(page.locator('[data-testid="filter-page"]')).toBeVisible();

            // 设置筛选条件
            await page.selectOption('[data-testid="industry-filter"]', '金融');
            await page.fill('[data-testid="price-min"]', '10');
            await page.fill('[data-testid="price-max"]', '50');
            await page.click('[data-testid="apply-filter"]');

            // 验证筛选结果
            await expect(page.locator('[data-testid="filter-results"]')).toBeVisible();
            const resultCount = await page.locator('[data-testid="result-count"]').textContent();
            expect(parseInt(resultCount)).toBeGreaterThan(0);
        });

        test('历史数据查询功能', async ({ page }) => {
            await helpers.login(page);

            // 搜索股票
            await page.goto(`${BASE_URL}/stock/000001`);

            // 切换到历史数据标签页
            await page.click('[data-testid="history-tab"]');
            await expect(page.locator('[data-testid="history-chart"]')).toBeVisible();

            // 测试时间范围选择
            await page.selectOption('[data-testid="time-range"]', '1月');
            await expect(page.locator('[data-testid="history-data"]')).toBeVisible();

            // 验证数据完整性
            const dataPoints = await page.locator('[data-testid="data-point"]').count();
            expect(dataPoints).toBeGreaterThan(15); // 至少15个交易日数据
        });
    });

    test.describe('技术分析功能', () => {
        test('技术指标计算和显示', async ({ page }) => {
            await helpers.login(page);
            await page.goto(`${BASE_URL}/stock/000001`);

            // 切换到技术分析标签页
            await page.click('[data-testid="technical-tab"]');
            await expect(page.locator('[data-testid="technical-analysis"]')).toBeVisible();

            // 测试添加技术指标
            await page.click('[data-testid="add-indicator"]');
            await page.selectOption('[data-testid="indicator-select"]', 'MA');
            await page.fill('[data-testid="ma-period"]', '5');
            await page.click('[data-testid="confirm-indicator"]');

            // 验证指标显示
            await expect(page.locator('[data-testid="ma-indicator"]')).toBeVisible();

            // 测试多个指标
            await page.click('[data-testid="add-indicator"]');
            await page.selectOption('[data-testid="indicator-select"]', 'MACD');
            await page.click('[data-testid="confirm-indicator"]');

            await expect(page.locator('[data-testid="macd-indicator"]')).toBeVisible();
        });

        test('图表交互功能', async ({ page }) => {
            await helpers.login(page);
            await page.goto(`${BASE_URL}/stock/000001`);

            // 测试图表缩放
            await page.click('[data-testid="chart-zoom-in"]');
            await page.click('[data-testid="chart-zoom-out"]');

            // 测试图表拖拽
            const chart = page.locator('[data-testid="price-chart"]');
            await chart.hover();
            await page.mouse.down();
            await page.mouse.move(100, 100);
            await page.mouse.up();

            // 测试十字线
            await chart.hover();
            await expect(page.locator('[data-testid="crosshair"]')).toBeVisible();
        });

        test('图表类型切换', async ({ page }) => {
            await helpers.login(page);
            await page.goto(`${BASE_URL}/stock/000001`);

            // 测试不同图表类型
            const chartTypes = ['K线', '分时', '美国线'];
            for (const chartType of chartTypes) {
                await page.selectOption('[data-testid="chart-type"]', chartType);
                await expect(page.locator('[data-testid="price-chart"]')).toBeVisible();

                // 验证图表类型切换后的内容
                const currentType = await page.locator('[data-testid="current-chart-type"]').textContent();
                expect(currentType).toContain(chartType);
            }
        });
    });

    test.describe('策略管理功能', () => {
        test('策略创建和保存', async ({ page }) => {
            await helpers.login(page);
            await page.goto(`${BASE_URL}/strategy`);

            // 创建新策略
            await page.click('[data-testid="create-strategy"]');
            await page.fill('[data-testid="strategy-name"]', '测试策略');
            await page.selectOption('[data-testid="strategy-type"]', '均线交叉');
            await page.fill('[data-testid="short-ma"]', '5');
            await page.fill('[data-testid="long-ma"]', '20');
            await page.click('[data-testid="save-strategy"]');

            // 验证策略保存成功
            await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
            await expect(page.locator('[data-testid="strategy-list"]')).toContainText('测试策略');
        });

        test('策略回测功能', async ({ page }) => {
            await helpers.login(page);
            await page.goto(`${BASE_URL}/strategy`);

            // 选择策略进行回测
            await page.click('[data-testid="strategy-item"]:first-child');
            await page.click('[data-testid="run-backtest"]');

            // 等待回测完成
            await expect(page.locator('[data-testid="backtest-results"]')).toBeVisible({ timeout: 10000 });

            // 验证回测结果
            const totalReturn = await page.locator('[data-testid="total-return"]').textContent();
            const winRate = await page.locator('[data-testid="win-rate"]').textContent();
            const maxDrawdown = await page.locator('[data-testid="max-drawdown"]').textContent();

            expect(totalReturn).toMatch(/^-?\d+\.\d+%$/);
            expect(winRate).match(/^\d+\.\d+%$/);
            expect(maxDrawdown).match(/^\d+\.\d+%$/);
        });

        test('策略执行监控', async ({ page }) => {
            await helpers.login(page);
            await page.goto(`${BASE_URL}/strategy`);

            // 启动策略执行
            await page.click('[data-testid="strategy-item"]:first-child');
            await page.click('[data-testid="start-strategy"]');

            // 验证执行状态
            await expect(page.locator('[data-testid="strategy-status"]')).toContainText('运行中');

            // 检查执行记录
            await page.click('[data-testid="execution-records"]');
            await expect(page.locator('[data-testid="execution-log"]')).toBeVisible();
        });
    });

    test.describe('实时监控功能', () => {
        test('实时数据推送', async ({ page }) => {
            await helpers.login(page);
            await page.goto(`${BASE_URL}/stock/000001`);

            // 监听WebSocket连接
            const wsMessages = [];
            page.on('websocket', ws => {
                ws.on('framesent', event => wsMessages.push({ type: 'sent', payload: event.payload }));
                ws.on('framereceived', event => wsMessages.push({ type: 'received', payload: event.payload }));
            });

            // 等待实时数据推送
            await expect(page.locator('[data-testid="realtime-price"]')).toBeVisible();

            // 验证WebSocket消息
            expect(wsMessages.length).toBeGreaterThan(0);

            const receivedMessages = wsMessages.filter(m => m.type === 'received');
            expect(receivedMessages.length).toBeGreaterThan(0);

            // 验证消息格式
            const latestMessage = JSON.parse(receivedMessages[receivedMessages.length - 1].payload);
            expect(latestMessage).toHaveProperty('price');
            expect(latestMessage).toHaveProperty('timestamp');
        });

        test('价格提醒功能', async ({ page }) => {
            await helpers.login(page);
            await page.goto(`${BASE_URL}/alerts`);

            // 创建价格提醒
            await page.click('[data-testid="create-alert"]');
            await page.selectOption('[data-testid="alert-stock"]', '000001');
            await page.selectOption('[data-testid="alert-type"]', '价格突破');
            await page.fill('[data-testid="target-price"]', '15.00');
            await page.click('[data-testid="save-alert"]');

            // 验证提醒创建成功
            await expect(page.locator('[data-testid="alert-list"]')).toContainText('000001');
            await expect(page.locator('[data-testid="alert-list"]')).toContainText('15.00');
        });
    });
});

// 性能测试组
test.describe('⚡ 性能测试', () => {
    test('页面加载性能', async ({ page }) => {
        const startTime = Date.now();

        await page.goto(BASE_URL);
        await helpers.waitForPageLoad(page);

        const loadTime = Date.now() - startTime;

        // 验证页面加载时间不超过2秒
        expect(loadTime).toBeLessThan(2000);

        // 检查关键资源加载
        const performanceEntries = await page.evaluate(() => {
            const navigation = performance.getEntriesByType('navigation')[0];
            return {
                domContentLoaded: Math.round(navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart),
                loadComplete: Math.round(navigation.loadEventEnd - navigation.loadEventStart),
                firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0,
                firstContentfulPaint: performance.getEntriesByType('paint')[1]?.startTime || 0
            };
        });

        expect(performanceEntries.firstContentfulPaint).toBeLessThan(1500);
        expect(performanceEntries.domContentLoaded).toBeLessThan(1000);
    });

    test('API响应性能', async ({ page }) => {
        await page.goto(BASE_URL);
        await helpers.login(page);

        // 测试搜索API性能
        const searchTime = await helpers.measureLoadTime(page, '[data-testid="search-results"]');
        expect(searchTime).toBeLessThan(1000);

        // 测试数据加载API性能
        const dataLoadTime = await helpers.measureLoadTime(page, '[data-testid="stock-data"]');
        expect(dataLoadTime).toBeLessThan(1500);

        // 测试图表渲染性能
        await page.goto(`${BASE_URL}/stock/000001`);
        const chartRenderTime = await helpers.measureLoadTime(page, '[data-testid="price-chart"]');
        expect(chartRenderTime).toBeLessThan(2000);
    });

    test('并发访问性能', async ({ page, context }) => {
        // 创建多个并发页面
        const pages = [];
        const startTime = Date.now();

        for (let i = 0; i < 5; i++) {
            const newPage = await context.newPage();
            pages.push(newPage);
        }

        // 并发访问不同页面
        const pageUrls = [
            `${BASE_URL}/dashboard`,
            `${BASE_URL}/stock/000001`,
            `${BASE_URL}/stock/000002`,
            `${BASE_URL}/strategy`,
            `${BASE_URL}/alerts`
        ];

        const loadPromises = pages.map((p, index) =>
            p.goto(pageUrls[index]).then(() => helpers.waitForPageLoad(p))
        );

        await Promise.all(loadPromises);

        const totalTime = Date.now() - startTime;

        // 验证并发加载时间合理
        expect(totalTime).toBeLessThan(5000);

        // 清理页面
        for (const p of pages) {
            await p.close();
        }
    });

    test('网络慢速条件下的性能', async ({ page }) => {
        // 模拟慢速网络
        await helpers.simulateSlowNetwork(page);

        const startTime = Date.now();
        await page.goto(BASE_URL);
        await helpers.waitForPageLoad(page);

        const loadTime = Date.now() - startTime;

        // 即使在慢速网络下，页面也应该在10秒内加载完成
        expect(loadTime).toBeLessThan(10000);

        // 验证加载指示器显示
        await expect(page.locator('[data-testid="loading-indicator"]')).toBeVisible();
    });
});

// 安全性测试组
test.describe('🔒 安全性测试', () => {
    test('XSS防护测试', async ({ page }) => {
        await page.goto(`${BASE_URL}/login`);

        // 尝试注入恶意脚本
        const xssPayload = '<script>alert("XSS")</script>';
        await page.fill('[data-testid="username-input"]', xssPayload);
        await page.click('[data-testid="login-button"]');

        // 验证脚本未执行（没有alert弹出）
        await expect(page.locator('[data-testid="error-message"]')).toBeVisible();

        // 验证输入被正确转义
        const inputValue = await page.inputValue('[data-testid="username-input"]');
        expect(inputValue).not.toContain('<script>');
    });

    test('SQL注入防护测试', async ({ page }) => {
        await page.goto(`${BASE_URL}/dashboard`);

        // 尝试SQL注入
        const sqlPayload = "'; DROP TABLE users; --";
        await page.fill('[data-testid="search-input"]', sqlPayload);
        await page.press('[data-testid="search-input"]', 'Enter');

        // 验证页面没有崩溃，搜索结果要么为空要么正常显示
        await expect(page.locator('body')).toBeVisible();

        // 检查是否有错误信息
        const errorExists = await helpers.isElementVisible(page, '[data-testid="database-error"]');
        expect(errorExists).toBe(false);
    });

    test('CSRF防护测试', async ({ page, context }) => {
        // 登录获取会话
        await helpers.login(page);

        // 尝试跨站请求伪造
        const maliciousPage = await context.newPage();
        await maliciousPage.goto('data:text/html,<form id="csrf" method="POST" action="http://localhost:8020/api/user/delete"><input type="hidden" name="user_id" value="admin"></form>');
        await maliciousPage.click('#csrf input[type="submit"]');

        // 验证请求被拒绝
        await expect(maliciousPage.locator('body')).toContainText('Forbidden');

        await maliciousPage.close();
    });

    test('敏感信息泄露测试', async ({ page }) => {
        await page.goto(BASE_URL);

        // 检查页面源码中是否包含敏感信息
        const pageContent = await page.content();

        // 不应包含密码、API密钥等敏感信息
        expect(pageContent).not.toMatch(/password/i);
        expect(pageContent).not.toMatch(/api[_-]?key/i);
        expect(pageContent).not.toMatch(/secret/i);

        // 检查控制台错误
        const consoleErrors = [];
        page.on('console', msg => {
            if (msg.type() === 'error') {
                consoleErrors.push(msg.text());
            }
        });

        await helpers.login(page);

        // 不应该有暴露敏感信息的控制台错误
        const sensitiveErrors = consoleErrors.filter(error =>
            error.match(/password|token|key|secret/i)
        );
        expect(sensitiveErrors.length).toBe(0);
    });
});

// 用户体验测试组
test.describe('👤 用户体验测试', () => {
    test('响应式设计测试', async ({ page }) => {
        // 桌面视图
        await page.setViewportSize({ width: 1920, height: 1080 });
        await page.goto(`${BASE_URL}/dashboard`);

        await expect(page.locator('[data-testid="sidebar"]')).toBeVisible();
        await expect(page.locator('[data-testid="main-content"]')).toBeVisible();
    });

    test('无障碍访问测试', async ({ page }) => {
        await page.goto(BASE_URL);

        // 检查键盘导航
        await page.keyboard.press('Tab');
        const focusedElement = await page.evaluate(() => document.activeElement.tagName);
        expect(['BUTTON', 'INPUT', 'SELECT', 'A']).toContain(focusedElement);

        // 检查ARIA标签
        await page.goto(`${BASE_URL}/login`);
        await expect(page.locator('[data-testid="username-input"]')).toHaveAttribute('aria-label');
        await expect(page.locator('[data-testid="password-input"]')).toHaveAttribute('aria-label');

        // 检查图片alt属性
        await page.goto(`${BASE_URL}/dashboard`);
        const images = await page.locator('img').all();
        for (const img of images) {
            const hasAlt = await img.getAttribute('alt');
            expect(hasAlt).toBeTruthy();
        }
    });

    test('交互反馈测试', async ({ page }) => {
        await page.goto(`${BASE_URL}/login`);

        // 测试按钮点击反馈
        await page.click('[data-testid="login-button"]');

        // 验证loading状态
        await expect(page.locator('[data-testid="loading-spinner"]')).toBeVisible();

        // 验证错误提示
        await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
        await expect(page.locator('[data-testid="error-message"]')).toHaveText(/用户名或密码错误/);
    });

    test('导航流畅性测试', async ({ page }) => {
        await helpers.login(page);

        // 测试页面间导航
        const navigationTests = [
            { from: '/dashboard', to: '/strategy', element: '[data-testid="strategy-nav"]' },
            { from: '/strategy', to: '/alerts', element: '[data-testid="alerts-nav"]' },
            { from: '/alerts', to: '/dashboard', element: '[data-testid="dashboard-nav"]' }
        ];

        for (const test of navigationTests) {
            const startTime = Date.now();

            await page.goto(`${BASE_URL}${test.from}`);
            await page.click(test.element);
            await helpers.waitForPageLoad(page);

            const navigationTime = Date.now() - startTime;
            expect(navigationTime).toBeLessThan(1000); // 导航应在1秒内完成

            // 验证目标页面加载
            await expect(page).toHaveURL(new RegExp(test.to));
        }
    });
});

// 数据质量测试组
test.describe('📊 数据质量测试', () => {
    test('数据准确性测试', async ({ page }) => {
        await helpers.login(page);
        await page.goto(`${BASE_URL}/stock/000001`);

        // 获取多个数据源的数据进行对比
        const currentPageData = await page.evaluate(() => {
            return {
                currentPrice: document.querySelector('[data-testid="current-price"]')?.textContent,
                volume: document.querySelector('[data-testid="volume"]')?.textContent,
                change: document.querySelector('[data-testid="price-change"]')?.textContent
            };
        });

        // 验证数据格式正确性
        expect(currentPageData.currentPrice).toMatch(/^\d+\.\d{2}$/);
        expect(currentPageData.volume).toMatch(/^\d+$/);
        expect(currentPageData.change).toMatch(/^[+-]?\d+\.\d{2}$/);

        // 验证数值合理性
        const price = parseFloat(currentPageData.currentPrice);
        const volume = parseInt(currentPageData.volume);
        const change = parseFloat(currentPageData.change);

        expect(price).toBeGreaterThan(0);
        expect(price).toBeLessThan(10000); // 合理的价格范围
        expect(volume).toBeGreaterThanOrEqual(0);
        expect(Math.abs(change)).toBeLessThan(price * 0.2); // 涨跌幅不应超过20%
    });

    test('数据完整性测试', async ({ page }) => {
        await helpers.login(page);

        // 测试多只股票的数据完整性
        for (const symbol of TEST_STOCKS) {
            await page.goto(`${BASE_URL}/stock/${symbol}`);

            // 检查必要数据字段
            const requiredFields = [
                '[data-testid="current-price"]',
                '[data-testid="volume"]',
                '[data-testid="price-change"]',
                '[data-testid="open-price"]',
                '[data-testid="high-price"]',
                '[data-testid="low-price"]',
                '[data-testid="close-price"]'
            ];

            for (const field of requiredFields) {
                const element = page.locator(field);
                await expect(element).toBeVisible();

                const text = await element.textContent();
                expect(text).toBeTruthy();
                expect(text.trim()).not.toBe('');
            }
        }
    });

    test('实时数据更新测试', async ({ page }) => {
        await helpers.login(page);
        await page.goto(`${BASE_URL}/stock/000001`);

        // 记录初始价格
        const initialPrice = await page.locator('[data-testid="current-price"]').textContent();

        // 等待数据更新（最多等待30秒）
        let priceUpdated = false;
        for (let i = 0; i < 30; i++) {
            await page.waitForTimeout(1000);
            const currentPrice = await page.locator('[data-testid="current-price"]').textContent();

            if (currentPrice !== initialPrice) {
                priceUpdated = true;
                break;
            }
        }

        // 验证最后更新时间
        const lastUpdateTime = await page.locator('[data-testid="last-update-time"]').textContent();
        expect(lastUpdateTime).toBeTruthy();

        // 检查实时指示器
        await expect(page.locator('[data-testid="realtime-indicator"]')).toBeVisible();
    });

    test('历史数据连续性测试', async ({ page }) => {
        await helpers.login(page);
        await page.goto(`${BASE_URL}/stock/000001`);

        // 切换到历史数据视图
        await page.click('[data-testid="history-tab"]');
        await page.selectOption('[data-testid="time-range"]', '1月');

        // 获取历史数据
        const historyData = await page.evaluate(() => {
            const rows = document.querySelectorAll('[data-testid="history-row"]');
            return Array.from(rows).map(row => ({
                date: row.querySelector('[data-testid="date"]')?.textContent,
                price: row.querySelector('[data-testid="price"]')?.textContent
            }));
        });

        // 验证数据点数量
        expect(historyData.length).toBeGreaterThan(15); // 至少15个交易日

        // 验证日期连续性（允许节假日间隔）
        for (let i = 1; i < historyData.length; i++) {
            const prevDate = new Date(historyData[i - 1].date);
            const currDate = new Date(historyData[i].date);

            const dayDiff = Math.floor((currDate - prevDate) / (1000 * 60 * 60 * 24));
            expect(dayDiff).toBeLessThanOrEqual(7); // 最多间隔7天
        }
    });
});

// 集成测试组
test.describe('🔗 集成测试', () => {
    test('端到端用户流程测试', async ({ page }) => {
        // 完整的用户使用流程
        await page.goto(BASE_URL);

        // 1. 登录
        await helpers.login(page);

        // 2. 搜索股票
        await page.fill('[data-testid="search-input"]', '平安银行');
        await page.press('[data-testid="search-input"]', 'Enter');
        await page.click('[data-testid="stock-000001"]');

        // 3. 查看技术分析
        await page.click('[data-testid="technical-tab"]');
        await page.click('[data-testid="add-indicator"]');
        await page.selectOption('[data-testid="indicator-select"]', 'MA');
        await page.click('[data-testid="confirm-indicator"]');

        // 4. 创建策略
        await page.goto(`${BASE_URL}/strategy`);
        await page.click('[data-testid="create-strategy"]');
        await page.fill('[data-testid="strategy-name"]', '集成测试策略');
        await page.click('[data-testid="save-strategy"]');

        // 5. 创建价格提醒
        await page.goto(`${BASE_URL}/alerts`);
        await page.click('[data-testid="create-alert"]');
        await page.selectOption('[data-testid="alert-stock"]', '000001');
        await page.fill('[data-testid="target-price"]', '15.00');
        await page.click('[data-testid="save-alert"]');

        // 验证整个流程成功
        await expect(page.locator('[data-testid="alert-list"]')).toContainText('000001');
    });

    test('多标签页数据同步测试', async ({ page, context }) => {
        await helpers.login(page);

        // 在第一个标签页搜索股票
        await page.goto(`${BASE_URL}/stock/000001`);
        const price1 = await page.locator('[data-testid="current-price"]').textContent();

        // 在第二个标签页搜索相同股票
        const page2 = await context.newPage();
        await page2.goto(`${BASE_URL}/login`);
        await helpers.login(page2);
        await page2.goto(`${BASE_URL}/stock/000001`);

        // 验证数据一致性
        const price2 = await page2.locator('[data-testid="current-price"]').textContent();
        expect(price1).toBe(price2);

        await page2.close();
    });
});

// 错误处理测试组
test.describe('🚨 错误处理测试', () => {
    test('网络错误处理', async ({ page }) => {
        await page.goto(`${BASE_URL}/login`);

        // 模拟网络断开
        await page.setOffline(true);

        // 尝试登录
        await page.fill('[data-testid="username-input"]', TEST_USER.username);
        await page.fill('[data-testid="password-input"]', TEST_USER.password);
        await page.click('[data-testid="login-button"]');

        // 验证网络错误提示
        await expect(page.locator('[data-testid="network-error"]')).toBeVisible();

        // 恢复网络连接
        await page.setOffline(false);

        // 验证重试按钮
        await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();
    });

    test('服务器错误处理', async ({ page }) => {
        // 模拟服务器错误
        await page.route('**/api/auth/login', route =>
            route.fulfill({ status: 500, body: '{"error": "Internal Server Error"}' })
        );

        await page.goto(`${BASE_URL}/login`);
        await page.fill('[data-testid="username-input"]', TEST_USER.username);
        await page.fill('[data-testid="password-input"]', TEST_USER.password);
        await page.click('[data-testid="login-button"]');

        // 验证错误提示
        await expect(page.locator('[data-testid="server-error"]')).toBeVisible();
        await expect(page.locator('[data-testid="error-message"]')).toContainText('服务器错误');
    });

    test('数据加载失败处理', async ({ page }) => {
        // 模拟数据加载失败
        await page.route('**/api/data/realtime/*', route =>
            route.fulfill({ status: 404, body: '{"error": "Data not found"}' })
        );

        await helpers.login(page);
        await page.goto(`${BASE_URL}/stock/000001`);

        // 验证数据加载失败提示
        await expect(page.locator('[data-testid="data-load-error"]')).toBeVisible();
        await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();
    });
});
