#!/usr/bin/env python3
"""
文件信息查询工具
用途：从PostgreSQL数据库查询文件信息、引用关系等
"""

import os
import sys
import psycopg2
from typing import Dict, List, Optional
import logging
import argparse
import json
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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


class FileQueryTool:
    """文件查询工具"""

    def __init__(self):
        self.conn = None

    def connect(self):
        """连接数据库"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            logger.info("数据库连接成功")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")

    def get_file_by_name(self, file_name: str) -> Optional[Dict]:
        """根据文件名查询文件"""
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    fm.id, fm.file_name, fm.file_path, fm.file_type,
                    fm.file_size, fm.line_count, fm.function_count,
                    fm.class_count, fm.file_function, fm.module_name,
                    fm.package_name, fm.imports_count, fm.exports_count,
                    fm.references_in_count, fm.references_out_count,
                    fm.complexity_score, fm.quality_score, fm.last_modified,
                    fm.analyzed_at, fc.category_name
                FROM file_metadata fm
                LEFT JOIN file_categories fc ON fm.category_id = fc.id
                WHERE fm.file_name LIKE %s
                ORDER BY fm.analyzed_at DESC
                LIMIT 10
            """, (f"%{file_name}%",))

            columns = [desc[0] for desc in cursor.description]
            results = []

            for row in cursor.fetchall():
                result = dict(zip(columns, row))
                # 转换datetime为字符串
                for key, value in result.items():
                    if isinstance(value, datetime):
                        result[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                results.append(result)

            cursor.close()
            return results

        except Exception as e:
            logger.error(f"查询文件失败: {e}")
            cursor.close()
            return None

    def get_file_by_path(self, file_path: str) -> Optional[Dict]:
        """根据文件路径查询文件"""
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    fm.id, fm.file_name, fm.file_path, fm.file_type,
                    fm.file_size, fm.line_count, fm.function_count,
                    fm.class_count, fm.file_function, fm.module_name,
                    fm.package_name, fm.imports_count, fm.exports_count,
                    fm.references_in_count, fm.references_out_count,
                    fm.complexity_score, fm.quality_score, fm.last_modified,
                    fm.analyzed_at, fc.category_name
                FROM file_metadata fm
                LEFT JOIN file_categories fc ON fm.category_id = fc.id
                WHERE fm.file_path = %s
            """, (file_path,))

            row = cursor.fetchone()

            if row:
                columns = [desc[0] for desc in cursor.description]
                result = dict(zip(columns, row))

                # 转换datetime为字符串
                for key, value in result.items():
                    if isinstance(value, datetime):
                        result[key] = value.strftime('%Y-%m-%d %H:%M:%S')

                cursor.close()
                return result

            cursor.close()
            return None

        except Exception as e:
            logger.error(f"查询文件失败: {e}")
            cursor.close()
            return None

    def get_file_references(self, file_id: int) -> List[Dict]:
        """获取文件的引用关系"""
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    fr.id, fr.reference_type, fr.reference_line,
                    fr.reference_code, fr.is_external, fr.is_valid,
                    fr.validation_message,
                    source.file_name as source_file,
                    target.file_name as target_file
                FROM file_references fr
                JOIN file_metadata source ON fr.source_file_id = source.id
                JOIN file_metadata target ON fr.target_file_id = target.id
                WHERE fr.source_file_id = %s OR fr.target_file_id = %s
                ORDER BY fr.reference_line
            """, (file_id, file_id))

            columns = [desc[0] for desc in cursor.description]
            results = []

            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            cursor.close()
            return results

        except Exception as e:
            logger.error(f"查询引用关系失败: {e}")
            cursor.close()
            return []

    def get_files_by_category(self, category_code: str) -> List[Dict]:
        """根据分类查询文件"""
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    fm.id, fm.file_name, fm.file_path, fm.file_type,
                    fm.line_count, fm.function_count, fm.complexity_score,
                    fc.category_name
                FROM file_metadata fm
                JOIN file_categories fc ON fm.category_id = fc.id
                WHERE fc.category_code = %s
                ORDER BY fm.complexity_score DESC
            """, (category_code,))

            columns = [desc[0] for desc in cursor.description]
            results = []

            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            cursor.close()
            return results

        except Exception as e:
            logger.error(f"查询分类文件失败: {e}")
            cursor.close()
            return []

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM file_statistics
            """)

            columns = [desc[0] for desc in cursor.description]
            results = []

            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            cursor.close()
            return results

        except Exception as e:
            logger.error(f"查询统计信息失败: {e}")
            cursor.close()
            return []

    def get_latest_analysis_run(self) -> Optional[Dict]:
        """获取最新的分析运行记录"""
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM analysis_runs
                ORDER BY start_time DESC
                LIMIT 1
            """)

            row = cursor.fetchone()

            if row:
                columns = [desc[0] for desc in cursor.description]
                result = dict(zip(columns, row))

                # 转换datetime为字符串
                for key, value in result.items():
                    if isinstance(value, datetime):
                        result[key] = value.strftime('%Y-%m-%d %H:%M:%S')

                cursor.close()
                return result

            cursor.close()
            return None

        except Exception as e:
            logger.error(f"查询分析运行记录失败: {e}")
            cursor.close()
            return None

    def get_most_referenced_files(self, limit: int = 10) -> List[Dict]:
        """获取被引用最多的文件"""
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    fm.id, fm.file_name, fm.file_path, fm.file_type,
                    fm.references_in_count, fm.references_out_count,
                    fm.complexity_score
                FROM file_metadata fm
                WHERE fm.references_in_count > 0
                ORDER BY fm.references_in_count DESC
                LIMIT %s
            """, (limit,))

            columns = [desc[0] for desc in cursor.description]
            results = []

            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            cursor.close()
            return results

        except Exception as e:
            logger.error(f"查询被引用最多的文件失败: {e}")
            cursor.close()
            return []


