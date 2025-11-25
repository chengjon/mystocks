#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库评估脚本
评估所有数据库的实际使用情况

用途: Week 2 Day 1 - 数据库使用情况评估
输出: database_assessment_YYYYMMDD_HHMMSS.json
"""
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
import json

# 添加项目根目录到路径
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

try:
    from src.data_access import (
        TDengineDataAccess,
        PostgreSQLDataAccess,
        MySQLDataAccess,
        RedisDataAccess,
    )
except ImportError as e:
    print(f"警告: 无法导入数据访问模块: {e}")
    print("尝试从db_manager导入...")
    from src.storage.database.database_manager import DatabaseTableManager


class DatabaseAssessor:
    """数据库评估器"""

    def __init__(self):
        self.results = {"assessment_time": datetime.now().isoformat(), "databases": {}}

    def assess_tdengine(self) -> Dict[str, Any]:
        """评估TDengine使用情况"""
        print("\n" + "=" * 60)
        print("评估 TDengine")
        print("=" * 60)

        try:
            td = TDengineDataAccess()

            results = {
                "status": "success",
                "databases": [],
                "total_size_mb": 0,
                "total_rows": 0,
                "tables": [],
                "connection": "✓ 连接成功",
            }

            # 获取数据库列表
            try:
                databases = td.execute("SHOW DATABASES")
                print(f"数据库数量: {len(databases)}")

                # 评估每个数据库
                for db in databases:
                    db_name = db[0]
                    # 跳过系统数据库
                    if (
                        db_name.startswith("information_schema")
                        or db_name == "performance_schema"
                        or db_name == "log"
                    ):
                        continue

                    print(f"\n数据库: {db_name}")
                    td.execute(f"USE {db_name}")

                    # 获取表列表
                    tables = td.execute("SHOW TABLES")
                    print(f"  表数量: {len(tables)}")

                    db_info = {
                        "name": db_name,
                        "table_count": len(tables),
                        "tables": [],
                    }

                    # 评估每个表
                    for table in tables:
                        table_name = table[0]

                        try:
                            # 获取行数
                            count_result = td.execute(
                                f"SELECT COUNT(*) FROM `{table_name}`"
                            )
                            row_count = count_result[0][0] if count_result else 0

                            # 粗略估算大小（TDengine压缩比很高）
                            estimated_size_mb = row_count * 0.0001  # 假设每行100字节

                            table_info = {
                                "name": table_name,
                                "rows": row_count,
                                "estimated_size_mb": round(estimated_size_mb, 2),
                            }

                            db_info["tables"].append(table_info)
                            results["total_rows"] += row_count
                            results["total_size_mb"] += estimated_size_mb

                            print(
                                f"    {table_name}: {row_count:,} 行, ~{estimated_size_mb:.2f} MB"
                            )
                        except Exception as e:
                            print(f"    {table_name}: 评估失败 - {e}")

                    results["databases"].append(db_info)

            except Exception as e:
                print(f"评估TDengine表结构失败: {e}")
                results["error"] = str(e)

            print(f"\nTDengine 总计:")
            print(f"  总大小: ~{results['total_size_mb']:.2f} MB")
            print(f"  总行数: {results['total_rows']:,}")

            return results

        except Exception as e:
            print(f"✗ TDengine连接失败: {e}")
            return {"status": "error", "connection": "✗ 连接失败", "message": str(e)}

    def assess_postgresql(self) -> Dict[str, Any]:
        """评估PostgreSQL使用情况"""
        print("\n" + "=" * 60)
        print("评估 PostgreSQL")
        print("=" * 60)

        try:
            pg = PostgreSQLDataAccess()

            results = {
                "status": "success",
                "total_size_mb": 0,
                "total_rows": 0,
                "tables": [],
                "connection": "✓ 连接成功",
            }

            # 获取所有表的信息
            query = """
                SELECT
                    schemaname,
                    tablename,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes,
                    n_live_tup as row_count
                FROM pg_stat_user_tables
                ORDER BY size_bytes DESC;
            """

            tables = pg.execute(query)
            print(f"用户表数量: {len(tables)}")

            for table in tables:
                schema, name, size_bytes, rows = table
                size_mb = (size_bytes or 0) / 1024 / 1024
                row_count = rows or 0

                results["tables"].append(
                    {
                        "schema": schema,
                        "name": name,
                        "size_mb": round(size_mb, 2),
                        "rows": row_count,
                    }
                )

                results["total_size_mb"] += size_mb
                results["total_rows"] += row_count

                print(f"  {schema}.{name}: {size_mb:.2f} MB, {row_count:,} 行")

            print(f"\nPostgreSQL 总计:")
            print(f"  总大小: {results['total_size_mb']:.2f} MB")
            print(f"  总行数: {results['total_rows']:,}")

            return results

        except Exception as e:
            print(f"✗ PostgreSQL连接失败: {e}")
            return {"status": "error", "connection": "✗ 连接失败", "message": str(e)}

    def assess_mysql(self) -> Dict[str, Any]:
        """评估MySQL使用情况"""
        print("\n" + "=" * 60)
        print("评估 MySQL")
        print("=" * 60)

        try:
            mysql = MySQLDataAccess()

            results = {
                "status": "success",
                "database": None,
                "total_size_mb": 0,
                "total_rows": 0,
                "tables": [],
                "connection": "✓ 连接成功",
            }

            # 获取当前数据库
            current_db_result = mysql.execute("SELECT DATABASE()")
            current_db = current_db_result[0][0] if current_db_result else None
            results["database"] = current_db

            print(f"当前数据库: {current_db}")

            if current_db:
                # 获取表信息
                query = """
                    SELECT
                        table_name,
                        table_rows,
                        data_length,
                        index_length
                    FROM information_schema.TABLES
                    WHERE table_schema = %s
                    ORDER BY data_length DESC;
                """

                tables = mysql.execute(query, (current_db,))
                print(f"表数量: {len(tables)}")

                for table in tables:
                    name, rows, data_len, index_len = table
                    total_size = ((data_len or 0) + (index_len or 0)) / 1024 / 1024
                    row_count = rows or 0

                    results["tables"].append(
                        {
                            "name": name,
                            "rows": row_count,
                            "size_mb": round(total_size, 2),
                        }
                    )

                    results["total_size_mb"] += total_size
                    results["total_rows"] += row_count

                    print(f"  {name}: {total_size:.2f} MB, {row_count:,} 行")

            print(f"\nMySQL 总计:")
            print(f"  总大小: {results['total_size_mb']:.2f} MB")
            print(f"  总行数: {results['total_rows']:,}")

            return results

        except Exception as e:
            print(f"✗ MySQL连接失败: {e}")
            return {"status": "error", "connection": "✗ 连接失败", "message": str(e)}

    def assess_redis(self) -> Dict[str, Any]:
        """评估Redis使用情况"""
        print("\n" + "=" * 60)
        print("评估 Redis")
        print("=" * 60)

        try:
            redis = RedisDataAccess()

            results = {
                "status": "success",
                "total_keys": 0,
                "used_memory": "0",
                "sample_keys": [],
                "connection": "✓ 连接成功",
            }

            # 获取基本信息
            info = redis.client.info()

            # 获取key数量
            db_keys = redis.client.dbsize()
            results["total_keys"] = db_keys

            # 获取内存使用
            used_memory = info.get("used_memory_human", "Unknown")
            results["used_memory"] = used_memory

            print(f"总Key数量: {db_keys:,}")
            print(f"内存使用: {used_memory}")

            # 采样一些keys
            if db_keys > 0:
                sample_keys = []
                for key in redis.client.scan_iter(count=100):
                    key_type = redis.client.type(key).decode("utf-8")
                    key_str = (
                        key.decode("utf-8") if isinstance(key, bytes) else str(key)
                    )
                    sample_keys.append({"key": key_str, "type": key_type})
                    if len(sample_keys) >= 100:
                        break

                results["sample_keys"] = sample_keys[:10]  # 只保存前10个样本

                print(f"\nKey样本 (前5个):")
                for key in sample_keys[:5]:
                    print(f"  - {key['key']} ({key['type']})")
            else:
                print("\n没有找到任何Key")

            return results

        except Exception as e:
            print(f"✗ Redis连接失败: {e}")
            return {"status": "error", "connection": "✗ 连接失败", "message": str(e)}

    def generate_report(self):
        """生成评估报告"""
        print("\n" + "=" * 60)
        print("开始数据库评估")
        print("=" * 60)

        # 评估所有数据库
        self.results["databases"]["tdengine"] = self.assess_tdengine()
        self.results["databases"]["postgresql"] = self.assess_postgresql()
        self.results["databases"]["mysql"] = self.assess_mysql()
        self.results["databases"]["redis"] = self.assess_redis()

        # 生成总结
        print("\n" + "=" * 60)
        print("评估总结")
        print("=" * 60)

        total_size = 0
        total_rows = 0
        successful_connections = 0

        for db_name, db_result in self.results["databases"].items():
            print(f"\n{db_name.upper()}:")
            if db_result.get("status") == "success":
                successful_connections += 1
                size = db_result.get("total_size_mb", 0)
                rows = db_result.get("total_rows", 0)
                total_size += size
                total_rows += rows

                print(f"  状态: {db_result.get('connection', '未知')}")
                print(f"  大小: {size:.2f} MB")
                print(f"  行数: {rows:,}")
            else:
                print(f"  状态: {db_result.get('connection', '✗ 失败')}")
                print(f"  错误: {db_result.get('message', '未知错误')}")

        print(f"\n" + "=" * 60)
        print(f"总计 ({successful_connections}/4 数据库成功连接):")
        print(f"  总大小: {total_size:.2f} MB (~{total_size/1024:.2f} GB)")
        print(f"  总行数: {total_rows:,}")
        print("=" * 60)

        # 保存结果
        report_file = (
            f"database_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n详细报告已保存到: {report_file}")

        # 生成简单的建议
        print("\n" + "=" * 60)
        print("初步建议")
        print("=" * 60)

        if total_size < 100:  # 小于100MB
            print("✓ 数据量很小(<100MB)，单一PostgreSQL数据库即可满足需求")
        elif total_size < 1024:  # 小于1GB
            print("✓ 数据量较小(<1GB)，单一PostgreSQL数据库完全足够")
        elif total_size < 10240:  # 小于10GB
            print("⚠ 数据量中等(<10GB)，PostgreSQL + TimescaleDB可以满足")
        else:
            print("⚠ 数据量较大(>10GB)，需要仔细评估数据库策略")

        print("\n下一步:")
        print("  1. 查看详细报告: cat", report_file)
        print("  2. 分析查询模式: python3 scripts/week2/analyze_query_patterns.py")
        print("  3. 完整备份数据: ./scripts/week2/backup_all_databases.sh")

        return self.results


def main():
    """主函数"""
    print("=" * 60)
    print("MyStocks 数据库评估工具")
    print("Week 2 Day 1 - 数据库使用情况评估")
    print("=" * 60)

    assessor = DatabaseAssessor()
    assessor.generate_report()


if __name__ == "__main__":
    main()
