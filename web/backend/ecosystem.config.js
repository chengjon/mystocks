module.exports = {
  apps: [
    {
      name: 'mystocks-backend',
      script: 'uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 8000 --reload',
      cwd: '/opt/claude/mystocks_spec/web/backend',
      interpreter: 'python3',
      env: {
        PYTHONPATH: '/opt/claude/mystocks_spec/web/backend',
        NODE_ENV: 'development'
      },
      error_file: '/root/.pm2/logs/mystocks-backend-error.log',
      out_file: '/root/.pm2/logs/mystocks-backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      watch: false
    }
  ]
}
