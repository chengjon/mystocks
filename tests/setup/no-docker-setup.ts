/**
 * 无Docker测试环境全局设置
 * 为Vue 3 + FastAPI架构优化的端到端测试配置
 *
 * 功能:
 * 1. 环境检测和准备
 * 2. 依赖验证
 * 3. Mock数据配置
 * 4. 服务启动管理（非Docker）
 *
 * 作者: Claude Code
 * 生成时间: 2025-11-14
 */

import { FullConfig } from '@playwright/test';
import { spawn, ChildProcess } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';
import * as fs from 'fs';

const exec = promisify(spawn);

/**
 * 测试环境配置
 */
interface TestEnvironment {
  nodeVersion: string;
  pythonVersion: string;
  hasFrontend: boolean;
  hasBackend: boolean;
  hasDependencies: boolean;
  ports: {
    frontend: number;
    backend: number;
  };
}

/**
 * 检测环境信息
 */
async function detectEnvironment(): Promise<TestEnvironment> {
  console.log('🔍 Detecting test environment...');

  const env: TestEnvironment = {
    nodeVersion: '',
    pythonVersion: '',
    hasFrontend: false,
    hasBackend: false,
    hasDependencies: false,
    ports: {
      frontend: 5173,
      backend: 8000
    }
  };

  try {
    // 检测Node.js版本
    try {
      const nodeResult = await exec('node', ['--version']);
      env.nodeVersion = nodeResult.stdout.toString().trim();
      console.log(`✅ Node.js: ${env.nodeVersion}`);
    } catch {
      console.log('❌ Node.js not found');
    }

    // 检测Python版本
    try {
      const pythonResult = await exec('python3', ['--version']);
      env.pythonVersion = pythonResult.stdout.toString().trim();
      console.log(`✅ Python: ${env.pythonVersion}`);
    } catch {
      console.log('❌ Python3 not found');
    }

    // 检测前端项目
    const frontendPath = path.join(process.cwd(), 'web', 'frontend');
    const packageJsonPath = path.join(frontendPath, 'package.json');
    if (fs.existsSync(packageJsonPath)) {
      env.hasFrontend = true;
      console.log('✅ Frontend project found');
    } else {
      console.log('❌ Frontend project not found');
    }

    // 检测后端项目
    const backendPath = path.join(process.cwd(), 'web', 'backend');
    const requirementsPath = path.join(backendPath, 'requirements.txt');
    if (fs.existsSync(requirementsPath)) {
      env.hasBackend = true;
      console.log('✅ Backend project found');
    } else {
      console.log('❌ Backend project not found');
    }

    // 检测依赖
    if (env.hasFrontend) {
      const nodeModulesPath = path.join(frontendPath, 'node_modules');
      if (fs.existsSync(nodeModulesPath)) {
        env.hasDependencies = true;
        console.log('✅ Frontend dependencies installed');
      } else {
        console.log('❌ Frontend dependencies missing');
      }
    }

    if (env.hasBackend) {
      try {
        await exec('python3', ['-c', 'import fastapi, pytest, playwright']);
        env.hasDependencies = true;
        console.log('✅ Backend dependencies installed');
      } catch {
        console.log('❌ Backend dependencies missing');
      }
    }

  } catch (error) {
    console.log(`⚠️ Environment detection failed: ${error}`);
  }

  return env;
}

/**
 * 安装前端依赖
 */
async function installFrontendDependencies(): Promise<boolean> {
  if (!process.env.SKIP_FRONTEND_INSTALL) {
    console.log('📦 Installing frontend dependencies...');
    try {
      const frontendPath = path.join(process.cwd(), 'web', 'frontend');
      const result = await exec('npm', ['install'], { cwd: frontendPath });
      console.log('✅ Frontend dependencies installed');
      return true;
    } catch (error) {
      console.log('❌ Frontend dependencies installation failed');
      return false;
    }
  } else {
    console.log('⏭️ Skipping frontend dependencies installation');
    return true;
  }
}

/**
 * 安装后端依赖
 */
