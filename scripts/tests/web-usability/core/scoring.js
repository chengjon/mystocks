const scoringMethods = {
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
    ["performance", "security", "usability", "dataQuality"].forEach(category => {
      const categoryData = this.testResults[category];
      Object.values(categoryData).forEach(test => {
        if (Array.isArray(test)) {
          test.forEach(item => {
            if (item.status !== undefined) {
              totalTests += 1;
              if (item.status === "passed" || item.accurate || item.safe || item.success) {
                totalPassed += 1;
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
  },

  evaluatePassingCriteria() {
    const criteria = {
      functional: {
        required: 95,
        actual: this.calculateFunctionalPassRate(),
      },
      performance: {
        required: 95,
        actual: this.calculatePerformanceScore(),
      },
      security: {
        required: 100,
        actual: this.calculateSecurityScore(),
      },
      usability: {
        required: 90,
        actual: this.calculateUsabilityScore(),
      },
      dataQuality: {
        required: 99,
        actual: this.calculateDataQualityScore(),
      },
    };

    console.log("\n📊 通过标准评估:");
    Object.entries(criteria).forEach(([category, evaluation]) => {
      const status = evaluation.actual >= evaluation.required ? "✅" : "❌";
      console.log(`  ${status} ${category}: ${evaluation.actual}% (要求: ${evaluation.required}%)`);
    });

    const overallScore =
      Object.values(criteria).reduce((sum, criterion) => sum + criterion.actual, 0) / Object.keys(criteria).length;
    const meetsOverallStandard = overallScore >= 95;

    console.log(`\n🎯 总体评分: ${Math.round(overallScore)}%`);
    console.log(`${meetsOverallStandard ? "✅" : "❌"} ${meetsOverallStandard ? '达到"完全可用"标准' : '未达到"完全可用"标准'}`);

    this.testResults.summary.overallScore = Math.round(overallScore);
    this.testResults.summary.meetsStandard = meetsOverallStandard;
    this.testResults.summary.criteria = criteria;
  },

  calculateFunctionalPassRate() {
    const functional = this.testResults.functional;
    let total = 0;
    let passed = 0;

    Object.values(functional).forEach(category => {
      if (category.total) {
        total += category.total;
        passed += category.passed;
      }
    });

    return total > 0 ? Math.round((passed / total) * 100) : 0;
  },

  calculatePerformanceScore() {
    const performance = this.testResults.performance;
    let score = 0;
    let factors = 0;

    if (performance.lighthouse && performance.lighthouse.performance) {
      score += performance.lighthouse.performance;
      factors += 1;
    }

    if (performance.api && Array.isArray(performance.api)) {
      const avgResponseTime = performance.api.reduce((sum, item) => sum + item.average, 0) / performance.api.length;
      const responseScore = Math.max(0, 100 - avgResponseTime / 10); // 每10ms扣1分
      score += Math.min(100, responseScore);
      factors += 1;
    }

    return factors > 0 ? Math.round(score / factors) : 0;
  },

  calculateSecurityScore() {
    const security = this.testResults.security;
    let totalTests = 0;
    let passedTests = 0;

    Object.values(security).forEach(category => {
      if (Array.isArray(category)) {
        category.forEach(test => {
          totalTests += 1;
          if (test.status === "passed" || test.safe || test.accurate) {
            passedTests += 1;
          }
        });
      }
    });

    return totalTests > 0 ? Math.round((passedTests / totalTests) * 100) : 0;
  },

  calculateUsabilityScore() {
    const usability = this.testResults.usability;
    let score = 0;
    let factors = 0;

    Object.values(usability).forEach(category => {
      if (Array.isArray(category)) {
        const passed = category.filter(item => item.success || item.found).length;
        const scoreFactor = (passed / category.length) * 100;
        score += scoreFactor;
        factors += 1;
      }
    });

    return factors > 0 ? Math.round(score / factors) : 0;
  },

  calculateDataQualityScore() {
    const dataQuality = this.testResults.dataQuality;
    let totalTests = 0;
    let passedTests = 0;

    Object.values(dataQuality).forEach(category => {
      if (Array.isArray(category)) {
        category.forEach(test => {
          totalTests += 1;
          if (test.accurate || test.realTime || test.integrity) {
            passedTests += 1;
          }
        });
      }
    });

    return totalTests > 0 ? Math.round((passedTests / totalTests) * 100) : 0;
  },
};

module.exports = scoringMethods;
