#!/usr/bin/env python3
"""Support tests extracted from `scripts/tests/test_tdx_server_config.py`."""

import os
import tempfile
from unittest.mock import patch, mock_open

from src.utils.tdx_server_config import TdxServerConfig


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

        with open(config_file, "w", encoding="utf-8") as file_obj:
            file_obj.write(config_content)

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

        with open(config_file, "w", encoding="gbk") as file_obj:
            file_obj.write(config_content)

        config = TdxServerConfig(config_file)
        assert len(config.servers) == 1
        assert config.servers[0] == ("101.227.73.20", 7709, "默认服务器")

    def test_extremely_large_host_num(self):
        """测试极大的HostNum值"""
        config_file = os.path.join(self.temp_dir, "large_host_num.cfg")
        config_content = """[HQHOST]
HostNum=99999
PrimaryHost=1
HostName01=唯一服务器
IPAddress01=192.168.1.100
Port01=7709
"""

        with open(config_file, "w", encoding="gbk") as file_obj:
            file_obj.write(config_content)

        config = TdxServerConfig(config_file)
        assert len(config.servers) == 1

    def test_config_file_permission_error(self):
        """测试配置文件权限错误"""
        config_file = os.path.join(self.temp_dir, "protected.cfg")

        with open(config_file, "w") as file_obj:
            file_obj.write("test")

        with patch("builtins.open", side_effect=PermissionError("权限拒绝")):
            config = TdxServerConfig(config_file)
            assert len(config.servers) == 1
            assert config.servers[0] == ("101.227.73.20", 7709, "默认服务器")

    def test_config_file_io_error(self):
        """测试配置文件IO错误"""
        config_file = os.path.join(self.temp_dir, "io_error.cfg")

        with patch("builtins.open", side_effect=IOError("IO错误")):
            config = TdxServerConfig(config_file)
            assert len(config.servers) == 1
            assert config.servers[0] == ("101.227.73.20", 7709, "默认服务器")

    def test_server_name_with_special_characters(self):
        """测试包含特殊字符的服务器名称"""
        config_file = os.path.join(self.temp_dir, "special_chars.cfg")
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

        with open(config_file, "w", encoding="gbk") as file_obj:
            file_obj.write(config_content)

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

        with open(config_file, "w", encoding="gbk") as file_obj:
            file_obj.write(config_content)

        config = TdxServerConfig(config_file)

        assert len(config.servers) == 2
        assert config.servers[0][0] == "192.168.1.100"
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

        with open(config_file, "w", encoding="gbk") as file_obj:
            file_obj.write(real_world_config)

        config = TdxServerConfig(config_file)

        assert len(config.servers) == 5
        assert config.primary_index == 0

        primary_host, primary_port = config.get_primary_server()
        assert primary_host == "58.246.109.27"
        assert primary_port == 7709

        failover_servers = config.get_failover_servers(max_count=3)
        assert len(failover_servers) == 3
        assert failover_servers[0] == (primary_host, primary_port)

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

        with open(config_file, "w", encoding="gbk") as file_obj:
            file_obj.write(config_content)

        config = TdxServerConfig(config_file)
        failover_servers = config.get_failover_servers(max_count=4)

        connection_attempts = []
        for host, port in failover_servers:
            connection_attempts.append(f"尝试连接 {host}:{port}")
            if port == 7712:
                connection_attempts.append("连接成功！")
                break
            connection_attempts.append("连接失败，尝试下一个...")

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

        with open(config_file, "w", encoding="gbk") as file_obj:
            file_obj.write(config_content)

        config = TdxServerConfig(config_file)

        client_assignments = []
        for client_id in range(10):
            server = config.get_random_server()
            client_assignments.append(f"客户端{client_id} -> {server[0]}:{server[1]}")

        unique_servers = set()
        for assignment in client_assignments:
            ip = assignment.split(" -> ")[1].split(":")[0]
            unique_servers.add(ip)

        assert len(unique_servers) >= 1
        assert all(ip in ["192.168.1.100", "192.168.1.101", "192.168.1.102"] for ip in unique_servers)

    def test_configuration_validation_workflow(self):
        """测试配置验证工作流"""
        config_file = os.path.join(self.temp_dir, "validation_test.cfg")
        test_cases = [
            ("", 0, 0),
            ("[OTHER]\nHostNum=1", 0, 0),
            ("[HQHOST]\nHostNum=invalid\nPrimaryHost=1", 0, 0),
            (
                "[HQHOST]\nHostNum=1\nPrimaryHost=1\nHostName01=测试\nIPAddress01=1.1.1.1\nPort01=7709",
                1,
                7709,
            ),
        ]

        for index, (config_content, expected_servers, expected_port) in enumerate(test_cases):
            test_file = os.path.join(self.temp_dir, f"test_{index}.cfg")
            with open(test_file, "w", encoding="gbk") as file_obj:
                file_obj.write(config_content)

            config = TdxServerConfig(test_file)

            if expected_servers == 0:
                assert len(config.servers) == 1
                assert config.servers[0] == ("101.227.73.20", 7709, "默认服务器")
            else:
                assert len(config.servers) == expected_servers
                _, port = config.get_primary_server()
                assert port == expected_port

    def test_environment_integration_workflow(self):
        """测试环境集成工作流"""
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

        with open(config_file, "w", encoding="gbk") as file_obj:
            file_obj.write(config_content)

        with patch.dict(os.environ, {"TDX_PATH": tdx_path}):
            config = TdxServerConfig()

            assert config.config_file == config_file
            assert len(config.servers) == 1
            assert config.servers[0] == ("10.0.0.100", 7709, "环境测试服务器")