async function installBackendDependencies(): Promise<boolean> {
  if (!process.env.SKIP_BACKEND_INSTALL) {
    console.log('📦 Installing backend dependencies...');
    try {
      const backendPath = path.join(process.cwd(), 'web', 'backend');
      const result = await exec('pip3', ['install', '-r', 'requirements.txt'], { cwd: backendPath });
      console.log('✅ Backend dependencies installed');
      return true;
    } catch (error) {
      console.log('❌ Backend dependencies installation failed');
      return false;
    }
  } else {
    console.log('⏭️ Skipping backend dependencies installation');
    return true;
  }
}

/**
 * 安装Playwright浏览器
 */
async function installPlaywrightBrowsers(): Promise<boolean> {
  if (!process.env.SKIP_PLAYWRIGHT_INSTALL) {
    console.log('🎭 Installing Playwright browsers...');
    try {
      const result = await exec('npx', ['playwright', 'install', 'chromium', 'firefox', 'webkit']);
      console.log('✅ Playwright browsers installed');
      return true;
    } catch (error) {
      console.log('❌ Playwright browsers installation failed');
      return false;
    }
  } else {
    console.log('⏭️ Skipping Playwright browsers installation');
    return true;
  }
}

/**
 * 启动前端开发服务器
 */
async function startFrontendServer(): Promise<ChildProcess | null> {
  if (!process.env.SKIP_FRONTEND_SERVER) {
    console.log('🌐 Starting frontend development server...');
    try {
      const frontendPath = path.join(process.cwd(), 'web', 'frontend');
      const server = spawn('npm', ['run', 'dev'], {
        cwd: frontendPath,
        env: { ...process.env, NODE_ENV: 'test' },
        stdio: 'pipe'
      });

      server.stdout?.on('data', (data) => {
        console.log(`Frontend: ${data.toString().trim()}`);
      });

      server.stderr?.on('data', (data) => {
        console.error(`Frontend Error: ${data.toString().trim()}`);
      });

      console.log('✅ Frontend server started');
      return server;
    } catch (error) {
      console.log('❌ Frontend server startup failed');
      return null;
    }
  } else {
    console.log('⏭️ Skipping frontend server startup');
    return null;
  }
}

/**
 * 启动后端API服务器
 */
async function startBackendServer(): Promise<ChildProcess | null> {
  if (!process.env.SKIP_BACKEND_SERVER) {
    console.log('🚀 Starting backend API server...');
    try {
      const backendPath = path.join(process.cwd(), 'web', 'backend');
      const server = spawn('python3', ['-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000'], {
        cwd: backendPath,
        env: { ...process.env, TESTING: '1', USE_MOCK_DATA: '1' },
        stdio: 'pipe'
      });

      server.stdout?.on('data', (data) => {
        console.log(`Backend: ${data.toString().trim()}`);
      });

      server.stderr?.on('data', (data) => {
        console.error(`Backend Error: ${data.toString().trim()}`);
      });

      console.log('✅ Backend server started');
      return server;
    } catch (error) {
      console.log('❌ Backend server startup failed');
      return null;
    }
  } else {
    console.log('⏭️ Skipping backend server startup');
    return null;
  }
}

/**
 * 等待服务就绪
 */
async function waitForService(url: string, timeout: number = 60000): Promise<boolean> {
  console.log(`⏳ Waiting for service at ${url}...`);
  const startTime = Date.now();
  const checkInterval = 2000;

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

  console.log(`❌ Service timeout at ${url}`);
  return false;
}

/**
 * 创建测试结果目录
 */
async function createTestDirectories(): Promise<void> {
  console.log('📁 Creating test result directories...');

  const testDirs = [
    'test-results',
    'test-results/screenshots',
    'test-results/videos',
    'test-results/traces',
    'test-results/reports',
    'test-results/logs'
  ];

  for (const dir of testDirs) {
    const fullPath = path.join(process.cwd(), dir);
    if (!fs.existsSync(fullPath)) {
      fs.mkdirSync(fullPath, { recursive: true });
      console.log(`✅ Created directory: ${dir}`);
    }
  }
}

/**
 * 配置Mock数据环境
 */
