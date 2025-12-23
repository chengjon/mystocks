#!/usr/bin/env python3
"""
TDX服务器配置模块测试套件
基于Phase 6成功模式：功能→边界→异常→性能→集成测试
"""

import sys
import os
import tempfile
import configparser
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import pytest

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入被测试的模块
from src.utils.tdx_server_config import TdxServerConfig, get_global_config


class TestTdxServerConfigInit:
    """TdxServerConfig初始化测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        # 清理临时目录
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_init_with_default_path(self):
        """测试使用默认路径初始化"""
        config = TdxServerConfig()
        assert config.config_file is not None
        assert isinstance(config.servers, list)
        assert isinstance(config.primary_index, int)

    def test_init_with_custom_path(self):
        """测试使用自定义路径初始化"""
        custom_path = os.path.join(self.temp_dir, "custom_connect.cfg")
        config = TdxServerConfig(custom_path)
        assert config.config_file == custom_path

    def test_init_with_tdx_path_env(self):
        """测试使用TDX_PATH环境变量"""
        tdx_path = os.path.join(self.temp_dir, "tdx")
        os.makedirs(tdx_path, exist_ok=True)

        with patch.dict(os.environ, {"TDX_PATH": tdx_path}):
            config = TdxServerConfig()
            expected_path = os.path.join(tdx_path, "connect.cfg")
            assert config.config_file == expected_path

    def test_init_without_tdx_path_env(self):
        """测试没有TDX_PATH环境变量时的默认路径"""
        # 确保TDX_PATH不存在
        env_backup = os.environ.get("TDX_PATH")
        if "TDX_PATH" in os.environ:
            del os.environ["TDX_PATH"]

        try:
            config = TdxServerConfig()
            # 应该使用默认项目路径
            assert config.config_file.endswith("connect.cfg")
            assert "temp" in config.config_file
        finally:
            # 恢复环境变量
            if env_backup:
                os.environ["TDX_PATH"] = env_backup

    def test_init_logger_setup(self):
        """测试日志器设置"""
        config = TdxServerConfig()
        assert config.logger is not None
        assert config.logger.name == "src.utils.tdx_server_config"

    def test_init_defaults(self):
        """测试初始化默认值"""
        # 使用不存在的文件，避免加载配置
        config = TdxServerConfig("/nonexistent/file.cfg")
        assert config.servers == [
            ("101.227.73.20", 7709, "默认服务器")
        ]  # 加载后的默认值
        assert config.primary_index == 0


class TestLoadConfig:
    """配置加载功能测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "connect.cfg")

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_load_nonexistent_file(self):
        """测试加载不存在的配置文件"""
        config = TdxServerConfig(self.config_file)

        # 应该使用默认服务器
        assert len(config.servers) == 1
        assert config.servers[0] == ("101.227.73.20", 7709, "默认服务器")
        assert config.primary_index == 0

    def test_load_valid_config_gbk_encoding(self):
        """测试加载有效的GBK编码配置文件"""
        # 创建有效的配置文件内容
        config_content = """[HQHOST]
HostNum=3
PrimaryHost=2
HostName01=主服务器
IPAddress01=192.168.1.100
Port01=7709
HostName02=备用服务器1
IPAddress02=192.168.1.101
Port02=7710
HostName03=备用服务器2
IPAddress03=192.168.1.102
Port03=7711
"""

        with open(self.config_file, "w", encoding="gbk") as f:
            f.write(config_content)

        config = TdxServerConfig(self.config_file)

        assert len(config.servers) == 3
        assert config.servers[0] == ("192.168.1.100", 7709, "主服务器")
        assert config.servers[1] == ("192.168.1.101", 7710, "备用服务器1")
        assert config.servers[2] == ("192.168.1.102", 7711, "备用服务器2")
        assert config.primary_index == 1  # PrimaryHost=2，所以索引为1

    def test_load_valid_config_utf8_encoding(self):
        """测试加载UTF8编码配置文件（GBK失败后备选）"""
        config_content = """[HQHOST]
HostNum=2
PrimaryHost=1
HostName01=主服务器
IPAddress01=192.168.1.100
Port01=7709
HostName02=备用服务器
IPAddress02=192.168.1.101
Port02=7710
"""

        with open(self.config_file, "w", encoding="utf-8") as f:
            f.write(config_content)

        with patch(
            "builtins.open",
            side_effect=[
                # 第一次GBK读取失败
                UnicodeDecodeError("gbk", b"", 0, 1, "invalid start byte"),
                # 第二次UTF8成功
                mock_open(read_data=config_content)(self.config_file, "r"),
            ],
        ):
            config = TdxServerConfig(self.config_file)
            assert len(config.servers) == 2

    def test_load_config_missing_hqhost_section(self):
        """测试配置文件缺少HQHOST部分"""
        config_content = """[OTHER_SECTION]
SomeValue=123
"""
        with open(self.config_file, "w", encoding="gbk") as f:
            f.write(config_content)

        config = TdxServerConfig(self.config_file)

        # 应该使用默认服务器
        assert len(config.servers) == 1
        assert config.servers[0] == ("101.227.73.20", 7709, "默认服务器")

    def test_load_config_invalid_host_num(self):
        """测试无效的HostNum值"""
        config_content = """[HQHOST]
HostNum=invalid
PrimaryHost=1
"""
        with open(self.config_file, "w", encoding="gbk") as f:
            f.write(config_content)

        config = TdxServerConfig(self.config_file)

        # 应该使用默认服务器（解析失败）
        assert len(config.servers) == 1
        assert config.servers[0] == ("101.227.73.20", 7709, "默认服务器")

    def test_load_config_missing_primary_host(self):
        """测试缺少PrimaryHost配置"""
        config_content = """[HQHOST]
HostNum=2
HostName01=服务器1
IPAddress01=192.168.1.100
Port01=7709
HostName02=服务器2
IPAddress02=192.168.1.101
Port02=7710
"""
        with open(self.config_file, "w", encoding="gbk") as f:
            f.write(config_content)

        config = TdxServerConfig(self.config_file)

        assert len(config.servers) == 2
        assert config.primary_index == 0  # 默认使用第一个

    def test_load_config_primary_host_out_of_range(self):
        """测试PrimaryHost超出范围"""
        config_content = """[HQHOST]
HostNum=2
PrimaryHost=5
HostName01=服务器1
IPAddress01=192.168.1.100
Port01=7709
HostName02=服务器2
IPAddress02=192.168.1.101
Port02=7710
"""
        with open(self.config_file, "w", encoding="gbk") as f:
            f.write(config_content)

        config = TdxServerConfig(self.config_file)

        assert len(config.servers) == 2
        assert config.primary_index == 0  # 超出范围，使用默认

    def test_load_config_filter_invalid_servers(self):
        """测试过滤无效服务器"""
        config_content = """[HQHOST]
HostNum=4
PrimaryHost=1
HostName01=有效服务器
IPAddress01=192.168.1.100
Port01=7709
HostName02=空IP服务器
IPAddress02=
Port02=7710
HostName03=零端口服务器
IPAddress03=192.168.1.102
Port03=0
HostName04=有效服务器2
IPAddress04=192.168.1.103
Port04=7711
"""
        with open(self.config_file, "w", encoding="gbk") as f:
            f.write(config_content)

        config = TdxServerConfig(self.config_file)

        # 只有2个有效服务器（空IP和端口0的被过滤）
        assert len(config.servers) == 2
        assert config.servers[0] == ("192.168.1.100", 7709, "有效服务器")
        assert config.servers[1] == ("192.168.1.103", 7711, "有效服务器2")

    def test_load_config_exception_handling(self):
        """测试配置加载异常处理"""
        with patch(
            "configparser.ConfigParser.read_file", side_effect=Exception("模拟异常")
        ):
            config = TdxServerConfig(self.config_file)

            # 应该使用默认服务器
            assert len(config.servers) == 1
            assert config.servers[0] == ("101.227.73.20", 7709, "默认服务器")

    def test_load_config_missing_server_info(self):
        """测试服务器信息不完整"""
        config_content = """[HQHOST]
HostNum=2
PrimaryHost=1
HostName01=完整服务器
IPAddress01=192.168.1.100
Port01=7709
HostName02=不完整服务器
# 缺少IPAddress02和Port02
"""
        with open(self.config_file, "w", encoding="gbk") as f:
            f.write(config_content)

        config = TdxServerConfig(self.config_file)

        # 只有1个完整的服务器
        assert len(config.servers) == 1
        assert config.servers[0] == ("192.168.1.100", 7709, "完整服务器")


