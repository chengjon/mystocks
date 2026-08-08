"""结果存储模块"""

import json
import os
from datetime import datetime
from typing import List
from .models import FileInventoryRecord, ScanSummary, ValidationResult


class ResultStorage:
    """扫描结果存储"""

    def __init__(self, output_dir: str = "data/code_inventory"):
        """初始化
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

    def save_inventory(self, records: List[FileInventoryRecord], filename: str = "inventory.json") -> str:
        """保存详细登记记录
        
        Args:
            records: 登记记录列表
            filename: 文件名
            
        Returns:
            保存的文件路径
        """
        filepath = os.path.join(self.output_dir, filename)

        data = {
            "generated_at": datetime.now().isoformat(),
            "records": [r.to_dict() for r in records]
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return filepath

    def save_summary(self, summary: ScanSummary, filename: str = "summary.json") -> str:
        """保存扫描摘要
        
        Args:
            summary: 扫描摘要
            filename: 文件名
            
        Returns:
            保存的文件路径
        """
        filepath = os.path.join(self.output_dir, filename)

        data = {
            "generated_at": datetime.now().isoformat(),
            "summary": summary.to_dict()
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return filepath

    def save_validation(self, result: ValidationResult, filename: str = "validation.json") -> str:
        """保存验证结果
        
        Args:
            result: 验证结果
            filename: 文件名
            
        Returns:
            保存的文件路径
        """
        filepath = os.path.join(self.output_dir, filename)

        data = {
            "validated_at": datetime.now().isoformat(),
            "result": result.to_dict()
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return filepath

    def save_violations(self, records: List[FileInventoryRecord], filename: str = "violations.json") -> str:
        """保存违规记录
        
        Args:
            records: 登记记录列表
            filename: 文件名
            
        Returns:
            保存的文件路径
        """
        # 筛选出违规记录（超过阈值或使用Mock）
        violations = [
            r.to_dict() for r in records
            if r.is_over_threshold or r.uses_mock_data
        ]

        filepath = os.path.join(self.output_dir, filename)

        data = {
            "generated_at": datetime.now().isoformat(),
            "total_violations": len(violations),
            "violations": violations
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return filepath

    def load_inventory(self, filename: str = "inventory.json") -> List[FileInventoryRecord]:
        """加载登记记录
        
        Args:
            filename: 文件名
            
        Returns:
            登记记录列表
        """
        filepath = os.path.join(self.output_dir, filename)

        if not os.path.exists(filepath):
            return []

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [FileInventoryRecord.from_dict(r) for r in data.get("records", [])]

    def get_output_dir(self) -> str:
        """获取输出目录
        
        Returns:
            输出目录路径
        """
        return self.output_dir
