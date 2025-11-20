// PM2 多服务进程管理配置 (整合优化版)
// 支持开发/生产环境自动切换
module.exports = {
  apps: [{
    // 核心服务: 后端 API 服务
    name: 'mystocks-backend',
    script: 'python',
    args: '-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload',
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
      LOG_LEVEL: 'debug'
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

    // 健康检查
    health_check: {
      enable: true,
      url: 'http://localhost:8000/health',
      interval: 1000,
      max_retries: 3,
      timeout: 5000
    },

    // 日志配置
    log_file: './logs/backend.log',
    out_file: './logs/backend.log',
    error_file: './logs/backend.log',
    time: true,
    log_date_format: 'YYYY-MM-DD HH:mm:ss',

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