class TestServerSelectionMethods:
    """服务器选择方法测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "connect.cfg")

        # 创建测试配置
        config_content = """[HQHOST]
HostNum=3
PrimaryHost=2
HostName01=主服务器
IPAddress01=192.168.1.100
Port01=7709
HostName02=首选服务器
IPAddress02=192.168.1.101
Port02=7710
HostName03=备用服务器
IPAddress03=192.168.1.102
Port03=7711
"""
        with open(self.config_file, "w", encoding="gbk") as f:
            f.write(config_content)

        self.config = TdxServerConfig(self.config_file)

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_get_primary_server(self):
        """测试获取主服务器"""
        host, port = self.config.get_primary_server()

        assert host == "192.168.1.101"
        assert port == 7710

    def test_get_primary_server_empty_list(self):
        """测试空服务器列表时获取主服务器"""
        self.config.servers = []
        host, port = self.config.get_primary_server()

        assert host == "101.227.73.20"
        assert port == 7709

    def test_get_random_server(self):
        """测试获取随机服务器"""
        # 多次调用确保随机性
        results = set()
        for _ in range(10):
            host, port = self.config.get_random_server()
            results.add((host, port))

        # 应该有多种结果（因为是随机的）
        assert len(results) >= 1
        # 所有结果应该是有效的服务器
        for host, port in results:
            assert (host, port) in [
                ("192.168.1.100", 7709),
                ("192.168.1.101", 7710),
                ("192.168.1.102", 7711),
            ]

    def test_get_random_server_empty_list(self):
        """测试空服务器列表时获取随机服务器"""
        self.config.servers = []
        host, port = self.config.get_random_server()

        assert host == "101.227.73.20"
        assert port == 7709

    def test_get_all_servers(self):
        """测试获取所有服务器"""
        all_servers = self.config.get_all_servers()

        assert len(all_servers) == 3
        assert all_servers[0] == ("192.168.1.100", 7709, "主服务器")
        assert all_servers[1] == ("192.168.1.101", 7710, "首选服务器")
        assert all_servers[2] == ("192.168.1.102", 7711, "备用服务器")

        # 确保返回的是副本
        all_servers.append(("test", 1234, "test"))
        assert len(self.config.servers) == 3

    def test_get_server_by_index_valid(self):
        """测试根据索引获取服务器（有效索引）"""
        host, port = self.config.get_server_by_index(1)

        assert host == "192.168.1.101"
        assert port == 7710

    def test_get_server_by_index_invalid(self):
        """测试根据索引获取服务器（无效索引）"""
        result = self.config.get_server_by_index(-1)
        assert result is None

        result = self.config.get_server_by_index(10)
        assert result is None

    def test_get_failover_servers_default_count(self):
        """测试获取故障转移服务器（默认数量）"""
        servers = self.config.get_failover_servers()

        # 默认max_count=3，应该返回主服务器+最多2个备用服务器
        assert len(servers) >= 1
        assert len(servers) <= 3
        # 第一个应该是主服务器
        primary_host, primary_port = servers[0]
        assert primary_host == "192.168.1.101"
        assert primary_port == 7710

    def test_get_failover_servers_custom_count(self):
        """测试获取故障转移服务器（自定义数量）"""
        servers = self.config.get_failover_servers(max_count=2)

        assert len(servers) <= 2
        # 第一个应该是主服务器
        assert servers[0] == ("192.168.1.101", 7710)

    def test_get_failover_servers_single_server(self):
        """测试单个服务器的故障转移列表"""
        self.config.servers = [("192.168.1.100", 7709, "唯一服务器")]
        self.config.primary_index = 0

        servers = self.config.get_failover_servers(max_count=3)

        assert len(servers) == 1
        assert servers[0] == ("192.168.1.100", 7709)

    def test_get_failover_servers_empty_list(self):
        """测试空服务器列表的故障转移"""
        self.config.servers = []

        servers = self.config.get_failover_servers()

        assert len(servers) == 1
        assert servers[0] == ("101.227.73.20", 7709)

    def test_get_server_count(self):
        """测试获取服务器数量"""
        count = self.config.get_server_count()
        assert count == 3

        self.config.servers = [("test", 1234, "test")]
        count = self.config.get_server_count()
        assert count == 1

        self.config.servers = []
        count = self.config.get_server_count()
        assert count == 0


class TestStringRepresentation:
    """字符串表示测试类"""

    def test_str_representation_with_servers(self):
        """测试有服务器时的字符串表示"""
        temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(temp_dir, "connect.cfg")

        try:
            config_content = """[HQHOST]
