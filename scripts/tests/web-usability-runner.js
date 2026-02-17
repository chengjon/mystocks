#!/usr/bin/env node

/**
 * Thin entrypoint for Web usability test runner.
 * Core implementation has been moved to ./web-usability/runner-core.js.
 */

const WebUsabilityTestRunner = require('./web-usability/runner-core');

if (require.main === module) {
  const runner = new WebUsabilityTestRunner();
  runner
    .runAllTests()
    .then(results => {
      console.log('\n🎉 测试执行完成！');
      console.log(`📊 总体评分: ${results.summary.overallScore}%`);
      console.log(
        `${results.summary.meetsStandard ? '✅' : '❌'} ${
          results.summary.meetsStandard ? '达到"完全可用"标准' : '未达到"完全可用"标准'
        }`
      );
      process.exit(results.summary.meetsStandard ? 0 : 1);
    })
    .catch(error => {
      console.error('❌ 测试执行失败:', error);
      process.exit(1);
    });
}

module.exports = WebUsabilityTestRunner;
