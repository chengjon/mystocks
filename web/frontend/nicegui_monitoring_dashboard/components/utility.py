# 通用工具函数


通用工具函数


    def __init__(self):
        """初始化监控仪表板"""
        self.alert_manager = AIAlertManager()
        self.monitor = AIRealtimeMonitor()
        
        # 仪表板数据存储
        self.dashboard_data = {
            'last_update': None,
            'chart_data': {
                'timestamps': [],
                'cpu_history': [],
                'gpu_history': [],
                'memory_history': [],
                'stock_data': {
                    'symbols': ['000001.SZ', '600000.SH', '000002.SZ'],
                    'kline_data': {},
                    'realtime_quotes': {}
                }
            },
            'metrics_summary': {},
            'alert_summary': {},
            'active_alerts': [],
            'system_health': {},
            'kline_config': {
                'chart_type': 'candlestick',
                'timeframe': '1m',
                'theme': 'light',
                'show_volume': True,
                'show_indicators': True
            }
        }
        
        # 图表实例存储
        self.chart_instances = {}
        self.kline_instances = {}
        
        # 性能指标
        self.performance_metrics = {
            'total_updates': 0,
            'avg_response_time': 0.0,
            'peak_cpu_usage': 0.0,
            'peak_gpu_usage': 0.0
        }
        
        # 主题状态
        self.is_dark_theme = False
        
        # 初始化仪表板
        self._initialize_dashboard()
    


    def _initialize_dashboard(self):
        """初始化仪表板界面"""
        logger.info("🚀 启动增强版K线监控仪表板")
        
        # 全局配置
        ui.query('body').style('background-color: #f5f5f5')
        
        # 主题切换按钮
        self._create_theme_toggle()
        
        # 主标题和状态栏
        self._create_header()
        
        # 指标卡片区域
        self._create_metrics_cards()
        
        # K线图表区域 (主要功能)
        self._create_kline_charts()
        
        # 实时性能图表
        self._create_realtime_charts()
        
        # 告警面板
        self._create_alert_panel()
        
        # 控制面板
        self._create_control_panel()
        
        # 浮动操作按钮
        self._create_floating_actions()
        
        # 键盘快捷键
        self._add_keyboard_shortcuts()
        
        # 定时数据更新
        self._setup_auto_refresh()
        
        logger.info("✅ K线监控仪表板初始化完成")
    


    def _create_header(self):
        """创建页面头部"""
        with ui.card().classes('w-full q-pa-lg bg-primary text-white dashboard-card'):
            with ui.row().classes('items-center justify-between'):
                with ui.row().classes('items-center q-gutter-md'):
                    ui.icon('monitor', size='32px', color='white')
                    ui.label('MyStocks AI K线监控仪表板').classes('text-h4 text-weight-bold')
                    ui.badge('v2.0', color='orange', text_color='white')
                
                # 系统状态指示器
                with ui.row().classes('items-center q-gutter-md'):
                    self.status_indicator = ui.html('<span class="status-indicator status-normal"></span>')
                    self.status_text = ui.label('系统正常').classes('text-subtitle1')
                    
                    # 更新时间
                    self.update_time = ui.label('').classes('text-caption')
                    self.update_time.set_text(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    


    def _create_metrics_cards(self):
        """创建指标卡片"""
        with ui.row().classes('q-gutter-md q-pa-md items-stretch'):
            
            # 系统指标卡片
            with ui.card().classes('metric-card dashboard-card flex-grow-1'):
                with ui.column().classes('items-center'):
                    ui.icon('memory', size='32px', color='white')
                    self.metrics_cards['cpu_usage'] = ui.label('0%').classes('text-h4 text-weight-bold')
                    ui.label('CPU使用率').classes('text-caption text-white-7')
            
            with ui.card().classes('metric-card dashboard-card flex-grow-1'):
                with ui.column().classes('items-center'):
                    ui.icon('memory', size='32px', color='white')
                    self.metrics_cards['gpu_usage'] = ui.label('0%').classes('text-h4 text-weight-bold')
                    ui.label('GPU使用率').classes('text-caption text-white-7')
            
            with ui.card().classes('metric-card dashboard-card flex-grow-1'):
                with ui.column().classes('items-center'):
                    ui.icon('storage', size='32px', color='white')
                    self.metrics_cards['memory_usage'] = ui.label('0%').classes('text-h4 text-weight-bold')
                    ui.label('内存使用率').classes('text-caption text-white-7')
            
            # 告警统计卡片
            with ui.card().classes('metric-card dashboard-card flex-grow-1'):
                with ui.row().classes('w-full items-center justify-around'):
                    with ui.column().classes('items-center'):
                        self.metrics_cards['critical_count'] = ui.label('0').classes('text-h6 text-white')
                        ui.label('严重').classes('text-caption text-white-7')
                    with ui.column().classes('items-center'):
                        self.metrics_cards['warning_count'] = ui.label('0').classes('text-h6 text-white')
                        ui.label('警告').classes('text-caption text-white-7')
                    with ui.column().classes('items-center'):
                        self.metrics_cards['info_count'] = ui.label('0').classes('text-h6 text-white')
                        ui.label('信息').classes('text-caption text-white-7')
    


    def _initialize_performance_monitoring(self):
        """初始化性能监控"""
        ui.run_javascript('''
        // 性能监控图表初始化
        function initializePerformanceCharts() {
            const ctx = document.getElementById('combinedChart');
            if (!ctx) return;
            
            window.combinedChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'CPU使用率 (%)',
                            data: [],
                            borderColor: '#3f51b5',
                            backgroundColor: 'rgba(63, 81, 181, 0.1)',
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: 'GPU使用率 (%)',
                            data: [],
                            borderColor: '#9c27b0',
                            backgroundColor: 'rgba(156, 39, 176, 0.1)',
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: '内存使用率 (%)',
                            data: [],
                            borderColor: '#4caf50',
                            backgroundColor: 'rgba(76, 175, 80, 0.1)',
                            tension: 0.4,
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                        }
                    },
                    interaction: {
                        mode: 'nearest',
                        axis: 'x',
                        intersect: false
                    }
                }
            });
        }
        
        // 页面加载时初始化
        setTimeout(initializePerformanceCharts, 500);
        ''')
    


    def _show_timeframe_options(self):
        """显示周期选项"""
        with ui.dialog() as dialog, ui.card():
            ui.label('选择K线周期').classes('text-h6 text-weight-bold q-mb-md')
            
            timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M']
            for tf in timeframes:
                ui.button(tf, on_click=lambda tf=tf: [self._change_timeframe(tf), dialog.close()]).classes('q-ma-xs')
    


    def _show_indicator_settings(self):
        """显示指标设置"""
        with ui.dialog() as dialog, ui.card():
            ui.label('技术指标设置').classes('text-h6 text-weight-bold q-mb-md')
            
            with ui.column().classes('q-gutter-md'):
                with ui.row().classes('items-center'):
                    ui.checkbox('显示移动平均线 (MA)', value=True)
                    ui.select(options=[5, 10, 20, 60], value=20).classes('w-20')
                
                with ui.row().classes('items-center'):
                    ui.checkbox('显示RSI', value=False)
                    ui.select(options=[6, 12, 24], value=12).classes('w-20')
                
                with ui.row().classes('items-center'):
                    ui.checkbox('显示MACD', value=False)
                    ui.select(options=[12, 26], value=[12, 26]).classes('w-20')
            
            with ui.row().classes('q-mt-lg justify-end'):
                ui.button('取消', on_click=dialog.close).classes('q-mr-sm')
                ui.button('应用', on_click=dialog.close, color='primary')
    


    def _update_ui_display(self):
        """更新UI显示"""
        try:
            current_metrics = self.dashboard_data['metrics_summary'].get('current_metrics', {})
            
            # 更新指标卡片
            self.metrics_cards['cpu_usage'].set_text(current_metrics.get('cpu_usage', '0%'))
            self.metrics_cards['gpu_usage'].set_text(current_metrics.get('gpu_utilization', '0%'))
            self.metrics_cards['memory_usage'].set_text(current_metrics.get('memory_usage', '0%'))
            
            # 更新告警统计
            alert_summary = self.dashboard_data['alert_summary']
            self.metrics_cards['critical_count'].set_text(str(alert_summary.get('critical_count', 0)))
            self.metrics_cards['warning_count'].set_text(str(alert_summary.get('warning_count', 0)))
            self.metrics_cards['info_count'].set_text(str(alert_summary.get('info_count', 0)))
            
            # 更新系统状态
            system_health = self.dashboard_data.get('system_health', {})
            if system_health.get('overall_status') == 'healthy':
                self.status_text.set_text('系统正常')
            else:
                self.status_text.set_text('需要关注')
            
            # 更新时间显示
            self.update_time.set_text(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"❌ 更新UI显示失败: {e}")
    


    def _update_performance_metrics(self, current_metrics):
        """更新性能指标"""
        try:
            cpu_usage = float(current_metrics.get('cpu_usage', '0%').replace('%', ''))
            gpu_usage = float(current_metrics.get('gpu_utilization', '0%').replace('%', ''))
            
            # 更新峰值指标
            self.performance_metrics['peak_cpu_usage'] = max(self.performance_metrics['peak_cpu_usage'], cpu_usage)
            self.performance_metrics['peak_gpu_usage'] = max(self.performance_metrics['peak_gpu_usage'], gpu_usage)
            
            # 计算平均响应时间
            self.performance_metrics['total_updates'] += 1
            
        except Exception as e:
            logger.error(f"❌ 更新性能指标失败: {e}")
    


    def _export_dashboard_data(self):
        """导出仪表板数据"""
        try:
            # 生成CSV格式数据
            csv_data = []
            for i, timestamp in enumerate(self.dashboard_data['chart_data']['timestamps']):
                csv_data.append({
                    '时间戳': timestamp,
                    'CPU使用率': self.dashboard_data['chart_data']['cpu_history'][i] if i < len(self.dashboard_data['chart_data']['cpu_history']) else '0',
                    'GPU使用率': self.dashboard_data['chart_data']['gpu_history'][i] if i < len(self.dashboard_data['chart_data']['gpu_history']) else '0',
                    '内存使用率': self.dashboard_data['chart_data']['memory_history'][i] if i < len(self.dashboard_data['chart_data']['memory_history']) else '0'
                })
            
            # 保存为CSV文件
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_filename = f'/tmp/mystocks_dashboard_{timestamp_str}.csv'
            
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['时间戳', 'CPU使用率', 'GPU使用率', '内存使用率']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
            
            # 显示下载链接
            ui.notify(f'✅ 数据已导出到: {csv_filename}', type='success')
            logger.info(f"📊 仪表板数据导出完成: {csv_filename}")
            
        except Exception as e:
            logger.error(f"❌ 导出数据失败: {e}")
            ui.notify(f'❌ 导出失败: {e}', type='negative')
    


    def _share_dashboard(self):
        """分享仪表板"""
        try:
            # 生成分享URL
            share_url = f"http://localhost:{nicegui.globals.app.port if hasattr(nicegui.globals.app, 'port') else 8080}/?dashboard={self.dashboard_data['last_update']}"
            
            ui.run_javascript(f'''
            // 复制分享链接到剪贴板
            navigator.clipboard.writeText('{share_url}').then(() => {{
                alert('✅ 分享链接已复制到剪贴板');
            }}).catch(() => {{
                prompt('请复制以下链接:', '{share_url}');
            }});
            ''')
            
            logger.info(f"📱 生成分享链接: {share_url}")
            
        except Exception as e:
            logger.error(f"❌ 生成分享链接失败: {e}")
    


    def _manual_refresh(self):
        """手动刷新数据"""
        ui.notify('🔄 正在刷新数据...', type='info')
        
        # 立即更新数据
        asyncio.create_task(self._update_dashboard_data())
        
        logger.info("🔄 手动刷新触发")
    


    def _add_keyboard_shortcuts(self):
        """添加键盘快捷键"""
        ui.run_javascript('''
        document.addEventListener('keydown', function(event) {
            // Ctrl+R: 刷新数据
            if (event.ctrlKey && event.key === 'r') {
                event.preventDefault();
                // 触发刷新按钮点击事件
                window.location.reload();
            }
            
            // Ctrl+S: 导出数据
            if (event.ctrlKey && event.key === 's') {
                event.preventDefault();
                // 这里可以添加导出功能
                console.log('快捷键: Ctrl+S - 导出数据');
            }
            
            // F11: 切换全屏
            if (event.key === 'F11') {
                event.preventDefault();
                if (!document.fullscreenElement) {
                    document.documentElement.requestFullscreen();
                } else {
                    document.exitFullscreen();
                }
            }
            
            // Space: 暂停/恢复自动更新
            if (event.key === ' ' && event.target.tagName !== 'INPUT') {
                event.preventDefault();
                console.log('快捷键: Space - 暂停/恢复更新');
            }
            
            // Esc: 关闭对话框
            if (event.key === 'Escape') {
                // 关闭所有打开的对话框
                const dialogs = document.querySelectorAll('[role="dialog"]');
                dialogs.forEach(dialog => dialog.close());
            }
        });
        ''')
    


    def _setup_auto_refresh(self):
        """设置自动刷新"""
        async def auto_update():
            while True:
                try:
                    await asyncio.sleep(self._get_adaptive_interval())
                    if not hasattr(self, '_auto_refresh_enabled') or self._auto_refresh_enabled:
                        await self._update_dashboard_data()
                except Exception as e:
                    logger.error(f"❌ 自动刷新失败: {e}")
                    await asyncio.sleep(10)  # 错误时等待10秒再重试
        
        # 启动自动刷新任务
        asyncio.create_task(auto_update())
        logger.info("🔄 自动刷新任务已启动")
    


    def _get_adaptive_interval(self) -> int:
        """获取自适应刷新间隔"""
        # 根据系统负载动态调整刷新频率
        cpu_usage = float(self.dashboard_data['metrics_summary'].get('current_metrics', {}).get('cpu_usage', '0%').replace('%', ''))
        
        if cpu_usage > 80:
            return 10  # 高负载时降低刷新频率
        elif cpu_usage > 50:
            return 5   # 中等负载时保持正常刷新
        else:
            return 3   # 低负载时可以提高刷新频率
    


    def _show_dashboard_report(self):
        """显示仪表板报告"""
        try:
            # 生成报告数据
            report_data = {
                '仪表板': 'MyStocks AI K线监控仪表板',
                '版本': 'v2.0 (Klinechart版本)',
                '最后更新': self.dashboard_data['last_update'],
                '总更新次数': self.performance_metrics['total_updates'],
                '峰值CPU使用率': f"{self.performance_metrics['peak_cpu_usage']:.1f}%",
                '峰值GPU使用率': f"{self.performance_metrics['peak_gpu_usage']:.1f}%",
                '当前主题': '深色' if self.is_dark_theme else '浅色',
                '活跃告警数': len(self.dashboard_data['active_alerts']),
                '图表数据点数': len(self.dashboard_data['chart_data']['timestamps'])
            }
            
            # 显示报告对话框
            with ui.dialog() as dialog, ui.card().classes('q-pa-lg'):
                ui.label('📊 仪表板报告').classes('text-h6 text-weight-bold q-mb-md')
                
                with ui.column().classes('q-gutter-sm'):
                    for key, value in report_data.items():
                        ui.label(f'• {key}: {value}')
                
                with ui.row().classes('q-mt-lg justify-end'):
                    ui.button('关闭', on_click=dialog.close, color='primary')
            
            logger.info("📊 显示仪表板报告")
            
        except Exception as e:
            logger.error(f"❌ 显示报告失败: {e}")

