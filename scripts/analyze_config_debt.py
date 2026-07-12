#!/usr/bin/env python3
"""配置管理技术债务清理脚本
Configuration Management Technical Debt Cleanup Script

识别和清理配置管理中的技术债务：
- 重复配置
- 过时配置
- 格式不一致
- 缺少验证
"""

import hashlib
import json
import os
from typing import Dict, List

import yaml


class ConfigDebtAnalyzer:
    """配置债务分析器"""

    def __init__(self):
        self.config_files = []
        self.issues = []
        self.statistics = {
            "total_files": 0,
            "valid_yaml": 0,
            "invalid_yaml": 0,
            "duplicates": 0,
            "empty_files": 0,
            "large_files": 0,
        }

    def scan_configs(self, root_dir: str = ".") -> Dict:
        """扫描所有配置文件"""
        print("🔍 扫描配置文件...")

        # 查找所有YAML文件
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.endswith((".yaml", ".yml")):
                    file_path = os.path.join(root, file)
                    self.config_files.append(file_path)

        self.statistics["total_files"] = len(self.config_files)
        print(f"发现 {len(self.config_files)} 个配置文件")

        # 分析每个文件
        file_hashes = {}
        for file_path in self.config_files:
            self._analyze_config_file(file_path, file_hashes)

        return {
            "statistics": self.statistics,
            "issues": self.issues,
            "recommendations": self._generate_recommendations(),
        }

    def _analyze_config_file(self, file_path: str, file_hashes: Dict):
        """分析单个配置文件"""
        try:
            # 检查文件大小
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if size_mb > 1:  # 大于1MB
                self.issues.append(
                    {
                        "type": "large_file",
                        "file": file_path,
                        "size_mb": size_mb,
                        "severity": "medium",
                        "message": f"配置文件过大 ({size_mb:.1f}MB)，建议拆分",
                    },
                )
                self.statistics["large_files"] += 1

            # 检查是否为空
            if os.path.getsize(file_path) == 0:
                self.issues.append(
                    {
                        "type": "empty_file",
                        "file": file_path,
                        "severity": "low",
                        "message": "空配置文件",
                    },
                )
                self.statistics["empty_files"] += 1
                return

            # 验证YAML格式
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # 计算内容哈希以检测重复
            content_hash = hashlib.md5(content.encode()).hexdigest()
            if content_hash in file_hashes:
                self.issues.append(
                    {
                        "type": "duplicate_content",
                        "file": file_path,
                        "duplicate_of": file_hashes[content_hash],
                        "severity": "high",
                        "message": f"与 {file_hashes[content_hash]} 内容完全相同",
                    },
                )
                self.statistics["duplicates"] += 1
            else:
                file_hashes[content_hash] = file_path

            # 解析YAML
            try:
                data = yaml.safe_load(content)
                self.statistics["valid_yaml"] += 1

                # 检查数据源配置特有问题
                if "data_sources" in str(file_path).lower():
                    self._analyze_data_source_config(file_path, data)

            except yaml.YAMLError as e:
                self.issues.append(
                    {
                        "type": "invalid_yaml",
                        "file": file_path,
                        "error": str(e),
                        "severity": "high",
                        "message": f"YAML格式错误: {e}",
                    },
                )
                self.statistics["invalid_yaml"] += 1

        except Exception as e:
            self.issues.append(
                {
                    "type": "read_error",
                    "file": file_path,
                    "error": str(e),
                    "severity": "high",
                    "message": f"无法读取文件: {e}",
                },
            )

    def _analyze_data_source_config(self, file_path: str, data: Dict):
        """分析数据源配置特有问题"""
        if not isinstance(data, dict):
            return

        data_sources = data.get("data_sources", {})
        if not data_sources:
            return

        # 检查数据源配置完整性
        for source_name, source_config in data_sources.items():
            if not isinstance(source_config, dict):
                continue

            # 检查必需字段
            required_fields = ["source_name", "source_type", "data_category"]
            missing_fields = [field for field in required_fields if field not in source_config]

            if missing_fields:
                self.issues.append(
                    {
                        "type": "incomplete_config",
                        "file": file_path,
                        "source": source_name,
                        "missing_fields": missing_fields,
                        "severity": "medium",
                        "message": f"数据源 {source_name} 缺少必需字段: {', '.join(missing_fields)}",
                    },
                )

            # 检查数据分类一致性
            data_category = source_config.get("data_category")
            data_classification = source_config.get("data_classification")

            if data_category and data_classification:
                # 这里可以添加更复杂的验证逻辑
                pass

    def _generate_recommendations(self) -> List[str]:
        """生成修复建议"""
        recommendations = []

        if self.statistics["invalid_yaml"] > 0:
            recommendations.append(
                f"🔴 修复 {self.statistics['invalid_yaml']} 个YAML格式错误",
            )

        if self.statistics["duplicates"] > 0:
            recommendations.append(
                f"🟡 清理 {self.statistics['duplicates']} 个重复配置文件",
            )

        if self.statistics["large_files"] > 0:
            recommendations.append(f"🟡 拆分 {self.statistics['large_files']} 个大文件")

        if self.statistics["empty_files"] > 0:
            recommendations.append(
                f"🟢 删除 {self.statistics['empty_files']} 个空配置文件",
            )

        recommendations.extend(
            [
                "📋 建立配置schema验证",
                "🔄 实现配置版本控制",
                "📊 添加配置健康监控",
                "🏷️ 为配置添加文档注释",
            ],
        )

        return recommendations

    def generate_report(self) -> Dict:
        """生成分析报告"""
        report = self.scan_configs()

        print("\n📊 配置债务分析报告")
        print("=" * 50)
        print(f"总配置文件数: {report['statistics']['total_files']}")
        print(f"有效YAML文件: {report['statistics']['valid_yaml']}")
        print(f"无效YAML文件: {report['statistics']['invalid_yaml']}")
        print(f"重复文件: {report['statistics']['duplicates']}")
        print(f"空文件: {report['statistics']['empty_files']}")
        print(f"大文件: {report['statistics']['large_files']}")

        print(f"\n发现问题: {len(report['issues'])} 个")

        # 按严重程度分组显示问题
        severity_levels = ["high", "medium", "low"]
        for severity in severity_levels:
            issues = [i for i in report["issues"] if i["severity"] == severity]
            if issues:
                print(f"\n{severity.upper()} 严重程度问题 ({len(issues)} 个):")
                for issue in issues[:5]:  # 只显示前5个
                    print(f"  • {issue['file']}: {issue['message']}")

        if len(report["issues"]) > 5:
            print(f"  ... 还有 {len(report['issues']) - 5} 个问题")

        print("\n💡 修复建议:")
        for rec in report["recommendations"]:
            print(f"  - {rec}")

        return report


def main():
    """主函数"""
    analyzer = ConfigDebtAnalyzer()
    report = analyzer.generate_report()

    # 保存详细报告
    with open("config_debt_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n📄 详细报告已保存到: config_debt_report.json")  # 返回错误码
    has_critical_issues = any(issue["severity"] == "high" for issue in report["issues"])
    return 1 if has_critical_issues else 0


if __name__ == "__main__":
    exit(main())