HostNum=2
PrimaryHost=1
HostName01=主服务器
IPAddress01=192.168.1.100
Port01=7709
HostName02=备用服务器
IPAddress02=192.168.1.101
Port02=7710
"""
            with open(config_file, "w", encoding="gbk") as f:
                f.write(config_content)

            config = TdxServerConfig(config_file)
            str_repr = str(config)

            assert "TdxServerConfig" in str_repr
            assert "2个服务器" in str_repr
            assert "主服务器" in str_repr
            assert "192.168.1.100:7709" in str_repr

        finally:
            import shutil

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def test_str_representation_empty_servers(self):
        """测试无服务器时的字符串表示"""
        config = TdxServerConfig("nonexistent_file.cfg")
        config.servers = []  # 强制设为空

        str_repr = str(config)
        assert str_repr == "TdxServerConfig: 无可用服务器"


class TestGlobalConfig:
    """全局配置测试类"""

    def test_get_global_config_singleton(self):
        """测试全局配置单例"""
        config1 = get_global_config()
        config2 = get_global_config()

        assert config1 is config2
        assert isinstance(config1, TdxServerConfig)

    def test_get_global_config_initialization(self):
        """测试全局配置初始化"""
        # 清除全局变量
        import src.utils.tdx_server_config

        src.utils.tdx_server_config._global_config = None

        config = get_global_config()
        assert isinstance(config, TdxServerConfig)
        assert config.servers is not None


class TestEdgeCasesAndErrorHandling:
    """边界条件和错误处理测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_config_file_with_unicode_content(self):
        """测试包含Unicode内容的配置文件"""
        config_file = os.path.join(self.temp_dir, "unicode_config.cfg")
        config_content = """[HQHOST]
HostNum=1
PrimaryHost=1
HostName01=测试🚀服务器
IPAddress01=192.168.1.100
Port01=7709
"""

        # 先用UTF8写入，然后用GBK方式读取（会失败，然后用UTF8重试）
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(config_content)

        with patch(
            "builtins.open",
            side_effect=[
                UnicodeDecodeError("gbk", b"", 0, 1, "invalid start byte"),
                mock_open(read_data=config_content)(config_file, "r"),
            ],
        ):
            config = TdxServerConfig(config_file)
            assert len(config.servers) == 1
            assert config.servers[0][2] == "测试🚀服务器"

    def test_malformed_port_values(self):
        """测试格式错误的端口值"""
        config_file = os.path.join(self.temp_dir, "malformed_port.cfg")
        config_content = """[HQHOST]
HostNum=2
PrimaryHost=1
HostName01=正常服务器
IPAddress01=192.168.1.100
Port01=7709
HostName02=格式错误服务器
IPAddress02=192.168.1.101
Port02=invalid_port
"""

        with open(config_file, "w", encoding="gbk") as f:
            f.write(config_content)

        config = TdxServerConfig(config_file)

        # 解析失败，使用默认服务器
        assert len(config.servers) == 1
        assert config.servers[0] == ("101.227.73.20", 7709, "默认服务器")

    def test_extremely_large_host_num(self):
        """测试极大的HostNum值"""
        config_file = os.path.join(self.temp_dir, "large_host_num.cfg")
        config_content = f"""[HQHOST]
HostNum=99999
PrimaryHost=1
HostName01=唯一服务器
IPAddress01=192.168.1.100
Port01=7709
"""

        with open(config_file, "w", encoding="gbk") as f:
            f.write(config_content)

        config = TdxServerConfig(config_file)

        # 只有实际配置的服务器会被添加
        assert len(config.servers) == 1

    def test_config_file_permission_error(self):
        """测试配置文件权限错误"""
        config_file = os.path.join(self.temp_dir, "protected.cfg")

        # 创建文件
        with open(config_file, "w") as f:
            f.write("test")

        # 模拟权限错误
        with patch("builtins.open", side_effect=PermissionError("权限拒绝")):
            config = TdxServerConfig(config_file)

            # 应该使用默认服务器
            assert len(config.servers) == 1
            assert config.servers[0] == ("101.227.73.20", 7709, "默认服务器")

    def test_config_file_io_error(self):
        """测试配置文件IO错误"""
        config_file = os.path.join(self.temp_dir, "io_error.cfg")

        with patch("builtins.open", side_effect=IOError("IO错误")):
            config = TdxServerConfig(config_file)

            # 应该使用默认服务器
            assert len(config.servers) == 1
            assert config.servers[0] == ("101.227.73.20", 7709, "默认服务器")

    def test_server_name_with_special_characters(self):
        """测试包含特殊字符的服务器名称"""
        config_file = os.path.join(self.temp_dir, "special_chars.cfg")
        # 注意：configparser中的%字符有特殊含义，需要转义
        config_content = """[HQHOST]
HostNum=2
PrimaryHost=1
HostName01=服务器&特殊字符@#%%
IPAddress01=192.168.1.100
Port01=7709
HostName02=服务器"引号'单引号
IPAddress02=192.168.1.101
Port02=7710
"""

        with open(config_file, "w", encoding="gbk") as f:
            f.write(config_content)

        config = TdxServerConfig(config_file)

        assert len(config.servers) == 2
        assert config.servers[0][2] == "服务器&特殊字符@#%"
        assert config.servers[1][2] == "服务器\"引号'单引号"

    def test_host_ip_with_whitespace(self):
        """测试IP地址包含空白字符"""
        config_file = os.path.join(self.temp_dir, "whitespace_ip.cfg")
        config_content = """[HQHOST]
HostNum=2
PrimaryHost=1
HostName01=空白IP服务器
IPAddress01=  192.168.1.100
Port01= 7709
HostName02=正常服务器
IPAddress02=192.168.1.101
Port02=7710
"""

        with open(config_file, "w", encoding="gbk") as f:
            f.write(config_content)

        config = TdxServerConfig(config_file)

        assert len(config.servers) == 2
        assert config.servers[0][0] == "192.168.1.100"  # 空白被去除
        assert config.servers[0][1] == 7709
        assert config.servers[1][0] == "192.168.1.101"


