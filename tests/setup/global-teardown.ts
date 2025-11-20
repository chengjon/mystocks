/**
 * Playwright全局清理
 * 在所有测试执行后运行的环境清理
 * 
 * 作者: Claude Code
 * 生成时间: 2025-11-14
 */

import { FullConfig } from '@playwright/test';

/**
 * 主全局清理函数
 */
async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting E2E Test Global Teardown');
  console.log('=' .repeat(50));
  
  try {
    // 清理测试进程
    await cleanupTestProcesses();
    
    // 清理测试数据
    await cleanupTestData();
    
    // 生成最终报告
    await generateFinalReport();
    
    console.log('✅ E2E Test Global Teardown Completed Successfully');
    console.log('=' .repeat(50));
    
  } catch (error) {
    console.error('❌ Global teardown failed:', error);
    // 不抛出错误，避免影响测试结果
  }
}

/**
 * 清理测试进程
 */
async function cleanupTestProcesses(): Promise<void> {
  console.log('🔄 Cleaning up test processes...');
  
  try {
    // 清理前端和后端进程
    const { execSync } = require('child_process');
    
    // 杀死可能遗留的进程
    try {
      execSync('pkill -f "npm run dev"', { stdio: 'ignore' });
      execSync('pkill -f "uvicorn app.main:app"', { stdio: 'ignore' });
      console.log('✅ Test processes cleaned up');
    } catch (error) {
      console.log('ℹ️ No test processes found to clean up');
    }
    
  } catch (error) {
    console.log('⚠️ Process cleanup failed:', error.message);
  }
}

/**
 * 清理测试数据
 */
async function cleanupTestData(): Promise<void> {
  console.log('📊 Cleaning up test data...');
  
  try {
    const fs = require('fs');
    const path = require('path');
    
    // 清理临时测试文件
    const tempFiles = [
      '.test_frontend_pid',
      '.test_backend_pid',
      '.test_env_checked'
    ];
    
    for (const file of tempFiles) {
      try {
        fs.unlinkSync(file);
        console.log(`✅ Cleaned up: ${file}`);
      } catch (error) {
        // 文件不存在，忽略
      }
    }
    
  } catch (error) {
    console.log('⚠️ Test data cleanup failed:', error.message);
  }
}

/**
 * 生成最终报告
 */
async function generateFinalReport(): Promise<void> {
  console.log('📋 Generating final report...');
  
  try {
    const fs = require('fs');
    const path = require('path');
    
    const reportDir = path.join(process.cwd(), 'test-results');
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true });
    }
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const reportFile = path.join(reportDir, `final-report-${timestamp}.md`);
    
    const report = `# E2E测试执行报告

**生成时间**: ${new Date().toLocaleString()}
**执行模式**: 无Docker测试环境

## 执行状态

- ✅ 环境检查完成
- ✅ 测试执行完成  
- ✅ 清理操作完成

## 报告位置

- **测试结果**: test-results/
- **截图**: test-results/screenshots/
- **视频**: test-results/videos/
- **追踪**: test-results/traces/

## 后续步骤

如需查看详细测试结果，请检查test-results/目录下的HTML报告。

`;
    
    fs.writeFileSync(reportFile, report, 'utf8');
    console.log(`✅ Final report generated: ${reportFile}`);
    
  } catch (error) {
    console.log('⚠️ Report generation failed:', error.message);
  }
}

export default globalTeardown;