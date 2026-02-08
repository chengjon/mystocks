// PM2 增强版多服务进程管理配置
// 支持开发/生产环境自动切换
// 集成健康检查、自动重启、日志管理和部署自动化功能
// 版本: 2.0 Enhanced
// 作者: MyStocks开发团队
// 创建日期: 2026-01-27

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
    
    // 增强健康检查配置
    health_check: {
      url: 'http://localhost:3002',
      timeout: 5000,
      retries: 3,
      interval: 10000,
      // 增加健康状态检查
      endpoint: '/api/health',
      expected_status: 200,
      response_time_threshold: 3000 // 3秒内响应为健康
    },
    
    // 增强自动重启配置
    autorestart: true,
    max_restarts: 30,
    min_uptime: '10s',
    restart_delay: 5000,
    // 增加重启策略
    restart_strategy: {
      mode: 'exponential_backoff', // 指数退避策略
      base_delay: 2000,
      max_delay: 30000,
      failure_threshold: 3 // 连续3次失败后触发指数退避
    },
    
    // 增强日志配置
    log_file: '/tmp/pm2-mystocks-frontend.log',
    out_file: '/tmp/pm2-mystocks-frontend-out.log',
    error_file: '/tmp/pm2-mystocks-frontend-error.log',
    merge_logs: true,
    // 增强日志轮转
    log_rotation: {
      enabled: true,
      size: '100M',
      keep: 5,
      date_format: 'YYYY-MM-DD'
    },
    
    // 资源限制和监控
    max_memory_restart: '1G',
    cpu_threshold: 80, // CPU使用率超过80%告警
    memory_threshold: 85, // 内存使用率超过85%告警
    disk_threshold: 90,  // 磁盘使用率超过90%告警
    
    // 增强部署配置
    deployment: {
      auto_deploy: false, // 是否自动部署
      git_pull: true, // 自动拉取最新代码
      build_command: 'npm run build', // 构建命令
      deploy_command: 'pm2 reload ecosystem.enhanced.config.js' // 部署命令
    },
    
    // 增强监控集成
    monitoring: {
      metrics_enabled: true,
      health_endpoint: '/api/metrics',
      log_level: 'info',
      alert_webhook: process.env.ALERT_WEBHOOK_URL || null
    }
  },
  
  {
    // 核心服务: 后端 API 服务
    name: 'mystocks-backend',
    script: './start_backend.sh',
    cwd: '/opt/claude/mystocks_spec/web/backend',
    instances: 1,
    exec_mode: 'fork',

    // 环境差异化配置
    env: {
      NODE_ENV: 'dev',
      USE_MOCK: 'true',
      LOG_LEVEL: 'debug',
      TESTING: 'true',
      PYTHONPATH: '/opt/claude/mystocks_spec'
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

    // 增强自动重启策略
    autorestart: true,
    watch: false,  // 生产环境禁用
    max_restarts: 10,
    restart_delay: 5000,
    restart_strategy: {
      mode: 'exponential_backoff',
      base_delay: 3000,
      max_delay: 20000,
      failure_threshold: 2
    },

    // 增强健康检查配置
    health_check: {
      url: 'http://localhost:8000/api/health',
      timeout: 3000,
      retries: 3,
      interval: 15000,
      // 增加数据库连接检查
      database_check: {
        enabled: true,
        query: 'SELECT 1',
        timeout: 5000,
        connection_pool_check: true
      },
      // 增加API端点检查
      endpoints_check: [
        { path: '/api/health', method: 'GET', expected_status: 200 },
        { path: '/api/stocks', method: 'GET', expected_status: 200 },
        { path: '/api/strategies', method: 'GET', expected_status: 200 }
      ]
    },

    // 增强日志配置
    log_file: '/tmp/pm2-mystocks-backend.log',
    out_file: '/tmp/pm2-mystocks-backend-out.log',
    error_file: '/tmp/pm2-mystocks-backend-error.log',
    merge_logs: true,
    log_rotation: {
      enabled: true,
      size: '100M',
      keep: 10,
      date_format: 'YYYY-MM-DD'
    },

    // 资源限制和监控
    max_memory_restart: '2G',
    cpu_threshold: 80,
    memory_threshold: 85,
    disk_threshold: 90,

    // 增强监控集成
    monitoring: {
      metrics_enabled: true,
      health_endpoint: '/api/metrics',
      log_level: 'info',
      performance_monitoring: {
        enabled: true,
        slow_query_threshold: 1000, // 慢查询阈值1秒
        response_time_threshold: 3000 // 响应时间阈值3秒
      },
      error_tracking: {
        enabled: true,
        error_rate_threshold: 0.05, // 错误率超过5%告警
        critical_errors: ['OutOfMemoryError', 'ConnectionTimeout', 'DatabaseConnectionFailed']
      }
    },

    // 增强部署配置
    deployment: {
      auto_deploy: false,
      git_pull: true,
      build_command: 'pip install -r requirements.txt',
      deploy_command: 'pm2 reload ecosystem.enhanced.config.js'
    }
  },

  // 监控应用 - 新增
  {
    name: 'mystocks-monitoring',
    script: 'python scripts/automation/monitor_and_fix.py',
    interpreter: 'python',
    cwd: '/opt/claude/mystocks_spec',
    instances: 1,
    exec_mode: 'fork',
    autorestart: true,
    max_restarts: 5,
    min_uptime: '30s',
    
    // 监控专用配置
    env: {
      PYTHONPATH: '/opt/claude/mystocks_spec',
      LOG_LEVEL: 'info',
      CHECK_INTERVAL: 60, // 检查间隔60秒
      ALERT_COOLDOWN: 300, // 告警冷却期5分钟
      MAX_RESTART_ATTEMPTS: 3, // 最大重启尝试次数
      WEBHOOK_URL: process.env.ALERT_WEBHOOK_URL || ''
    },

    // 健康检查
    health_check: {
      url: 'http://localhost:8000/api/monitoring/health',
      timeout: 5000,
      retries: 2,
      interval: 30000
    },

    // 日志配置
    log_file: '/tmp/pm2-mystocks-monitoring.log',
    out_file: '/tmp/pm2-mystocks-monitoring-out.log',
    error_file: '/tmp/pm2-mystocks-monitoring-error.log',
    merge_logs: false // 监控日志独立管理
  },

  // GPU加速服务 - 如果存在
  {
    name: 'mystocks-gpu-api',
    script: 'python main_server.py',
    cwd: '/opt/claude/mystocks_spec/gpu_api_system',
    instances: 1,
    exec_mode: 'fork',
    autorestart: true,
    max_restarts: 3,
    min_uptime: '30s',
    
    // GPU服务专用配置
    env: {
      PYTHONPATH: '/opt/claude/mystocks_spec/gpu_api_system',
      CUDA_VISIBLE_DEVICES: '0',
      GPU_MEMORY_FRACTION: '0.8',
      LOG_LEVEL: 'info'
    },

    // 健康检查
    health_check: {
      url: 'http://localhost:8001/health',
      timeout: 3000,
      retries: 3,
      interval: 10000
    },

    // 日志配置
    log_file: '/tmp/pm2-mystocks-gpu-api.log',
    out_file: '/tmp/pm2-mystocks-gpu-api-out.log',
    error_file: '/tmp/pm2-mystocks-gpu-api-error.log',
    merge_logs: true,

    // GPU资源监控
    resource_monitoring: {
      gpu_memory_threshold: 90,
      gpu_util_threshold: 85,
      temperature_threshold: 80
    }
  },

  // 数据同步服务配置 - 增强错误处理
  {
    name: "data-sync-basic",
    script: "scripts/data_sync/sync_stock_basic.py",
    interpreter: "python3",
    cwd: "/opt/claude/mystocks_spec",
    cron_restart: "0 3 * * 0", // 每周日凌晨3点
    out_file: "logs/data_sync/stock_basic_sync.log",
    error_file: "logs/data_sync/stock_basic_sync_error.log",
    
    // 增强数据同步配置
    sync_config: {
      retry_attempts: 3,
      retry_delay: 300000, // 5分钟重试间隔
      timeout: 600000, // 10分钟超时
      data_validation: true, // 启用数据验证
      backup_enabled: true, // 启用备份
      backup_retention: 7 // 保留7天备份
    },
    
    env: {
      NODE_ENV: 'dev',
      PYTHONPATH: "/opt/claude/mystocks_spec",
      LOG_LEVEL: 'info'
    }
  },

  // 增强其他数据同步服务配置
  {
    name: "data-sync-kline",
    script: "scripts/data_sync/sync_stock_kline.py",
    interpreter: "python3",
    cwd: "/opt/claude/mystocks_spec",
    cron_restart: "0 2 * * *", // 每日凌晨2点
    out_file: "logs/data_sync/stock_kline_sync.log",
    error_file: "logs/data_sync/stock_kline_sync_error.log",
    sync_config: {
      retry_attempts: 3,
      retry_delay: 300000,
      timeout: 600000,
      data_validation: true,
      backup_enabled: true,
      backup_retention: 7
    },
    env: {
      NODE_ENV: 'dev',
      PYTHONPATH: "/opt/claude/mystocks_spec",
      LOG_LEVEL: 'info'
    }
  },

  {
    name: "data-sync-minute-kline",
    script: "scripts/data_sync/sync_minute_kline.py",
    interpreter: "python3",
    args: "--periods 1m 5m 15m 30m 60m",
    cwd: "/opt/claude/mystocks_spec",
    cron_restart: "0 17 * * 1-5", // 周一到周五17:00
    out_file: "logs/data_sync/minute_kline_sync.log",
    error_file: "logs/data_sync/minute_kline_sync.error.log",
    sync_config: {
      retry_attempts: 3,
      retry_delay: 300000,
      timeout: 600000,
      data_validation: true,
      backup_enabled: true,
      backup_retention: 7
    },
    env: {
      NODE_ENV: 'dev',
      PYTHONPATH: "/opt/claude/mystocks_spec",
      LOG_LEVEL: 'info'
    }
  }
  ],

  // 增强部署配置
  deploy: {
    production: {
      user: 'deploy',
      host: '192.168.123.104',
      ref: 'origin/main',
      repo: 'https://github.com/your-org/mystocks.git',
      path: '/opt/claude/mystocks_spec',
      'pre-deploy-local': 'echo "Starting deployment..."',
      'post-deploy': 'echo "Deployment completed. Services restarted."',
      'setup-commands': [
        'npm install --production',
        'pip install -r requirements.txt'
      ]
    }
  },

  // 增强全局配置
  monitoring_integration: {
    enabled: true,
    log_aggregation: true,
    dashboard_url: 'http://localhost:3000', // 前端监控面板
    metrics_endpoint: 'http://localhost:8000/api/metrics', // 后端指标端点
    alerting: {
      enabled: true,
      channels: ['email', 'webhook', 'slack'],
      thresholds: {
        cpu_usage: 80,
        memory_usage: 85,
        disk_usage: 90,
        error_rate: 0.05,
        response_time: 3000
      }
    }
  },

  // 增强开发环境配置
  development: {
    hot_reload: {
      enabled: true,
      patterns: ['**/*.py', '**/*.js', '**/*.vue'],
      ignored: ['node_modules/**', 'logs/**', 'temp/**']
    },
    debugging: {
      enabled: true,
      verbose_logging: false,
      source_maps: true
    }
  }
};