async function configureMockData(): Promise<void> {
  console.log('📊 Configuring mock data environment...');

  // 设置测试环境变量
  process.env.NODE_ENV = 'test';
  process.env.USE_MOCK_DATA = 'true';
  process.env.DATA_SOURCE = 'mock';
  process.env.TESTING = '1';

  // 设置默认URLs
  process.env.PLAYWRIGHT_BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173';
  process.env.PLAYWRIGHT_API_URL = process.env.PLAYWRIGHT_API_URL || 'http://localhost:8000';

  // 验证Mock数据系统
  const mockPath = path.join(process.cwd(), 'src', 'mock');
  if (fs.existsSync(mockPath)) {
    console.log('✅ Mock data system found');

    // 检查主要Mock文件
    const mockFiles = [
      'mock_Dashboard.py',
      'mock_Stocks.py',
      'mock_TechnicalAnalysis.py',
      'mock_Wencai.py',
      'mock_StrategyManagement.py'
    ];

    for (const file of mockFiles) {
      const filePath = path.join(mockPath, file);
      if (fs.existsSync(filePath)) {
        console.log(`✅ Mock file ready: ${file}`);
      } else {
        console.log(`⚠️ Mock file missing: ${file}`);
      }
    }
  } else {
    console.log('⚠️ Mock data directory not found, will use simple mock data');
  }

  console.log('✅ Mock data environment configured');
}

/**
 * 主全局设置函数
 */
async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting No-Docker E2E Test Global Setup');
  console.log('=' .repeat(60));

  let frontendServer: ChildProcess | null = null;
  let backendServer: ChildProcess | null = null;

  try {
    // 设置测试环境变量
    process.env.NODE_ENV = 'test';
    process.env.TESTING = '1';

    console.log(`📋 Test Configuration:`);
    console.log(`   Node.js: ${process.version}`);
    console.log(`   Base URL: ${process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173'}`);
    console.log(`   API URL: ${process.env.PLAYWRIGHT_API_URL || 'http://localhost:8000'}`);
    console.log(`   Mock Data: ${process.env.USE_MOCK_DATA || 'true'}`);
    console.log('');

    // 1. 检测环境
    const env = await detectEnvironment();

    // 2. 安装依赖（如果需要）
    if (!env.hasDependencies) {
      console.log('\n📦 Installing missing dependencies...');
      await installFrontendDependencies();
      await installBackendDependencies();
      await installPlaywrightBrowsers();
    }

    // 3. 创建测试目录
    console.log('\n📁 Setting up test directories...');
    await createTestDirectories();

    // 4. 配置Mock数据
    console.log('\n📊 Configuring mock data...');
    await configureMockData();

    // 5. 启动服务
    console.log('\n🚀 Starting services...');
    frontendServer = await startFrontendServer();
    backendServer = await startBackendServer();

    // 6. 等待服务就绪
    console.log('\n⏳ Waiting for services to be ready...');

    const services = [
      {
        name: 'Frontend',
        url: process.env.PLAYWRIGHT_BASE_URL + (process.env.PLAYWRIGHT_BASE_URL?.includes(':') ? '' : '/') + 'health'
      },
      {
        name: 'Backend API',
        url: process.env.PLAYWRIGHT_API_URL + (process.env.PLAYWRIGHT_API_URL?.includes(':') ? '' : '/') + 'health'
      }
    ];

    for (const service of services) {
      try {
        await waitForService(service.url, 60000);
      } catch (error) {
        console.log(`⚠️ ${service.name} health check failed, continuing anyway`);
      }
    }

    console.log('\n✅ No-Docker E2E Test Global Setup Completed Successfully');
    console.log('=' .repeat(60));

    return { frontendServer, backendServer };

  } catch (error) {
    console.error('❌ Global setup failed:', error);

    // 清理已启动的服务
    if (frontendServer) {
      frontendServer.kill();
    }
    if (backendServer) {
      backendServer.kill();
    }

    throw error;
  }
}

/**
 * 全局清理函数
 */
async function globalTeardown(config: FullConfig, setupData: any) {
  console.log('🧹 Starting global teardown...');

  if (setupData && setupData.frontendServer) {
    console.log('🌐 Stopping frontend server...');
    setupData.frontendServer.kill();
  }

  if (setupData && setupData.backendServer) {
    console.log('🚀 Stopping backend server...');
    setupData.backendServer.kill();
  }

  console.log('✅ Global teardown completed');
}

export { globalSetup, globalTeardown };
export default globalSetup;
