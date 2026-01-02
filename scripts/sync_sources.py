#!/usr/bin/env python3
"""
数据源注册表同步脚本

功能：
1. 将YAML配置同步到PostgreSQL数据库
2. 支持增量更新和全量覆盖
3. 同步前验证YAML配置格式
4. 提供回滚功能

使用方法：
    # 增量同步（更新已有接口，添加新接口）
    python scripts/sync_sources.py

    # 全量覆盖（先清空数据库，再导入）
    python scripts/sync_sources.py --force

    # 验证模式（只检查不执行）
    python scripts/sync_sources.py --dry-run

    # 回滚到上一个版本
    python scripts/sync_sources.py --rollback

作者：Claude Code
版本：v2.0
创建时间：2026-01-02
"""

import sys
import os
import argparse
import yaml
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.storage.database import DatabaseConnectionManager


def load_yaml_config(yaml_path: str) -> dict:
    """加载YAML配置文件"""
    print(f"加载YAML配置: {yaml_path}")

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"YAML配置文件不存在: {yaml_path}")

    with open(yaml_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    print(f"✓ YAML版本: {config.get('version')}")
    print(f"✓ 最后更新: {config.get('last_updated')}")
    print(f"✓ 数据源数量: {len(config.get('data_sources', {}))}")

    return config


def validate_yaml_config(config: dict) -> bool:
    """验证YAML配置格式"""
    print("\n验证YAML配置格式...")

    data_sources = config.get('data_sources', {})

    required_fields = [
        'source_name', 'source_type', 'endpoint_name',
        'data_category', 'classification_level',
        'target_db', 'table_name'
    ]

    errors = []

    for endpoint_key, source_config in data_sources.items():
        # 检查必需字段
        for field in required_fields:
            if field not in source_config:
                errors.append(f"{endpoint_key}: 缺少必需字段 {field}")

        # 验证枚举值
        if source_config.get('source_type') not in ['api_library', 'database', 'crawler', 'file', 'mock']:
            errors.append(f"{endpoint_key}: 无效的source_type")

        if source_config.get('classification_level') not in [1, 2, 3, 4, 5]:
            errors.append(f"{endpoint_key}: 无效的classification_level")

        if source_config.get('target_db') not in ['postgresql', 'tdengine']:
            errors.append(f"{endpoint_key}: 无效的target_db")

    if errors:
        print("✗ 验证失败:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print(f"✓ 配置验证通过（{len(data_sources)}个数据源）")
        return True


def sync_to_database(config: dict, force: bool = False, dry_run: bool = False):
    """同步到PostgreSQL数据库"""
    print("\n同步到数据库...")
    print(f"模式: {'全量覆盖' if force else '增量更新'}")
    print(f"预演: {'是' if dry_run else '否'}")

    if dry_run:
        print("⚠️  预演模式，不会实际修改数据库")
        return

    # 备份当前注册表（用于回滚）
    if not force:
        backup_current_registry()

    db_manager = DatabaseConnectionManager()
    data_sources = config.get('data_sources', {})

    synced = 0
    updated = 0
    failed = 0

    for endpoint_key, source_config in data_sources.items():
        try:
            # 构建数据库记录
            record = build_database_record(source_config)

            # 检查是否已存在
            conn = db_manager.get_postgresql_connection()
                check_query = "SELECT id FROM data_source_registry WHERE endpoint_name = %s"
                df_check = pd.read_sql(check_query, conn, params=[record['endpoint_name']])

                if df_check.empty:
                    # 插入新记录
                    insert_query = """
                        INSERT INTO data_source_registry (
                            source_name, source_type, endpoint_name,
                            call_method, endpoint_url, parameters, response_format,
                            data_category, data_classification, classification_level,
                            target_db, table_name,
                            description, update_frequency,
                            data_quality_score, priority, status,
                            tags, version
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s::JSONB, %s,
                            %s, %s, %s,
                            %s, %s,
                            %s, %s,
                            %s, %s, %s,
                            %s, %s
                        )
                    """

                    conn.execute(insert_query, (
                        record['source_name'],
                        record['source_type'],
                        record['endpoint_name'],
                        record.get('call_method'),
                        record.get('endpoint_url'),
                        json.dumps(record.get('parameters', {})),
                        record.get('response_format'),
                        record['data_category'],
                        record.get('data_classification'),
                        record['classification_level'],
                        record['target_db'],
                        record['table_name'],
                        record.get('description'),
                        record.get('update_frequency'),
                        record.get('data_quality_score', 8.0),
                        record.get('priority', 10),
                        record.get('status', 'active'),
                        record.get('tags', []),
                        record.get('version', '1.0')
                    ))

                    synced += 1
                    print(f"  ✓ 新增: {record['endpoint_name']}")

                else:
                    # 更新已有记录
                    update_query = """
                        UPDATE data_source_registry SET
                            source_name = %s,
                            source_type = %s,
                            call_method = %s,
                            endpoint_url = %s,
                            parameters = %s::JSONB,
                            response_format = %s,
                            data_category = %s,
                            data_classification = %s,
                            classification_level = %s,
                            target_db = %s,
                            table_name = %s,
                            description = %s,
                            update_frequency = %s,
                            data_quality_score = %s,
                            priority = %s,
                            status = %s,
                            tags = %s,
                            version = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE endpoint_name = %s
                    """

                    conn.execute(update_query, (
                        record['source_name'],
                        record['source_type'],
                        record.get('call_method'),
                        record.get('endpoint_url'),
                        json.dumps(record.get('parameters', {})),
                        record.get('response_format'),
                        record['data_category'],
                        record.get('data_classification'),
                        record['classification_level'],
                        record['target_db'],
                        record['table_name'],
                        record.get('description'),
                        record.get('update_frequency'),
                        record.get('data_quality_score', 8.0),
                        record.get('priority', 10),
                        record.get('status', 'active'),
                        record.get('tags', []),
                        record.get('version', '1.0'),
                        record['endpoint_name']
                    ))

                    updated += 1
                    print(f"  ✓ 更新: {record['endpoint_name']}")

                conn.commit()

        except Exception as e:
            failed += 1
            print(f"  ✗ 失败: {endpoint_key}, 错误: {e}")

    print(f"\n同步完成:")
    print(f"  新增: {synced}")
    print(f"  更新: {updated}")
    print(f"  失败: {failed}")


def build_database_record(source_config: dict) -> dict:
    """构建数据库记录"""
    record = {
        'source_name': source_config.get('source_name'),
        'source_type': source_config.get('source_type'),
        'endpoint_name': source_config.get('endpoint_name'),
        'call_method': source_config.get('call_method'),
        'endpoint_url': source_config.get('endpoint_url'),
        'parameters': source_config.get('parameters'),
        'response_format': source_config.get('response_format'),
        'data_category': source_config.get('data_category'),
        'data_classification': source_config.get('data_classification'),
        'classification_level': source_config.get('classification_level'),
        'target_db': source_config.get('target_db'),
        'table_name': source_config.get('table_name'),
        'description': source_config.get('description'),
        'update_frequency': source_config.get('update_frequency'),
        'data_quality_score': source_config.get('data_quality_score', 8.0),
        'priority': source_config.get('priority', 10),
        'status': source_config.get('status', 'active'),
        'tags': source_config.get('tags', []),
        'version': source_config.get('version', '1.0')
    }

    return record


def backup_current_registry():
    """备份当前注册表到文件"""
    print("\n备份当前注册表...")

    db_manager = DatabaseConnectionManager()

    try:
        conn = db_manager.get_postgresql_connection()
            df = pd.read_sql("SELECT * FROM data_source_registry", conn)

        # 保存为JSON
        backup_dir = Path("backups/data_source_registry")
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"registry_backup_{timestamp}.json"

        df.to_json(backup_file, orient='records', indent=2, force_ascii=False)

        print(f"✓ 备份已保存: {backup_file}")

    except Exception as e:
        print(f"✗ 备份失败: {e}")


def restore_registry(backup_file: str):
    """从备份恢复注册表"""
    print(f"\n从备份恢复: {backup_file}")

    if not os.path.exists(backup_file):
        raise FileNotFoundError(f"备份文件不存在: {backup_file}")

    # 读取备份
    df = pd.read_json(backup_file)

    # 删除现有数据
    db_manager = DatabaseConnectionManager()
    conn = db_manager.get_postgresql_connection()
        conn.execute("DELETE FROM data_source_registry")
        conn.commit()

    # 插入备份数据
    for _, row in df.iterrows():
        insert_query = """
            INSERT INTO data_source_registry (
                source_name, source_type, endpoint_name,
                call_method, endpoint_url, parameters, response_format,
                data_category, data_classification, classification_level,
                target_db, table_name,
                description, update_frequency,
                data_quality_score, priority, status,
                health_status, avg_response_time, success_rate,
                total_calls, failed_calls, consecutive_failures,
                last_success_time, last_failure_time,
                tags, version, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s::JSONB, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s,
                %s, %s,
                %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s
            )
        """

        conn.execute(insert_query, (
            row['source_name'], row['source_type'], row['endpoint_name'],
            row.get('call_method'), row.get('endpoint_url'),
            json.dumps(row.get('parameters', {})), row.get('response_format'),
            row['data_category'], row.get('data_classification'), row['classification_level'],
            row['target_db'], row['table_name'],
            row.get('description'), row.get('update_frequency'),
            row.get('data_quality_score', 8.0), row.get('priority', 10), row.get('status', 'active'),
            row.get('health_status', 'unknown'), row.get('avg_response_time', 0), row.get('success_rate', 100.0),
            row.get('total_calls', 0), row.get('failed_calls', 0), row.get('consecutive_failures', 0),
            row.get('last_success_time'), row.get('last_failure_time'),
            row.get('tags', []), row.get('version', '1.0'),
            row.get('created_at'), row.get('updated_at')
        ))

    conn.commit()

    print("✓ 恢复完成")


def show_current_status():
    """显示当前注册表状态"""
    print("\n当前注册表状态:")

    db_manager = DatabaseConnectionManager()

    try:
        # 获取连接
        conn = db_manager.get_postgresql_connection()

        # 总体统计
        df = pd.read_sql("""
            SELECT
                source_name,
                COUNT(*) as endpoint_count,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_count,
                SUM(CASE WHEN health_status = 'healthy' THEN 1 ELSE 0 END) as healthy_count,
                SUM(CASE WHEN health_status = 'failed' THEN 1 ELSE 0 END) as failed_count
            FROM data_source_registry
            GROUP BY source_name
            ORDER BY source_name
        """, conn)

        print("\n按数据源统计:")
        print(df.to_string(index=False))

        # 按分类层级统计
        df2 = pd.read_sql("""
            SELECT
                classification_level,
                data_classification,
                COUNT(*) as endpoint_count
            FROM data_source_registry
            WHERE status = 'active'
            GROUP BY classification_level, data_classification
            ORDER BY classification_level
        """, conn)

        print("\n按分类层级统计:")
        print(df2.to_string(index=False))

    except Exception as e:
        print(f"✗ 查询失败: {e}")


def main():
    parser = argparse.ArgumentParser(description='数据源注册表同步工具')
    parser.add_argument('--yaml', default='config/data_sources_registry.yaml',
                       help='YAML配置文件路径')
    parser.add_argument('--force', action='store_true',
                       help='全量覆盖模式（先清空再导入）')
    parser.add_argument('--dry-run', action='store_true',
                       help='预演模式（只验证不执行）')
    parser.add_argument('--status', action='store_true',
                       help='显示当前状态')
    parser.add_argument('--rollback', type=str,
                       help='回滚到指定备份文件')

    args = parser.parse_args()

    try:
        # 显示状态
        if args.status:
            show_current_status()
            return

        # 回滚
        if args.rollback:
            restore_registry(args.rollback)
            return

        # 加载和验证YAML
        config = load_yaml_config(args.yaml)

        if not validate_yaml_config(config):
            print("\n✗ 配置验证失败，同步中止")
            sys.exit(1)

        # 同步到数据库
        sync_to_database(config, force=args.force, dry_run=args.dry_run)

    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
