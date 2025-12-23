"""
页面对象模型 (Page Object Model - POM)

提供所有页面的对象定义和交互方法
"""

from .base_page import BasePage
from .login_page import LoginPage
from .dashboard_page import DashboardPage
from .data_table_page import DataTablePage
from .search_page import SearchPage

__all__ = [
    "BasePage",
    "LoginPage",
    "DashboardPage",
    "DataTablePage",
    "SearchPage",
]