def print_file_info(file_info: Dict):
    """打印文件信息"""
    print("\n" + "=" * 80)
    print(f"文件信息: {file_info['file_name']}")
    print("=" * 80)
    print(f"文件路径: {file_info['file_path']}")
    print(f"文件类型: {file_info['file_type']}")
    print(f"分类: {file_info['category_name']}")
    print(f"文件大小: {file_info['file_size']} bytes")
    print(f"行数: {file_info['line_count']}")
    print(f"函数数: {file_info['function_count']}")
    print(f"类数: {file_info['class_count']}")
    print(f"功能描述: {file_info['file_function']}")
    print(f"模块名: {file_info['module_name']}")
    print(f"包名: {file_info['package_name']}")
    print(f"导入数: {file_info['imports_count']}")
    print(f"导出数: {file_info['exports_count']}")
    print(f"被引用次数: {file_info['references_in_count']}")
    print(f"引用次数: {file_info['references_out_count']}")
    print(f"复杂度: {file_info['complexity_score']}")
    print(f"质量评分: {file_info['quality_score']}")
    print(f"最后修改: {file_info['last_modified']}")
    print(f"分析时间: {file_info['analyzed_at']}")
    print("=" * 80)


def print_references(references: List[Dict]):
    """打印引用关系"""
    if not references:
        print("\n无引用关系")
        return

    print("\n" + "=" * 80)
    print("引用关系")
    print("=" * 80)

    for ref in references:
        print(f"\n类型: {ref['reference_type']}")
        print(f"源文件: {ref['source_file']}")
        print(f"目标文件: {ref['target_file']}")
        print(f"行号: {ref['reference_line']}")
        print(f"代码: {ref['reference_code']}")
        print(f"是否有效: {ref['is_valid']}")
        print(f"是否外部: {ref['is_external']}")
        print(f"验证信息: {ref['validation_message']}")

    print("=" * 80)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='文件信息查询工具')
    subparsers = parser.add_subparsers(dest='command', help='查询命令')

    # 按文件名查询
    name_parser = subparsers.add_parser('name', help='按文件名查询')
    name_parser.add_argument('name', help='文件名（支持模糊匹配）')

    # 按路径查询
    path_parser = subparsers.add_parser('path', help='按文件路径查询')
    path_parser.add_argument('path', help='文件路径')

    # 按分类查询
    category_parser = subparsers.add_parser('category', help='按分类查询')
    category_parser.add_argument('category', help='分类代码')

    # 统计信息
    subparsers.add_parser('stats', help='查看统计信息')

    # 最新分析记录
    subparsers.add_parser('latest', help='查看最新分析记录')

    # 被引用最多的文件
    top_parser = subparsers.add_parser('top', help='查看被引用最多的文件')
    top_parser.add_argument('--limit', type=int, default=10, help='返回数量')

    # JSON输出
    parser.add_argument('--json', action='store_true', help='以JSON格式输出')

    args = parser.parse_args()

    # 创建查询工具
    tool = FileQueryTool()

    if not tool.connect():
        return 1

    try:
        if args.command == 'name':
            results = tool.get_file_by_name(args.name)

            if args.json:
                print(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                for result in results:
                    print_file_info(result)

        elif args.command == 'path':
            result = tool.get_file_by_path(args.path)

            if result:
                if args.json:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print_file_info(result)
                    references = tool.get_file_references(result['id'])
                    print_references(references)
            else:
                print("未找到文件")

        elif args.command == 'category':
            results = tool.get_files_by_category(args.category)

            if args.json:
                print(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                print(f"\n分类 {args.category} 的文件:")
                for result in results:
                    print(f"  - {result['file_name']} ({result['file_path']})")

        elif args.command == 'stats':
            results = tool.get_statistics()

            if args.json:
                print(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                print("\n文件统计信息:")
                for result in results:
                    print(f"\n分类: {result['category_name']}")
                    print(f"  类型: {result['file_type']}")
                    print(f"  文件数: {result['file_count']}")
                    print(f"  总行数: {result['total_lines']}")
                    print(f"  函数数: {result['total_functions']}")
                    print(f"  类数: {result['total_classes']}")
                    print(f"  平均复杂度: {result['avg_complexity']:.2f}")
                    print(f"  平均质量: {result['avg_quality']:.2f}")

        elif args.command == 'latest':
            result = tool.get_latest_analysis_run()

            if result:
                if args.json:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print("\n最新分析运行记录:")
                    for key, value in result.items():
                        print(f"  {key}: {value}")
            else:
                print("未找到分析记录")

        elif args.command == 'top':
            results = tool.get_most_referenced_files(args.limit)

            if args.json:
                print(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                print(f"\n被引用最多的{args.limit}个文件:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result['file_name']}")
                    print(f"   路径: {result['file_path']}")
                    print(f"   被引用次数: {result['references_in_count']}")
                    print(f"   引用次数: {result['references_out_count']}")
                    print(f"   复杂度: {result['complexity_score']}")

        else:
            parser.print_help()

        return 0

    except Exception as e:
        logger.error(f"查询失败: {e}")
        return 1

    finally:
        tool.close()


if __name__ == '__main__':
    sys.exit(main())
