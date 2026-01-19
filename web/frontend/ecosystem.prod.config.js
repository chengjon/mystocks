/**
 * MyStocks Frontend - PM2 Production Configuration
 * 生产环境专用配置（优化版）
 *
 * 使用方法:
 * 1. 构建生产版本: npm run build
 * 2. 启动PM2: pm2 start ecosystem.prod.config.js
 * 3. 查看状态: pm2 status
 */

module.exports = {
  apps: [
    {
      name: 'mystocks-frontend-prod',

      // 使用 npm run preview (vite preview) - 符合Vite最佳实践
      script: 'npm',
      args: 'run preview -- --port 3001 --host',

      cwd: '/opt/claude/mystocks_spec/web/frontend',

      // 环境变量
      env: {
        NODE_ENV: 'production',
        PORT: 3001,
        VITE_API_BASE_URL: process.env.VITE_API_BASE_URL || 'http://localhost:8000'
      },

      // 实例配置
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',

      // 日志配置
      error_file: './logs/pm2-error.log',
      out_file: './logs/pm2-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,

      // 进程管理
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000,
      kill_timeout: 5000,
      listen_timeout: 10000,
      shutdown_with_message: true,

      // Node.js参数
      node_args: '--max-old-space-size=2048',

      // 时区配置
      time: true,

      // 自动重启配置
      watch: false,
      ignore_watch: [
        'node_modules',
        'logs',
        'dist',
        '.git'
      ]
    }
  ]
};
