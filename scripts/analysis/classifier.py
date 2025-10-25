"""
模块分类器 - 将模块分类到五大功能类别

使用规则引擎和启发式方法将模块分类为：
- 核心功能 (Core)
- 辅助功能 (Auxiliary)
- 基础设施功能 (Infrastructure)
- 监控功能 (Monitoring)
- 工具功能 (Utility)

作者: MyStocks Team
日期: 2025-10-19
"""

from typing import List, Dict, Set
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))

from models import ModuleMetadata, CategoryEnum


class ModuleClassifier:
    """模块分类器"""

    def __init__(self):
        """初始化分类器规则"""
        self._init_classification_rules()

    def _init_classification_rules(self):
        """初始化分类规则"""

        # 核心功能特征
        self.core_indicators = {
            'path_keywords': [
                'unified_manager', 'core.py', 'data_access',
                'main.py', 'mystocks_main', 'manager/unified'
            ],
            'class_keywords': [
                'UnifiedManager', 'DataAccess', 'CoreManager',
                'DataClassification', 'DataStorageStrategy'
            ],
            'function_keywords': [
                'save_data_by_classification', 'load_data_by_classification',
                'route_data', 'orchestrate', 'initialize_system'
            ],
            'import_keywords': [
                'data_access', 'core', 'classification'
            ]
        }

        # 辅助功能特征
        self.auxiliary_indicators = {
            'path_keywords': [
                'adapter', 'factory', 'strategy', 'backtest',
                'ml_strategy', 'automation', 'realtime'
            ],
            'class_keywords': [
                'Adapter', 'DataSource', 'Factory', 'Strategy',
                'BacktestEngine', 'MLStrategy'
            ],
            'function_keywords': [
                'fetch_data', 'get_historical', 'create_adapter',
                'run_backtest', 'train_model'
            ],
            'base_classes': [
                'IDataSource', 'BaseAdapter', 'BaseStrategy'
            ]
        }

        # 基础设施功能特征
        self.infrastructure_indicators = {
            'path_keywords': [
                'db_manager', 'database', 'config', 'model',
                'table_manager', 'connection'
            ],
            'class_keywords': [
                'DatabaseManager', 'TableManager', 'ConnectionPool',
                'ConfigManager', 'ORM', 'Model'
            ],
            'function_keywords': [
                'create_table', 'get_connection', 'load_config',
                'validate_table', 'migrate', 'init_db'
            ],
            'import_keywords': [
                'pymysql', 'psycopg2', 'taospy', 'redis',
                'sqlalchemy', 'yaml'
            ]
        }

        # 监控功能特征
        self.monitoring_indicators = {
            'path_keywords': [
                'monitoring', 'alert', 'performance_monitor',
                'data_quality', 'logger', 'metrics'
            ],
            'class_keywords': [
                'Monitor', 'AlertManager', 'PerformanceMonitor',
                'DataQualityMonitor', 'MetricsCollector'
            ],
            'function_keywords': [
                'log_operation', 'track_performance', 'check_quality',
                'send_alert', 'collect_metrics', 'monitor'
            ],
            'import_keywords': [
                'logging', 'prometheus', 'grafana'
            ]
        }

        # 工具功能特征
        self.utility_indicators = {
            'path_keywords': [
                'util', 'helper', 'decorator', 'validation',
                'date_utils', 'symbol_utils', 'column_mapper'
            ],
            'class_keywords': [
                'Utils', 'Helper', 'Validator', 'Mapper'
            ],
            'function_keywords': [
                'format_date', 'convert_symbol', 'map_columns',
                'retry', 'validate', 'normalize'
            ],
            'decorators': [
                'retry', 'cache', 'timing', 'validate_params'
            ]
        }

    def classify_module(self, module: ModuleMetadata) -> CategoryEnum:
        """
        对模块进行分类

        Args:
            module: 模块元数据

        Returns:
            分类结果
        """
        # 计算各类别的匹配分数
        scores = {
            CategoryEnum.CORE: self._score_category(module, self.core_indicators),
            CategoryEnum.AUXILIARY: self._score_category(module, self.auxiliary_indicators),
            CategoryEnum.INFRASTRUCTURE: self._score_category(module, self.infrastructure_indicators),
            CategoryEnum.MONITORING: self._score_category(module, self.monitoring_indicators),
            CategoryEnum.UTILITY: self._score_category(module, self.utility_indicators)
        }

        # 选择得分最高的类别
        max_score = max(scores.values())

        if max_score == 0:
            return CategoryEnum.UNKNOWN

        # 获取得分最高的类别
        for category, score in scores.items():
            if score == max_score:
                return category

        return CategoryEnum.UNKNOWN

    def _score_category(self, module: ModuleMetadata, indicators: Dict[str, List[str]]) -> int:
        """
        计算模块与某类别的匹配分数

        Args:
            module: 模块元数据
            indicators: 类别指标

        Returns:
            匹配分数
        """
        score = 0

        # 检查路径关键词（权重：3）
        if 'path_keywords' in indicators:
            for keyword in indicators['path_keywords']:
                if keyword in module.file_path.lower():
                    score += 3
                    break  # 只计一次

        # 检查类名关键词（权重：2）
        if 'class_keywords' in indicators:
            for cls in module.classes:
                for keyword in indicators['class_keywords']:
                    if keyword.lower() in cls.name.lower():
                        score += 2
                        break

        # 检查基类（权重：3）
        if 'base_classes' in indicators:
            for cls in module.classes:
                for base in cls.base_classes:
                    if base in indicators['base_classes']:
                        score += 3

        # 检查函数名关键词（权重：1）
        if 'function_keywords' in indicators:
            all_functions = module.functions.copy()
            for cls in module.classes:
                all_functions.extend(cls.methods)

            for func in all_functions:
                for keyword in indicators['function_keywords']:
                    if keyword.lower() in func.name.lower():
                        score += 1

        # 检查导入关键词（权重：1）
        if 'import_keywords' in indicators:
            for imp in module.imports:
                for keyword in indicators['import_keywords']:
                    if keyword.lower() in imp.lower():
                        score += 1

        # 检查装饰器（权重：2）
        if 'decorators' in indicators:
            all_functions = module.functions.copy()
            for cls in module.classes:
                all_functions.extend(cls.methods)

            for func in all_functions:
                for decorator in func.decorators:
                    if decorator in indicators['decorators']:
                        score += 2

        return score

    def classify_batch(self, modules: List[ModuleMetadata]) -> Dict[CategoryEnum, List[ModuleMetadata]]:
        """
        批量分类模块

        Args:
            modules: 模块列表

        Returns:
            按类别分组的模块字典
        """
        categorized = {
            CategoryEnum.CORE: [],
            CategoryEnum.AUXILIARY: [],
            CategoryEnum.INFRASTRUCTURE: [],
            CategoryEnum.MONITORING: [],
            CategoryEnum.UTILITY: [],
            CategoryEnum.UNKNOWN: []
        }

        for module in modules:
            category = self.classify_module(module)
            module.category = category
            categorized[category].append(module)

        return categorized

    def get_category_stats(self, modules: List[ModuleMetadata]) -> Dict[str, Dict[str, int]]:
        """
        获取分类统计信息

        Args:
            modules: 模块列表

        Returns:
            统计信息字典
        """
        categorized = self.classify_batch(modules)
        stats = {}

        for category, module_list in categorized.items():
            total_functions = sum(
                len(m.functions) + sum(len(c.methods) for c in m.classes)
                for m in module_list
            )
            total_classes = sum(len(m.classes) for m in module_list)
            total_lines = sum(m.lines_of_code for m in module_list)

            stats[category.value] = {
                'modules': len(module_list),
                'classes': total_classes,
                'functions': total_functions,
                'lines': total_lines
            }

        return stats

    def suggest_recategorization(self, module: ModuleMetadata) -> List[str]:
        """
        建议可能的重新分类

        Args:
            module: 模块元数据

        Returns:
            建议列表
        """
        suggestions = []

        # 计算所有类别的分数
        scores = {
            'Core': self._score_category(module, self.core_indicators),
            'Auxiliary': self._score_category(module, self.auxiliary_indicators),
            'Infrastructure': self._score_category(module, self.infrastructure_indicators),
            'Monitoring': self._score_category(module, self.monitoring_indicators),
            'Utility': self._score_category(module, self.utility_indicators)
        }

        # 获取前两名
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if len(sorted_scores) >= 2:
            first_cat, first_score = sorted_scores[0]
            second_cat, second_score = sorted_scores[1]

            # 如果得分接近（差距小于 20%）
            if second_score > 0 and (first_score - second_score) / first_score < 0.2:
                suggestions.append(
                    f"模块可能同时具有 {first_cat} 和 {second_cat} 特征，"
                    f"建议审查分类（分数：{first_score} vs {second_score}）"
                )

        # 检查是否有多重职责
        if len([s for s in scores.values() if s > 5]) > 1:
            suggestions.append("模块可能承担多重职责，建议考虑拆分")

        return suggestions


