/**
 * MyStocks Frontend - PM2 Ecosystem Configuration
 * Phase 3: Bloomberg Terminal Style Verification Environment
 * Production-ready PM2 configuration for MyStocks Vue 3 frontend
 * with comprehensive logging and monitoring
 */

const fs = require('node:fs');
const path = require('node:path');

if (typeof process.loadEnvFile === 'function') {
  for (const envFile of [path.join(__dirname, '.env'), path.join(__dirname, '..', '..', '.env')]) {
    if (fs.existsSync(envFile)) {
      process.loadEnvFile(envFile);
    }
  }
}

module.exports = {
  apps: [
    {
      // 前端服务：Vite Preview (生产模式) - 解决Node 24不稳定性
      name: 'mystocks-frontend',
      script: 'npm',
      args: `run preview -- --port ${process.env.FRONTEND_PORT || 3020} --host 0.0.0.0 --strictPort`,
      cwd: '/opt/claude/mystocks_spec/web/frontend',
      
      // Environment configuration
      env: {
        NODE_ENV: 'production',
        PORT: process.env.FRONTEND_PORT || 3020,
        FRONTEND_PORT: process.env.FRONTEND_PORT || 3020,
        BACKEND_PORT: process.env.BACKEND_PORT || 8020,
        HOST: '0.0.0.0',
        VITE_API_BASE_URL: '/api'
      },
      
      // Instance configuration
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '5s',
      
      // Logging
      log_file: './logs/frontend-access.log',
      error_file: './logs/frontend-error.log',
      out_file: './logs/frontend-out.log',
      merge_logs: true,
      
      // Stability
      exp_backoff_restart_delay: 1000,
    },
    
    {
      // 前端服务：静态资源服务（生产环境）
      name: 'mystocks-frontend-static',
      script: 'npm',
      args: `run preview -- --port ${process.env.FRONTEND_BACKUP_PORT || 3021} --host 0.0.0.0 --strictPort`,
      cwd: '/opt/claude/mystocks_spec/web/frontend',
      disabled: true,  // 开发环境先不启用
      instances: 1,
      exec_mode: 'fork',
      
      env: {
        NODE_ENV: 'production',
        PORT: process.env.FRONTEND_BACKUP_PORT || 3021,
        FRONTEND_PORT: process.env.FRONTEND_BACKUP_PORT || 3021,
        BACKEND_PORT: process.env.BACKEND_PORT || 8020,
        HOST: '0.0.0.0',
      },
      
      // 静态资源服务配置
      log_file: './logs/frontend-frontend-static-error.log',
      error_file: './logs/frontend-frontend-static-error.log',
      out_file: './logs/frontend-frontend-static-out.log',
      
      // Instance configuration
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_restarts: 5,
      min_uptime: '30s',
    },
  ],
  
  /**
   * Deployment configuration (optional, for future CI/CD integration)
   */
  deploy: {
    production: {
      user: 'root',
      host: 'localhost',
      ref: 'origin/main',
      repo: 'git@github.com:your-org/mystocks.git',
      path: '/opt/laude/mystocks_spec/web/frontend',
      'post-deploy': 'npm install && npm run build && pm2 reload ecosystem.config.js --env production',
    }
  },
}
