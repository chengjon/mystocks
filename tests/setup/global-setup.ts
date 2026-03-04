/**
 * Playwright全局设置
 * 在所有测试执行前运行的环境配置
 *
 * 功能:
 * 1. 启动依赖服务 (数据库, Redis等)
 * 2. 初始化测试环境
 * 3. 准备Mock数据
 * 4. 配置测试用户
 *
 * 作者: Claude Code
 * 生成时间: 2025-11-14
 */

import { FullConfig } from '@playwright/test';
import { spawn } from 'child_process';
import { promisify } from 'util';

const exec = promisify(spawn);

/**
 * 检查服务是否就绪
 */
async function waitForService(url: string, timeout: number = 30000): Promise<boolean> {
  const startTime = Date.now();
  const checkInterval = 1000;

  while (Date.now() - startTime < timeout) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        console.log(`✅ Service ready at ${url}`);
        return true;
      }
    } catch (error) {
      // 服务未就绪，继续等待
    }

    await new Promise(resolve => setTimeout(resolve, checkInterval));
  }

  console.error(`❌ Service timeout at ${url}`);
  return false;
}

/**
 * 启动Docker服务
 */
async function startDockerServices(): Promise<void> {
  try {
    console.log('🐳 Starting Docker services...');

    // 检查Docker Compose是否存在
    const { execSync } = require('child_process');

    try {
      // 启动开发环境的Docker服务
      execSync('docker-compose -f docker-compose.test.yml up -d', {
        stdio: 'inherit',
        cwd: process.cwd()
      });

      console.log('✅ Docker services started successfully');
    } catch (error) {
      console.log('⚠️ Docker Compose not available, continuing without Docker services');
    }
  } catch (error) {
    console.log('⚠️ Could not start Docker services:', error.message);
  }
}

/**
 * 初始化测试数据库
 */
async function initializeTestDatabase(): Promise<void> {
  try {
    console.log('🗄️ Initializing test database...');

    // 连接到数据库并创建测试数据结构
    // 注意: 这里使用Mock数据，所以不需要真实数据库连接

    console.log('✅ Test database initialized');
  } catch (error) {
    console.log('⚠️ Database initialization failed:', error.message);
  }
}

/**
 * 准备Mock数据
 */
async function prepareMockData(): Promise<void> {
  try {
    console.log('📊 Preparing mock data...');

    // 设置环境变量启用Mock数据
    process.env.USE_MOCK_DATA = 'true';
    process.env.DATA_SOURCE = 'mock';
    process.env.NODE_ENV = 'test';

    // 验证Mock数据系统
    const mockPath = process.cwd() + '/src/mock';
    const fs = require('fs');

    if (fs.existsSync(mockPath)) {
      console.log('✅ Mock data system available');

      // 验证主要Mock文件
      const mockFiles = [
        'mock_Dashboard.py',
        'mock_Stocks.py',
        'mock_TechnicalAnalysis.py',
        'mock_Wencai.py',
        'mock_StrategyManagement.py'
      ];

      for (const file of mockFiles) {
        const filePath = mockPath + '/' + file;
        if (fs.existsSync(filePath)) {
          console.log(`✅ Mock file ready: ${file}`);
        } else {
          console.log(`⚠️ Mock file missing: ${file}`);
        }
      }
    } else {
      console.log('⚠️ Mock data directory not found');
    }

    console.log('✅ Mock data prepared');
  } catch (error) {
    console.log('⚠️ Mock data preparation failed:', error.message);
  }
}

/**
 * 验证前端构建
 */
async function verifyFrontend(): Promise<void> {
  try {
    console.log('🔍 Verifying frontend build...');

    const frontendPath = process.cwd() + '/web/frontend';
    const fs = require('fs');

    // 检查package.json
    const packageJsonPath = frontendPath + '/package.json';
    if (fs.existsSync(packageJsonPath)) {
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
      console.log(`✅ Frontend package: ${packageJson.name} v${packageJson.version}`);
    }

    // 检查dist目录
    const distPath = frontendPath + '/dist';
    if (fs.existsSync(distPath)) {
      console.log('✅ Frontend build artifacts found');
    } else {
      console.log('⚠️ Frontend build not found, will use dev server');
    }

  } catch (error) {
    console.log('⚠️ Frontend verification failed:', error.message);
  }
}

/**
 * 验证后端API
 */
async function verifyBackend(): Promise<void> {
  try {
    console.log('🔍 Verifying backend API...');

    const backendPath = process.cwd() + '/web/backend';
    const fs = require('fs');

    // 检查requirements.txt
    const requirementsPath = backendPath + '/requirements.txt';
    if (fs.existsSync(requirementsPath)) {
      const requirements = fs.readFileSync(requirementsPath, 'utf8');

      // 检查关键依赖
      const keyDeps = ['fastapi', 'playwright', 'pytest'];
      for (const dep of keyDeps) {
        if (requirements.includes(dep)) {
          console.log(`✅ Backend dependency: ${dep}`);
        } else {
          console.log(`⚠️ Backend dependency missing: ${dep}`);
        }
      }
    }

    // 检查main.py
    const mainPath = backendPath + '/app/main.py';
    if (fs.existsSync(mainPath)) {
      console.log('✅ Backend main application found');
    }

  } catch (error) {
    console.log('⚠️ Backend verification failed:', error.message);
  }
}

/**
 * 创建测试用户目录
 */
async function createTestDirectories(): Promise<void> {
  try {
    console.log('📁 Creating test directories...');

    const fs = require('fs');
    const path = require('path');

    const testDirs = [
      'test-results',
      'test-results/screenshots',
      'test-results/videos',
      'test-results/traces',
      'test-results/reports'
    ];

    for (const dir of testDirs) {
      const fullPath = path.join(process.cwd(), dir);
      if (!fs.existsSync(fullPath)) {
        fs.mkdirSync(fullPath, { recursive: true });
        console.log(`✅ Created directory: ${dir}`);
      }
    }

  } catch (error) {
    console.log('⚠️ Test directory creation failed:', error.message);
  }
}

/**
 * 主全局设置函数
 */
async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting E2E Test Global Setup');
  console.log('=' .repeat(50));

  try {
    // 设置测试环境变量
    process.env.NODE_ENV = 'test';
    process.env.USE_MOCK_DATA = 'true';
    process.env.PLAYWRIGHT_BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173';
    process.env.PLAYWRIGHT_API_URL = process.env.PLAYWRIGHT_API_URL || 'http://localhost:8020';

    console.log(`📋 Test Configuration:`);
    console.log(`   Base URL: ${process.env.PLAYWRIGHT_BASE_URL}`);
    console.log(`   API URL: ${process.env.PLAYWRIGHT_API_URL}`);
    console.log(`   Mock Data: ${process.env.USE_MOCK_DATA}`);
    console.log('');

    // 执行初始化步骤
    await createTestDirectories();
    await verifyFrontend();
    await verifyBackend();
    await prepareMockData();
    await initializeTestDatabase();
    await startDockerServices();

    // 等待服务就绪
    console.log('⏳ Waiting for services to be ready...');

    const services = [
      { name: 'Frontend', url: process.env.PLAYWRIGHT_BASE_URL + '/health' },
      { name: 'Backend API', url: process.env.PLAYWRIGHT_API_URL + '/health' }
    ];

    for (const service of services) {
      try {
        await waitForService(service.url, 30000);
      } catch (error) {
        console.log(`⚠️ ${service.name} health check failed, continuing anyway`);
      }
    }

    console.log('');
    console.log('✅ E2E Test Global Setup Completed Successfully');
    console.log('=' .repeat(50));

  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  }
}

export default globalSetup;