def create_category_report(modules: List[ModuleMetadata]) -> str:
    """
    创建分类报告

    Args:
        modules: 模块列表

    Returns:
        Markdown 格式的报告
    """
    classifier = ModuleClassifier()
    categorized = classifier.classify_batch(modules)
    stats = classifier.get_category_stats(modules)

    report = ["# 模块分类报告\n"]
    report.append(f"**总模块数**: {len(modules)}\n")
    report.append(f"**生成时间**: {Path(__file__).stat().st_mtime}\n\n")

    report.append("## 分类统计\n")
    report.append("| 类别 | 模块数 | 类数 | 函数数 | 代码行数 |")
    report.append("|------|--------|------|--------|----------|")

    category_names = {
        'core': '核心功能',
        'auxiliary': '辅助功能',
        'infrastructure': '基础设施',
        'monitoring': '监控功能',
        'utility': '工具功能',
        'unknown': '未分类'
    }

    for cat_key, cat_name in category_names.items():
        if cat_key in stats:
            s = stats[cat_key]
            report.append(
                f"| {cat_name} | {s['modules']} | {s['classes']} | "
                f"{s['functions']} | {s['lines']} |"
            )

    report.append("\n")

    # 详细列表
    for category, module_list in categorized.items():
        if not module_list:
            continue

        cat_name = category_names.get(category.value, category.value)
        report.append(f"## {cat_name}\n")

        for module in sorted(module_list, key=lambda m: m.file_path):
            report.append(f"### {module.module_name}")
            report.append(f"- **路径**: `{module.file_path}`")
            report.append(f"- **类**: {len(module.classes)}")
            report.append(f"- **函数**: {len(module.functions)}")
            report.append(f"- **代码行**: {module.lines_of_code}")

            if module.docstring:
                first_line = module.docstring.split('\n')[0]
                report.append(f"- **说明**: {first_line}")

            report.append("")

    return '\n'.join(report)


if __name__ == "__main__":
    # 测试代码
    from utils.ast_parser import ASTParser

    project_root = "/opt/claude/mystocks_spec"
    parser = ASTParser(project_root)
    classifier = ModuleClassifier()

    # 测试几个关键文件
    test_files = [
        "unified_manager.py",
        "core.py",
        "adapters/akshare_adapter.py",
        "db_manager/database_manager.py",
        "monitoring/performance_monitor.py",
        "utils/date_utils.py"
    ]

    print("模块分类测试:\n")
    for file_name in test_files:
        file_path = Path(project_root) / file_name
        if file_path.exists():
            module = parser.parse_file(file_path)
            if module:
                category = classifier.classify_module(module)
                print(f"{file_name:40} -> {category.value}")
