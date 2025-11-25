#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks NiceGUI增强版监控面板 (UI/UX优化版)

基于NiceGUI的现代化AI监控系统Web界面，支持实时监控、告警管理、性能分析等功能。
专门针对UI/UX进行深度优化，提供更好的用户体验。

UI/UX优化特性:
- 🎨 现代化Material Design风格界面
- 📊 实时图表和可视化数据
- 🌙 深色/浅色主题切换
- 📱 完全响应式设计
- ⚡ 性能优化和智能刷新
- 🔔 智能告警通知系统
- 🎯 用户偏好设置
- 📈 数据导出功能
- ⌨️ 键盘快捷键支持

作者: MyStocks AI开发团队
创建日期: 2025-11-16
版本: 2.0.0 (UI/UX增强版)
依赖: nicegui, uvicorn, chart.js
注意事项: 专为生产环境设计的现代化监控界面
版权: MyStocks Project © 2025
"""

import logging
from nicegui import ui

logger = logging.getLogger(__name__)

# 导入核心模块
from .core import EnhancedNiceGUIMonitoringDashboard


# 应用入口点
class NiceGUIMonitoringApp:
    """NiceGUI监控应用包装类，简化创建和运行监控界面"""
    
    def __init__(self):
        self.dashboard = None
        
    def create_and_run(self):
        """创建并运行增强版监控应用"""
        from src.monitoring.ai_alert_manager import get_ai_alert_manager
        from src.monitoring.ai_realtime_monitor import get_ai_realtime_monitor
        
        # 创建告警管理器和监控器
        alert_manager = get_ai_alert_manager()
        monitor = get_ai_realtime_monitor(alert_manager)
        
        # 创建增强版监控面板
        self.dashboard = EnhancedNiceGUIMonitoringDashboard(alert_manager, monitor)
        
        # 创建路由
        @ui.page('/')
        def index():
            self.dashboard.create_monitoring_page()
            
            # 添加浮动操作按钮
            if hasattr(self.dashboard, '_create_floating_actions'):
                self.dashboard._create_floating_actions()
        
        @ui.page('/api/enhanced/health')
        async def enhanced_health_check():
            """增强版健康检查API"""
            try:
                if self.dashboard and hasattr(self.dashboard, 'monitor'):
                    health = await self.dashboard.monitor.run_health_check()
                    return ui.json_response({
                        'status': 'success',
                        'version': '2.0.0',
                        'features': ['enhanced_ui', 'real_time_charts', 'theme_switching'],
                        'health': health
                    })
                else:
                    return ui.json_response({'error': 'Dashboard not initialized'}, status_code=500)
            except Exception as e:
                return ui.json_response({'error': str(e)}, status_code=500)
        
        @ui.page('/api/enhanced/alerts')
        async def enhanced_alerts_api():
            """增强版告警API"""
            try:
                if self.dashboard and hasattr(self.dashboard, 'alert_manager'):
                    alert_summary = self.dashboard.alert_manager.get_alert_summary()
                    active_alerts = [alert.to_dict() for alert in self.dashboard.alert_manager.get_active_alerts()]
                    
                    return ui.json_response({
                        'status': 'success',
                        'summary': alert_summary,
                        'active_alerts': active_alerts,
                        'version': '2.0.0'
                    })
                else:
                    return ui.json_response({'error': 'Dashboard not initialized'}, status_code=500)
            except Exception as e:
                return ui.json_response({'error': str(e)}, status_code=500)


def create_enhanced_monitoring_app():
    """创建增强版监控应用"""
    return NiceGUIMonitoringApp()


if __name__ == "__main__":
    # 创建并启动增强版监控仪表板
    app = create_enhanced_monitoring_app()
    app.create_and_run()
    
    # 启动NiceGUI
    ui.run(
        title='MyStocks 增强版监控仪表板',
        host='0.0.0.0',
        port=8080,
        reload=False
    )