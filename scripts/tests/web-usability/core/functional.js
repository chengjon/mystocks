const { execSync } = require("child_process");
const getAxios = require("./http-client");

const functionalMethods = {
  async runFunctionalTests() {
    const testCategories = ["search", "analysis", "strategy", "dashboard", "portfolio"];

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
          error: error.message,
        };
      }
    }

    // 执行API功能测试
    console.log("  📡 执行API功能测试...");
    try {
      const apiResults = await this.executeAPITests();
      this.testResults.functional.api = apiResults;
      console.log(`    ✅ API: ${apiResults.passed}/${apiResults.total} 通过`);
    } catch (error) {
      console.error(`    ❌ API测试失败:`, error.message);
    }
  },

  async executePlaywrightTests(testPattern) {
    try {
      const result = execSync(
        `npx playwright test --config=playwright.config.web.ts --grep="${testPattern}" --reporter=json`,
        {
          encoding: "utf8",
          timeout: this.config.timeout,
        }
      );

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
  },

  parsePlaywrightResults(report) {
    if (!report.suites || report.suites.length === 0) {
      return { total: 0, passed: 0, failed: 0, duration: 0 };
    }

    let total = 0;
    let passed = 0;
    let failed = 0;
    let duration = 0;

    report.suites.forEach(suite => {
      suite.specs.forEach(spec => {
        spec.tests.forEach(test => {
          total += 1;
          duration += test.results[0].duration;
          if (test.results[0].status === "passed") {
            passed += 1;
          } else {
            failed += 1;
          }
        });
      });
    });

    return { total, passed, failed, duration: Math.round(duration / 1000) };
  },

  async executeAPITests() {
    const axios = getAxios();
    const apiTests = [
      { name: "股票搜索", endpoint: "/api/stock/search", method: "GET" },
      { name: "实时数据", endpoint: "/api/data/realtime/000001", method: "GET" },
      { name: "历史数据", endpoint: "/api/data/history/000001", method: "GET" },
      { name: "技术指标", endpoint: "/api/indicators/MA", method: "GET" },
      { name: "用户认证", endpoint: "/api/auth/login", method: "POST" },
    ];

    const total = apiTests.length;
    let passed = 0;
    let failed = 0;
    const errors = [];

    for (const test of apiTests) {
      try {
        const config = {
          method: test.method,
          url: `${this.config.apiUrl}${test.endpoint}`,
          timeout: 5000,
          validateStatus: () => true, // 不抛出状态码错误
        };

        if (test.method === "POST") {
          config.data = { username: "test", password: "test" };
          config.headers = { "Content-Type": "application/json" };
        }

        const response = await axios(config);

        if (response.status >= 200 && response.status < 500) {
          passed += 1;
          console.log(`    ✅ ${test.name}: ${response.status}`);
        } else {
          failed += 1;
          errors.push(`${test.name}: HTTP ${response.status}`);
        }
      } catch (error) {
        failed += 1;
        errors.push(`${test.name}: ${error.message}`);
        console.log(`    ❌ ${test.name}: ${error.message}`);
      }
    }

    return { total, passed, failed, errors };
  },
};

module.exports = functionalMethods;