class TestIntegrationScenarios:
    """集成场景测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_real_world_config_parsing_workflow(self):
        """测试真实世界配置解析工作流"""
        # 创建模拟的TDX connect.cfg文件
        config_file = os.path.join(self.temp_dir, "connect.cfg")
        real_world_config = """; 通达信配置文件
[HQHOST]
HostNum=5
PrimaryHost=1
HostName01=上海电信1
IPAddress01=58.246.109.27
Port01=7709
HostName02=上海电信2
IPAddress02=58.246.109.28
Port02=7709
HostName03=上海联通
IPAddress03=218.75.126.9
Port03=7709
HostName04=北京电信
IPAddress04=202.108.253.130
Port04=7709
HostName05=北京联通
IPAddress05=123.125.104.241
Port05=7709
"""

        with open(config_file, "w", encoding="gbk") as f:
            f.write(real_world_config)

        # 创建配置实例
        config = TdxServerConfig(config_file)

        # 验证解析结果
        assert len(config.servers) == 5
        assert config.primary_index == 0  # PrimaryHost=1

        # 测试各种服务器选择方法
        primary_host, primary_port = config.get_primary_server()
        assert primary_host == "58.246.109.27"
        assert primary_port == 7709

        # 测试故障转移
        failover_servers = config.get_failover_servers(max_count=3)
        assert len(failover_servers) == 3
        assert failover_servers[0] == (primary_host, primary_port)

        # 测试随机选择
        random_host, random_port = config.get_random_server()
        assert random_port == 7709
        assert random_host in [
            "58.246.109.27",
            "58.246.109.28",
            "218.75.126.9",
            "202.108.253.130",
            "123.125.104.241",
        ]

    def test_failover_simulation_workflow(self):
        """测试故障转移模拟工作流"""
        config_file = os.path.join(self.temp_dir, "failover_test.cfg")
        config_content = """[HQHOST]
