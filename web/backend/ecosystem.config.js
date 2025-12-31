/**
 * PM2 Ecosystem Configuration for MyStocks Backend
 *
 * PM2进程管理器配置文件
 * 用于管理和监控FastAPI后端服务
 *
 * Author: Backend CLI (Claude Code)
 * Date: 2025-12-31
 *
 * 使用方法:
 * - 启动服务: pm2 start ecosystem.config.js
 * - 停止服务: pm2 stop ecosystem.config.js
 * - 重启服务: pm2 restart ecosystem.config.js
 * - 查看状态: pm2 status
 * - 查看日志: pm2 logs mystocks-backend
 * - 监控: pm2 monit
 */

module.exports = {
  apps: [
    {
      // 应用名称
      name: 'mystocks-backend',

      // 启动脚本
      script: 'run_server.py',

      // 解释器
      interpreter: 'python3',

      // 工作目录
      cwd: '/opt/claude/mystocks_phase7_backend/web/backend',

      // 实例数量（1表示单实例，可设置为'max'使用CPU核心数）
      instances: 1,

      // 执行模式（cluster模式可用于多实例负载均衡）
      exec_mode: 'fork',

      // 自动重启配置
      autorestart: true,

      // 最大重启次数（超过后停止重启）
      max_restarts: 10,

      // 最小运行时间（毫秒，如果在此时间内退出，视为异常启动）
      min_uptime: '10s',

      // 重启延迟（毫秒）
      restart_delay: 4000,

      // 环境变量
      env: {
        // 生产环境配置
        NODE_ENV: 'production',
        USE_MOCK_DATA: 'false',
        PYTHONPATH: '/opt/claude/mystocks_phase7_backend/web/backend:/opt/claude/mystocks_phase7_backend',
        BACKEND_HOST: '0.0.0.0',
        BACKEND_PORT: '8000',
        // 日志级别
        LOG_LEVEL: 'info',
      },

      // 开发环境配置（使用: pm2 start ecosystem.config.js --env development）
      env_development: {
        NODE_ENV: 'development',
        USE_MOCK_DATA: 'true',
        LOG_LEVEL: 'debug',
      },

      // 日志配置
      error_file: './logs/pm2-error.log',
      out_file: './logs/pm2-out.log',
      log_file: './logs/pm2-combined.log',
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',

      // 日志轮转配置
      log_type: 'json',

      // 合并日志（将error和out合并到一个文件）
      combine_logs: true,

      // 进程监控
      watch: false, // 生产环境不启用文件监控

      // 内存限制（超过后自动重启）
      max_memory_restart: '1G',

      // CPU限制（0-1，1=100%）
      // cpu: 0.8,

      // 优雅关闭（等待请求处理完成）
      kill_timeout: 5000,
      wait_ready: true,
      listen_timeout: 10000,

      // 优雅启动（等待应用准备好才接收流量）
      // ready_signal: 'READY',

      // 进程ID文件
      pid_file: './logs/pm2.pid',

      // 实例相关配置（仅cluster模式）
      // instance_var: 'INSTANCE_ID',

      // 自动转储（内存问题时生成core dump）
      // auto_dump: true,

      // 禁用跟踪
      disable_trace: true,

      // Cron重启（定时重启）
      // cron_restart: '0 2 * * *', // 每天凌晨2点重启
    },
  ],

  // 部署配置（可选）
  // deploy: {
  //   production: {
  //     user: 'node',
  //     host: 'localhost',
  //     ref: 'origin/main',
  //     repo: 'git@github.com:username/repo.git',
  //     path: '/var/www/myapp',
  //     'post-deploy': 'pm2 restart ecosystem.config.js --env production',
  //   },
  // },
};
