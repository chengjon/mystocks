"""数据模型"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class MockDetectionResult:
    """Mock检测结果"""
    has_mock: bool = False
    imports: List[str] = field(default_factory=list)
    calls: List[str] = field(default_factory=list)
    severity: str = "info"  # "error", "warning", "info"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FileInventoryRecord:
    """文件登记记录"""
    file_path: str
    file_type: str           # .py, .vue, .ts etc.
    line_count: int
    is_over_threshold: bool   # 是否超过行数阈值
    uses_mock_data: bool = False
    mock_imports: List[str] = field(default_factory=list)
    mock_calls: List[str] = field(default_factory=list)
    mock_severity: str = "info"
    last_scanned: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FileInventoryRecord":
        return cls(**data)


@dataclass
class ScanSummary:
    """扫描摘要"""
    total_files: int = 0
    total_lines: int = 0
    over_threshold_count: int = 0
    mock_usage_count: int = 0
    files_by_type: Dict[str, int] = field(default_factory=dict)
    lines_by_type: Dict[str, int] = field(default_factory=dict)
    over_threshold_by_type: Dict[str, int] = field(default_factory=dict)
    mock_usage_by_type: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_records(cls, records: List[FileInventoryRecord]) -> "ScanSummary":
        summary = cls()
        summary.total_files = len(records)
        
        for record in records:
            # 统计总行数
            summary.total_lines += record.line_count
            
            # 按文件类型统计
            ft = record.file_type
            summary.files_by_type[ft] = summary.files_by_type.get(ft, 0) + 1
            summary.lines_by_type[ft] = summary.lines_by_type.get(ft, 0) + record.line_count
            
            # 超过阈值统计
            if record.is_over_threshold:
                summary.over_threshold_count += 1
                summary.over_threshold_by_type[ft] = summary.over_threshold_by_type.get(ft, 0) + 1
            
            # Mock使用统计
            if record.uses_mock_data:
                summary.mock_usage_count += 1
                summary.mock_usage_by_type[ft] = summary.mock_usage_by_type.get(ft, 0) + 1
        
        return summary


@dataclass
class EnvConfigInfo:
    """环境配置信息"""
    use_mock_data: bool = False
    data_source: str = "real"
    is_valid: bool = True
    issues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationResult:
    """验证结果"""
    mode: str = "REAL"
    is_valid: bool = True
    violations: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
