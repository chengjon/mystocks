// PM2 Playwright Testing Configuration
// 用于运行前端E2E测试的PM2配置

module.exports = {
  apps: [
    {
      // Playwright测试服务 - Portfolio页面测试
      name: 'playwright-portfolio-test',
      script: '/root/miniconda3/envs/stock/bin/python',
      args: '/tmp/test_portfolio_playwright.py',
      interpreter: 'none',
      cwd: '/opt/claude/mystocks_spec',
      instances: 1,
      exec_mode: 'fork',

      // 输出配置
      error_file: '/var/log/pm2/playwright-portfolio-error.log',
      out_file: '/var/log/pm2/playwright-portfolio-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,

      // 环境变量
      env: {
        PYTHONUNBUFFERED: '1',
        PLAYWRIGHT_BROWSERS_PATH: '/root/.cache/ms-playwright',
      },

      // 自动重启配置（测试通常不需要自动重启）
      autorestart: false,
      watch: false,
      max_restarts: 1,
      restart_delay: 5000,

      // 时间限制（测试最多运行5分钟）
      max_memory_restart: '500M',
      kill_timeout: 300000,

      // 健康检查（不适用于测试）
      health_check: {
        enable: false
      }
    },

    {
      // Playwright测试服务 - API调试模式
      name: 'playwright-api-debug',
      script: '/root/miniconda3/envs/stock/bin/python',
      args: '/tmp/debug_portfolio.py',
      interpreter: 'none',
      cwd: '/opt/claude/mystocks_spec',
      instances: 1,
      exec_mode: 'fork',

      error_file: '/var/log/pm2/playwright-api-debug-error.log',
      out_file: '/var/log/pm2/playwright-api-debug-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,

      env: {
        PYTHONUNBUFFERED: '1',
        PLAYWRIGHT_BROWSERS_PATH: '/root/.cache/ms-playwright',
      },

      autorestart: false,
      watch: false,
      max_restarts: 1,
    },

    {
      // 简化的快速测试（无截图，快速验证）
      name: 'playwright-quick-test',
      script: '/root/miniconda3/envs/stock/bin/python',
      args: '/tmp/check_console_errors.py',
      interpreter: 'none',
      cwd: '/opt/claude/mystocks_spec',
      instances: 1,
      exec_mode: 'fork',

      error_file: '/var/log/pm2/playwright-quick-error.log',
      out_file: '/var/log/pm2/playwright-quick-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,

      env: {
        PYTHONUNBUFFERED: '1',
      },

      autorestart: false,
      watch: false,
      max_restarts: 1,
    },

    {
      // Playwright测试服务 - Dashboard页面测试
      name: 'playwright-dashboard-test',
      script: '/root/miniconda3/envs/stock/bin/python',
      args: '/tmp/test_dashboard_playwright.py',
      interpreter: 'none',
      cwd: '/opt/claude/mystocks_spec',
      instances: 1,
      exec_mode: 'fork',

      error_file: '/var/log/pm2/playwright-dashboard-error.log',
      out_file: '/var/log/pm2/playwright-dashboard-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,

      env: {
        PYTHONUNBUFFERED: '1',
        PLAYWRIGHT_BROWSERS_PATH: '/root/.cache/ms-playwright',
      },

      autorestart: false,
      watch: false,
      max_restarts: 1,
      max_memory_restart: '500M',
      kill_timeout: 300000,
      health_check: { enable: false }
    }
  ]
}
