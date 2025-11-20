"""
MyStocks NiceGUI监控面板

基于NiceGUI的完整AI监控系统Web界面，支持实时监控、告警管理、性能分析等功能。
专为mystocks_nice分支设计，提供现代化的监控用户体验。

作者: MyStocks AI开发团队
创建日期: 2025-11-16
版本: 1.0.0 (NiceGUI版本)
依赖: nicegui, uvicorn
注意事项: 本文件是MyStocks v3.0 NiceGUI前端组件
版权: MyStocks Project © 2025
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from nicegui import ui, app
import uvicorn

from src.monitoring.ai_alert_manager import (
    AIAlertManager,
    Alert,
    AlertSeverity,
    AlertType,
    get_ai_alert_manager,
)

from src.monitoring.ai_realtime_monitor import (
    AIRealtimeMonitor,
    MonitoringConfig,
    get_ai_realtime_monitor,
)


logger = logging.getLogger(__name__)


class NiceGUIMonitoringDashboard:
    """NiceGUI监控面板主类"""
    
    def __init__(self, alert_manager: AIAlertManager, monitor: AIRealtimeMonitor):
        """初始化监控面板"""
        self.alert_manager = alert_manager
        self.monitor = monitor
        self.dashboard_refresh_interval = 5  # 5秒刷新
        self.dashboard_data = {
            'metrics_history': [],
            'active_alerts': [],
            'system_health': {},
            'last_update': None
        }
        
        # 页面组件引用
        self.metrics_cards = {}
        self.alert_components = {}
        self.chart_components = {}
        self.status_indicators = {}
        
        logger.info("✅ NiceGUI监控面板初始化完成")
    
    def create_monitoring_page(self):
        """创建监控页面"""
        self._create_header()
        self._create_metrics_overview()
        self._create_alert_management()
        self._create_system_health()
        self._create_realtime_charts()
        self._create_control_panel()
        self._create_alert_history()
        
        # 启动自动刷新
        self._start_auto_refresh()
    
    def _create_header(self):
        """创建页面标题栏"""
        # 主标题
        with ui.row().classes('w-full items-center justify-between q-pa-md bg-primary text-white'):
            with ui.column().classes('col-auto'):
                ui.label('🔍 MyStocks AI实时监控系统').classes('text-h4 text-weight-bold')
                ui.label('NiceGUI Web监控面板').classes('text-subtitle2 opacity-80')
            
            # 状态指示器
            with ui.row().classes('col-auto items-center q-gutter-md'):
                ui.badge('🟢 在线', color='green').bind_text_from(self._get_online_status)
                ui.label('最后更新:').classes('text-caption')
                self.last_update_label = ui.label('未更新').classes('text-caption')
    
    def _create_metrics_overview(self):
        """创建指标概览卡片"""
        with ui.card().classes('w-full q-pa-md q-mb-md'):
            ui.label('📊 系统指标概览').classes('text-h6 text-weight-bold q-mb-md')
            
            with ui.row().classes('q-gutter-md'):
                # CPU使用率卡片
                with ui.card().classes('col-3 q-pa-md text-center bg-blue-1'):
                    ui.label('CPU使用率').classes('text-subtitle2 text-grey-8')
                    self.cpu_usage_label = ui.label('0%').classes('text-h5 text-primary text-weight-bold')
                    self.cpu_progress = ui.progress(value=0, size='lg', color='primary').classes('w-full')
                    self.cpu_status_label = ui.label('正常').classes('text-caption text-green')
                
                # GPU使用率卡片
                with ui.card().classes('col-3 q-pa-md text-center bg-purple-1'):
                    ui.label('GPU使用率').classes('text-subtitle2 text-grey-8')
                    self.gpu_usage_label = ui.label('0%').classes('text-h5 text-secondary text-weight-bold')
                    self.gpu_progress = ui.progress(value=0, size='lg', color='secondary').classes('w-full')
                    self.gpu_status_label = ui.label('正常').classes('text-caption text-green')
                
                # 内存使用率卡片
                with ui.card().classes('col-3 q-pa-md text-center bg-green-1'):
                    ui.label('内存使用率').classes('text-subtitle2 text-grey-8')
                    self.memory_usage_label = ui.label('0%').classes('text-h5 text-accent text-weight-bold')
                    self.memory_progress = ui.progress(value=0, size='lg', color='accent').classes('w-full')
                    self.memory_status_label = ui.label('正常').classes('text-caption text-green')
                
                # 活跃告警卡片
                with ui.card().classes('col-3 q-pa-md text-center bg-red-1'):
                    ui.label('活跃告警').classes('text-subtitle2 text-grey-8')
                    self.alerts_count_label = ui.label('0').classes('text-h5 text-negative text-weight-bold')
                    ui.separator()
                    with ui.row().classes('q-gutter-sm justify-center'):
                        self.critical_alerts_badge = ui.badge('0', color='red', size='sm')
                        self.warning_alerts_badge = ui.badge('0', color='orange', size='sm')
                        self.info_alerts_badge = ui.badge('0', color='blue', size='sm')
    
    def _create_alert_management(self):
        """创建告警管理区域"""
        with ui.card().classes('w-full q-pa-md q-mb-md'):
            ui.label('🚨 告警状态管理').classes('text-h6 text-weight-bold q-mb-md')
            
            # 告警状态概览
            with ui.row().classes('q-gutter-md q-mb-md'):
                ui.badge('🔴 严重', color='red').bind_text_from(lambda: f"🔴 严重 {self._get_critical_alerts_count()}")
                ui.badge('🟡 警告', color='orange').bind_text_from(lambda: f"🟡 警告 {self._get_warning_alerts_count()}")
                ui.badge('🔵 信息', color='blue').bind_text_from(lambda: f"🔵 信息 {self._get_info_alerts_count()}")
            
            # 活跃告警列表
            with ui.column().classes('q-gutter-sm'):
                ui.label('当前活跃告警:').classes('text-subtitle1')
                self.active_alerts_container = ui.column().classes('q-gutter-sm')
    
    def _create_system_health(self):
        """创建系统健康状态"""
        with ui.card().classes('w-full q-pa-md q-mb-md'):
            ui.label('💚 系统健康状态').classes('text-h6 text-weight-bold q-mb-md')
            
            with ui.row().classes('q-gutter-md'):
                # 健康状态概览
                with ui.column().classes('col-6'):
                    ui.label('健康状态:').classes('text-subtitle2')
                    self.health_status_label = ui.label('健康').classes('text-h6 text-positive')
                    
                    ui.label('监控状态:').classes('text-subtitle2')
                    self.monitoring_status_label = ui.label('未运行').classes('text-body1')
                
                # 性能统计
                with ui.column().classes('col-6'):
                    ui.label('监控统计:').classes('text-subtitle2')
                    self.monitor_stats_label = ui.label('无数据').classes('text-body2')
                    
                    ui.label('成功率:').classes('text-subtitle2')
                    self.success_rate_label = ui.label('0%').classes('text-body2')
    
    def _create_realtime_charts(self):
        """创建实时图表区域"""
        with ui.card().classes('w-full q-pa-md q-mb-md'):
            ui.label('📈 实时性能图表').classes('text-h6 text-weight-bold q-mb-md')
            
            # 简单的文本图表代替复杂图表
            with ui.column().classes('q-gutter-md'):
                # CPU使用率趋势
                ui.label('CPU使用率趋势 (最近1分钟):').classes('text-subtitle2')
                self.cpu_trend_chart = ui.textarea(
                    value="等待数据...",
                    readonly=True,
                    validation={'输入限制': lambda x: len(x) <= 500}
                ).classes('w-full text-mono')
                
                # GPU使用率趋势
                ui.label('GPU使用率趋势 (最近1分钟):').classes('text-subtitle2')
                self.gpu_trend_chart = ui.textarea(
                    value="等待数据...",
                    readonly=True,
                    validation={'输入限制': lambda x: len(x) <= 500}
                ).classes('w-full text-mono')
                
                # 内存使用率趋势
                ui.label('内存使用率趋势 (最近1分钟):').classes('text-subtitle2')
                self.memory_trend_chart = ui.textarea(
                    value="等待数据...",
                    readonly=True,
                    validation={'输入限制': lambda x: len(x) <= 500}
                ).classes('w-full text-mono')
    
    def _create_control_panel(self):
        """创建控制面板"""
        with ui.card().classes('w-full q-pa-md q-mb-md'):
            ui.label('🎮 控制面板').classes('text-h6 text-weight-bold q-mb-md')
            
            with ui.row().classes('q-gutter-md'):
                self.start_monitoring_btn = ui.button(
                    '▶️ 开始监控',
                    on_click=self._start_monitoring,
                    color='positive'
                ).classes('q-mr-sm')
                
                self.stop_monitoring_btn = ui.button(
                    '⏹️ 停止监控',
                    on_click=self._stop_monitoring,
                    color='negative'
                ).classes('q-mr-sm')
                
                self.test_alert_btn = ui.button(
                    '🧪 测试告警',
                    on_click=self._test_alert,
                    color='warning'
                ).classes('q-mr-sm')
                
                self.refresh_btn = ui.button(
                    '🔄 刷新数据',
                    on_click=self._refresh_data,
                    color='primary'
                )
    
    def _create_alert_history(self):
        """创建告警历史"""
        with ui.card().classes('w-full q-pa-md q-mb-md'):
            ui.label('📋 告警历史').classes('text-h6 text-weight-bold q-mb-md')
            
            # 历史告警表格
            self.alert_history_table = ui.table({
                'columns': [
                    {'name': 'time', 'label': '时间', 'field': 'time', 'align': 'left'},
                    {'name': 'rule', 'label': '规则', 'field': 'rule', 'align': 'left'},
                    {'name': 'severity', 'label': '严重性', 'field': 'severity', 'align': 'center'},
                    {'name': 'message', 'label': '消息', 'field': 'message', 'align': 'left'},
                    {'name': 'status', 'label': '状态', 'field': 'status', 'align': 'center'}
                ],
                'rows': []
            }).classes('w-full').props('flat bordered')
            
            # 添加表格样式
            self.alert_history_table.style('max-height: 300px; overflow-y: auto;')
    
    def _start_auto_refresh(self):
        """启动自动刷新"""
        async def auto_refresh():
            while True:
                try:
                    await asyncio.sleep(self.dashboard_refresh_interval)
                    await self._update_dashboard_data()
                    self._update_dashboard_ui()
                except Exception as e:
                    logger.error(f"❌ 自动刷新失败: {e}")
                    await asyncio.sleep(10)  # 错误后等待更长时间
        
        # 在后台运行自动刷新
        asyncio.create_task(auto_refresh())
        logger.info("✅ 自动刷新已启动")
    
    async def _update_dashboard_data(self):
        """更新仪表板数据"""
        try:
            # 更新监控摘要
            metrics_summary = self.monitor.get_metrics_summary()
            
            # 更新告警摘要
            alert_summary = self.alert_manager.get_alert_summary()
            
            # 更新活跃告警
            active_alerts = self.alert_manager.get_active_alerts()
            
            # 获取系统健康状态
            health_check = await self.monitor.run_health_check()
            
            # 更新时间戳
            self.dashboard_data['last_update'] = datetime.now().isoformat()
            
            # 保存数据
            self.dashboard_data.update({
                'metrics_summary': metrics_summary,
                'alert_summary': alert_summary,
                'active_alerts': [alert.to_dict() for alert in active_alerts],
                'system_health': health_check
            })
            
        except Exception as e:
            logger.error(f"❌ 更新仪表板数据失败: {e}")
    
    def _update_dashboard_ui(self):
        """更新仪表板UI"""
        try:
            data = self.dashboard_data
            
            if 'metrics_summary' not in data:
                return
            
            metrics = data['metrics_summary']
            alert_summary = data['alert_summary']
            health = data['system_health']
            
            # 更新指标概览
            if 'current_metrics' in metrics:
                current_metrics = metrics['current_metrics']
                
                # CPU
                cpu_text = current_metrics.get('cpu_usage', '0%')
                cpu_value = float(cpu_text.replace('%', ''))
                self.cpu_usage_label.text = cpu_text
                self.cpu_progress.value = cpu_value
                self.cpu_status_label.text = '正常' if cpu_value < 80 else '警告' if cpu_value < 95 else '严重'
                
                # GPU
                gpu_text = current_metrics.get('gpu_utilization', '0%')
                gpu_value = float(gpu_text.replace('%', ''))
                self.gpu_usage_label.text = gpu_text
                self.gpu_progress.value = gpu_value
                self.gpu_status_label.text = '正常' if gpu_value < 85 else '警告' if gpu_value < 95 else '严重'
                
                # 内存
                memory_text = current_metrics.get('memory_usage', '0%')
                memory_value = float(memory_text.replace('%', ''))
                self.memory_usage_label.text = memory_text
                self.memory_progress.value = memory_value
                self.memory_status_label.text = '正常' if memory_value < 85 else '警告' if memory_value < 95 else '严重'
            
            # 更新告警计数
            active_count = alert_summary['active_alerts_count']
            self.alerts_count_label.text = str(active_count)
            
            self.critical_alerts_badge.text = str(alert_summary['critical_alerts'])
            self.warning_alerts_badge.text = str(alert_summary['warning_alerts'])
            self.info_alerts_badge.text = str(alert_summary['info_alerts'])
            
            # 更新系统健康状态
            self.health_status_label.text = health['overall_status'].upper()
            self.health_status_label.classes = f'text-h6 {"text-positive" if health["overall_status"] == "healthy" else "text-warning" if health["overall_status"] == "warning" else "text-negative"}'
            
            # 更新监控状态
            monitoring_status = metrics.get('monitoring_status', 'stopped')
            self.monitoring_status_label.text = monitoring_status.upper()
            
            # 更新统计信息
            if 'statistics' in metrics:
                stats = metrics['statistics']
                self.monitor_stats_label.text = f"总循环: {stats['total_cycles']} | 成功: {stats['successful_cycles']}"
                self.success_rate_label.text = stats.get('success_rate', '0%')
            
            # 更新活跃告警列表
            self._update_active_alerts_display()
            
            # 更新时间戳
            if self.dashboard_data['last_update']:
                update_time = datetime.fromisoformat(self.dashboard_data['last_update'])
                self.last_update_label.text = update_time.strftime('%H:%M:%S')
            
            # 更新图表趋势
            self._update_trend_charts()
            
        except Exception as e:
            logger.error(f"❌ 更新UI失败: {e}")
    
    def _update_active_alerts_display(self):
        """更新活跃告警显示"""
        # 清空现有告警
        self.active_alerts_container.clear()
        
        active_alerts = self.dashboard_data.get('active_alerts', [])
        
        if not active_alerts:
            with self.active_alerts_container:
                ui.label('✅ 暂无活跃告警').classes('text-positive text-subtitle2')
            return
        
        # 显示活跃告警
        for alert_data in active_alerts:
            severity_color = {
                'critical': 'red',
                'warning': 'orange', 
                'info': 'blue'
            }.get(alert_data['severity'], 'grey')
            
            with self.active_alerts_container:
                with ui.card().classes('q-pa-sm bg-grey-1'):
                    with ui.row().classes('items-center justify-between'):
                        with ui.column().classes('col-auto'):
                            ui.badge(
                                f"{alert_data['severity'].upper()}",
                                color=severity_color,
                                size='sm'
                            )
                            ui.label(alert_data['rule_name']).classes('text-weight-bold')
                            ui.label(alert_data['message']).classes('text-body2 text-grey-8')
                        
                        with ui.column().classes('col-auto'):
                            ui.button(
                                '✅ 确认',
                                on_click=lambda a=alert_data: self._acknowledge_alert(a['id']),
                                color='positive',
                                size='sm'
                            ).props('flat dense')
    
    def _update_trend_charts(self):
        """更新趋势图表"""
        metrics = self.dashboard_data.get('metrics_summary', {})
        
        if 'current_metrics' in metrics:
            # 生成简单的文本趋势图
            current_metrics = metrics['current_metrics']
            
            cpu_text = current_metrics.get('cpu_usage', '0%')
            gpu_text = current_metrics.get('gpu_utilization', '0%')
            memory_text = current_metrics.get('memory_usage', '0%')
            
            # 更新文本图表
            self.cpu_trend_chart.value = f"当前: {cpu_text}\n" + "=" * int(float(cpu_text.replace('%', '')) / 2)
            self.gpu_trend_chart.value = f"当前: {gpu_text}\n" + "=" * int(float(gpu_text.replace('%', '')) / 2)
            self.memory_trend_chart.value = f"当前: {memory_text}\n" + "=" * int(float(memory_text.replace('%', '')) / 2)
    
    def _get_online_status(self) -> str:
        """获取在线状态"""
        return '🟢 在线' if self.monitor.running else '🔴 离线'
    
    def _get_critical_alerts_count(self) -> str:
        """获取严重告警数"""
        return str(self.dashboard_data.get('alert_summary', {}).get('critical_alerts', 0))
    
    def _get_warning_alerts_count(self) -> str:
        """获取警告告警数"""
        return str(self.dashboard_data.get('alert_summary', {}).get('warning_alerts', 0))
    
    def _get_info_alerts_count(self) -> str:
        """获取信息告警数"""
        return str(self.dashboard_data.get('alert_summary', {}).get('info_alerts', 0))
    
    async def _start_monitoring(self):
        """开始监控"""
        try:
            self.start_monitoring_btn.disable()
            ui.notify('🔍 开始监控...', color='positive')
            
            # 在后台启动监控
            asyncio.create_task(self.monitor.start_monitoring(duration_seconds=3600))  # 1小时
            
        except Exception as e:
            logger.error(f"❌ 启动监控失败: {e}")
            ui.notify(f'启动监控失败: {e}', color='negative')
        finally:
            self.start_monitoring_btn.enable()
    
    async def _stop_monitoring(self):
        """停止监控"""
        try:
            self.monitor.stop_monitoring()
            ui.notify('⏹️ 监控已停止', color='warning')
        except Exception as e:
            logger.error(f"❌ 停止监控失败: {e}")
            ui.notify(f'停止监控失败: {e}', color='negative')
    
    async def _test_alert(self):
        """测试告警"""
        try:
            ui.notify('🧪 发送测试告警...', color='info')
            
            # 创建一个测试告警
            test_alert = Alert(
                id=f"test_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                rule_name="测试告警",
                alert_type=AlertType.SYSTEM_RESOURCE_HIGH,
                severity=AlertSeverity.WARNING,
                message="这是一个测试告警",
                timestamp=datetime.now(),
                metrics={'test': True}
            )
            
            # 处理告警
            await self.alert_manager._handle_alert(test_alert)
            
            ui.notify('✅ 测试告警发送成功', color='positive')
            
        except Exception as e:
            logger.error(f"❌ 测试告警失败: {e}")
            ui.notify(f'测试告警失败: {e}', color='negative')
    
    async def _refresh_data(self):
        """刷新数据"""
        try:
            ui.notify('🔄 刷新数据...', color='info')
            await self._update_dashboard_data()
            self._update_dashboard_ui()
            ui.notify('✅ 数据刷新完成', color='positive')
        except Exception as e:
            logger.error(f"❌ 数据刷新失败: {e}")
            ui.notify(f'数据刷新失败: {e}', color='negative')
    
    def _acknowledge_alert(self, alert_id: str):
        """确认告警"""
        try:
            success = self.alert_manager.acknowledge_alert(alert_id, "NiceGUI")
            if success:
                ui.notify('✅ 告警已确认', color='positive')
                # 刷新显示
                self._update_dashboard_ui()
            else:
                ui.notify('❌ 确认告警失败', color='negative')
        except Exception as e:
            logger.error(f"❌ 确认告警失败: {e}")
            ui.notify(f'确认告警失败: {e}', color='negative')


def create_monitoring_app():
    """创建监控应用"""
    # 创建告警管理器和监控器
    alert_manager = get_ai_alert_manager()
    monitor = get_ai_realtime_monitor(alert_manager)
    
    # 创建监控面板
    dashboard = NiceGUIMonitoringDashboard(alert_manager, monitor)
    
    # 创建路由
    @ui.page('/')
    def index():
        dashboard.create_monitoring_page()
    
    @ui.page('/api/health')
    async def health_check():
        """健康检查API"""
        try:
            health = await monitor.run_health_check()
            return ui.json_response(health)
        except Exception as e:
            return ui.json_response({'error': str(e)}, status_code=500)
    
    @ui.page('/api/alerts')
    async def alerts_api():
        """告警API"""
        try:
            alert_summary = alert_manager.get_alert_summary()
            active_alerts = [alert.to_dict() for alert in alert_manager.get_active_alerts()]
            
            return ui.json_response({
                'summary': alert_summary,
                'active_alerts': active_alerts
            })
        except Exception as e:
            return ui.json_response({'error': str(e)}, status_code=500)
    
    @ui.page('/api/metrics')
    async def metrics_api():
        """指标API"""
        try:
            metrics_summary = monitor.get_metrics_summary()
            return ui.json_response(metrics_summary)
        except Exception as e:
            return ui.json_response({'error': str(e)}, status_code=500)
    
    @ui.page('/api/control/{action}')
    async def control_api(action: str):
        """控制API"""
        try:
            if action == 'start':
                asyncio.create_task(monitor.start_monitoring(duration_seconds=3600))
                return ui.json_response({'status': 'success', 'message': '监控已启动'})
            elif action == 'stop':
                monitor.stop_monitoring()
                return ui.json_response({'status': 'success', 'message': '监控已停止'})
            else:
                return ui.json_response({'error': 'Invalid action'}, status_code=400)
        except Exception as e:
            return ui.json_response({'error': str(e)}, status_code=500)


def run_monitoring_server(host: str = "127.0.0.1", port: int = 8889, debug: bool = False):
    """运行监控服务器"""
    # 创建应用
    create_monitoring_app()
    
    # 配置应用
    app.title = "MyStocks AI监控系统"
    app.version = "1.0.0"
    app.description = "基于NiceGUI的AI实时监控面板"
    
    # 添加静态文件目录
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.add_static_files('/static', static_dir)
    
    # 启动服务器
    logger.info(f"🚀 启动MyStocks AI监控服务器: http://{host}:{port}")
    
    uvicorn.run(
        "nicegui_monitoring_dashboard:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )


if __name__ == "__main__":
    """运行监控面板"""
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # 命令行参数解析
    host = "127.0.0.1"
    port = 8889
    debug = False
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    if len(sys.argv) > 3:
        debug = sys.argv[3].lower() == "true"
    
    # 启动服务器
    run_monitoring_server(host, port, debug)
