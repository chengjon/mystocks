"""
MyStocks NiceGUI增强版监控面板 - 指标组件模块

作者: MyStocks AI开发团队
版本: 2.0.0 (UI/UX增强版)
日期: 2025-11-25
"""

from nicegui import ui


def create_metrics_overview(dashboard):
    """创建指标概览卡片"""
    with ui.card().classes('w-full q-pa-lg dashboard-card'):
        with ui.row().classes('items-center justify-between q-mb-md'):
            ui.label('📊 系统指标概览').classes('text-h6 text-weight-bold')
            with ui.row().classes('items-center q-gutter-sm'):
                ui.icon('refresh', size='20px', color='blue')
                ui.button('实时刷新', on_click=dashboard._refresh_data, color='blue', size='sm').classes('control-btn')
        
        with ui.row().classes('responsive-grid'):
            # CPU使用率卡片
            dashboard._create_metric_card(
                'cpu', 'CPU使用率', 'processor', '#3f51b5', 
                'CPU', '正常', 'CPU处理器使用情况'
            )
            
            # GPU使用率卡片
            dashboard._create_metric_card(
                'gpu', 'GPU使用率', 'memory', '#9c27b0', 
                'GPU', '正常', '图形处理器使用情况'
            )
            
            # 内存使用率卡片
            dashboard._create_metric_card(
                'memory', '内存使用率', 'memory', '#4caf50', 
                '内存', '正常', '系统内存使用情况'
            )
            
            # 活跃告警卡片
            dashboard._create_alert_metric_card()


# 将相关方法移动到dashboard对象中
def _create_metric_card(dashboard, card_id, title, icon_name, color, value_label, status_label, description):
    """创建单个指标卡片"""
    with ui.card().classes('metric-card'):
        with ui.column().classes('items-center text-center q-pa-md'):
            # 图标和状态
            with ui.row().classes('w-full items-center justify-between'):
                ui.icon(icon_name, size='32px', color='white')
                with ui.row().classes('items-center q-gutter-xs'):
                    dashboard.metrics_cards[f'{card_id}_status_icon'] = ui.icon('check_circle', size='16px', color='light-green')
                    ui.label(status_label).classes('text-caption text-light-green')
            
            # 标题
            ui.label(title).classes('text-subtitle2 text-white q-mt-sm')
            
            # 主要数值
            with ui.row().classes('items-center justify-center q-mt-sm'):
                dashboard.metrics_cards[f'{card_id}_value'] = ui.label('0%').classes('text-h4 text-weight-bold text-white')
                ui.label(value_label).classes('text-body2 text-white-7 q-ml-sm')
            
            # 进度条
            dashboard.metrics_cards[f'{card_id}_progress'] = ui.linear_progress(
                value=0, 
                color='white', 
                size='lg'
            ).classes('w-full q-mt-md')
            
            # 描述
            with ui.tooltip(description):
                ui.icon('info', size='16px', color='white-7').classes('text-white-7 q-mt-sm')


# 将相关方法移动到dashboard对象中
def _create_alert_metric_card(dashboard):
    """创建告警指标卡片"""
    with ui.card().classes('metric-card bg-gradient-to-r from-red-500 to-pink-600'):
        with ui.column().classes('items-center text-center q-pa-md'):
            # 图标和状态
            with ui.row().classes('w-full items-center justify-between'):
                ui.icon('warning', size='32px', color='white')
                with ui.row().classes('items-center q-gutter-xs'):
                    dashboard.metrics_cards['alerts_status_icon'] = ui.icon('info', size='16px', color='white')
                    ui.label('无告警').classes('text-caption text-white-7')
            
            # 标题
            ui.label('活跃告警').classes('text-subtitle2 text-white q-mt-sm')
            
            # 主要数值
            with ui.row().classes('items-center justify-center q-mt-sm'):
                dashboard.metrics_cards['alerts_total_value'] = ui.label('0').classes('text-h4 text-weight-bold text-white')
                ui.label('总数').classes('text-body2 text-white-7 q-ml-sm')
            
            # 告警分布
            with ui.row().classes('w-full q-mt-md items-center justify-around'):
                with ui.column().classes('items-center'):
                    dashboard.metrics_cards['critical_count'] = ui.label('0').classes('text-h6 text-white')
                    ui.label('严重').classes('text-caption text-white-7')
                with ui.column().classes('items-center'):
                    dashboard.metrics_cards['warning_count'] = ui.label('0').classes('text-h6 text-white')
                    ui.label('警告').classes('text-caption text-white-7')
                with ui.column().classes('items-center'):
                    dashboard.metrics_cards['info_count'] = ui.label('0').classes('text-h6 text-white')
                    ui.label('信息').classes('text-caption text-white-7')


# 添加这些方法到dashboard类中
EnhancedNiceGUIMonitoringDashboard._create_metric_card = _create_metric_card
EnhancedNiceGUIMonitoringDashboard._create_alert_metric_card = _create_alert_metric_card