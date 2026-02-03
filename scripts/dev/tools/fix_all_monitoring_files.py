#!/usr/bin/env python3
"""
Batch fix all monitoring module syntax-errors.

Day 6: Fix remaining 8 files with indentation issues
"""

import re
from pathlib import Path


MONITORING_FILES = [
    "src/domain/monitoring/multi_channel_alert_manager.py",
    "src/domain/monitoring/performance_monitor.py",
    "src/domain/monitoring/data_source_metrics.py",
    "src/domain/monitoring/signal_decorator.py",
    "src/domain/monitoring/decoupled_monitoring.py",
    "src/domain/monitoring/intelligent_threshold_manager.py",
    "src/domain/monitoring/monitoring_service.py",
    "src/domain/monitoring/alert_notifier.py",
]


def fix_multi_channel_alert_manager():
    """Fix multi_channel_alert_manager.py line 1093 (unindent issue)."""
    file_path = Path("src/domain/monitoring/multi_channel_alert_manager.py")

    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Line 1093 has incorrect indentation
    # It should be at module level (0 spaces), not inside a function
    # Issue: line 1093 is "    asyncio.run(main())" but should be "asyncio.run(main())"

    # Check if line 1092 is a comment about running demo
    if len(lines) > 1092:
        line_1092 = lines[1091]  # 0-indexed
        line_1093 = lines[1092]  # 0-indexed

        print(f"   Line 1092: {repr(line_1092)}")
        print(f"   Line 1093: {repr(line_1093)}")

        # If line 1093 starts with 4 spaces and line 1092 is a comment ending a function
        # Remove the 4 spaces
        if line_1093.startswith('    asyncio.run(main())'):
            lines[1092] = line_1093[4:]  # Remove 4 leading spaces
            print(f"   ✅ Fixed line 1093: Removed 4-space indent")

    # Write back
    fixed_content = '\n'.join(lines)
    file_path.write_text(fixed_content, encoding='utf-8')
    print(f"   ✅ Fixed: {file_path.name}")
    return True


def fix_performance_monitor():
    """Fix performance_monitor.py line 54 (unindent issue)."""
    file_path = Path("src/domain/monitoring/performance_monitor.py")

    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Line 54 has unindent error
    # Let's check the context
    if len(lines) > 53:
        for i in range(45, min(60, len(lines))):
            line_num = i + 1
            prefix = ">>> " if line_num == 54 else "    "
            print(f"   {prefix}Line {line_num}: {repr(lines[i])}")

    # This needs manual inspection - let's just report for now
    print(f"   ⚠️  {file_path.name}: Needs manual inspection at line 54")
    return False


def fix_data_source_metrics():
    """Fix data_source_metrics.py line 116 (unindent issue)."""
    file_path = Path("src/domain/monitoring/data_source_metrics.py")

    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Line 116 has unindent error
    if len(lines) > 115:
        for i in range(107, min(125, len(lines))):
            line_num = i + 1
            prefix = ">>> " if line_num == 116 else "    "
            print(f"   {prefix}Line {line_num}: {repr(lines[i])}")

    print(f"   ⚠️  {file_path.name}: Needs manual inspection at line 116")
    return False


def fix_signal_decorator():
    """Fix signal_decorator.py line 600 (unindent issue)."""
    file_path = Path("src/domain/monitoring/signal_decorator.py")

    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Line 600 has unindent error
    if len(lines) > 599:
        for i in range(590, min(610, len(lines))):
            line_num = i + 1
            prefix = ">>> " if line_num == 600 else "    "
            print(f"   {prefix}Line {line_num}: {repr(lines[i])}")

    print(f"   ⚠️  {file_path.name}: Needs manual inspection at line 600")
    return False


def fix_decoupled_monitoring():
    """Fix decoupled_monitoring.py line 122 (unexpected unindent)."""
    file_path = Path("src/domain/monitoring/decoupled_monitoring.py")

    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Line 122 has unexpected unindent
    if len(lines) > 121:
        for i in range(112, min(132, len(lines))):
            line_num = i + 1
            prefix = ">>> " if line_num == 122 else "    "
            print(f"   {prefix}Line {line_num}: {repr(lines[i])}")

    print(f"   ⚠️  {file_path.name}: Needs manual inspection at line 122")
    return False


def fix_intelligent_threshold_manager():
    """Fix intelligent_threshold_manager.py line 1315 (unindent issue)."""
    file_path = Path("src/domain/monitoring/intelligent_threshold_manager.py")

    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Line 1315 has unindent error
    if len(lines) > 1314:
        for i in range(1305, min(1325, len(lines))):
            line_num = i + 1
            prefix = ">>> " if line_num == 1315 else "    "
            print(f"   {prefix}Line {line_num}: {repr(lines[i])}")

    print(f"   ⚠️  {file_path.name}: Needs manual inspection at line 1315")
    return False


def fix_monitoring_service():
    """Fix monitoring_service.py line 1043 (expected indented block)."""
    file_path = Path("src/domain/monitoring/monitoring_service.py")

    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Line 1043 expects indented block after function definition on line 1042
    if len(lines) > 1041:
        for i in range(1033, min(1053, len(lines))):
            line_num = i + 1
            prefix = ">>> " if line_num in [1042, 1043] else "    "
            print(f"   {prefix}Line {line_num}: {repr(lines[i])}")

    print(f"   ⚠️  {file_path.name}: Needs manual inspection at line 1043")
    return False


def fix_alert_notifier():
    """Fix alert_notifier.py line 112 (unindent issue)."""
    file_path = Path("src/domain/monitoring/alert_notifier.py")

    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Line 112 has unindent error
    if len(lines) > 111:
        for i in range(102, min(122, len(lines))):
            line_num = i + 1
            prefix = ">>> " if line_num == 112 else "    "
            print(f"   {prefix}Line {line_num}: {repr(lines[i])}")

    print(f"   ⚠️  {file_path.name}: Needs manual inspection at line 112")
    return False


def main():
    """Main entry point."""
    print("🔧 Day 6: Fixing remaining monitoring module syntax-errors\n")

    results = {}

    # Fix 1: multi_channel_alert_manager.py
    print("1. multi_channel_alert_manager.py:")
    results['multi_channel_alert_manager'] = fix_multi_channel_alert_manager()
    print()

    # Check remaining files (needs manual inspection)
    remaining = [
        ('performance_monitor', fix_performance_monitor),
        ('data_source_metrics', fix_data_source_metrics),
        ('signal_decorator', fix_signal_decorator),
        ('decoupled_monitoring', fix_decoupled_monitoring),
        ('intelligent_threshold_manager', fix_intelligent_threshold_manager),
        ('monitoring_service', fix_monitoring_service),
        ('alert_notifier', fix_alert_notifier),
    ]

    for idx, (name, fix_func) in enumerate(remaining, start=2):
        print(f"{idx}. {name}.py:")
        results[name] = fix_func()
        print()

    # Summary
    print("=" * 60)
    print("📊 SUMMARY:")
    fixed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"   Fixed: {fixed}/{total}")
    print(f"   Need manual inspection: {total - fixed}/{total}")
    print("\n✅ Remaining files need manual review and fixing")


if __name__ == "__main__":
    main()
