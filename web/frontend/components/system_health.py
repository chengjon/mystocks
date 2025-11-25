"""
MyStocks NiceGUI增强版监控面板 - 系统健康组件模块

作者: MyStocks AI开发团队
版本: 2.0.0 (UI/UX增强版)
日期: 2025-11-25
"""

from nicegui import ui


def create_system_health(dashboard):
    """创建系统健康状态"""
    with ui.card().classes('w-full q-pa-lg dashboard-card'):
        with ui.row().classes('items-center justify-between q-mb-md'):
            ui.label('💚 系统健康监控').classes('text-h6 text-weight-bold')
            with ui.row().classes('items-center q-gutter-sm'):
                ui.icon('analytics', size='20px', color='green')
                ui.button('健康报告', on_click=dashboard._generate_health_report, color='green', size='sm').classes('control-btn')
        
        with ui.row().classes('responsive-grid'):
            # 健康状态概览
            with ui.card().classes('q-pa-md flex-grow-1'):
                ui.label('系统状态:').classes('text-subtitle2 text-weight-medium')
                with ui.row().classes('items-center q-mt-sm'):
                    dashboard.health_status_icon = ui.icon('check_circle', color='green', size='24px')
                    dashboard.health_status_label = ui.label('健康').classes('text-h5 text-weight-bold text-green')
                
                ui.label('监控状态:').classes('text-subtitle2 text-weight-medium q-mt-md')
                dashboard.monitoring_status_label = ui.label('未运行').classes('text-body1 q-mt-sm')
            
            # 性能统计
            with ui.card().classes('q-pa-md flex-grow-1'):
                ui.label('性能统计:').classes('text-subtitle2 text-weight-medium')
                dashboard.monitor_stats_label = ui.label('无数据').classes('text-body1 q-mt-sm')
                
                ui.label('成功率:').classes('text-subtitle2 text-weight-medium q-mt-md')
                dashboard.success_rate_label = ui.label('0%').classes('text-body1 text-weight-bold q-mt-sm')
            
            # 系统信息
            with ui.card().classes('q-pa-md flex-grow-1'):
                ui.label('系统信息:').classes('text-subtitle2 text-weight-medium')
                dashboard.system_info_label = ui.label('正在获取...').classes('text-body1 q-mt-sm')
                
                ui.label('运行时长:').classes('text-subtitle2 text-weight-medium q-mt-md')
                dashboard.uptime_label = ui.label('0分钟').classes('text-body1 q-mt-sm')