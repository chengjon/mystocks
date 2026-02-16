"""test_dashboard 拆分包"""
from .dashboard_widget_type import DashboardWidgetType  # noqa: F401
from .dashboard_widget_type import DashboardMetric  # noqa: F401
from .dashboard_widget_type import TestExecutionStatus  # noqa: F401
from .dashboard_widget_type import AlertConfig  # noqa: F401
from .dashboard_widget_type import TestDashboard  # noqa: F401
from .create_dashboard_templates import create_dashboard_templates  # noqa: F401
from .create_dashboard_templates import demo_test_dashboard  # noqa: F401

__all__ = ['DashboardWidgetType', 'DashboardMetric', 'TestExecutionStatus', 'AlertConfig', 'TestDashboard', 'create_dashboard_templates', 'demo_test_dashboard']
