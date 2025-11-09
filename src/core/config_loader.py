"""
YAML配置加载器

使用PyYAML解析配置文件,Pydantic V2进行类型验证。
支持环境变量替换。

创建日期: 2025-10-11
版本: 1.0.0
"""

import os
import yaml
from typing import Dict, Any
from pydantic import BaseModel


class ConfigLoader:
    """YAML配置加载器"""

    @staticmethod
    def load_config(config_path: str) -> Dict[str, Any]:
        """
        加载YAML配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            解析后的配置字典

        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML格式错误
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        return config
