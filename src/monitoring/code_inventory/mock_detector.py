"""Mock数据检测器"""

import re
from typing import List
from .models import MockDetectionResult


class MockDetector:
    """Mock数据检测器"""

    def __init__(self, import_patterns: List[str] = None, call_patterns: List[str] = None):
        """初始化

        Args:
            import_patterns: import导入模式列表
            call_patterns: 函数调用模式列表
        """
        self.import_patterns = import_patterns or []
        self.call_patterns = call_patterns or []

    def detect_file(self, file_path: str) -> MockDetectionResult:
        """检测文件是否使用Mock数据

        Args:
            file_path: 文件路径

        Returns:
            检测结果
        """
        result = MockDetectionResult()

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # 检测import导入
            for pattern in self.import_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    result.has_mock = True
                    result.imports.extend(matches)
                    result.severity = "warning"

            # 检测函数调用
            for pattern in self.call_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    result.has_mock = True
                    result.calls.extend(matches)
                    result.severity = "error"  # 函数调用更严重

            # 去重
            result.imports = list(set(result.imports))
            result.calls = list(set(result.calls))

        except Exception:
            pass

        return result

    def check_content(self, content: str) -> MockDetectionResult:
        """检测代码内容是否使用Mock数据

        Args:
            content: 代码内容

        Returns:
            检测结果
        """
        result = MockDetectionResult()

        # 检测import导入
        for pattern in self.import_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                result.has_mock = True
                result.imports.extend(matches)
                result.severity = "warning"

        # 检测函数调用
        for pattern in self.call_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                result.has_mock = True
                result.calls.extend(matches)
                result.severity = "error"

        # 去重
        result.imports = list(set(result.imports))
        result.calls = list(set(result.calls))

        return result
