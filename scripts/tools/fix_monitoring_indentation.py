#!/usr/bin/env python3
"""
Fix indentation issues in monitoring module files.

Day 6: Fix syntax-error in monitoring directory
"""

import os
from pathlib import Path


def fix_monitoring_database():
    """Fix monitoring_database.py indentation (lines 32-767 need +4 spaces)."""
    file_path = Path("src/domain/monitoring/monitoring_database.py")

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    # Read file
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    print(f"📄 Processing {file_path}")
    print(f"   Total lines: {len(lines)}")

    # Fix lines 32-767 (0-indexed: 31-766)
    # Add 4 spaces to these lines
    fixed_lines = []
    for i, line in enumerate(lines):
        line_num = i + 1  # 1-indexed

        if 32 <= line_num <= 767:
            # Add 4 spaces if line is not empty and doesn't already start with 4+ spaces
            if line.strip():  # Non-empty line
                if not line.startswith('    '):  # Doesn't start with 4 spaces
                    fixed_lines.append('    ' + line)
                else:
                    # Already has some indentation, keep as is
                    fixed_lines.append(line)
            else:
                # Empty line, keep as is
                fixed_lines.append(line)
        else:
            # Lines outside range, keep as is
            fixed_lines.append(line)

    # Write back
    fixed_content = '\n'.join(fixed_lines)
    file_path.write_text(fixed_content, encoding='utf-8')

    print(f"✅ Fixed: {file_path}")
    print(f"   Modified lines: 32-767 (added 4-space indentation)")
    return True


def fix_async_monitoring():
    """Fix async_monitoring.py indentation (line 46 has unexpected indent)."""
    file_path = Path("src/domain/monitoring/async_monitoring.py")

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    # Read file
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    print(f"\n📄 Processing {file_path}")
    print(f"   Total lines: {len(lines)}")

    # Check line 46 (0-indexed: 45)
    # The error says "unexpected unindent" at line 46
    # We need to examine the context
    for i in range(max(0, 40), min(len(lines), 55)):
        line_num = i + 1
        prefix = ">>> " if line_num == 46 else "    "
        print(f"{prefix}Line {line_num}: {repr(lines[i])}")

    # Read lines around 46 to understand the issue
    # Based on error, likely need to fix indentation at line 46
    # Let's read the file to see what's wrong
    return False  # Will inspect manually first


def main():
    """Main entry point."""
    print("🔧 Day 6: Fixing monitoring module syntax-errors\n")

    # Fix 1: monitoring_database.py
    result1 = fix_monitoring_database()

    # Fix 2: async_monitoring.py (inspect first)
    result2 = fix_async_monitoring()

    if result1:
        print("\n✅ monitoring_database.py fixed")
    else:
        print("\n❌ monitoring_database.py fix failed")

    print("\n📝 Next steps:")
    print("   1. Review async_monitoring.py manually")
    print("   2. Fix remaining 8 files")
    print("   3. Run tests to verify")


if __name__ == "__main__":
    main()
