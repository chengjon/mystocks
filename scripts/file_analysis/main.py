#!/usr/bin/env python3
"""
文件分析系统主程序
用途：整合所有分析器，扫描项目文件并保存到PostgreSQL数据库
"""

import os
import sys
import uuid
import psycopg2
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging
import argparse

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from python_analyzer import PythonAnalyzer
from typescript_analyzer import TypeScriptAnalyzer
from html_analyzer import HTMLAnalyzer
from css_analyzer import CSSAnalyzer
from json_analyzer import JSONAnalyzer
from reference_analyzer import ReferenceAnalyzer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('ANALYSIS_DB', 'file_analysis_db'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres')
}


class FileAnalysisSystem:
    """文件分析系统"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.run_id = str(uuid.uuid4())

        # 初始化分析器
        self.python_analyzer = PythonAnalyzer()
        self.ts_analyzer = TypeScriptAnalyzer()
        self.html_analyzer = HTMLAnalyzer()
        self.css_analyzer = CSSAnalyzer()
        self.json_analyzer = JSONAnalyzer()
        self.reference_analyzer = ReferenceAnalyzer(str(self.project_root))

        # 数据库连接
        self.conn = None

        # 统计信息
        self.stats = {
            'total_files': 0,
            'python_files': 0,
            'typescript_files': 0,
            'javascript_files': 0,
            'vue_files': 0,
            'html_files': 0,
            'css_files': 0,
            'json_files': 0,
            'errors': 0
        }

        # 分析结果
        self.file_metadata = []
        self.references = []

    def connect_database(self):
        """连接数据库"""
        logger.info("开始连接数据库")
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.conn.autocommit = True
            logger.info("数据库连接成功")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False

    def create_analysis_run(self):
        """创建分析运行记录"""
        logger.info(f"创建分析运行记录: {self.run_id}")

        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO analysis_runs (run_id, status, start_time)
                VALUES (%s, 'running', NOW())
                RETURNING id
            """, (self.run_id,))

            run_db_id = cursor.fetchone()[0]
            logger.info(f"分析运行记录创建成功，ID: {run_db_id}")
            cursor.close()

            return run_db_id

        except Exception as e:
            logger.error(f"创建分析运行记录失败: {e}")
            cursor.close()
            return None

    def update_analysis_run(self, status: str, error_message: str = None):
        """更新分析运行记录"""
        logger.info(f"更新分析运行记录: {status}")

        cursor = self.conn.cursor()

        try:
            update_sql = """
                UPDATE analysis_runs
                SET status = %s, end_time = NOW(),
                    total_files = %s, python_files = %s,
                    typescript_files = %s, javascript_files = %s,
                    vue_files = %s, html_files = %s,
                    css_files = %s, json_files = %s
            """

            params = [
                status,
                self.stats['total_files'],
                self.stats['python_files'],
                self.stats['typescript_files'],
                self.stats['javascript_files'],
                self.stats['vue_files'],
                self.stats['html_files'],
                self.stats['css_files'],
                self.stats['json_files']
            ]

            if error_message:
                update_sql += ", error_message = %s"
                params.append(error_message)

            update_sql += " WHERE run_id = %s"
            params.append(self.run_id)

            cursor.execute(update_sql, params)
            cursor.close()

        except Exception as e:
            logger.error(f"更新分析运行记录失败: {e}")
            cursor.close()

    def scan_files(self) -> List[str]:
        """扫描项目文件"""
        logger.info(f"开始扫描项目文件: {self.project_root}")

        file_patterns = [
            '**/*.py',
            '**/*.ts',
            '**/*.tsx',
            '**/*.js',
            '**/*.jsx',
            '**/*.vue',
            '**/*.html',
            '**/*.htm',
            '**/*.css',
            '**/*.json'
        ]

        files = []

        for pattern in file_patterns:
            for file_path in self.project_root.rglob(pattern):
                # 排除特定目录
                if any(part in file_path.parts for part in [
                    '__pycache__',
                    '.git',
                    'node_modules',
                    '.pytest_cache',
                    'venv',
                    'env',
                    '.venv'
                ]):
                    continue

                files.append(str(file_path))

        logger.info(f"扫描完成，共找到 {len(files)} 个文件")
        return files

    def scan_files_incremental(self, last_scan_time: datetime) -> List[str]:
        """
        增量扫描文件（只扫描修改过的文件）

        Args:
            last_scan_time: 上次扫描时间

        Returns:
            修改过的文件列表
        """
        logger.info(f"开始增量扫描项目文件: {self.project_root}")
        logger.info(f"只扫描修改时间晚于 {last_scan_time} 的文件")

        file_patterns = [
            '**/*.py',
            '**/*.ts',
            '**/*.tsx',
            '**/*.js',
            '**/*.jsx',
            '**/*.vue',
            '**/*.html',
            '**/*.htm',
            '**/*.css',
            '**/*.json'
        ]

        files = []

        for pattern in file_patterns:
            for file_path in self.project_root.rglob(pattern):
                # 排除特定目录
                if any(part in file_path.parts for part in [
                    '__pycache__',
                    '.git',
                    'node_modules',
                    '.pytest_cache',
                    'venv',
                    'env',
                    '.venv'
                ]):
                    continue

                # 只添加修改时间晚于上次扫描时间的文件
                try:
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime > last_scan_time:
                        files.append(str(file_path))
                except Exception as e:
                    logger.warning(f"无法获取文件修改时间: {file_path} - {e}")

        logger.info(f"增量扫描完成，共找到 {len(files)} 个修改过的文件")
        return files

    def analyze_file(self, file_path: str) -> Optional[Dict]:
        """分析单个文件"""
        file_ext = Path(file_path).suffix.lower()

        try:
            if file_ext == '.py':
                result = self.python_analyzer.analyze_file(file_path)
                self.stats['python_files'] += 1
            elif file_ext in ['.ts', '.tsx']:
                result = self.ts_analyzer.analyze_file(file_path)
                self.stats['typescript_files'] += 1
            elif file_ext in ['.js', '.jsx', '.mjs']:
                result = self.ts_analyzer.analyze_file(file_path)
                self.stats['javascript_files'] += 1
            elif file_ext == '.vue':
                result = self.html_analyzer.analyze_file(file_path)
                self.stats['vue_files'] += 1
            elif file_ext in ['.html', '.htm']:
                result = self.html_analyzer.analyze_file(file_path)
                self.stats['html_files'] += 1
            elif file_ext == '.css':
                result = self.css_analyzer.analyze_file(file_path)
                self.stats['css_files'] += 1
            elif file_ext == '.json':
                result = self.json_analyzer.analyze_file(file_path)
                self.stats['json_files'] += 1
            else:
                return None

            self.stats['total_files'] += 1
            return result

        except Exception as e:
            logger.error(f"分析文件失败: {file_path} - {e}")
            self.stats['errors'] += 1
            return None

    def save_file_metadata(self, file_info: Dict):
        """保存文件元数据到数据库"""
        cursor = self.conn.cursor()

        try:
            # 确定分类ID
            category_id = self._get_category_id(file_info['file_type'])

            cursor.execute("""
                INSERT INTO file_metadata (
                    run_id, file_name, file_path, file_type, file_size,
                    line_count, function_count, class_count, category_id,
                    file_function, module_name, package_name,
                    imports_count, exports_count, complexity_score,
                    last_modified, file_created, analyzed_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, NOW()
                )
                RETURNING id
            """, (
                self.run_id,
                file_info['file_name'],
                file_info['file_path'],
                file_info['file_type'],
                file_info.get('file_size', 0),
                file_info.get('line_count', 0),
                file_info.get('function_count', 0),
                file_info.get('class_count', 0),
                category_id,
                file_info.get('file_function', ''),
                file_info.get('module_name'),
                file_info.get('package_name'),
                file_info.get('imports_count', 0),
                file_info.get('exports_count', 0),
                file_info.get('complexity_score', 0),
                file_info.get('last_modified'),
                file_info.get('file_created')
            ))

            file_id = cursor.fetchone()[0]

            # 更新文件信息
            file_info['id'] = file_id
            self.file_metadata.append(file_info)

            cursor.close()

        except Exception as e:
            logger.error(f"保存文件元数据失败: {e}")
            cursor.close()

    def _get_category_id(self, file_type: str) -> Optional[int]:
        """获取分类ID"""
        cursor = self.conn.cursor()

        try:
            category_map = {
                'python': 'py_backend',
                'typescript': 'ts_frontend',
                'javascript': 'js_utility',
                'vue': 'vue_component',
                'html': 'html_page',
                'css': 'config',  # CSS通常用于样式配置
                'json': 'config'   # JSON通常用于配置
            }

            category_code = category_map.get(file_type, 'other')

            cursor.execute("""
                SELECT id FROM file_categories WHERE category_code = %s
            """, (category_code,))

            result = cursor.fetchone()
            cursor.close()

            return result[0] if result else None

        except Exception as e:
            logger.error(f"获取分类ID失败: {e}")
            cursor.close()
            return None

    def save_references(self):
        """保存引用关系到数据库"""
        logger.info("开始保存引用关系")

        cursor = self.conn.cursor()

        try:
            for ref in self.references:
                cursor.execute("""
                    INSERT INTO file_references (
                        run_id, source_file_id, target_file_id,
                        reference_type, reference_line, reference_code,
                        is_external, is_valid, validation_message
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    self.run_id,
                    ref.get('source_file_id'),
                    ref.get('target_file_id'),
                    ref.get('reference_type'),
                    ref.get('reference_line'),
                    ref.get('reference_code'),
                    ref.get('is_external'),
                    ref.get('is_valid'),
                    ref.get('validation_message')
                ))

            self.conn.commit()
            cursor.close()

            logger.info(f"引用关系保存完成，共 {len(self.references)} 条")

        except Exception as e:
            logger.error(f"保存引用关系失败: {e}")
            self.conn.rollback()
            cursor.close()

    def analyze_references(self):
        """分析所有文件的引用关系"""
        logger.info("开始分析引用关系")

        # 构建文件索引
        self.reference_analyzer.build_file_index(self.file_metadata)

        # 分析每个文件的引用
        for file_info in self.file_metadata:
            references = self.reference_analyzer.analyze_references(file_info)
            self.references.extend(references)

            logger.info(f"文件 {file_info['file_name']}: {len(references)} 个引用")

        logger.info(f"引用关系分析完成，共 {len(self.references)} 条")

    def run(self, incremental: bool = False, since: str = None):
        """
        运行分析流程

        Args:
            incremental: 是否启用增量扫描
            since: 增量扫描的起始时间字符串
        """
        logger.info("=" * 60)
        logger.info("文件分析系统开始运行")
        if incremental:
            logger.info("模式: 增量扫描")
        else:
            logger.info("模式: 全量扫描")
        logger.info("=" * 60)

        start_time = datetime.now()

        try:
            # 连接数据库
            if not self.connect_database():
                logger.error("数据库连接失败，退出")
                return 1

            # 创建分析运行记录
            run_db_id = self.create_analysis_run()
            if not run_db_id:
                logger.error("创建分析运行记录失败，退出")
                return 1

            # 确定扫描模式
            if incremental:
                # 增量扫描
                if since:
                    # 使用用户指定的时间
                    last_scan_time = datetime.strptime(since, '%Y-%m-%d %H:%M:%S')
                else:
                    # 从数据库获取上次扫描时间
                    cursor = self.conn.cursor()
                    cursor.execute("""
                        SELECT MAX(start_time) FROM analysis_runs
                        WHERE status = 'completed'
                    """)
                    result = cursor.fetchone()
                    cursor.close()

                    if result and result[0]:
                        last_scan_time = result[0]
                        logger.info(f"使用上次扫描时间: {last_scan_time}")
                    else:
                        logger.warning("未找到历史扫描记录，执行全量扫描")
                        incremental = False
                        last_scan_time = None

                if incremental:
                    files = self.scan_files_incremental(last_scan_time)
                else:
                    files = self.scan_files()
            else:
                # 全量扫描
                files = self.scan_files()

            if not files:
                logger.warning("未找到任何文件")
                self.update_analysis_run('completed')
                return 0

            # 分析文件
            logger.info(f"开始分析 {len(files)} 个文件")
            for i, file_path in enumerate(files, 1):
                if i % 100 == 0:
                    logger.info(f"进度: {i}/{len(files)}")

                result = self.analyze_file(file_path)
                if result and not result.get('error'):
                    self.save_file_metadata(result)

            logger.info(f"文件分析完成，成功分析 {len(self.file_metadata)} 个文件")

            # 分析引用关系
            self.analyze_references()

            # 保存引用关系
            self.save_references()

            # 更新分析运行记录
            self.update_analysis_run('completed')

            # 生成报告
            self.generate_report()

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            logger.info("=" * 60)
            logger.info("文件分析系统运行完成")
            logger.info(f"总耗时: {duration:.2f}秒")
            logger.info(f"分析文件数: {self.stats['total_files']}")
            logger.info(f"Python文件: {self.stats['python_files']}")
            logger.info(f"TypeScript文件: {self.stats['typescript_files']}")
            logger.info(f"JavaScript文件: {self.stats['javascript_files']}")
            logger.info(f"Vue文件: {self.stats['vue_files']}")
            logger.info(f"HTML文件: {self.stats['html_files']}")
            logger.info(f"CSS文件: {self.stats['css_files']}")
            logger.info(f"JSON文件: {self.stats['json_files']}")
            logger.info(f"错误数: {self.stats['errors']}")
            logger.info(f"引用关系数: {len(self.references)}")
            logger.info("=" * 60)

            return 0

        except Exception as e:
            logger.error(f"分析系统运行失败: {e}")
            self.update_analysis_run('failed', str(e))
            return 1

        finally:
            if self.conn:
                self.conn.close()

    def generate_report(self):
        """生成分析报告"""
        logger.info("生成分析报告")

        report_file = f"analysis_report_{self.run_id[:8]}.md"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 文件分析报告\n\n")
            f.write(f"## 分析概览\n\n")
            f.write(f"- **运行ID**: {self.run_id}\n")
            f.write(f"- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- **项目路径**: {self.project_root}\n\n")

            f.write(f"## 统计信息\n\n")
            f.write(f"- **总文件数**: {self.stats['total_files']}\n")
            f.write(f"- **Python文件**: {self.stats['python_files']}\n")
            f.write(f"- **TypeScript文件**: {self.stats['typescript_files']}\n")
            f.write(f"- **JavaScript文件**: {self.stats['javascript_files']}\n")
            f.write(f"- **Vue文件**: {self.stats['vue_files']}\n")
            f.write(f"- **HTML文件**: {self.stats['html_files']}\n")
            f.write(f"- **CSS文件**: {self.stats['css_files']}\n")
            f.write(f"- **JSON文件**: {self.stats['json_files']}\n")
            f.write(f"- **错误数**: {self.stats['errors']}\n")
            f.write(f"- **引用关系数**: {len(self.references)}\n\n")

            # 引用统计
            valid_refs = sum(1 for ref in self.references if ref.get('is_valid'))
            invalid_refs = len(self.references) - valid_refs

            f.write(f"## 引用关系统计\n\n")
            f.write(f"- **有效引用**: {valid_refs}\n")
            f.write(f"- **无效引用**: {invalid_refs}\n")
            f.write(f"- **外部引用**: {sum(1 for ref in self.references if ref.get('is_external'))}\n\n")

            # 复杂度最高的文件
            top_complex = sorted(
                self.file_metadata,
                key=lambda x: x.get('complexity_score', 0),
                reverse=True
            )[:10]

            f.write(f"## 复杂度最高的10个文件\n\n")
            f.write("| 文件名 | 路径 | 复杂度 | 行数 | 函数数 | 类数 |\n")
            f.write("|--------|------|--------|------|--------|------|\n")

            for file_info in top_complex:
                f.write(f"| {file_info['file_name']} | {file_info['file_path'][:50]}... | "
                       f"{file_info.get('complexity_score', 0)} | {file_info.get('line_count', 0)} | "
                       f"{file_info.get('function_count', 0)} | {file_info.get('class_count', 0)} |\n")

        logger.info(f"分析报告已保存: {report_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='文件分析系统')
    parser.add_argument(
        'project_root',
        nargs='?',
        default='/opt/claude/mystocks_spec',
        help='项目根目录路径'
    )
    parser.add_argument(
        '--incremental',
        action='store_true',
        help='启用增量扫描（只扫描修改过的文件）'
    )
    parser.add_argument(
        '--since',
        type=str,
        help='增量扫描的起始时间（格式：YYYY-MM-DD HH:MM:SS）'
    )

    args = parser.parse_args()

    # 创建分析系统
    system = FileAnalysisSystem(args.project_root)

    # 运行分析
    return system.run(incremental=args.incremental, since=args.since)


if __name__ == '__main__':
    sys.exit(main())
