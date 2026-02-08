// MyStocks 生产环境 PM2 配置
// 优化版：支持自动端口分配、健康检查、错误回滚
module.exports = {
  apps: [
    {
      // 核心服务: 后端 API 服务
      name: 'mystocks-backend',
      script: '/root/miniconda3/envs/stock/bin/python',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4',
      cwd: '/opt/claude/mystocks_spec/web/backend',
      interpreter: 'none',

      // 生产环境集群配置
      instances: 1,
      exec_mode: 'fork',

      // 生产环境变量
      env: {
        NODE_ENV: 'production',
        USE_MOCK: 'false',
        ENVIRONMENT: 'production',
        PYTHONPATH: '/opt/claude/mystocks_spec',
        LOG_LEVEL: 'info'
      },

      // 自动重启策略
      autorestart: true,
      watch: false,
      max_restarts: 10,
      restart_delay: 5000,
      min_uptime: '10s',

      // 资源限制
      max_memory_restart: '1G',
      node_args: '--max-old-space-size=1024',

      // 健康检查
      health_check: {
        enable: true,
        url: 'http://localhost:8000/api/monitoring/health',
        interval: 30000,
        max_retries: 3,
        timeout: 5000
      },

      // 日志配置
      log_file: '/opt/mystocks/logs/backend.log',
      out_file: '/opt/mystocks/logs/backend-out.log',
      error_file: '/opt/mystocks/logs/backend-error.log',
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,

      // 错误回滚
      kill_timeout: 5000
    },

    {
      // 前端静态文件服务
      name: 'mystocks-frontend',
      script: '/root/.nvm/versions/node/v24.7.0/bin/npx',
      args: 'serve web/frontend/dist -l 3000 -s',
      cwd: '/opt/claude/mystocks_spec',

      instances: 1,
      exec_mode: 'fork',
      interpreter: 'none',

      env: {
        NODE_ENV: 'production',
        PORT: 3000
      },

      autorestart: true,
      watch: false,
      max_restarts: 5,
      restart_delay: 3000,
      min_uptime: '5s',

      max_memory_restart: '512M',

      health_check: {
        enable: true,
        url: 'http://localhost:3000',
        interval: 30000,
        max_retries: 2,
        timeout: 3000
      },

      log_file: '/opt/mystocks/logs/frontend.log',
      out_file: '/opt/mystocks/logs/frontend-out.log',
      error_file: '/opt/mystocks/logs/frontend-error.log',
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,

      kill_timeout: 3000
    },

    {
      // 数据同步服务: 股票基础信息同步
      name: "data-sync-basic",
      script: "python",
      args: "scripts/data_sync/sync_stock_basic.py",
      cwd: "/opt/claude/mystocks_spec",
      interpreter: 'none',

      instances: 1,
      exec_mode: 'fork',

      env: {
        NODE_ENV: 'production',
        ENVIRONMENT: 'production',
        PYTHONPATH: "/opt/claude/mystocks_spec"
      },

      cron_restart: "0 3 * * 0", // 每周日凌晨3点
      autorestart: true,
      watch: false,
      max_restarts: 3,
      restart_delay: 10000,

      max_memory_restart: '512M',

      out_file: '/opt/mystocks/logs/data-sync-basic.log',
      error_file: '/opt/mystocks/logs/data-sync-basic-error.log',
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',

      kill_timeout: 10000
    },

    {
      // 数据同步服务: 股票K线数据同步
      name: "data-sync-kline",
      script: "python",
      args: "scripts/data_sync/sync_stock_kline.py",
      cwd: "/opt/claude/mystocks_spec",
      interpreter: 'none',

      instances: 1,
      exec_mode: 'fork',

      env: {
        NODE_ENV: 'production',
        ENVIRONMENT: 'production',
        PYTHONPATH: "/opt/claude/mystocks_spec"
      },

      cron_restart: "0 2 * * *", // 每日凌晨2点
      autorestart: true,
      watch: false,
      max_restarts: 3,
      restart_delay: 10000,

      max_memory_restart: '512M',

      out_file: '/opt/mystocks/logs/data-sync-kline.log',
      error_file: '/opt/mystocks/logs/data-sync-kline-error.log',
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',

      kill_timeout: 10000
    },

    {
      // 数据同步服务: 分时线数据同步
      name: "data-sync-minute-kline",
      script: "python",
      args: "scripts/data_sync/sync_minute_kline.py --periods 1m 5m 15m 30m 60m",
      cwd: "/opt/claude/mystocks_spec",
      interpreter: 'none',

      instances: 1,
      exec_mode: 'fork',

      env: {
        NODE_ENV: 'production',
        ENVIRONMENT: 'production',
        PYTHONPATH: "/opt/claude/mystocks_spec"
      },

      cron_restart: "0 17 * * 1-5", // 周一到周五 17:00
      autorestart: true,
      watch: false,
      max_restarts: 3,
      restart_delay: 10000,

      max_memory_restart: '512M',

      out_file: '/opt/mystocks/logs/data-sync-minute-kline.log',
      error_file: '/opt/mystocks/logs/data-sync-minute-kline-error.log',
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',

      kill_timeout: 10000
    },

    {
      // 数据同步服务: 行业分类数据同步
      name: "data-sync-industry-classify",
      script: "python",
      args: "scripts/data_sync/sync_industry_classify.py",
      cwd: "/opt/claude/mystocks_spec",
      interpreter: 'none',

      instances: 1,
      exec_mode: 'fork',

      env: {
        NODE_ENV: 'production',
        ENVIRONMENT: 'production',
        PYTHONPATH: "/opt/claude/mystocks_spec"
      },

      cron_restart: "0 4 * * 1", // 每周一凌晨4点
      autorestart: true,
      watch: false,
      max_restarts: 3,
      restart_delay: 10000,

      max_memory_restart: '256M',

      out_file: '/opt/mystocks/logs/data-sync-industry.log',
      error_file: '/opt/mystocks/logs/data-sync-industry-error.log',
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',

      kill_timeout: 10000
    },

    {
      // 数据同步服务: 概念分类数据同步
      name: "data-sync-concept-classify",
      script: "python",
      args: "scripts/data_sync/sync_concept_classify.py",
      cwd: "/opt/claude/mystocks_spec",
      interpreter: 'none',

      instances: 1,
      exec_mode: 'fork',

      env: {
        NODE_ENV: 'production',
        ENVIRONMENT: 'production',
        PYTHONPATH: "/opt/claude/mystocks_spec"
      },

      cron_restart: "30 4 * * 1", // 每周一凌晨4:30
      autorestart: true,
      watch: false,
      max_restarts: 3,
      restart_delay: 10000,

      max_memory_restart: '256M',

      out_file: '/opt/mystocks/logs/data-sync-concept.log',
      error_file: '/opt/mystocks/logs/data-sync-concept-error.log',
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',

      kill_timeout: 10000
    },

    {
      // 监控服务: 系统性能监控
      name: "system-monitor",
      script: "python",
      args: "src/monitoring/performance_monitor.py",
      cwd: "/opt/claude/mystocks_spec",
      interpreter: 'none',

      instances: 1,
      exec_mode: 'fork',

      env: {
        NODE_ENV: 'production',
        ENVIRONMENT: 'production',
        PYTHONPATH: "/opt/claude/mystocks_spec"
      },

      autorestart: true,
      watch: false,
      max_restarts: 5,
      restart_delay: 5000,

      max_memory_restart: '256M',

      out_file: '/opt/mystocks/logs/system-monitor.log',
      error_file: '/opt/mystocks/logs/system-monitor-error.log',
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',

      kill_timeout: 5000
    }
  ],

  // PM2 部署配置
  deploy: {
    production: {
      user: 'mystocks',
      host: ['your-production-server.com'],
      ref: 'origin/main',
      repo: 'git@github.com:your-org/mystocks.git',
      path: '/opt/mystocks',
      'post-deploy': 'npm install && pip install -r requirements.txt && npm run build && pm2 reload ecosystem.production.config.js --env production',
      'pre-setup': 'apt update && apt install -y python3 python3-pip nodejs npm postgresql postgresql-contrib redis-server'
    }
  }
};
