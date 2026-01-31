# -*- coding: utf-8 -*-
"""
TDX配置管理模块
基于PyTDX配置管理器，适配MyStocks项目

@author: MyStocks Project
@version: 1.0
@created: 2026-01-02
"""

import configparser
import os
from pathlib import Path
from typing import Dict, List, Tuple


class TdxConfigManager:
    """
    TDX配置管理器

    管理TDX数据源的所有配置参数，包括：
    - 本地通达信路径和端口
    - 网络服务器列表（备用）
    - 连接超时和重试参数
    - 数据验证参数
    """


    def __init__(self, config_file: str = None):
        """
        初始化配置管理器

        Args:
            config_file: 配置文件路径，默认为 config/tdx_settings.conf
        """
        if config_file is None:
            # 默认配置文件路径
            project_root = Path(__file__).parent.parent.parent.parent
            config_file = project_root / "config" / "tdx_settings.conf"

        self.config_file = str(config_file)
        self.config = configparser.ConfigParser()
        self.load_config()


    def load_config(self) -> None:
        """
        加载配置文件

        如果配置文件不存在，则创建默认配置文件。
        """
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding="utf-8")
        else:
            logger.warning("配置文件不存在: {self.config_file")
            self._create_default_config()


    def _create_default_config(self):
        """创建默认配置文件"""
        # 创建默认配置节
        self.config["TDX"] = {
            "install_path": os.getenv("TDX_DATA_PATH", "D:\\ProgramData\\tdx_new"),
            "exe_name": "TdxW.exe",
            "local_host": "127.0.0.1",
            "local_port": "7709",
        }

        self.config["SERVER"] = {
            "network_servers": "180.153.18.170:7709,101.227.73.20:7709,119.147.212.81:7709,114.80.63.12:7709"
        }

        self.config["PERFORMANCE"] = {
            "connect_timeout": "5",
            "api_timeout": "30",
            "retry_count": "3",
            "heartbeat_enabled": "false",
            "auto_retry_enabled": "true",
        }

        self.config["VALIDATION"] = {
            "max_sh_stocks": "30000",
            "max_sz_stocks": "25000",
            "min_stock_price": "0.01",
            "max_stock_price": "10000.0",
        }

        # 保存默认配置
        self._save_config()


    def _save_config(self):
        """保存配置文件"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            self.config.write(f)
        logger.info("已创建默认配置文件: {self.config_file")


    def get(self, section: str, key: str, fallback=None):
        """获取配置值"""
        return self.config.get(section, key, fallback=fallback)


    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        """获取整数配置值"""
        return self.config.getint(section, key, fallback=fallback)


    def get_float(self, section: str, key: str, fallback: float = 0.0) -> float:
        """获取浮点数配置值"""
        return self.config.getfloat(section, key, fallback=fallback)


    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """获取布尔配置值"""
        return self.config.getboolean(section, key, fallback=fallback)


    def get_list(self, section: str, key: str, fallback: List[str] = None, separator: str = ",") -> List[str]:
        """获取列表配置值"""
        value = self.config.get(section, key, fallback=fallback)
        if value is None:
            return fallback or []
        return [item.strip() for item in value.split(separator) if item.strip()]


    def get_server_list(self) -> List[Tuple[str, int]]:
        """
        获取服务器列表（本地优先 + 网络备用）

        Returns:
            [(主机, 端口), ...] 格式的服务器列表
        """
        servers = []

        # 先添加本地服务器
        local_host = self.get("TDX", "local_host", "127.0.0.1")
        local_port = self.get_int("TDX", "local_port", 7709)
        servers.append((local_host, local_port))

        # 添加网络服务器作为备用
        network_servers = self.get("SERVER", "network_servers", "")
        for server in network_servers.split(","):
            server = server.strip()
            if ":" in server:
                host, port = server.rsplit(":", 1)
                try:
                    servers.append((host, int(port)))
                except ValueError:
                    continue

        return servers

    def get_tdx_path(self) -> str:
        """
        获取通达信安装路径

        Returns:
            通达信安装路径（从环境变量或配置文件）
        """
        # 优先使用环境变量
        env_path = os.getenv("TDX_DATA_PATH")
        if env_path:
            return env_path

        # 否则使用配置文件
        return self.get("TDX", "install_path", "D:\\ProgramData\\tdx_new")

    def get_performance_config(self) -> Dict[str, any]:
        """获取性能配置"""
        return {
            "connect_timeout": self.get_int("PERFORMANCE", "connect_timeout", 5),
            "api_timeout": self.get_int("PERFORMANCE", "api_timeout", 30),
            "retry_count": self.get_int("PERFORMANCE", "retry_count", 3),
            "heartbeat_enabled": self.get_bool("PERFORMANCE", "heartbeat_enabled", False),
            "auto_retry_enabled": self.get_bool("PERFORMANCE", "auto_retry_enabled", True),
        }


# 全局配置实例
tdx_config = TdxConfigManager()


def get_tdx_config() -> TdxConfigManager:
    """获取全局TDX配置实例"""
    return tdx_config


def get_tdx_server_list() -> List[Tuple[str, int]]:
    """获取TDX服务器列表"""
    return tdx_config.get_server_list()


def get_tdx_path() -> str:
    """获取通达信安装路径（便利函数）"""
    return tdx_config.get_tdx_path()


# 临时导入logger（后续会从loguru导入）
try:
    from loguru import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


if __name__ == "__main__":
    # 测试配置加载
    print("=== TDX配置管理器测试 ===")
    print(f"配置文件路径: {tdx_config.config_file}")
    print(f"文件是否存在: {os.path.exists(tdx_config.config_file)}")

    print("\n服务器列表:")
    for host, port in get_tdx_server_list():
        print(f"  {host}:{port}")

    print(f"\n通达信路径: {get_tdx_path()}")

    perf_config = tdx_config.get_performance_config()
    print(f"\n性能配置: {perf_config}")
