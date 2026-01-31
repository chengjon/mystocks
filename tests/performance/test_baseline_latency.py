#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能基准测试套件
测量架构优化前的系统性能基线

测试目标:
- PostgreSQL 批量插入延迟 (1000条记录)
- TDengine 批量插入延迟 (1000条记录)
- 查询性能基线
- 连接建立开销

基线目标: 1000条记录保存 ≤120ms
优化目标: 1000条记录保存 ≤80ms (提升33%)
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict

import pandas as pd
import psycopg2
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class PerformanceBaseline:
    """性能基准测试类"""

    def __init__(self):
        """初始化测试环境"""
        self.results = {
            "测试时间": datetime.now().isoformat(),
            "测试环境": {
                "Python版本": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "Pandas版本": pd.__version__,
            },
            "数据库连接": {},
            "性能指标": {},
        }

        # PostgreSQL 配置
        self.pg_config = {
            "host": os.getenv("POSTGRESQL_HOST", "localhost"),
            "port": int(os.getenv("POSTGRESQL_PORT", "5432")),
            "user": os.getenv("POSTGRESQL_USER", "postgres"),
            "password": os.getenv("POSTGRESQL_PASSWORD", ""),
            "database": os.getenv("POSTGRESQL_DATABASE", "mystocks"),
        }

        # TDengine 配置
        self.td_config = {
            "host": os.getenv("TDENGINE_HOST", "localhost"),
            "port": int(os.getenv("TDENGINE_PORT", "6030")),
            "user": os.getenv("TDENGINE_USER", "root"),
            "password": os.getenv("TDENGINE_PASSWORD", "taosdata"),
            "database": os.getenv("TDENGINE_DATABASE", "market_data"),
        }

    def generate_test_data(self, n_rows: int = 1000) -> pd.DataFrame:
        """
        生成测试数据

        Args:
            n_rows: 数据行数

        Returns:
            测试数据DataFrame
        """
        base_time = datetime.now()
        data = {
            "timestamp": [base_time + timedelta(seconds=i) for i in range(n_rows)],
            "symbol": [f"60000{i % 10}" for i in range(n_rows)],
            "price": [100.0 + (i % 50) * 0.1 for i in range(n_rows)],
            "volume": [1000 * (i % 100 + 1) for i in range(n_rows)],
            "amount": [100000.0 * (i % 100 + 1) for i in range(n_rows)],
        }
        return pd.DataFrame(data)

    def benchmark_postgresql_insert(self, n_rows: int = 1000) -> Dict[str, Any]:
        """
        测试 PostgreSQL 批量插入性能

        Args:
            n_rows: 插入行数

        Returns:
            性能指标字典
        """
        print(f"\n{'=' * 60}")
        print(f"PostgreSQL 批量插入性能测试 ({n_rows}条记录)")
        print(f"{'=' * 60}")

        try:
            # 生成测试数据
            df = self.generate_test_data(n_rows)
            print(f"✓ 测试数据生成完成: {len(df)} 行")

            # 连接数据库
            start_conn = time.time()
            conn = psycopg2.connect(**self.pg_config)
            cursor = conn.cursor()
            conn_time = (time.time() - start_conn) * 1000
            print(f"✓ 数据库连接建立: {conn_time:.2f}ms")

            # 创建临时测试表
            cursor.execute("DROP TABLE IF EXISTS test_baseline_performance")
            cursor.execute(
                """
                CREATE TABLE test_baseline_performance (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    symbol VARCHAR(20),
                    price NUMERIC(10, 2),
                    volume INTEGER,
                    amount NUMERIC(15, 2)
                )
            """
            )
            conn.commit()
            print("✓ 测试表创建完成")

            # 批量插入测试
            start_insert = time.time()
            insert_sql = """
                INSERT INTO test_baseline_performance (timestamp, symbol, price, volume, amount)
                VALUES (%s, %s, %s, %s, %s)
            """

            for _, row in df.iterrows():
                cursor.execute(
                    insert_sql,
                    (
                        row["timestamp"],
                        row["symbol"],
                        row["price"],
                        row["volume"],
                        row["amount"],
                    ),
                )

            conn.commit()
            insert_time = (time.time() - start_insert) * 1000
            print(f"✓ 批量插入完成: {insert_time:.2f}ms")

            # 查询验证
            start_query = time.time()
            cursor.execute("SELECT COUNT(*) FROM test_baseline_performance")
            count = cursor.fetchone()[0]
            query_time = (time.time() - start_query) * 1000
            print(f"✓ 查询验证完成: {count} 行, {query_time:.2f}ms")

            # 清理测试表
            cursor.execute("DROP TABLE test_baseline_performance")
            conn.commit()

            cursor.close()
            conn.close()

            result = {
                "状态": "成功",
                "记录数": n_rows,
                "连接时间_ms": round(conn_time, 2),
                "插入时间_ms": round(insert_time, 2),
                "查询时间_ms": round(query_time, 2),
                "总时间_ms": round(conn_time + insert_time + query_time, 2),
                "平均插入速度_条秒": round(n_rows / (insert_time / 1000), 2),
            }

            # 判断是否满足基线目标
            if insert_time <= 120:
                print(f"\n✓ 性能满足基线目标: {insert_time:.2f}ms ≤ 120ms")
            else:
                print(f"\n⚠ 性能未达基线目标: {insert_time:.2f}ms > 120ms")

            return result

        except Exception as e:
            print(f"✗ PostgreSQL 测试失败: {e}")
            return {"状态": "失败", "错误": str(e)}

    def benchmark_tdengine_insert(self, n_rows: int = 1000) -> Dict[str, Any]:
        """
        测试 TDengine 批量插入性能

        Args:
            n_rows: 插入行数

        Returns:
            性能指标字典
        """
        print(f"\n{'=' * 60}")
        print(f"TDengine 批量插入性能测试 ({n_rows}条记录)")
        print(f"{'=' * 60}")

        try:
            # 尝试导入 TDengine 模块
            try:
                import taos
            except ImportError:
                print("⚠ TDengine 模块未安装，跳过测试")
                return {"状态": "跳过", "原因": "TDengine 模块未安装"}

            # 生成测试数据
            df = self.generate_test_data(n_rows)
            print(f"✓ 测试数据生成完成: {len(df)} 行")

            # 连接数据库
            start_conn = time.time()
            conn = taos.connect(
                host=self.td_config["host"],
                user=self.td_config["user"],
                password=self.td_config["password"],
                port=self.td_config["port"],
            )
            cursor = conn.cursor()
            conn_time = (time.time() - start_conn) * 1000
            print(f"✓ 数据库连接建立: {conn_time:.2f}ms")

            # 创建数据库和超级表
            cursor.execute("CREATE DATABASE IF NOT EXISTS test_baseline")
            cursor.execute("USE test_baseline")
            cursor.execute("DROP TABLE IF EXISTS test_perf")
            cursor.execute(
                """
                CREATE STABLE IF NOT EXISTS test_perf (
                    ts TIMESTAMP,
                    price FLOAT,
                    volume INT,
                    amount FLOAT
                ) TAGS (symbol NCHAR(20))
            """
            )
            print("✓ 测试表创建完成")

            # 批量插入测试
            start_insert = time.time()

            for symbol in df["symbol"].unique():
                # 为每个symbol创建子表
                table_name = f"test_perf_{symbol}"
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} USING test_perf TAGS ('{symbol}')")

                # 插入数据
                symbol_data = df[df["symbol"] == symbol]
                for _, row in symbol_data.iterrows():
                    ts = int(row["timestamp"].timestamp() * 1000)  # 转换为毫秒时间戳
                    cursor.execute(
                        f"INSERT INTO {table_name} VALUES ({ts}, {row['price']}, {row['volume']}, {row['amount']})"
                    )

            insert_time = (time.time() - start_insert) * 1000
            print(f"✓ 批量插入完成: {insert_time:.2f}ms")

            # 查询验证
            start_query = time.time()
            cursor.execute("SELECT COUNT(*) FROM test_perf")
            count = cursor.fetchone()[0]
            query_time = (time.time() - start_query) * 1000
            print(f"✓ 查询验证完成: {count} 行, {query_time:.2f}ms")

            # 清理测试数据
            cursor.execute("DROP DATABASE IF EXISTS test_baseline")

            cursor.close()
            conn.close()

            result = {
                "状态": "成功",
                "记录数": n_rows,
                "连接时间_ms": round(conn_time, 2),
                "插入时间_ms": round(insert_time, 2),
                "查询时间_ms": round(query_time, 2),
                "总时间_ms": round(conn_time + insert_time + query_time, 2),
                "平均插入速度_条秒": round(n_rows / (insert_time / 1000), 2),
            }

            # 判断是否满足基线目标
            if insert_time <= 120:
                print(f"\n✓ 性能满足基线目标: {insert_time:.2f}ms ≤ 120ms")
            else:
                print(f"\n⚠ 性能未达基线目标: {insert_time:.2f}ms > 120ms")

            return result

        except Exception as e:
            print(f"✗ TDengine 测试失败: {e}")
            return {"状态": "失败", "错误": str(e)}

    def run_all_benchmarks(self) -> None:
        """运行所有性能基准测试"""
        print("\n" + "=" * 60)
        print("性能基准测试套件")
        print("=" * 60)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("测试目标: 1000条记录插入 ≤120ms (基线) / ≤80ms (优化目标)")

        # PostgreSQL 测试
        pg_result = self.benchmark_postgresql_insert(1000)
        self.results["性能指标"]["PostgreSQL"] = pg_result
        self.results["数据库连接"]["PostgreSQL"] = "成功" if pg_result.get("状态") == "成功" else "失败"

        # TDengine 测试
        td_result = self.benchmark_tdengine_insert(1000)
        self.results["性能指标"]["TDengine"] = td_result
        self.results["数据库连接"]["TDengine"] = (
            "成功" if td_result.get("状态") == "成功" else td_result.get("状态", "失败")
        )

        # 保存结果
        self._save_results()

        # 显示总结
        self._print_summary()

    def _save_results(self) -> None:
        """保存测试结果到文件"""
        output_dir = "metrics"
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, "baseline_performance.json")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 测试结果已保存到: {output_file}")

    def _print_summary(self) -> None:
        """打印测试总结"""
        print("\n" + "=" * 60)
        print("性能基准测试总结")
        print("=" * 60)

        for db_name, metrics in self.results["性能指标"].items():
            if metrics.get("状态") == "成功":
                print(f"\n{db_name}:")
                print(f"  记录数: {metrics['记录数']} 条")
                print(f"  插入时间: {metrics['插入时间_ms']} ms")
                print(f"  插入速度: {metrics['平均插入速度_条秒']} 条/秒")
                print(f"  查询时间: {metrics['查询时间_ms']} ms")
                print(f"  总时间: {metrics['总时间_ms']} ms")

                # 性能评估
                insert_time = metrics["插入时间_ms"]
                if insert_time <= 80:
                    print("  评估: ✓ 优秀 (≤80ms优化目标)")
                elif insert_time <= 120:
                    print("  评估: ✓ 良好 (≤120ms基线目标)")
                else:
                    print(f"  评估: ⚠ 需优化 (>{120}ms)")
            elif metrics.get("状态") == "跳过":
                print(f"\n{db_name}: ⚠ 跳过 - {metrics.get('原因', '未知')}")
            else:
                print(f"\n{db_name}: ✗ 失败 - {metrics.get('错误', '未知错误')}")

        print("\n" + "=" * 60)


def main():
    """主函数"""
    baseline = PerformanceBaseline()
    baseline.run_all_benchmarks()


if __name__ == "__main__":
    main()
