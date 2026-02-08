// PM2 多服务进程管理配置 (整合优化版)
// 支持开发/生产环境自动切换
module.exports = {
  apps: [{
    // 前端服务: Vite开发服务器
    name: 'mystocks-frontend',
    script: 'npm run dev',
    cwd: '/opt/claude/mystocks_spec/web/frontend',
    env: {
      NODE_ENV: 'development',
      PORT: 3002,
      HOST: '0.0.0.0'
    },
    instances: 1,
    exec_mode: 'fork',
    // 健康检查配置
    health_check: {
      url: 'http://localhost:3002',
      timeout: 5000,
      retries: 3,
      interval: 10000
    },
    // 自动重启配置
    autorestart: true,
    max_restarts: 30,
    min_uptime: '10s',
    // 日志配置
    log_file: '/tmp/pm2-mystocks-frontend.log',
    out_file: '/tmp/pm2-mystocks-frontend-out.log',
    error_file: '/tmp/pm2-mystocks-frontend-error.log',
    merge_logs: true,
    // 资源限制
    max_memory_restart: '1G'
  },
  {
    // 核心服务: 后端 API 服务
    name: 'mystocks-backend',
    script: 'python -m uvicorn app.main:app',
    args: '--host 0.0.0.0 --port 8000 --reload',
    interpreter: 'python',
    cwd: '/opt/claude/mystocks_spec/web/backend',
    instances: 1,
    exec_mode: 'fork',

    // 环境差异化配置
    env: {
      NODE_ENV: 'dev',
      USE_MOCK: 'true',
      DB_HOST: 'localhost',
      DB_NAME: 'quant_dev',
      DB_USER: 'dev_user',
      DB_PASS: 'dev_pass',
      LOG_LEVEL: 'debug',
      TESTING: 'true',
      PYTHONPATH: '/opt/claude/mystocks_spec/web/backend:/opt/claude/mystocks_spec'
    },
    env_production: {
      NODE_ENV: 'prod',
      USE_MOCK: 'false',
      DB_HOST: 'db-prod',
      DB_NAME: 'quant_prod',
      DB_USER: 'prod_user',
      DB_PASS: 'prod_pass',
      LOG_LEVEL: 'info'
    },

    // 自动重启策略
    autorestart: true,
    watch: false,  // 生产环境禁用
    max_restarts: 10,
    restart_delay: 5000,

    // 资源限制
    max_memory_restart: '1G',

    // 健康检查配置
    health_check: {
      url: 'http://localhost:8000/api/health',
      timeout: 3000,
      retries: 3,
      interval: 15000
    },

    // 日志配置
    log_file: '/tmp/pm2-mystocks-backend.log',
    out_file: '/tmp/pm2-mystocks-backend-out.log',
    error_file: '/tmp/pm2-mystocks-backend-error.log',
    merge_logs: true,

    // 进程管理
    min_uptime: '10s'
  },
  {
    // 数据同步服务: 股票基础信息同步
    name: "data-sync-basic",
    script: "scripts/data_sync/sync_stock_basic.py",
    interpreter: "python3",
    cwd: "/opt/claude/mystocks_spec",
    cron_restart: "0 3 * * 0", // 每周日凌晨3点
    out_file: "logs/data_sync/stock_basic_sync.log",
    error_file: "logs/data_sync/stock_basic_sync_error.log",
    env: {
      NODE_ENV: 'dev',
      PYTHONPATH: "/opt/claude/mystocks_spec"
    }
  },
  {
    // 数据同步服务: 股票K线数据同步
    name: "data-sync-kline",
    script: "scripts/data_sync/sync_stock_kline.py",
    interpreter: "python3",
    cwd: "/opt/claude/mystocks_spec",
    cron_restart: "0 2 * * *", // 每日凌晨2点
    out_file: "logs/data_sync/stock_kline_sync.log",
    error_file: "logs/data_sync/stock_kline_sync_error.log",
    env: {
      NODE_ENV: 'dev',
      PYTHONPATH: "/opt/claude/mystocks_spec"
    }
  },
  {
    // 数据同步服务: 分时线数据同步
    name: "data-sync-minute-kline",
    script: "scripts/data_sync/sync_minute_kline.py",
    interpreter: "python3",
    args: "--periods 1m 5m 15m 30m 60m",
    cwd: "/opt/claude/mystocks_spec",
    cron_restart: "0 17 * * 1-5", // 周一到周五 17:00（交易日收盘后1小时）
    out_file: "logs/data_sync/minute_kline_sync.log",
    error_file: "logs/data_sync/minute_kline_sync_error.log",
    env: {
      NODE_ENV: 'dev',
      PYTHONPATH: "/opt/claude/mystocks_spec"
    }
  },
  {
    // 数据同步服务: 行业分类数据同步
    name: "data-sync-industry-classify",
    script: "scripts/data_sync/sync_industry_classify.py",
    interpreter: "python3",
    cwd: "/opt/claude/mystocks_spec",
    cron_restart: "0 4 * * 1", // 每周一凌晨4点
    out_file: "logs/data_sync/industry_classify_sync.log",
    error_file: "logs/data_sync/industry_classify_sync_error.log",
    env: {
      NODE_ENV: 'dev',
      PYTHONPATH: "/opt/claude/mystocks_spec"
    }
  },
  {
    // 数据同步服务: 概念分类数据同步
    name: "data-sync-concept-classify",
    script: "scripts/data_sync/sync_concept_classify.py",
    interpreter: "python3",
    cwd: "/opt/claude/mystocks_spec",
    cron_restart: "30 4 * * 1", // 每周一凌晨4:30（错开30分钟避免资源冲突）
    out_file: "logs/data_sync/concept_classify_sync.log",
    error_file: "logs/data_sync/concept_classify_sync_error.log",
    env: {
      NODE_ENV: 'dev',
      PYTHONPATH: "/opt/claude/mystocks_spec"
    }
  },
  {
    // 数据同步服务: 个股-行业概念关联数据同步
    name: "data-sync-stock-industry-concept",
    script: "scripts/data_sync/sync_stock_industry_concept.py",
    interpreter: "python3",
    cwd: "/opt/claude/mystocks_spec",
    cron_restart: "0 5 * * 1", // 每周一凌晨5:00（确保跟随行业概念分类同步）
    out_file: "logs/data_sync/stock_industry_concept_sync.log",
    error_file: "logs/data_sync/stock_industry_concept_sync_error.log",
    env: {
      NODE_ENV: 'dev',
      PYTHONPATH: "/opt/claude/mystocks_spec"
    }
  }]
};
