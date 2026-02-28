"""报告生成模块"""

from typing import List
from .models import FileInventoryRecord, ScanSummary, ValidationResult


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        pass
    
    def generate_text_report(
        self, 
        records: List[FileInventoryRecord], 
        summary: ScanSummary,
        validation: ValidationResult = None
    ) -> str:
        """生成文本报告
        
        Args:
            records: 登记记录列表
            summary: 扫描摘要
            validation: 验证结果（可选）
            
        Returns:
            文本报告
        """
        lines = []
        
        # 标题
        lines.append("=" * 60)
        lines.append("代码清单扫描报告")
        lines.append("=" * 60)
        lines.append("")
        
        # 摘要统计
        lines.append("【摘要统计】")
        lines.append(f"  总文件数: {summary.total_files}")
        lines.append(f"  总代码行数: {summary.total_lines}")
        lines.append(f"  超过阈值文件数: {summary.over_threshold_count}")
        lines.append(f"  使用Mock文件数: {summary.mock_usage_count}")
        lines.append("")
        
        # 按文件类型统计
        lines.append("【按文件类型统计】")
        for ft in sorted(summary.files_by_type.keys()):
            count = summary.files_by_type[ft]
            lines.append(str(count))
            lines_by_ft = summary.lines_by_type.get(ft, 0)
            over_by_ft = summary.over_threshold_by_type.get(ft, 0)
            mock_by_ft = summary.mock_usage_by_type.get(ft, 0)
            lines.append(f"  {ft}: {count} 文件, {lines_by_ft} 行, {over_by_ft} 超过阈值, {mock_by_ft} 使用Mock")
        lines.append("")
        
        # 超过阈值的文件列表
        if summary.over_threshold_count > 0:
            lines.append(f"【超过阈值文件列表】(共 {summary.over_threshold_count} 个)")
            for record in sorted(records, key=lambda r: r.line_count, reverse=True):
                if record.is_over_threshold:
                    lines.append(f"  {record.file_path}: {record.line_count} 行")
            lines.append("")
        
        # 使用Mock的文件列表
        if summary.mock_usage_count > 0:
            lines.append(f"【使用Mock数据文件列表】(共 {summary.mock_usage_count} 个)")
            for record in records:
                if record.uses_mock_data:
                    mock_info = ", ".join(record.mock_imports[:3])
                    if len(record.mock_imports) > 3:
                        mock_info += "..."
                    lines.append(f"  {record.file_path}")
                    lines.append(f"    [严重性: {record.mock_severity}] {mock_info}")
            lines.append("")
        
        # 验证结果
        if validation:
            lines.append("【REAL模式验证】")
            lines.append(f"  当前模式: {validation.mode}")
            lines.append(f"  验证结果: {'通过' if validation.is_valid else '失败'}")
            if validation.violations:
                lines.append("  违规项:")
                for v in validation.violations:
                    lines.append(f"    - [{v['severity']}] {v['message']}")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_json_report(
        self, 
        records: List[FileInventoryRecord], 
        summary: ScanSummary,
        validation: ValidationResult = None
    ) -> dict:
        """生成JSON报告
        
        Args:
            records: 登记记录列表
            summary: 扫描摘要
            validation: 验证结果（可选）
            
        Returns:
            JSON报告
        """
        import json
        from datetime import datetime
        
        data = {
            "generated_at": datetime.now().isoformat(),
            "summary": summary.to_dict(),
            "records": [r.to_dict() for r in records],
        }
        
        if validation:
            data["validation"] = validation.to_dict()
        
        return data
