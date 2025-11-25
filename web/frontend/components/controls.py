"""
MyStocks NiceGUI增强版监控面板 - 控制面板组件模块

作者: MyStocks AI开发团队
版本: 2.0.0 (UI/UX增强版)
日期: 2025-11-25
"""

from nicegui import ui


def create_control_panel(dashboard):
    """创建控制面板"""
    with ui.card().classes('w-full q-pa-lg dashboard-card'):
        with ui.row().classes('items-center justify-between q-mb-md'):
            ui.label('🎮 智能控制面板').classes('text-h6 text-weight-bold')
            with ui.row().classes('items-center q-gutter-sm'):
                ui.icon('tune', size='20px', color='purple')
                ui.button('偏好设置', on_click=dashboard._show_preferences, color='purple', size='sm').classes('control-btn')
        
        with ui.row().classes('q-gutter-md q-mb-lg items-center'):
            dashboard.start_monitoring_btn = ui.button(
                '▶️ 开始监控',
                on_click=dashboard._start_monitoring,
                color='positive',
                size='lg'
            ).classes('control-btn q-px-lg q-py-sm')
            
            dashboard.stop_monitoring_btn = ui.button(
                '⏹️ 停止监控',
                on_click=dashboard._stop_monitoring,
                color='negative',
                size='lg'
            ).classes('control-btn q-px-lg q-py-sm')
            
            dashboard.test_alert_btn = ui.button(
                '🧪 测试告警',
                on_click=dashboard._test_alert,
                color='warning',
                size='lg'
            ).classes('control-btn q-px-lg q-py-sm')
            
            dashboard.export_btn = ui.button(
                '📊 导出报告',
                on_click=dashboard._export_dashboard_report,
                color='info',
                size='lg'
            ).classes('control-btn q-px-lg q-py-sm')
        
        # 状态指示器
        with ui.row().classes('items-center justify-center q-gutter-xl q-mt-md'):
            with ui.column().classes('items-center'):
                ui.icon('memory', size='24px', color='blue')
                ui.label('系统运行中').classes('text-caption')
            with ui.column().classes('items-center'):
                ui.icon('notifications', size='24px', color='orange')
                ui.label('告警启用').classes('text-caption')
            with ui.column().classes('items-center'):
                ui.icon('timeline', size='24px', color='green')
                ui.label('实时监控').classes('text-caption')
        
        # 添加浮动操作按钮
        create_floating_actions(dashboard)


def create_floating_actions(dashboard):
    """创建浮动操作按钮"""
    with ui.floating_action_button(
        icon='more_vert',
        color='primary',
        fab=False
    ).classes('floating-actions'):
        # 快捷操作菜单
        with ui.menu():
            ui.item('🚀 性能测试', on_click=dashboard._run_performance_test)
            ui.item('📊 数据导出', on_click=dashboard._quick_export)
            ui.item('🔔 通知测试', on_click=dashboard._test_notifications)
            ui.item('⚙️ 高级设置', on_click=dashboard._show_advanced_settings)


def add_keyboard_shortcuts(dashboard):
    """添加键盘快捷键"""
    # 添加键盘事件处理
    @ui.keyboard_event('alt+m')
    def toggle_monitoring():
        if hasattr(dashboard, 'monitor') and dashboard.monitor.is_running():
            dashboard._stop_monitoring()
        else:
            dashboard._start_monitoring()
    
    @ui.keyboard_event('alt+f')
    def toggle_fullscreen():
        dashboard._show_fullscreen_charts()
    
    @ui.keyboard_event('alt+t')
    def toggle_theme():
        if dashboard.theme_toggle:
            dashboard.theme_toggle.value = not dashboard.theme_toggle.value
            dashboard._toggle_theme()
    
    @ui.keyboard_event('alt+c')
    def toggle_compact_mode():
        if dashboard.compact_mode_toggle:
            dashboard.compact_mode_toggle.value = not dashboard.compact_mode_toggle.value
            dashboard._toggle_compact_mode()
    
    @ui.keyboard_event('alt+r')
    def refresh_data():
        dashboard._refresh_data()
    
    @ui.keyboard_event('alt+e')
    def export_report():
        dashboard._export_dashboard_report()
    
    @ui.keyboard_event('alt+a')
    def show_advanced_settings():
        dashboard._show_advanced_settings()
    
    # 添加快捷键提示
    ui.add_head_html("""
    <style>
    .keyboard-shortcuts-hint {
        position: fixed;
        bottom: 10px;
        left: 10px;
        background: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 12px;
        z-index: 1000;
        display: none;
    }
    
    .keyboard-shortcuts-hint.visible {
        display: block;
    }
    </style>
    <div class="keyboard-shortcuts-hint" id="keyboardShortcutsHint">
        按 <kbd>Alt+?</kbd> 显示快捷键提示
    </div>
    <div class="keyboard-shortcuts" id="keyboardShortcuts" style="display: none;">
        <div style="position: fixed; bottom: 50px; left: 10px; background: rgba(0, 0, 0, 0.8); color: white; padding: 15px; border-radius: 8px; font-size: 12px; z-index: 1000;">
            <h3 style="margin-top: 0;">快捷键</h3>
            <div><kbd>Alt+M</kbd> 开始/停止监控</div>
            <div><kbd>Alt+F</kbd> 全屏图表</div>
            <div><kbd>Alt+T</kbd> 切换主题</div>
            <div><kbd>Alt+C</kbd> 紧凑模式</div>
            <div><kbd>Alt+R</kbd> 刷新数据</div>
            <div><kbd>Alt+E</kbd> 导出报告</div>
            <div><kbd>Alt+A</kbd> 高级设置</div>
        </div>
    </div>
    <script>
    document.addEventListener('keydown', function(event) {
        if (event.altKey && event.key === '/') {
            event.preventDefault();
            var shortcuts = document.getElementById('keyboardShortcuts');
            if (shortcuts.style.display === 'none' || shortcuts.style.display === '') {
                shortcuts.style.display = 'block';
            } else {
                shortcuts.style.display = 'none';
            }
        }
        
        // 点击其他地方时隐藏快捷键
        document.addEventListener('click', function(event) {
            var shortcuts = document.getElementById('keyboardShortcuts');
            if (event.target !== document.querySelector('.keyboard-shortcuts') && 
                event.target !== document.querySelector('#keyboardShortcutsHint') &&
                !shortcuts.contains(event.target)) {
                shortcuts.style.display = 'none';
            }
        });
    });
    
    // 添加初始提示动画
    setTimeout(function() {
        var hint = document.getElementById('keyboardShortcutsHint');
        if (hint) {
            hint.classList.add('visible');
            setTimeout(function() {
                hint.classList.remove('visible');
            }, 3000);
        }
    }, 1000);
    </script>
    """)
