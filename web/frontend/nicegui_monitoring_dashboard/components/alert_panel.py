import logging
from nicegui import ui

logger = logging.getLogger(__name__)

# 告警面板功能


def _create_alert_panel(self):
    """创建告警面板"""
    with ui.card().classes("w-full q-pa-lg dashboard-card"):
        with ui.row().classes("items-center justify-between q-mb-md"):
            ui.label("🚨 实时告警").classes("text-h6 text-weight-bold")
            with ui.row().classes("items-center q-gutter-sm"):
                ui.button("清除全部", on_click=self._clear_all_alerts, color="red", size="sm").classes("control-btn")
                ui.button("设置", on_click=self._show_alert_settings, color="orange", size="sm").classes("control-btn")

        # 告警列表
        self.alert_list = ui.column().classes("q-gutter-sm")


def _clear_all_alerts(self):
    """清除所有告警"""
    self.alert_manager.clear_all_alerts()
    ui.notify("✅ 所有告警已清除", type="success")
    logger.info("🧹 所有告警已清除")


def _show_alert_settings(self):
    """显示告警设置"""
    with ui.dialog() as dialog, ui.card():
        ui.label("告警设置").classes("text-h6 text-weight-bold q-mb-md")

        with ui.column().classes("q-gutter-md"):
            ui.checkbox("启用邮件告警", value=True)
            ui.checkbox("启用声音告警", value=False)
            ui.checkbox("启用浏览器通知", value=True)

            ui.label("告警阈值设置").classes("text-subtitle1")
            ui.slider(min=0, max=100, value=80, step=5).props("label-always")
            ui.label("CPU使用率阈值 (%)")

            ui.slider(min=0, max=100, value=90, step=5).props("label-always")
            ui.label("GPU使用率阈值 (%)")

        with ui.row().classes("q-mt-lg justify-end"):
            ui.button("取消", on_click=dialog.close).classes("q-mr-sm")
            ui.button("保存", on_click=dialog.close, color="primary")
