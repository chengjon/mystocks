module.exports = {
  apps: [
    {
      name: 'mystocks-frontend-dev',
      script: 'npm',
      args: 'run dev -- --host 0.0.0.0 --strictPort',
      cwd: '/opt/claude/mystocks_spec/web/frontend',

      env: {
        NODE_ENV: 'development',
        PORT: process.env.FRONTEND_PORT || 3020,
        FRONTEND_PORT: process.env.FRONTEND_PORT || 3020,
        BACKEND_PORT: process.env.BACKEND_PORT || 8020,
        HOST: '0.0.0.0',
        VITE_API_BASE_URL: `http://localhost:${process.env.BACKEND_PORT || 8020}`
      },

      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      ignore_watch: ['node_modules', 'dist', '.git'],
      max_memory_restart: '1G',

      error_file: '/opt/claude/mystocks_spec/web/frontend/logs/pm2-dev-error.log',
      out_file: '/opt/claude/mystocks_spec/web/frontend/logs/pm2-dev-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,

      min_uptime: '5s',
      max_restarts: 10,
      restart_delay: 2000,
      kill_timeout: 5000,
      listen_timeout: 10000,

      node_args: '--max-old-space-size=1024'
    },
    {
      name: 'mystocks-backend',
      script: 'python',
      args: 'pm2_start.py',
      cwd: '/opt/claude/mystocks_spec/web/backend',

      env: {
        TESTING: 'false',
        USE_MOCK_DATA: 'false',
        BACKEND_PORT: process.env.BACKEND_PORT || 8020,
        BACKEND_BACKUP_PORT: process.env.BACKEND_BACKUP_PORT || 8021
      },

      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_memory_restart: '1G',

      error_file: '/opt/claude/mystocks_spec/web/backend/logs/pm2-error.log',
      out_file: '/opt/claude/mystocks_spec/web/backend/logs/pm2-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,

      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 3000,
      kill_timeout: 10000,
      listen_timeout: 15000
    }
  ]
}