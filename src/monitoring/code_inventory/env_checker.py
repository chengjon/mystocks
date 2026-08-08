"""环境配置检查器"""

import os
from .models import EnvConfigInfo, ValidationResult


class EnvConfigChecker:
    """环境配置检查器"""

    def __init__(self, env_file: str = ".env"):
        """初始化
        
        Args:
            env_file: .env文件路径
        """
        self.env_file = env_file

    def load_env_config(self, project_root: str = ".") -> EnvConfigInfo:
        """加载环境配置
        
        Args:
            project_root: 项目根目录
            
        Returns:
            环境配置信息
        """
        result = EnvConfigInfo()

        env_path = os.path.join(project_root, self.env_file)

        if not os.path.exists(env_path):
            result.issues.append(f"配置文件 {self.env_file} 不存在")
            result.is_valid = False
            return result

        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # 跳过注释和空行
                    if not line or line.startswith("#"):
                        continue

                    # 解析 key=value 格式
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip("\"'")

                        if key == "USE_MOCK_DATA":
                            result.use_mock_data = value.lower() in ("true", "1", "yes")
                        elif key == "DATA_SOURCE":
                            result.data_source = value.lower()

        except Exception as e:
            result.issues.append(f"读取配置文件失败: {str(e)}")
            result.is_valid = False

        return result

    def validate_real_mode(self, project_root: str = ".") -> ValidationResult:
        """验证REAL模式合规性
        
        Args:
            project_root: 项目根目录
            
        Returns:
            验证结果
        """
        result = ValidationResult()
        result.mode = "REAL"

        config = self.load_env_config(project_root)

        # 检查是否启用Mock
        if config.use_mock_data:
            result.is_valid = False
            result.violations.append({
                "type": "mock_enabled",
                "message": "USE_MOCK_DATA 已启用，不符合 REAL 模式要求",
                "severity": "error"
            })

        # 检查数据源配置
        if config.data_source == "mock":
            result.is_valid = False
            result.violations.append({
                "type": "mock_datasource",
                "message": "DATA_SOURCE 设置为 mock，不符合 REAL 模式要求",
                "severity": "error"
            })

        # 添加配置信息
        result.config = config.to_dict()

        return result

    def check_current_mode(self, project_root: str = ".") -> str:
        """检查当前模式
        
        Args:
            project_root: 项目根目录
            
        Returns:
            "REAL" 或 "MOCK"
        """
        config = self.load_env_config(project_root)

        if config.use_mock_data or config.data_source == "mock":
            return "MOCK"

        return "Real"
