const { execSync } = require("child_process");
const fs = require("fs");
const getAxios = require("./http-client");

const performanceMethods = {
  async runPerformanceTests() {
    // 1. Lighthouse性能审计
    console.log("  🔍 执行Lighthouse性能审计...");
    const lighthouseResults = await this.runLighthouseTest();
    this.testResults.performance.lighthouse = lighthouseResults;

    // 2. API响应时间测试
    console.log("  ⏱️ 执行API响应时间测试...");
    const apiPerfResults = await this.runAPIPerformanceTest();
    this.testResults.performance.api = apiPerfResults;

    // 3. 并发负载测试
    console.log("  🚀 执行并发负载测试...");
    const loadTestResults = await this.runLoadTest();
    this.testResults.performance.load = loadTestResults;

    // 4. 资源使用测试
    console.log("  💾 执行资源使用测试...");
    const resourceResults = await this.runResourceTest();
    this.testResults.performance.resources = resourceResults;
  },

  async runLighthouseTest() {
    try {
      // 使用lighthouse CLI
      execSync(
        `npx lighthouse ${this.config.baseUrl} --output=json --output-path=lighthouse-report.json --chrome-flags="--headless"`,
        {
          encoding: "utf8",
          timeout: 120000,
        }
      );

      const report = JSON.parse(fs.readFileSync("lighthouse-report.json", "utf8"));

      return {
        performance: Math.round(report.categories.performance.score * 100),
        accessibility: Math.round(report.categories.accessibility.score * 100),
        bestPractices: Math.round(report.categories["best-practices"].score * 100),
        seo: Math.round(report.categories.seo.score * 100),
        metrics: {
          firstContentfulPaint: Math.round(report.audits["first-contentful-paint"].numericValue),
          largestContentfulPaint: Math.round(report.audits["largest-contentful-paint"].numericValue),
          cumulativeLayoutShift: report.audits["cumulative-layout-shift"].numericValue,
          totalBlockingTime: report.audits["total-blocking-time"].numericValue,
        },
      };
    } catch (error) {
      console.error("❌ Lighthouse测试失败:", error.message);
      return { error: error.message };
    }
  },

  async runAPIPerformanceTest() {
    const axios = getAxios();
    const endpoints = [
      "/api/stock/search",
      "/api/data/realtime/000001",
      "/api/data/history/000001?period=1d&count=100",
      "/api/indicators/MA?symbol=000001&period=5",
    ];

    const results = [];

    for (const endpoint of endpoints) {
      const times = [];
      const iterations = 10;

      for (let i = 0; i < iterations; i += 1) {
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
          successRate: times.length / iterations,
        });
      }
    }

    return results;
  },

  async runLoadTest() {
    const axios = getAxios();
    // 简单的并发测试
    const concurrent = 50;
    const iterations = 10;
    const endpoint = `${this.config.apiUrl}/health`;

    console.log(`    🚀 并发测试: ${concurrent} 并发, ${iterations} 轮次`);

    const results = [];
    const startTime = Date.now();

    for (let i = 0; i < iterations; i += 1) {
      const promises = [];
      const iterationStart = Date.now();

      for (let j = 0; j < concurrent; j += 1) {
        promises.push(
          axios
            .get(endpoint, { timeout: 5000 })
            .then(() => ({ status: "success", time: Date.now() }))
            .catch(error => ({ status: "error", error: error.message, time: Date.now() }))
        );
      }

      const iterationResults = await Promise.all(promises);
      const iterationEnd = Date.now();
      const iterationDuration = iterationEnd - iterationStart;
      const successCount = iterationResults.filter(r => r.status === "success").length;

      results.push({
        iteration: i + 1,
        duration: iterationDuration,
        successCount,
        failureCount: concurrent - successCount,
        successRate: successCount / concurrent,
        throughput: Math.round(concurrent / (iterationDuration / 1000)),
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
      results,
    };
  },

  async runResourceTest() {
    const axios = getAxios();
    try {
      // 使用前端资源检查
      const response = await axios.get(`${this.config.baseUrl}`, { timeout: 10000 });
      const contentLength = response.headers["content-length"] || 0;

      return {
        pageSize: Math.round(contentLength / 1024), // KB
        loadTime: Date.now() - response.config.metadata?.startTime,
      };
    } catch (error) {
      return { error: error.message };
    }
  },
};

module.exports = performanceMethods;
