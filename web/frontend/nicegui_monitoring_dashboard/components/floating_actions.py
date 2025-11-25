# 浮动操作按钮功能


浮动操作按钮功能


    def _create_floating_actions(self):
        """创建浮动操作按钮"""
        with ui.row().classes('floating-action'):
            ui.button('📈', on_click=self._scroll_to_kline, color='transparent').classes('fab-btn')
        
        # 浮动按钮样式
        ui.add_head_html('''
        <style>
        .floating-action {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 1000;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            background: var(--primary-color);
            color: white;
            border: none;
            box-shadow: 0 10px 15px rgba(0,0,0,0.1);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }
        .floating-action:hover {
            transform: scale(1.1);
            background: var(--info-color);
        }
        .fab-btn {
            font-size: 24px !important;
            color: white !important;
        }
        </style>
        ''')
    
