"""
数据迁移工具模块
提供通用的数据迁移函数，用于架构优化过程中的数据迁移任务

主要功能:
- MySQL → PostgreSQL 数据迁移
- 数据验证和校验
- 迁移进度跟踪
- 回滚机制
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import psycopg2
import pandas as pd
from config.logging_config import logger, log_performance


class MigrationError(Exception):
    """迁移错误异常"""

    pass


class MigrationUtils:
    """数据迁移工具类"""

    def __init__(self):
        """初始化迁移工具"""
        self.source_conn = None
        self.target_conn = None
        self.migration_log = []

        # 从环境变量获取数据库配置
        self.pg_config = {
            "host": os.getenv("POSTGRESQL_HOST", "localhost"),
            "port": int(os.getenv("POSTGRESQL_PORT", "5432")),
            "user": os.getenv("POSTGRESQL_USER", "postgres"),
            "password": os.getenv("POSTGRESQL_PASSWORD", ""),
            "database": os.getenv("POSTGRESQL_DATABASE", "mystocks"),
        }

        logger.info("MigrationUtils 初始化完成")

    def connect_postgresql(self) -> psycopg2.extensions.connection:
        """
        连接 PostgreSQL 数据库

        Returns:
            数据库连接对象
        """
        try:
            conn = psycopg2.connect(**self.pg_config)
            logger.info(f"成功连接到 PostgreSQL: {self.pg_config['database']}")
            return conn
        except Exception as e:
            logger.error(f"连接 PostgreSQL 失败: {e}")
            raise MigrationError(f"无法连接到 PostgreSQL: {e}")

    @log_performance
    def migrate_table(
        self,
        source_table: str,
        target_table: str,
        source_conn: Any,
        batch_size: int = 1000,
        transform_func: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """
        迁移单个表的数据

        Args:
            source_table: 源表名
            target_table: 目标表名
            source_conn: 源数据库连接
            batch_size: 批处理大小
            transform_func: 数据转换函数 (可选)

        Returns:
            迁移结果字典
        """
        logger.info(f"开始迁移表: {source_table} → {target_table}")

        try:
            # 1. 从源数据库读取数据
            logger.info(f"从 {source_table} 读取数据...")
            df = pd.read_sql(f"SELECT * FROM {source_table}", source_conn)
            total_rows = len(df)
            logger.info(f"读取到 {total_rows} 行数据")

            if total_rows == 0:
                logger.warning(f"{source_table} 表为空，跳过迁移")
                return {
                    "source_table": source_table,
                    "target_table": target_table,
                    "rows_migrated": 0,
                    "status": "skipped",
                    "message": "源表为空",
                }

            # 2. 数据转换 (如果提供了转换函数)
            if transform_func:
                logger.info("应用数据转换...")
                df = transform_func(df)

            # 3. 连接目标数据库
            target_conn = self.connect_postgresql()
            cursor = target_conn.cursor()

            # 4. 批量插入数据
            logger.info(f"开始批量插入到 {target_table}...")
            migrated_rows = 0

            for start_idx in range(0, total_rows, batch_size):
                end_idx = min(start_idx + batch_size, total_rows)
                batch_df = df.iloc[start_idx:end_idx]

                # 生成INSERT语句
                columns = ", ".join(batch_df.columns)
                placeholders = ", ".join(["%s"] * len(batch_df.columns))

                insert_sql = (
                    f"INSERT INTO {target_table} ({columns}) VALUES ({placeholders})"
                )

                # 执行批量插入
                for _, row in batch_df.iterrows():
                    try:
                        cursor.execute(insert_sql, tuple(row))
                        migrated_rows += 1
                    except Exception as e:
                        logger.error(f"插入行失败: {e}, 行数据: {row.to_dict()}")
                        # 继续处理下一行

                target_conn.commit()
                logger.info(f"已迁移 {migrated_rows}/{total_rows} 行")

            # 5. 关闭连接
            cursor.close()
            target_conn.close()

            logger.success(f"表 {source_table} 迁移完成，共 {migrated_rows} 行")

            return {
                "source_table": source_table,
                "target_table": target_table,
                "total_rows": total_rows,
                "rows_migrated": migrated_rows,
                "status": "success",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"迁移表 {source_table} 失败: {e}")
            return {
                "source_table": source_table,
                "target_table": target_table,
                "rows_migrated": 0,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    @log_performance
    def validate_migration(
        self,
        source_table: str,
        target_table: str,
        source_conn: Any,
        check_row_count: bool = True,
        check_checksum: bool = False,
    ) -> Dict[str, Any]:
        """
        验证迁移结果

        Args:
            source_table: 源表名
            target_table: 目标表名
            source_conn: 源数据库连接
            check_row_count: 是否检查行数
            check_checksum: 是否检查校验和

        Returns:
            验证结果字典
        """
        logger.info(f"开始验证迁移: {source_table} → {target_table}")

        try:
            target_conn = self.connect_postgresql()
            cursor = target_conn.cursor()

            # 1. 检查行数
            if check_row_count:
                source_count = pd.read_sql(
                    f"SELECT COUNT(*) as count FROM {source_table}", source_conn
                ).iloc[0]["count"]

                cursor.execute(f"SELECT COUNT(*) FROM {target_table}")
                target_count = cursor.fetchone()[0]

                if source_count != target_count:
                    logger.error(f"行数不匹配: 源={source_count}, 目标={target_count}")
                    return {
                        "status": "failed",
                        "source_count": source_count,
                        "target_count": target_count,
                        "message": "行数不匹配",
                    }

                logger.info(f"行数验证通过: {source_count} 行")

            # 2. 检查校验和 (简化版本，仅检查数值列总和)
            if check_checksum:
                logger.info("校验和检查暂未实现")
                # TODO: 实现校验和检查

            cursor.close()
            target_conn.close()

            logger.success(f"迁移验证通过: {source_table} → {target_table}")

            return {
                "status": "success",
                "source_table": source_table,
                "target_table": target_table,
                "checks_passed": ["row_count"] if check_row_count else [],
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"验证失败: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def create_backup(self, table_name: str, backup_suffix: str = "backup") -> bool:
        """
        创建表备份

        Args:
            table_name: 表名
            backup_suffix: 备份后缀

        Returns:
            是否成功
        """
        try:
            conn = self.connect_postgresql()
            cursor = conn.cursor()

            backup_table = f"{table_name}_{backup_suffix}"
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {backup_table} AS SELECT * FROM {table_name}"
            )

            conn.commit()
            cursor.close()
            conn.close()

            logger.success(f"表备份成功: {table_name} → {backup_table}")
            return True

        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            return False

    def rollback_migration(self, backup_table: str, target_table: str) -> bool:
        """
        回滚迁移 (从备份恢复)

        Args:
            backup_table: 备份表名
            target_table: 目标表名

        Returns:
            是否成功
        """
        try:
            conn = self.connect_postgresql()
            cursor = conn.cursor()

            # 1. 删除目标表
            cursor.execute(f"DROP TABLE IF EXISTS {target_table}")

            # 2. 重命名备份表
            cursor.execute(f"ALTER TABLE {backup_table} RENAME TO {target_table}")

            conn.commit()
            cursor.close()
            conn.close()

            logger.success(f"回滚成功: {backup_table} → {target_table}")
            return True

        except Exception as e:
            logger.error(f"回滚失败: {e}")
            return False

    @log_performance
    def migrate_multiple_tables(
        self,
        table_mapping: Dict[str, str],
        source_conn: Any,
        batch_size: int = 1000,
        validate: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        迁移多个表

        Args:
            table_mapping: 表映射字典 {源表名: 目标表名}
            source_conn: 源数据库连接
            batch_size: 批处理大小
            validate: 是否验证迁移结果

        Returns:
            迁移结果列表
        """
        results = []

        for source_table, target_table in table_mapping.items():
            logger.info(f"迁移表 {source_table} → {target_table}")

            # 1. 迁移数据
            result = self.migrate_table(
                source_table, target_table, source_conn, batch_size
            )
            results.append(result)

            # 2. 验证迁移结果
            if validate and result["status"] == "success":
                validation_result = self.validate_migration(
                    source_table, target_table, source_conn
                )

                if validation_result["status"] != "success":
                    logger.error(f"表 {source_table} 验证失败")
                    result["validation"] = validation_result
                else:
                    logger.success(f"表 {source_table} 验证通过")

        return results

    def generate_migration_report(
        self, results: List[Dict[str, Any]], output_file: Optional[str] = None
    ) -> str:
        """
        生成迁移报告

        Args:
            results: 迁移结果列表
            output_file: 输出文件路径 (可选)

        Returns:
            报告内容
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("数据迁移报告")
        report_lines.append(f"生成时间: {datetime.now().isoformat()}")
        report_lines.append("=" * 60)
        report_lines.append("")

        # 统计
        total_tables = len(results)
        success_count = sum(1 for r in results if r["status"] == "success")
        failed_count = total_tables - success_count
        total_rows = sum(r.get("rows_migrated", 0) for r in results)

        report_lines.append("## 总览")
        report_lines.append(f"总表数: {total_tables}")
        report_lines.append(f"成功: {success_count}")
        report_lines.append(f"失败: {failed_count}")
        report_lines.append(f"迁移总行数: {total_rows}")
        report_lines.append("")

        # 详细结果
        report_lines.append("## 详细结果")
        for result in results:
            status_icon = "✅" if result["status"] == "success" else "❌"
            report_lines.append(
                f"{status_icon} {result['source_table']} → {result['target_table']}: "
                f"{result.get('rows_migrated', 0)} 行"
            )

            if result["status"] == "failed":
                report_lines.append(f"   错误: {result.get('error', 'Unknown')}")

        report_lines.append("")
        report_lines.append("=" * 60)

        report = "\n".join(report_lines)

        # 输出到文件
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info(f"迁移报告已保存到: {output_file}")

        return report


# 便捷函数
def quick_migrate(
    source_conn: Any, table_mapping: Dict[str, str], validate: bool = True
) -> List[Dict[str, Any]]:
    """
    快速迁移函数

    Args:
        source_conn: 源数据库连接
        table_mapping: 表映射字典
        validate: 是否验证

    Returns:
        迁移结果列表
    """
    utils = MigrationUtils()
    results = utils.migrate_multiple_tables(
        source_conn, table_mapping, validate=validate
    )

    # 生成报告
    report = utils.generate_migration_report(results)
    print(report)

    return results


if __name__ == "__main__":
    # 示例用法
    logger.info("数据迁移工具模块测试")

    # 创建工具实例
    utils = MigrationUtils()

    # 测试连接
    try:
        conn = utils.connect_postgresql()
        logger.success("PostgreSQL 连接测试成功")
        conn.close()
    except Exception as e:
        logger.error(f"PostgreSQL 连接测试失败: {e}")
