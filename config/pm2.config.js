/**
 * MyStocks PM2 服务管理配置文件
 * 用途: 管理前端和后端服务的启动、停止、重启、日志监控
 * 环境: 测试环境专用 (NODE_ENV=test, PYTHON_ENV=test)
 */

const path = require('path');
const fs = require('fs');

function loadEnvFile(envPath) {
  if (!fs.existsSync(envPath)) {
    return;
  }

  const lines = fs.readFileSync(envPath, 'utf8').split(/\r?\n/u);
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) {
      continue;
    }

    const separatorIndex = trimmed.indexOf('=');
    if (separatorIndex <= 0) {
      continue;
    }

    const key = trimmed.slice(0, separatorIndex).trim();
    if (!key || process.env[key] !== undefined) {
      continue;
    }

    let value = trimmed.slice(separatorIndex + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    process.env[key] = value;
  }
}

// 确保日志目录存在
const ensureLogDir = (logPath) => {
  const dir = path.dirname(logPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
};

// 项目根目录
const projectRoot = '/opt/claude/mystocks_spec';

for (const envPath of [path.join(projectRoot, '.env'), path.join(projectRoot, 'web', 'frontend', '.env')]) {
  if (typeof process.loadEnvFile === 'function') {
    try {
      process.loadEnvFile(envPath);
      continue;
    } catch {
      // fall through to manual parser
    }
  }
  loadEnvFile(envPath);
}

function requireEnv(name) {
  const value = process.env[name];
  if (!value) {
    throw new Error(`[port-config] Missing required env var: ${name}`);
  }
  return value;
}

const backendPort = requireEnv('BACKEND_PORT');
const backendBackupPort = requireEnv('BACKEND_BACKUP_PORT');
const frontendPort = requireEnv('FRONTEND_PORT');
const frontendBackupPort = requireEnv('FRONTEND_BACKUP_PORT');
const viteApiBaseUrl = process.env.VITE_API_BASE_URL || `http://localhost:${backendPort}`;
const viteWsUrl = process.env.VITE_WS_URL || `ws://localhost:${backendPort}`;

module.exports = {
  apps: [
    // 前端服务配置 (Vue3 + Vite)
    {
      name: 'mystocks-frontend',
      script: 'npm',
      args: 'run dev',
      cwd: path.join(projectRoot, 'web/frontend'),

      // 环境变量
      env: {
        NODE_ENV: 'test',
        FRONTEND_PORT: frontendPort,
        FRONTEND_BACKUP_PORT: frontendBackupPort,
        BACKEND_PORT: backendPort,
        BACKEND_BACKUP_PORT: backendBackupPort,
        VITE_API_BASE_URL: viteApiBaseUrl,
        VITE_WS_URL: viteWsUrl,
        VITE_APP_TITLE: 'MyStocks Test Environment'
      },
      env_test: {
        NODE_ENV: 'test',
        DEBUG: 'mystocks:*'
      },

      // 日志配置
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      out_file: path.join(projectRoot, 'var/log/frontend-access.log'),
      error_file: path.join(projectRoot, 'var/log/frontend-error.log'),
      log_file: path.join(projectRoot, 'var/log/frontend-combined.log'),

      // 日志轮转
      log_type: 'json',

      // 进程管理
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',

      // 端口配置
      port: frontendPort,

      // 启动延迟
      wait_ready: true,
      listen_timeout: 10000,
      kill_timeout: 5000,

      // 监控配置
      pmx: true,

      // 服务健康检查
      health_check: {
        script: `curl -f http://localhost:${frontendPort}/ > /dev/null 2>&1`,
        interval: 30000
      }
    },

    // 后端服务配置 (FastAPI + Uvicorn)
    {
      name: 'mystocks-backend',
      script: 'python',
      args: 'start_server.py',
      cwd: path.join(projectRoot, 'web/backend'),

      // 环境变量
      env: {
        PYTHON_ENV: 'test',
        PYTHONPATH: projectRoot,
        PYTHONUNBUFFERED: '1',

        // 数据库配置 (从 .env 读取,缺省回退到 localhost)
        POSTGRESQL_HOST: process.env.POSTGRESQL_HOST || 'localhost',
        POSTGRESQL_USER: process.env.POSTGRESQL_USER || 'postgres',
        POSTGRESQL_PASSWORD: process.env.POSTGRESQL_PASSWORD || '',
        POSTGRESQL_DATABASE: process.env.POSTGRESQL_DATABASE || 'mystocks',
        POSTGRESQL_PORT: process.env.POSTGRESQL_PORT || '5438',

        TDENGINE_HOST: process.env.TDENGINE_HOST || 'localhost',
        TDENGINE_USER: process.env.TDENGINE_USER || 'root',
        TDENGINE_PASSWORD: process.env.TDENGINE_PASSWORD || '',
        TDENGINE_DATABASE: process.env.TDENGINE_DATABASE || 'market_data_cache',
        TDENGINE_PORT: process.env.TDENGINE_PORT || '6030',

        // 服务配置
        API_HOST: '0.0.0.0',
        API_PORT: backendPort,
        BACKEND_PORT: backendPort,
        BACKEND_BACKUP_PORT: backendBackupPort,

        // 测试配置
        TESTING: 'true',
        DEBUG: 'true',
        LOG_LEVEL: 'DEBUG'
      },
      env_test: {
        PYTHON_ENV: 'test',
        TESTING: 'true',
        DEBUG: 'true'
      },

      // 日志配置
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      out_file: path.join(projectRoot, 'var/log/backend-access.log'),
      error_file: path.join(projectRoot, 'var/log/backend-error.log'),
      log_file: path.join(projectRoot, 'var/log/backend-combined.log'),

      // 日志轮转
      log_type: 'json',

      // 进程管理
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',

      // 端口配置
      port: backendPort,

      // 启动延迟
      wait_ready: true,
      listen_timeout: 15000,
      kill_timeout: 8000,
      restart_delay: 4000,

      // 监控配置
      pmx: true,

      // 服务健康检查
      health_check: {
        script: `curl -f http://localhost:${backendPort}/health > /dev/null 2>&1`,
        interval: 30000
      },

      // 启动时间
      min_uptime: '10s'
    },

    // 数据库监控服务 (暂时禁用 - 脚本文件不存在)
    // {
    //   name: 'mystocks-db-monitor',
    //   script: path.join(projectRoot, 'scripts/monitor/database_monitor.py'),
    //   ...
    // }
  ],

  // 部署配置
  deploy: {
    test: {
      user: 'node',
      host: 'localhost',
      ref: 'origin/main',
      repo: 'git@github.com:your-org/mystocks.git',
      path: projectRoot,
      'pre-deploy-local': '',
      'post-deploy': 'pm2 reload mystocks.config.js --env test'
    }
  }
};

// 确保日志目录存在
ensureLogDir(path.join(projectRoot, 'var/log/frontend-access.log'));
ensureLogDir(path.join(projectRoot, 'var/log/frontend-error.log'));
ensureLogDir(path.join(projectRoot, 'var/log/backend-access.log'));
ensureLogDir(path.join(projectRoot, 'var/log/backend-error.log'));
ensureLogDir(path.join(projectRoot, 'var/log/db-monitor-access.log'));
ensureLogDir(path.join(projectRoot, 'var/log/db-monitor-error.log'));
