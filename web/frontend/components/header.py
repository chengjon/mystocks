"""
MyStocks NiceGUI增强版监控面板 - 头部组件模块

作者: MyStocks AI开发团队
版本: 2.0.0 (UI/UX增强版)
日期: 2025-11-25
"""

from nicegui import ui


def create_header(dashboard):
    """创建页面标题栏"""
    with ui.header().classes('q-pa-md bg-gradient-to-r from-blue-600 to-purple-600 text-white'):
        with ui.row().classes('w-full items-center justify-between'):
            with ui.column().classes('col-auto'):
                with ui.row().classes('items-center q-gutter-sm'):
                    ui.icon('dashboard', size='32px').classes('text-white')
                    ui.label('MyStocks AI实时监控系统').classes('text-h4 text-weight-bold')
                ui.label('增强版监控面板').classes('text-subtitle2 opacity-80')
                
                # 性能指示器
                with ui.row().classes('items-center q-gutter-sm q-mt-sm'):
                    ui.icon('speed', size='16px', color='light-green')
                    dashboard.performance_indicator = ui.label('正常').classes('text-caption text-light-green')
                    dashboard.memory_usage_indicator = ui.label('内存: 0%').classes('text-caption text-light-green-7')
                    dashboard.refresh_rate_indicator = ui.label('刷新: 3s').classes('text-caption text-light-green-7')
                    
                    # 错误指示器
                    dashboard.error_indicator = ui.icon('error', size='16px', color='transparent').classes('text-light-green')
                    dashboard.error_count_label = ui.label('0').classes('text-caption text-light-green')
            
            with ui.column().classes('col-auto items-center q-gutter-md'):
                # 主题切换
                dashboard.theme_toggle = ui.switch(
                    label='深色主题',
                    value=False,
                    on_change=dashboard._toggle_theme
                ).classes('theme-toggle text-white')
                
                # 紧凑模式切换
                dashboard.compact_mode_toggle = ui.switch(
                    label='紧凑模式',
                    value=False,
                    on_change=dashboard._toggle_compact_mode
                ).classes('text-white')
                
                # 状态指示器
                with ui.row().classes('items-center q-gutter-sm'):
                    dashboard.status_indicator = ui.icon('wifi', size='24px', color='green').classes('status-online')
                    ui.label('在线').classes('text-white')
                    ui.separator(vertical=True).classes('text-white')
                    ui.label('最后更新:').classes('text-white')
                    dashboard.last_update_label = ui.label('未更新').classes('text-white')