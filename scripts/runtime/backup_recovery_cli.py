#!/usr/bin/env python3
"""
备份恢复命令行工具

使用方法:
    python backup_recovery_cli.py backup tdengine full
    python backup_recovery_cli.py backup postgresql full
    python backup_recovery_cli.py list backups
    python backup_recovery_cli.py restore tdengine backup_id
    python backup_recovery_cli.py verify backup_id
    python backup_recovery_cli.py scheduler start
"""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from src.backup_recovery import (
    BackupManager,
    RecoveryManager,
    BackupScheduler,
    IntegrityChecker,
)


def cmd_backup(args):
    """处理备份命令"""
    backup_mgr = BackupManager()

    if args.database == "tdengine":
        if args.type == "full":
            print("Starting TDengine full backup...")
            metadata = backup_mgr.backup_tdengine_full()

            print(f"\n✅ Backup completed: {metadata.backup_id}")
            print(f"   Status: {metadata.status}")
            print(f"   Size: {metadata.backup_size_bytes / 1024 / 1024:.2f} MB")
            print(f"   Compression ratio: {metadata.compression_ratio:.2f}x")
            print(f"   Tables: {len(metadata.tables_backed_up)}")
            print(f"   Rows: {metadata.total_rows}")
            print(f"   Duration: {metadata.duration_seconds:.2f}s")

            if metadata.error_message:
                print(f"   Error: {metadata.error_message}")
                return 1

            return 0

        elif args.type == "incremental":
            if not args.since:
                print("Error: --since backup_id is required for incremental backup")
                return 1

            print(f"Starting TDengine incremental backup since {args.since}...")
            metadata = backup_mgr.backup_tdengine_incremental(args.since)

            print(f"\n✅ Incremental backup completed: {metadata.backup_id}")
            print(f"   Status: {metadata.status}")
            print(f"   Rows: {metadata.total_rows}")

            if metadata.error_message:
                print(f"   Error: {metadata.error_message}")
                return 1

            return 0

    elif args.database == "postgresql":
        if args.type == "full":
            print("Starting PostgreSQL full backup...")
            metadata = backup_mgr.backup_postgresql_full()

            print(f"\n✅ Backup completed: {metadata.backup_id}")
            print(f"   Status: {metadata.status}")
            print(f"   Size: {metadata.backup_size_bytes / 1024 / 1024:.2f} MB")
            print(f"   Compression ratio: {metadata.compression_ratio:.2f}x")
            print(f"   Tables: {len(metadata.tables_backed_up)}")
            print(f"   Rows: {metadata.total_rows}")

            if metadata.error_message:
                print(f"   Error: {metadata.error_message}")
                return 1

            return 0

    return 1


def cmd_list(args):
    """处理列表命令"""
    backup_mgr = BackupManager()

    if args.resource == "backups":
        backups = backup_mgr.get_backup_list()

        if not backups:
            print("No backups found")
            return 0

        print(f"\nTotal backups: {len(backups)}\n")

        for backup in backups:
            db_label = "TDengine" if backup.database == "tdengine" else "PostgreSQL"
            type_label = "FULL" if backup.backup_type == "full" else "INCR"
            status_label = "✅" if backup.status == "success" else "❌"

            print(f"{status_label} [{db_label}] [{type_label}] {backup.backup_id}")
            print(
                f"    Size: {backup.backup_size_bytes / 1024 / 1024:.2f} MB | Rows: {backup.total_rows}"
            )
            print(f"    Time: {backup.start_time} ~ {backup.end_time}")
            print()

        return 0

    return 1


def cmd_restore(args):
    """处理恢复命令"""
    recovery_mgr = RecoveryManager()

    if args.database == "tdengine":
        if args.type == "full":
            print(f"Restoring TDengine from backup {args.backup_id}...")
            success, message = recovery_mgr.restore_tdengine_from_full_backup(
                args.backup_id,
                dry_run=args.dry_run,
            )

            if success:
                print(f"✅ {message}")
                return 0
            else:
                print(f"❌ {message}")
                return 1

        elif args.type == "pitr":
            if not args.target_time:
                print("Error: --target-time is required for PITR")
                return 1

            try:
                target_dt = datetime.fromisoformat(args.target_time)
            except ValueError:
                print(f"Error: Invalid ISO 8601 datetime format: {args.target_time}")
                return 1

            print(f"Restoring TDengine to point in time: {target_dt}...")
            success, message = recovery_mgr.restore_tdengine_point_in_time(target_dt)

            if success:
                print(f"✅ {message}")
                return 0
            else:
                print(f"❌ {message}")
                return 1

    elif args.database == "postgresql":
        if args.type == "full":
            print(f"Restoring PostgreSQL from backup {args.backup_id}...")
            success, message = recovery_mgr.restore_postgresql_from_full_backup(
                args.backup_id,
                dry_run=args.dry_run,
            )

            if success:
                print(f"✅ {message}")
                return 0
            else:
                print(f"❌ {message}")
                return 1

    return 1


