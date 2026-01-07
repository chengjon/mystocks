#!/usr/bin/env python3
"""
# 功能：启动异步监控系统
# 作者：Claude (基于多角色架构评估建议)
# 创建日期：2026-01-03
# 版本：1.0.0
# 用法：python scripts/async_monitoring/start_async_monitoring.py
# 注意事项：
#   本脚本启动异步监控系统的后台Worker
#   通常在应用启动时调用
# 版权：MyStocks Project © 2026
"""

import sys
import os
import time
import signal
import logging

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/async_monitoring.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("MyStocks 异步监控系统启动脚本")
    logger.info("=" * 60)

    # 检查环境变量
    if os.getenv('ENABLE_ASYNC_MONITORING', 'false').lower() != 'true':
        logger.warning("⚠️ 异步监控未启用")
        logger.info("💡 提示: 设置环境变量 ENABLE_ASYNC_MONITORING=true 来启用")
        return 0

    try:
        # 导入异步监控模块
        from src.monitoring.async_monitoring_manager import (
            initialize_async_monitoring,
            shutdown_async_monitoring,
        )

        # 初始化异步监控系统
        logger.info("🚀 正在初始化异步监控系统...")
        initialize_async_monitoring()
        logger.info("✅ 异步监控系统已启动")
        logger.info("📊 监控事件Worker正在后台运行...")

        # 设置信号处理器
        def signal_handler(signum, frame):
            logger.info(f"\n⏹️ 收到信号 {signum}，正在关闭...")
            shutdown_async_monitoring()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # 保持运行
        logger.info("💡 按 Ctrl+C 停止Worker")
        while True:
            time.sleep(1)

    except Exception as e:
        logger.error(f"❌ 启动失败: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n⏹️ 用户中断")
        sys.exit(0)