HostNum=4
PrimaryHost=1
HostName01=主服务器
IPAddress01=192.168.1.100
Port01=7709
HostName02=备用1
IPAddress02=192.168.1.101
Port02=7710
HostName03=备用2
IPAddress03=192.168.1.102
Port03=7711
HostName04=备用3
IPAddress04=192.168.1.103
Port04=7712
"""

        with open(config_file, "w", encoding="gbk") as f:
            f.write(config_content)

        config = TdxServerConfig(config_file)

        # 模拟连接失败，尝试故障转移
        failover_servers = config.get_failover_servers(max_count=4)

        connection_attempts = []
        for host, port in failover_servers:
            connection_attempts.append(f"尝试连接 {host}:{port}")
            # 模拟前3个失败，第4个成功
            if port == 7712:
                connection_attempts.append("连接成功！")
                break
            connection_attempts.append("连接失败，尝试下一个...")

        # 验证故障转移逻辑
        assert any("192.168.1.100:7709" in attempt for attempt in connection_attempts)
        assert any("192.168.1.103:7712" in attempt for attempt in connection_attempts)
        assert "连接成功！" in connection_attempts[-1]

    def test_load_balancing_workflow(self):
        """测试负载均衡工作流"""
        config_file = os.path.join(self.temp_dir, "load_balance.cfg")
        config_content = """[HQHOST]
