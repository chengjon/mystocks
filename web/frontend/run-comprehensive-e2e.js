#!/usr/bin/env node

/**
 * MyStocks E2E Test Runner
 * 运行完整的端到端自动化测试套件
 *
 * 使用方法:
 * npm run test:e2e:comprehensive
 * 或直接运行: node run-comprehensive-e2e.js
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const {
  loadPortEnv,
  resolveFrontendConfig,
  resolveBackendConfig
} = require('./tests/e2e/helpers/port-env.js');

loadPortEnv(__dirname);

const frontendConfig = resolveFrontendConfig();
const backendConfig = resolveBackendConfig();

const FRONTEND_CONFIG = {
  name: 'mystocks-frontend',
  port: frontendConfig.port,
  backupPort: frontendConfig.backupPort
};

const BACKEND_CONFIG = {
  name: 'mystocks-backend',
  port: backendConfig.port,
  backupPort: backendConfig.backupPort
};

function checkPM2Service(serviceName) {
  try {
    // 检查PM2是否可用
    execSync('pm2 --version', { stdio: 'pipe' });

    // 使用jlist命令获取JSON格式输出 (PM2 6.x兼容)
    const output = execSync('pm2 jlist', { encoding: 'utf-8' });
    const pm2List = JSON.parse(output);
    const service = pm2List.find(p => p.name === serviceName);
    return service && service.pm2_env.status === 'online';
  } catch {
    return false;
  }
}

function checkPort(port, retries = 5) {
  for (let i = 0; i < retries; i++) {
    try {
      execSync(`lsof -Pi :${port} -sTCP:LISTEN -t`, { stdio: 'pipe' });
      return true;
    } catch {
      try {
        const httpCode = execSync(
          `curl -sS -o /dev/null -m 2 -w "%{http_code}" http://127.0.0.1:${port}`,
          { stdio: 'pipe', encoding: 'utf-8' }
        ).trim();
        if (httpCode !== '000') {
          return true;
        }
      } catch {
        // keep retrying
      }
      if (i < retries - 1) {
        // Wait 1s before next retry
        execSync('sleep 1');
      }
    }
  }
  return false;
}

function runTests() {
  console.log('🚀 Starting MyStocks Comprehensive E2E Tests');
  console.log('='.repeat(60));

  // 前置检查
  console.log('📋 Phase 1: Pre-flight Checks');

  const frontendOnline = checkPM2Service(FRONTEND_CONFIG.name);
  const backendOnline = checkPM2Service(BACKEND_CONFIG.name);
  const frontendPortOpen = checkPort(FRONTEND_CONFIG.port) || checkPort(FRONTEND_CONFIG.backupPort);
  const backendPortOpen = checkPort(BACKEND_CONFIG.port) || checkPort(BACKEND_CONFIG.backupPort);

  console.log(`   Frontend PM2 (${FRONTEND_CONFIG.name}): ${frontendOnline ? '✅' : '❌'}`);
  console.log(`   Backend PM2 (${BACKEND_CONFIG.name}): ${backendOnline ? '✅' : '❌'}`);
  console.log(`   Frontend Port (${FRONTEND_CONFIG.port}/${FRONTEND_CONFIG.backupPort}): ${frontendPortOpen ? '✅' : '❌'}`);
  console.log(`   Backend Port (${BACKEND_CONFIG.port}/${BACKEND_CONFIG.backupPort}): ${backendPortOpen ? '✅' : '❌'}`);

  if (!frontendOnline || !backendOnline || !frontendPortOpen || !backendPortOpen) {
    console.error('❌ Pre-flight checks failed. Services not ready for testing.');
    console.error('   Please ensure both frontend and backend services are running via PM2');
    process.exit(1);
  }

  console.log('✅ Pre-flight checks passed');

  // 运行测试
  console.log('\n🧪 Phase 2: Running E2E Tests');

  try {
    const testCommand =
      'npx playwright test tests/comprehensive-e2e-validation.spec.ts --config playwright.config.ts --reporter=line,json --workers=1';
    console.log(`   Executing: ${testCommand}`);

    execSync(testCommand, {
      stdio: 'inherit',
      cwd: __dirname
    });

    console.log('\n✅ E2E Tests completed successfully');

  } catch (error) {
    console.error('\n❌ E2E Tests failed');
    console.error('   Check the detailed report in test-results/ directory');
    process.exit(1);
  }
}

function showReport() {
  const reportPath = path.join(__dirname, '..', 'test-results', 'test-summary.txt');

  if (fs.existsSync(reportPath)) {
    console.log('\n📊 Test Results Summary:');
    console.log('='.repeat(60));
    console.log(fs.readFileSync(reportPath, 'utf-8'));
    console.log('='.repeat(60));

    console.log('\n📁 Output Files:');
    const testResultsDir = path.join(__dirname, '..', 'test-results');
    if (fs.existsSync(testResultsDir)) {
      const files = fs.readdirSync(testResultsDir);
      files.forEach(file => {
        if (file.endsWith('.json') || file.endsWith('.txt')) {
          console.log(`   - ${path.join(testResultsDir, file)}`);
        }
      });
    }

    const screenshotsDir = path.join(testResultsDir, 'screenshots');
    if (fs.existsSync(screenshotsDir)) {
      const screenshots = fs.readdirSync(screenshotsDir);
      console.log(`   📸 Screenshots: ${screenshots.length} files in ${screenshotsDir}`);
    }

    const videosDir = path.join(testResultsDir, 'videos');
    if (fs.existsSync(videosDir)) {
      const videos = fs.readdirSync(videosDir);
      console.log(`   🎥 Videos: ${videos.length} files in ${videosDir}`);
    }
  }
}

// 主执行逻辑
if (require.main === module) {
  try {
    runTests();
    showReport();
    console.log('\n🎉 MyStocks E2E testing completed successfully!');
  } catch (error) {
    console.error('\n💥 E2E testing failed:', error.message);
    process.exit(1);
  }
}

module.exports = { runTests, showReport };
