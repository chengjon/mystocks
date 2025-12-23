"""
Data Source Manager Simple Test Suite
数据源管理器简单测试套件

创建日期: 2025-12-20
版本: 1.2.0
测试模块: src.adapters.data_source_manager (352行)
测试重点: 基础功能，避开接口检查问题
"""

import pytest
import sys
import os

# 添加src路径到导入路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))


class TestDataSourceManagerSimple:
    """数据源管理器简单测试 - 避开接口问题"""

    def test_data_source_manager_initialization(self):
        """测试数据源管理器初始化"""
        from adapters.data_source_manager import DataSourceManager

        manager = DataSourceManager()

        # 验证初始状态
        assert hasattr(manager, "_sources")
        assert isinstance(manager._sources, dict)
        assert len(manager._sources) == 0

        # 验证优先级配置
        assert hasattr(manager, "_priority_config")
        assert isinstance(manager._priority_config, dict)
        assert "real_time" in manager._priority_config
        assert "daily" in manager._priority_config
        assert "financial" in manager._priority_config

        # 验证日志器
        assert hasattr(manager, "logger")

    def test_get_source_not_exists(self):
        """测试获取不存在的数据源"""
        from adapters.data_source_manager import DataSourceManager

        manager = DataSourceManager()

        # 获取不存在的数据源
        result = manager.get_source("nonexistent")

        assert result is None

    def test_list_sources_empty(self):
        """测试列出空数据源列表"""
        from adapters.data_source_manager import DataSourceManager

        manager = DataSourceManager()

        # 列出数据源
        sources = manager.list_sources()

        assert isinstance(sources, list)
        assert len(sources) == 0

    def test_get_real_time_data_with_nonexistent_source(self):
        """测试使用不存在的数据源获取实时行情"""
        from adapters.data_source_manager import DataSourceManager

        manager = DataSourceManager()

        # 使用不存在的数据源获取实时行情
        result = manager.get_real_time_data("600519", source="nonexistent")

        # 验证结果
        assert isinstance(result, str)
        assert "不存在" in result

    def test_priority_config_structure(self):
        """测试优先级配置结构"""
        from adapters.data_source_manager import DataSourceManager

        manager = DataSourceManager()

        # 验证配置结构
        assert isinstance(manager._priority_config, dict)
        assert len(manager._priority_config) == 3

        # 验证每个优先级配置
        for key in ["real_time", "daily", "financial"]:
            assert key in manager._priority_config
            assert isinstance(manager._priority_config[key], list)
            assert len(manager._priority_config[key]) > 0

    def test_priority_config_values(self):
        """测试优先级配置值"""
        from adapters.data_source_manager import DataSourceManager

        manager = DataSourceManager()

        # 验证具体配置值
        assert "tdx" in manager._priority_config["real_time"]
        assert "akshare" in manager._priority_config["real_time"]
        assert "tdx" in manager._priority_config["daily"]
        assert "akshare" in manager._priority_config["daily"]
        assert "akshare" in manager._priority_config["financial"]
        assert "tdx" in manager._priority_config["financial"]

    def test_logger_functionality(self):
        """测试日志器功能"""
        from adapters.data_source_manager import DataSourceManager

        manager = DataSourceManager()

        # 验证日志器存在
        assert manager.logger is not None
        assert hasattr(manager.logger, "info")
        assert hasattr(manager.logger, "error")
        assert hasattr(manager.logger, "warning")

    def test_manager_attributes(self):
        """测试管理器属性"""
        from adapters.data_source_manager import DataSourceManager

        manager = DataSourceManager()

        # 验证所有预期属性存在
        expected_attributes = ["_sources", "_priority_config", "logger"]
        for attr in expected_attributes:
            assert hasattr(manager, attr), f"缺少属性: {attr}"

    def test_sources_dict_type(self):
        """测试数据源字典类型"""
        from adapters.data_source_manager import DataSourceManager

        manager = DataSourceManager()

        # 验证_sources是字典类型
        assert isinstance(manager._sources, dict)

    def test_register_source_type_error(self):
        """测试注册错误类型数据源时的异常"""
        from adapters.data_source_manager import DataSourceManager

        manager = DataSourceManager()

        # 尝试注册字符串应该抛出TypeError
        with pytest.raises(TypeError, match="数据源必须实现IDataSource接口"):
            manager.register_source("invalid", "not a data source")

    def test_priority_order(self):
        """测试优先级顺序"""
        from adapters.data_source_manager import DataSourceManager

        manager = DataSourceManager()

        # 验证tdx在优先级列表中排在akshare之前
        real_time_priority = manager._priority_config["real_time"]
        tdx_index = real_time_priority.index("tdx")
        akshare_index = real_time_priority.index("akshare")
        assert tdx_index < akshare_index, "TDX应该比Akshare有更高优先级"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--no-cov"])