HostNum=3
PrimaryHost=1
HostName01=服务器1
IPAddress01=192.168.1.100
Port01=7709
HostName02=服务器2
IPAddress02=192.168.1.101
Port02=7709
HostName03=服务器3
IPAddress03=192.168.1.102
Port03=7709
"""

        with open(config_file, "w", encoding="gbk") as f:
            f.write(config_content)

        config = TdxServerConfig(config_file)

        # 模拟多个客户端连接
        client_assignments = []
        for client_id in range(10):
            server = config.get_random_server()
            client_assignments.append(f"客户端{client_id} -> {server[0]}:{server[1]}")

        # 验证负载分散
        unique_servers = set()
        for assignment in client_assignments:
            # 提取服务器IP
            ip = assignment.split(" -> ")[1].split(":")[0]
            unique_servers.add(ip)

        # 应该使用多个服务器（负载分散）
        assert len(unique_servers) >= 1
        assert all(
            ip in ["192.168.1.100", "192.168.1.101", "192.168.1.102"]
            for ip in unique_servers
        )

    def test_configuration_validation_workflow(self):
        """测试配置验证工作流"""
        config_file = os.path.join(self.temp_dir, "validation_test.cfg")

        # 测试各种配置问题
        test_cases = [
            # 空文件
            ("", 0, 0),
            # 缺少HQHOST
            ("[OTHER]\nHostNum=1", 0, 0),
            # 无效HostNum
            ("[HQHOST]\nHostNum=invalid\nPrimaryHost=1", 0, 0),
            # 有效配置
            (
                "[HQHOST]\nHostNum=1\nPrimaryHost=1\nHostName01=测试\nIPAddress01=1.1.1.1\nPort01=7709",
                1,
                7709,
            ),
        ]

        for i, (config_content, expected_servers, expected_port) in enumerate(
            test_cases
        ):
            test_file = os.path.join(self.temp_dir, f"test_{i}.cfg")
            with open(test_file, "w", encoding="gbk") as f:
                f.write(config_content)

            config = TdxServerConfig(test_file)

            if expected_servers == 0:
                # 应该使用默认服务器
                assert len(config.servers) == 1
                assert config.servers[0] == ("101.227.73.20", 7709, "默认服务器")
            else:
                assert len(config.servers) == expected_servers
                host, port = config.get_primary_server()
                assert port == expected_port

    def test_environment_integration_workflow(self):
        """测试环境集成工作流"""
        # 测试TDX_PATH环境变量
        tdx_path = os.path.join(self.temp_dir, "custom_tdx")
        os.makedirs(tdx_path, exist_ok=True)

        config_file = os.path.join(tdx_path, "connect.cfg")
        config_content = """[HQHOST]
HostNum=1
PrimaryHost=1
HostName01=环境测试服务器
IPAddress01=10.0.0.100
Port01=7709
"""

        with open(config_file, "w", encoding="gbk") as f:
            f.write(config_content)

        with patch.dict(os.environ, {"TDX_PATH": tdx_path}):
            config = TdxServerConfig()  # 不指定路径，使用环境变量

            assert config.config_file == config_file
            assert len(config.servers) == 1
            assert config.servers[0] == ("10.0.0.100", 7709, "环境测试服务器")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
