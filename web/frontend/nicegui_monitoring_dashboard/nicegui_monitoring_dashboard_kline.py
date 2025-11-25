#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nicegui_monitoring_dashboard_kline.py - 模块化拆分版
原始文件: /opt/claude/mystocks_spec/web/frontend/nicegui_monitoring_dashboard_kline.py
拆分时间: 2025-11-25 14:14:51

这是模块化拆分后的主入口文件，保留了原有的功能，并导入了拆分后的组件模块。
"""

import asyncio
import logging
import json
import csv
import pandas as pd
from datetime import datetime, timedelta



# 为向后兼容性保留原有导入
from src.monitoring.ai_alert_manager import AIAlertManager
from src.monitoring.ai_realtime_monitor import AIRealtimeMonitor

# 导入核心类和组件
from .core import EnhancedKlineMonitoringDashboard
from .components import *

# 应用启动函数
def create_and_run_monitoring_app():
    """创建并运行监控应用"""
    from src.monitoring.ai_alert_manager import get_ai_alert_manager
    from src.monitoring.ai_realtime_monitor import get_ai_realtime_monitor
    
    # 创建告警管理器和监控器
    alert_manager = get_ai_alert_manager()
    monitor = get_ai_realtime_monitor(alert_manager)
    
    # 创建监控面板
    dashboard = EnhancedKlineMonitoringDashboard(alert_manager, monitor)
    
    # 创建路由
    @ui.page('/')
    def index():
        dashboard.create_monitoring_page()
    
    # 启动NiceGUI
    ui.run(
        title='MyStocks K线监控仪表板',
        host='0.0.0.0',
        port=8080,
        reload=False
    )

if __name__ == "__main__":
    create_and_run_monitoring_app()