def cmd_verify(args):
    """处理验证命令"""
    backup_mgr = BackupManager()
    integrity_checker = IntegrityChecker()

    # 获取备份元数据
    metadata = backup_mgr._load_metadata(args.backup_id)

    if not metadata:
        print(f"Error: Backup not found: {args.backup_id}")
        return 1

    print(f"Verifying backup integrity: {args.backup_id}...")

    if metadata["database"] == "tdengine":
        is_valid, details = integrity_checker.verify_tdengine_recovery(
            metadata,
            metadata["total_rows"],
        )
    elif metadata["database"] == "postgresql":
        is_valid, details = integrity_checker.verify_postgresql_recovery(
            metadata,
            metadata["total_rows"],
        )
    else:
        print(f"Error: Unknown database: {metadata['database']}")
        return 1

    print(
        f"\n{'✅' if is_valid else '❌'} Verification result: {'PASSED' if is_valid else 'FAILED'}"
    )
    print(f"   Tables checked: {details['tables_checked']}")
    print(f"   Tables passed: {details['tables_passed']}")
    print(f"   Tables failed: {details['tables_failed']}")
    print(f"   Rows: {details['total_rows_actual']} / {details['total_rows_expected']}")

    if details["errors"]:
        print(f"\n   Errors:")
        for error in details["errors"]:
            print(f"   - {error}")

    return 0 if is_valid else 1


def cmd_scheduler(args):
    """处理调度命令"""
    scheduler = BackupScheduler()

    if args.action == "start":
        print("Starting backup scheduler...")
        scheduler.start()
        print("✅ Backup scheduler started")

        # 显示计划的任务
        jobs = scheduler.get_scheduled_jobs()
        print(f"\nScheduled jobs ({len(jobs)}):")
        for job in jobs:
            print(f"  - {job['name']}: {job['trigger']}")

        return 0

    elif args.action == "stop":
        print("Stopping backup scheduler...")
        scheduler.stop()
        print("✅ Backup scheduler stopped")

        return 0

    elif args.action == "status":
        jobs = scheduler.get_scheduled_jobs()
        print(f"Scheduled jobs ({len(jobs)}):")
        for job in jobs:
            print(f"  - {job['name']}")
            print(f"    Trigger: {job['trigger']}")
            if job["next_run_time"]:
                print(f"    Next run: {job['next_run_time']}")
            print()

        return 0

    return 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="MyStocks 备份恢复工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 执行 TDengine 全量备份
  python backup_recovery_cli.py backup tdengine full

  # 执行 PostgreSQL 全量备份
  python backup_recovery_cli.py backup postgresql full

  # 列出所有备份
  python backup_recovery_cli.py list backups

  # 恢复 TDengine 全量备份
  python backup_recovery_cli.py restore tdengine full --backup-id <backup_id>

  # TDengine 点对点恢复
  python backup_recovery_cli.py restore tdengine pitr --target-time 2025-11-11T10:00:00

  # 验证备份完整性
  python backup_recovery_cli.py verify <backup_id>

  # 启动备份调度
  python backup_recovery_cli.py scheduler start

  # 查看调度状态
  python backup_recovery_cli.py scheduler status
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="命令")

    # backup 命令
    backup_parser = subparsers.add_parser("backup", help="执行备份")
    backup_parser.add_argument(
        "database", choices=["tdengine", "postgresql"], help="数据库类型"
    )
    backup_parser.add_argument("type", choices=["full", "incremental"], help="备份类型")
    backup_parser.add_argument("--since", help="增量备份基础 (上次备份 ID)")
    backup_parser.set_defaults(func=cmd_backup)

    # list 命令
    list_parser = subparsers.add_parser("list", help="列出资源")
    list_parser.add_argument("resource", choices=["backups"], help="资源类型")
    list_parser.set_defaults(func=cmd_list)

    # restore 命令
    restore_parser = subparsers.add_parser("restore", help="恢复数据")
    restore_parser.add_argument(
        "database", choices=["tdengine", "postgresql"], help="数据库类型"
    )
    restore_parser.add_argument("type", choices=["full", "pitr"], help="恢复类型")
    restore_parser.add_argument("--backup-id", help="备份 ID (用于 full 恢复)")
    restore_parser.add_argument("--target-time", help="目标时间 (ISO 8601, 用于 PITR)")
    restore_parser.add_argument(
        "--dry-run", action="store_true", help="测试运行，不修改数据库"
    )
    restore_parser.set_defaults(func=cmd_restore)

    # verify 命令
    verify_parser = subparsers.add_parser("verify", help="验证备份")
    verify_parser.add_argument("backup_id", help="备份 ID")
    verify_parser.set_defaults(func=cmd_verify)

    # scheduler 命令
    scheduler_parser = subparsers.add_parser("scheduler", help="管理备份调度")
    scheduler_parser.add_argument(
        "action", choices=["start", "stop", "status"], help="调度操作"
    )
    scheduler_parser.set_defaults(func=cmd_scheduler)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        return args.func(args)
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
