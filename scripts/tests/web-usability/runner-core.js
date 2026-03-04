#!/usr/bin/env node

/**
 * MyStocks Web端可用性测试执行器
 * 薄核心编排器：具体测试实现拆分至 ./core/*.js
 */

const fs = require("fs");

const environmentMethods = require("./core/environment");
const functionalMethods = require("./core/functional");
const performanceMethods = require("./core/performance");
const securityMethods = require("./core/security");
const usabilityMethods = require("./core/usability");
const dataQualityMethods = require("./core/data-quality");
const scoringMethods = require("./core/scoring");
const reportHtmlMethods = require("./core/report-html");

const FRONTEND_PORT = process.env.FRONTEND_PORT || "3020";
const BACKEND_PORT = process.env.BACKEND_PORT || "8020";

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
        passRate: 0,
      },
    };

    this.config = {
      baseUrl: process.env.BASE_URL || process.env.FRONTEND_URL || `http://localhost:${FRONTEND_PORT}`,
      apiUrl: process.env.API_URL || process.env.BACKEND_URL || `http://localhost:${BACKEND_PORT}`,
      timeout: parseInt(process.env.TEST_TIMEOUT, 10) || 60000,
      retries: parseInt(process.env.TEST_RETRIES, 10) || 2,
    };
  }

  async runAllTests() {
    console.log("🚀 开始执行MyStocks Web端可用性测试套件");
    console.log(`📊 基础URL: ${this.config.baseUrl}`);
    console.log(`🔗 API URL: ${this.config.apiUrl}`);

    try {
      // 1. 环境检查
      await this.checkEnvironment();

      // 2. 功能性测试
      console.log("\n🧪 执行功能性测试...");
      await this.runFunctionalTests();

      // 3. 性能测试
      console.log("\n⚡ 执行性能测试...");
      await this.runPerformanceTests();

      // 4. 安全性测试
      console.log("\n🔒 执行安全性测试...");
      await this.runSecurityTests();

      // 5. 用户体验测试
      console.log("\n👤 执行用户体验测试...");
      await this.runUsabilityTests();

      // 6. 数据质量测试
      console.log("\n📊 执行数据质量测试...");
      await this.runDataQualityTests();

      // 7. 生成测试报告
      console.log("\n📄 生成测试报告...");
      await this.generateReport();

      // 8. 计算通过标准
      console.log("\n✅ 评估测试通过标准...");
      this.evaluatePassingCriteria();

      console.log("\n🎉 所有测试执行完成！");
      console.log(`📊 总体通过率: ${this.testResults.summary.passRate}%`);

      return this.testResults;
    } catch (error) {
      console.error("❌ 测试执行过程中发生错误:", error);
      throw error;
    }
  }

  async generateReport() {
    // 计算总统计
    this.calculateSummary();

    // 生成HTML报告
    const htmlReport = this.generateHTMLReport();
    fs.writeFileSync("web-usability-test-report.html", htmlReport);

    // 生成JSON报告
    fs.writeFileSync("web-usability-test-results.json", JSON.stringify(this.testResults, null, 2));

    console.log("📄 测试报告已生成:");
    console.log("   - HTML报告: web-usability-test-report.html");
    console.log("   - JSON数据: web-usability-test-results.json");
  }
}

Object.assign(
  WebUsabilityTestRunner.prototype,
  environmentMethods,
  functionalMethods,
  performanceMethods,
  securityMethods,
  usabilityMethods,
  dataQualityMethods,
  scoringMethods,
  reportHtmlMethods
);

// 如果直接运行此脚本
if (require.main === module) {
  const runner = new WebUsabilityTestRunner();
  runner
    .runAllTests()
    .then(results => {
      console.log("\n🎉 测试执行完成！");
      console.log(`📊 总体评分: ${results.summary.overallScore}%`);
      console.log(
        `${results.summary.meetsStandard ? "✅" : "❌"} ${
          results.summary.meetsStandard ? '达到"完全可用"标准' : '未达到"完全可用"标准'
        }`
      );
      process.exit(results.summary.meetsStandard ? 0 : 1);
    })
    .catch(error => {
      console.error("❌ 测试执行失败:", error);
      process.exit(1);
    });
}

module.exports = WebUsabilityTestRunner;
