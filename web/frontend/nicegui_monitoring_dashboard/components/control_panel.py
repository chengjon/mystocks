# 控制面板功能


控制面板功能


    def _create_theme_toggle(self):
        """创建主题切换按钮"""
        with ui.row().classes('theme-toggle items-center q-gutter-sm'):
            self.theme_icon = ui.icon('light_mode', size='24px', color='orange')
            ui.button('切换主题', on_click=self._toggle_theme, color='primary').classes('theme-btn')
    


    def _create_control_panel(self):
        """创建控制面板"""
        with ui.card().classes('w-full q-pa-lg dashboard-card'):
            with ui.row().classes('items-center justify-between q-mb-md'):
                ui.label('⚙️ 控制面板').classes('text-h6 text-weight-bold')
            
            with ui.row().classes('q-gutter-md'):
                ui.button('📊 导出数据', on_click=self._export_dashboard_data, color='primary').classes('control-btn')
                ui.button('📱 分享仪表板', on_click=self._share_dashboard, color='info').classes('control-btn')
                ui.button('🔄 刷新数据', on_click=self._manual_refresh, color='success').classes('control-btn')
                ui.button('⏸️ 暂停更新', on_click=self._toggle_auto_refresh, color='warning').classes('control-btn')
    


    def _on_symbol_change(self, event):
        """股票代码变更事件"""
        selected_symbol = event.value
        logger.info(f"🔄 切换到股票: {selected_symbol}")
        
        # 更新图表标题
        ui.run_javascript(f'''
        document.getElementById('kline-symbol').textContent = '{selected_symbol} - 股票详情';
        ''')
        
        # 重新加载K线数据
        self._load_kline_data(selected_symbol)
    


    def _change_timeframe(self, timeframe: str):
        """切换K线周期"""
        logger.info(f"🔄 切换K线周期: {timeframe}")
        
        # 更新按钮样式
        for tf, btn in self.timeframe_buttons.items():
            if tf == timeframe:
                btn.classes('kline-timeframe-btn active')
            else:
                btn.classes('kline-timeframe-btn')
        
        # 更新图表
        ui.run_javascript(f'''
        if (window.klineChart) {{
            // 重新配置时间轴
            window.klineChart.createDataSource('xAxis', {{ timeScale: {{ timeVisible: true, secondsVisible: false }} }});
        }}
        if (window.lightweightChart) {{
            window.lightweightChart.timeScale().fitContent();
        }}
        ''')
        
        # 重新加载数据
        self._load_kline_data(self.symbol_selector.value, timeframe)
    


    def _toggle_indicators(self, event):
        """切换技术指标显示"""
        indicator_name = None
        for name, checkbox in self.indicator_checkboxes.items():
            if checkbox is event.sender:
                indicator_name = name
                break
        
        if indicator_name:
            is_checked = event.value
            logger.info(f"{'显示' if is_checked else '隐藏'} {indicator_name.upper()} 指标")
            
            ui.run_javascript(f'''
            // 这里可以添加指标切换逻辑
            console.log('切换指标: {indicator_name}', {is_checked});
            ''')
    


    def _toggle_theme(self):
        """切换主题"""
        self.is_dark_theme = not self.is_dark_theme
        
        if self.is_dark_theme:
            self.theme_icon.set_name('dark_mode')
            theme_color = '#121212'
            text_color = '#ffffff'
        else:
            self.theme_icon.set_name('light_mode')
            theme_color = '#ffffff'
            text_color = '#333333'
        
        ui.run_javascript(f'''
        document.body.style.backgroundColor = '{theme_color}';
        document.body.style.color = '{text_color}';
        ''')
        
        logger.info(f"🔄 切换到{'深色' if self.is_dark_theme else '浅色'}主题")
    


    def _toggle_auto_refresh(self):
        """切换自动刷新"""
        if hasattr(self, '_auto_refresh_enabled'):
            self._auto_refresh_enabled = not self._auto_refresh_enabled
        else:
            self._auto_refresh_enabled = False
        
        status = "开启" if self._auto_refresh_enabled else "关闭"
        ui.notify(f"🔄 自动刷新已{status}", type='info')
        
        logger.info(f"🔄 自动刷新{status}")
    
