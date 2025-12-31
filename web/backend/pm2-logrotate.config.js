/**
 * PM2 Logrotate Configuration
 *
 * PM2日志轮转配置
 * 用于管理PM2应用的日志文件大小和数量
 *
 * Author: Backend CLI (Claude Code)
 * Date: 2025-12-31
 *
 * 安装pm2-logrotate:
 * pm2 install pm2-logrotate
 *
 * 配置说明:
 * - maxSize: 日志文件最大大小
 * - retain: 保留的日志文件数量
 * - compress: 是否压缩旧日志
 * - dateFormat: 日志文件日期格式
 */

module.exports = {
  apps: [
    {
      name: 'mystocks-backend',

      // 日志轮转配置
      pm2_logrotate: {
        // 日志文件最大大小（可追加单位：K, M, G）
        maxSize: '100M',

        // 保留的日志文件数量
        retain: 7,

        // 是否压缩旧日志文件
        compress: true,

        // 压缩级别（1-9，9为最高压缩率）
        compressLevel: 9,

        // 日期格式
        dateFormat: 'YYYY-MM-DD_HH-mm-ss',

        // 轮转间隔（可选：daily, hourly）
        rotateInterval: '0 0 * * *', // 每天午夜轮转

        // 是否在轮转时创建新日志文件
        rotateModule: true,

        // 日志文件路径
        rotateFolder: './logs/archive',

        // 轮转的日志类型
        // - all: 所有日志
        // - error: 仅错误日志
        // - out: 仅输出日志
        rotateType: 'all',
      },
    },
  ],
};
