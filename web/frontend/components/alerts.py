"""
MyStocks NiceGUI增强版监控面板 - 告警组件模块

作者: MyStocks AI开发团队
版本: 2.0.0 (UI/UX增强版)
日期: 2025-11-25
"""

from nicegui import ui
from typing import Dict


def create_alert_management(dashboard):
    """创建告警管理区域"""
    with ui.card().classes('w-full q-pa-lg dashboard-card'):
        with ui.row().classes('items-center justify-between q-mb-md'):
            ui.label('🚨 智能告警中心').classes('text-h6 text-weight-bold')
            with ui.row().classes('items-center q-gutter-sm'):
                ui.icon('settings', size='20px', color='orange')
                ui.button('告警设置', on_click=dashboard._show_alert_settings, color='orange', size='sm').classes('control-btn')
                ui.button('全部确认', on_click=dashboard._acknowledge_all_alerts, color='green', size='sm').classes('control-btn')
        
        # 告警统计
        with ui.row().classes('q-gutter-md q-mb-lg'):
            with ui.card().classes('q-pa-md bg-red-1 text-center flex-grow-1'):
                ui.icon('priority_high', color='red', size='32px')
                dashboard.alert_stats_critical = ui.label('0').classes('text-h5 text-weight-bold text-red')
                ui.label('严重告警').classes('text-caption')
            
            with ui.card().classes('q-pa-md bg-orange-1 text-center flex-grow-1'):
                ui.icon('warning', color='orange', size='32px')
                dashboard.alert_stats_warning = ui.label('0').classes('text-h5 text-weight-bold text-orange')
                ui.label('警告告警').classes('text-caption')
            
            with ui.card().classes('q-pa-md bg-blue-1 text-center flex-grow-1'):
                ui.icon('info', color='blue', size='32px')
                dashboard.alert_stats_info = ui.label('0').classes('text-h5 text-weight-bold text-blue')
                ui.label('信息告警').classes('text-caption')
        
        # 活跃告警列表
        ui.label('当前活跃告警:').classes('text-subtitle2 text-weight-medium q-mb-md')
        dashboard.active_alerts_container = ui.column().classes('q-gutter-sm')


def create_alert_history(dashboard):
    """创建告警历史"""
    with ui.card().classes('w-full q-pa-lg dashboard-card'):
        with ui.row().classes('items-center justify-between q-mb-md'):
            ui.label('📋 告警历史记录').classes('text-h6 text-weight-bold')
            with ui.row().classes('items-center q-gutter-sm'):
                ui.icon('history', size='20px', color='indigo')
                ui.button('清空历史', on_click=dashboard._clear_alert_history, color='red', size='sm').classes('control-btn')
        
        # 过滤选项
        with ui.row().classes('q-gutter-md q-mb-md items-center'):
            ui.label('过滤:').classes('text-body2')
            dashboard.severity_filter = ui.select(
                options=['全部', 'critical', 'warning', 'info'],
                value='全部',
                on_change=dashboard._filter_alert_history
            ).classes('col-2')
            
            dashboard.date_filter = ui.select(
                options=['全部', '今天', '最近7天', '最近30天'],
                value='全部',
                on_change=dashboard._filter_alert_history
            ).classes('col-2')
        
        # 历史告警表格
        dashboard.alert_history_table = ui.table({
            'columns': [
                {'name': 'time', 'label': '时间', 'field': 'time', 'align': 'left', 'sortable': True},
                {'name': 'rule', 'label': '告警规则', 'field': 'rule', 'align': 'left'},
                {'name': 'severity', 'label': '严重性', 'field': 'severity', 'align': 'center'},
                {'name': 'message', 'label': '消息', 'field': 'message', 'align': 'left'},
                {'name': 'status', 'label': '状态', 'field': 'status', 'align': 'center'},
                {'name': 'actions', 'label': '操作', 'field': 'actions', 'align': 'center'}
            ],
            'rows': []
        }).classes('w-full').props('flat bordered selectable')
        
        # 添加表格样式
        dashboard.alert_history_table.style('max-height: 400px; overflow-y: auto; border-radius: 8px;')


# 将相关方法移动到dashboard对象中
def _create_alert_item(dashboard, alert, index):
    """创建告警项组件"""
    # 确定告警严重性的CSS类
    severity_class = ''
    if alert.severity.value == 'critical':
        severity_class = 'alert-critical'
    elif alert.severity.value == 'warning':
        severity_class = 'alert-warning'
    elif alert.severity.value == 'info':
        severity_class = 'alert-info'
    
    # 创建告警项
    with ui.card().classes(f'alert-item {severity_class}'):
        with ui.row().classes('items-center justify-between'):
            # 左侧：告警图标和信息
            with ui.row().classes('items-center q-gutter-md'):
                # 告警图标
                if alert.severity.value == 'critical':
                    ui.icon('priority_high', color='red')
                elif alert.severity.value == 'warning':
                    ui.icon('warning', color='orange')
                else:
                    ui.icon('info', color='blue')
                
                # 告警文本信息
                with ui.column().classes('q-gutter-xs'):
                    # 告警消息
                    ui.label(alert.message).classes('text-body1')
                    # 时间戳和规则
                    with ui.row().classes('items-center q-gutter-sm'):
                        ui.label(f"规则: {alert.rule_name}").classes('text-caption text-grey-7')
                        ui.separator(vertical=True).classes('text-grey-5')
                        ui.label(alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')).classes('text-caption text-grey-7')
            
            # 右侧：操作按钮
            with ui.row().classes('items-center q-gutter-sm'):
                ui.button('确认', on_click=lambda: dashboard._acknowledge_alert(alert.id), 
                         color='positive', size='sm').props('flat')
                ui.button('详情', on_click=lambda: dashboard._show_alert_details(alert), 
                         color='info', size='sm').props('flat')
        
        # 存储组件引用
        dashboard.alert_components[index] = {
            'card': None,  # 稍后将设置
            'alert': alert
        }
    
    # 存储card引用
    dashboard.alert_components[index]['card'] = ui.card().elements[-1]


# 添加这些方法到dashboard类中
EnhancedNiceGUIMonitoringDashboard._create_alert_item = _create_alert_item