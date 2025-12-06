"""
# 功能：TDX服务器配置模块，管理通达信服务器列表和连接参数
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025
"""

import os
import logging
import configparser
from typing import List, Tuple, Optional
import random


class TdxServerConfig:
    """
    TDX服务器配置管理器

    功能:
    - 解析connect.cfg文件提取服务器列表
    - 支持主服务器配置(PrimaryHost)
    - 支持随机服务器选择(负载均衡)
    - 支持故障转移(fallback到备用服务器)

    示例:
        >>> config = TdxServerConfig('/path/to/connect.cfg')
        >>> primary_host, primary_port = config.get_primary_server()
        >>> all_servers = config.get_all_servers()
        >>> random_server = config.get_random_server()
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化TDX服务器配置管理器

        Args:
            config_file: connect.cfg文件路径
                        如果为None,使用项目默认路径: temp/connect.cfg
        """
        self.logger = logging.getLogger(__name__)

        # 默认配置文件路径
        if config_file is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_file = os.path.join(project_root, "temp", "connect.cfg")

        self.config_file = config_file
        self.servers = []  # [(host, port, name), ...]
        self.primary_index = 0  # 主服务器索引

        # 加载配置
        self._load_config()

    def _load_config(self):
        """
        加载并解析connect.cfg文件

        解析[HQHOST]部分:
        - HostNum: 服务器总数
        - PrimaryHost: 主服务器索引(从1开始)
        - HostName##, IPAddress##, Port##: 服务器信息

        编码处理: connect.cfg使用GBK编码(中文Windows默认)
        """
        if not os.path.exists(self.config_file):
            self.logger.warning(
                f"TDX配置文件不存在: {self.config_file}, 使用默认服务器"
            )
            # 使用默认服务器
            self.servers = [("101.227.73.20", 7709, "默认服务器")]
            self.primary_index = 0
            return

        try:
            # 使用GBK编码读取(Windows TDX客户端使用GBK)
            # 如果GBK失败,尝试UTF-8
            config = configparser.ConfigParser()

            try:
                with open(self.config_file, "r", encoding="gbk") as f:
                    config.read_file(f)
            except UnicodeDecodeError:
                self.logger.warning("GBK编码失败,尝试UTF-8编码")
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config.read_file(f)

            # 解析[HQHOST]部分
            if "HQHOST" not in config:
                self.logger.error("配置文件中未找到[HQHOST]部分")
                self.servers = [("101.227.73.20", 7709, "默认服务器")]
                return

            hq_section = config["HQHOST"]

            # 读取服务器总数和主服务器索引
            host_num = int(hq_section.get("HostNum", "0"))
            primary_host = int(hq_section.get("PrimaryHost", "1"))

            self.logger.info(
                f"TDX配置: 共{host_num}个服务器, 主服务器索引={primary_host}"
            )

            # 解析每个服务器
            for i in range(1, host_num + 1):
                host_key = f"IPAddress{i:02d}"
                port_key = f"Port{i:02d}"
                name_key = f"HostName{i:02d}"

                if host_key in hq_section and port_key in hq_section:
                    host = hq_section[host_key].strip()
                    port = int(hq_section[port_key].strip())
                    name = hq_section.get(name_key, f"服务器{i}").strip()

                    # 过滤无效服务器(空IP或端口为0)
                    if host and port > 0:
                        self.servers.append((host, port, name))

            # 设置主服务器索引(注意:配置文件中索引从1开始,Python列表从0开始)
            if 1 <= primary_host <= len(self.servers):
                self.primary_index = primary_host - 1
            else:
                self.primary_index = 0

            self.logger.info(f"成功加载{len(self.servers)}个TDX服务器")
            if self.servers:
                primary = self.servers[self.primary_index]
                self.logger.info(f"主服务器: {primary[2]} ({primary[0]}:{primary[1]})")

        except Exception as e:
            self.logger.error(f"解析TDX配置文件失败: {e}", exc_info=True)
            # 使用默认服务器
            self.servers = [("101.227.73.20", 7709, "默认服务器")]
            self.primary_index = 0

    def get_primary_server(self) -> Tuple[str, int]:
        """
        获取主服务器(根据PrimaryHost配置)

        Returns:
            (host, port) 元组

        Example:
            >>> config = TdxServerConfig()
            >>> host, port = config.get_primary_server()
            >>> print(f"主服务器: {host}:{port}")
        """
        if not self.servers:
            return ("101.227.73.20", 7709)

        host, port, _ = self.servers[self.primary_index]
        return (host, port)

    def get_random_server(self) -> Tuple[str, int]:
        """
        随机选择一个服务器(负载均衡)

        Returns:
            (host, port) 元组

        适用场景:
            - 多个客户端同时连接,分散负载
            - 主服务器繁忙时的备选方案
        """
        if not self.servers:
            return ("101.227.73.20", 7709)

        host, port, _ = random.choice(self.servers)
        return (host, port)

    def get_all_servers(self) -> List[Tuple[str, int, str]]:
        """
        获取所有可用服务器列表

        Returns:
            List of (host, port, name) 元组

        适用场景:
            - 实现自定义负载均衡策略
            - 故障转移(依次尝试所有服务器)
            - 服务器状态监控
        """
        return self.servers.copy()

    def get_server_by_index(self, index: int) -> Optional[Tuple[str, int]]:
        """
        根据索引获取服务器

        Args:
            index: 服务器索引(从0开始)

        Returns:
            (host, port) 元组,如果索引无效返回None
        """
        if 0 <= index < len(self.servers):
            host, port, _ = self.servers[index]
            return (host, port)
        return None

    def get_failover_servers(self, max_count: int = 3) -> List[Tuple[str, int]]:
        """
        获取故障转移服务器列表(主服务器+备用服务器)

        Args:
            max_count: 最多返回的服务器数量(包括主服务器)

        Returns:
            List of (host, port) 元组

        适用场景:
            - 主服务器连接失败时,自动尝试备用服务器
            - 实现重试机制

        策略:
            1. 首先返回主服务器
            2. 然后随机选择其他服务器作为备用

        Example:
            >>> config = TdxServerConfig()
            >>> servers = config.get_failover_servers(max_count=3)
            >>> for host, port in servers:
            >>>     try:
            >>>         connect(host, port)
            >>>         break
            >>>     except:
            >>>         continue  # 尝试下一个服务器
        """
        if not self.servers:
            return [("101.227.73.20", 7709)]

        # 1. 主服务器
        primary = self.servers[self.primary_index]
        result = [(primary[0], primary[1])]

        # 2. 其他服务器(随机选择)
        if len(self.servers) > 1 and max_count > 1:
            # 排除主服务器后的其他服务器
            other_servers = [
                s for i, s in enumerate(self.servers) if i != self.primary_index
            ]

            # 随机打乱顺序
            random.shuffle(other_servers)

            # 取前(max_count - 1)个
            for server in other_servers[: max_count - 1]:
                result.append((server[0], server[1]))

        return result

    def get_server_count(self) -> int:
        """获取可用服务器总数"""
        return len(self.servers)

    def __str__(self):
        """字符串表示"""
        if not self.servers:
            return "TdxServerConfig: 无可用服务器"

        primary = self.servers[self.primary_index]
        return (
            f"TdxServerConfig: {len(self.servers)}个服务器, "
            f"主服务器={primary[2]}({primary[0]}:{primary[1]})"
        )


# 全局单例(可选,避免重复解析配置文件)
_global_config = None


def get_global_config() -> TdxServerConfig:
    """
    获取全局TDX服务器配置单例

    Returns:
        TdxServerConfig单例实例

    示例:
        >>> config = get_global_config()
        >>> host, port = config.get_primary_server()
    """
    global _global_config
    if _global_config is None:
        _global_config = TdxServerConfig()
    return _global_config
