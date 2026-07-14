"""核心扫描器"""

import os
from datetime import datetime
from typing import List, Dict, Any

from .config import ScanConfig
from .line_counter import count_lines, scan_files, get_file_type
from .mock_detector import MockDetector
from .models import FileInventoryRecord, ScanSummary
from .storage import ResultStorage
from .env_checker import EnvConfigChecker
from .reporter import ReportGenerator


class CodeInventoryScanner:
    """代码清单扫描器"""

    def __init__(self, config: ScanConfig = None):
        """初始化
        
        Args:
            config: 扫描配置
        """
        self.config = config or ScanConfig()
        self.detector = MockDetector(
            import_patterns=self.config.mock_import_patterns,
            call_patterns=self.config.mock_call_patterns
        )
        self.storage = ResultStorage(self.config.output_dir)
        self.env_checker = EnvConfigChecker()
        self.reporter = ReportGenerator()

    def scan(self, validate_real: bool = True) -> Dict[str, Any]:
        """执行扫描
        
        Args:
            validate_real: 是否验证REAL模式
            
        Returns:
            扫描结果字典
        """
        records: List[FileInventoryRecord] = []

        # 扫描各个目录
        for scan_dir in self.config.scan_dirs:
            scan_path = os.path.join(self.config.project_root, scan_dir)

            if not os.path.exists(scan_path):
                print(f"警告: 目录不存在: {scan_path}")
                continue

            print(f"正在扫描: {scan_dir}")

            # 获取文件列表
            files = scan_files(
                scan_path,
                self.config.file_extensions,
                self.config.exclude_dirs
            )

            # 扫描每个文件
            for file_path in files:
                record = self._scan_file(file_path)
                records.append(record)

        # 生成摘要
        summary = ScanSummary.from_records(records)

        # 验证REAL模式
        validation = None
        if validate_real:
            validation = self.env_checker.validate_real_mode(self.config.project_root)

        # 保存结果
        self.storage.save_inventory(records)
        self.storage.save_summary(summary)
        self.storage.save_violations(records)

        if validation:
            self.storage.save_validation(validation)

        # 输出报告
        print("\n" + "=" * 60)
        print(self.reporter.generate_text_report(records, summary, validation))

        return {
            "records": records,
            "summary": summary,
            "validation": validation,
            "output_dir": self.storage.get_output_dir()
        }

    def _scan_file(self, file_path: str) -> FileInventoryRecord:
        """扫描单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            登记记录
        """
        # 获取文件类型
        file_type = get_file_type(file_path)

        # 统计行数
        line_count = count_lines(file_path)

        # 判断是否超过阈值
        is_over_threshold = line_count > self.config.line_threshold

        # 检测Mock使用
        mock_result = self.detector.detect_file(file_path)

        # 创建记录
        record = FileInventoryRecord(
            file_path=file_path,
            file_type=file_type,
            line_count=line_count,
            is_over_threshold=is_over_threshold,
            uses_mock_data=mock_result.has_mock,
            mock_imports=mock_result.imports,
            mock_calls=mock_result.calls,
            mock_severity=mock_result.severity,
            last_scanned=datetime.now().isoformat()
        )

        return record

    def quick_scan(self) -> ScanSummary:
        """快速扫描（仅统计，不检测Mock）
        
        Returns:
            扫描摘要
        """
        records: List[FileInventoryRecord] = []

        for scan_dir in self.config.scan_dirs:
            scan_path = os.path.join(self.config.project_root, scan_dir)

            if not os.path.exists(scan_path):
                continue

            files = scan_files(
                scan_path,
                self.config.file_extensions,
                self.config.exclude_dirs
            )

            for file_path in files:
                file_type = get_file_type(file_path)
                line_count = count_lines(file_path)

                record = FileInventoryRecord(
                    file_path=file_path,
                    file_type=file_type,
                    line_count=line_count,
                    is_over_threshold=line_count > self.config.line_threshold,
                    last_scanned=datetime.now().isoformat()
                )
                records.append(record)

        return ScanSummary.from_records(records)

    def check_mock_usage(self) -> List[FileInventoryRecord]:
        """仅检查Mock使用情况
        
        Returns:
            使用Mock的文件列表
        """
        records: List[FileInventoryRecord] = []

        for scan_dir in self.config.scan_dirs:
            scan_path = os.path.join(self.config.project_root, scan_dir)

            if not os.path.exists(scan_path):
                continue

            # 只扫描Python文件
            files = scan_files(scan_path, [".py"], self.config.exclude_dirs)

            for file_path in files:
                mock_result = self.detector.detect_file(file_path)

                if mock_result.has_mock:
                    record = FileInventoryRecord(
                        file_path=file_path,
                        file_type=".py",
                        line_count=count_lines(file_path),
                        is_over_threshold=False,
                        uses_mock_data=True,
                        mock_imports=mock_result.imports,
                        mock_calls=mock_result.calls,
                        mock_severity=mock_result.severity,
                        last_scanned=datetime.now().isoformat()
                    )
                    records.append(record)

        return records
