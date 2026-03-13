/**
 * MyStocks PM2 测试环境配置
 * 当前口径：
 * - 前端默认端口：3020
 * - 后端默认端口：8020
 * - 路径根据当前仓库根动态解析
 */

const path = require("node:path");
const fs = require("node:fs");

const ensureLogDir = (logPath) => {
  const dir = path.dirname(logPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
};

const projectRoot = path.resolve(__dirname, "..", "..");
const frontendPort = process.env.FRONTEND_PORT || "3020";
const backendPort = process.env.BACKEND_PORT || "8020";

module.exports = {
  apps: [
    {
      name: "mystocks-frontend",
      script: "npm",
      args: `run dev -- --host 0.0.0.0 --port ${frontendPort}`,
      cwd: path.join(projectRoot, "web/frontend"),
      env: {
        NODE_ENV: "test",
        FRONTEND_PORT: frontendPort,
        VITE_API_BASE_URL: `http://localhost:${backendPort}`,
        VITE_WS_URL: `ws://localhost:${backendPort}`,
        VITE_APP_TITLE: "MyStocks Test Environment",
      },
      env_test: {
        NODE_ENV: "test",
        DEBUG: "mystocks:*",
      },
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
      out_file: path.join(projectRoot, "logs/frontend-access.log"),
      error_file: path.join(projectRoot, "logs/frontend-error.log"),
      log_file: path.join(projectRoot, "logs/frontend-combined.log"),
      log_type: "json",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      port: Number(frontendPort),
      wait_ready: true,
      listen_timeout: 10000,
      kill_timeout: 5000,
      pmx: true,
      health_check: {
        script: `curl -f http://localhost:${frontendPort}/ > /dev/null 2>&1`,
        interval: 30000,
      },
    },
    {
      name: "mystocks-backend",
      script: "python",
      args: "start_server.py",
      cwd: path.join(projectRoot, "web/backend"),
      env: {
        PYTHON_ENV: "test",
        PYTHONPATH: projectRoot,
        PYTHONUNBUFFERED: "1",
        POSTGRESQL_HOST: process.env.POSTGRESQL_HOST || "localhost",
        POSTGRESQL_USER: process.env.POSTGRESQL_USER || "postgres",
        POSTGRESQL_PASSWORD: process.env.POSTGRESQL_PASSWORD || "",
        POSTGRESQL_DATABASE: process.env.POSTGRESQL_DATABASE || "mystocks",
        POSTGRESQL_PORT: process.env.POSTGRESQL_PORT || "5438",
        TDENGINE_HOST: process.env.TDENGINE_HOST || "localhost",
        TDENGINE_USER: process.env.TDENGINE_USER || "root",
        TDENGINE_PASSWORD: process.env.TDENGINE_PASSWORD || "",
        TDENGINE_DATABASE: process.env.TDENGINE_DATABASE || "market_data_cache",
        TDENGINE_PORT: process.env.TDENGINE_PORT || "6030",
        API_HOST: "0.0.0.0",
        API_PORT: backendPort,
        BACKEND_PORT: backendPort,
        TESTING: "true",
        DEBUG: "true",
        LOG_LEVEL: "DEBUG",
      },
      env_test: {
        PYTHON_ENV: "test",
        TESTING: "true",
        DEBUG: "true",
      },
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
      out_file: path.join(projectRoot, "logs/backend-access.log"),
      error_file: path.join(projectRoot, "logs/backend-error.log"),
      log_file: path.join(projectRoot, "logs/backend-combined.log"),
      log_type: "json",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "2G",
      port: Number(backendPort),
      wait_ready: true,
      listen_timeout: 15000,
      kill_timeout: 8000,
      restart_delay: 4000,
      pmx: true,
      health_check: {
        script: `curl -f http://localhost:${backendPort}/health > /dev/null 2>&1`,
        interval: 30000,
      },
      min_uptime: "10s",
    },
  ],
  deploy: {
    test: {
      user: "node",
      host: "localhost",
      ref: "origin/main",
      repo: "git@github.com:your-org/mystocks.git",
      path: projectRoot,
      "pre-deploy-local": "",
      "post-deploy": "pm2 reload config/pm2/pm2.config.js --env test",
    },
  },
};

ensureLogDir(path.join(projectRoot, "logs/frontend-access.log"));
ensureLogDir(path.join(projectRoot, "logs/frontend-error.log"));
ensureLogDir(path.join(projectRoot, "logs/backend-access.log"));
ensureLogDir(path.join(projectRoot, "logs/backend-error.log"));
