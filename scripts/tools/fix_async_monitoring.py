#!/usr/bin/env python3
"""
Fix async_monitoring.py dataclass method indentation.

Issues:
- Line 36: def to_dict missing 4-space indent
- Line 46-47: @classmethod and def from_dict have 8 spaces (should be 4)
"""

from pathlib import Path


def fix_async_monitoring():
    """Fix async_monitoring.py indentation."""
    file_path = Path("src/domain/monitoring/async_monitoring.py")

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    # Read file
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    print(f"📄 Processing {file_path}")
    print(f"   Total lines: {len(lines)}")

    # Fix line 36: def to_dict - add 4 spaces
    # (0-indexed: line 35)
    if not lines[35].startswith('    '):  # Line 36
        lines[35] = '    ' + lines[35]
        print(f"   ✅ Fixed line 36: Added 4-space indent to def to_dict")

    # Fix lines 46-47: reduce from 8 spaces to 4 spaces
    # (0-indexed: lines 45-46)
    if lines[45].startswith('        '):  # Line 46: @classmethod
        lines[45] = lines[45][4:]  # Remove 4 leading spaces
        print(f"   ✅ Fixed line 46: Reduced indent from 8 to 4 spaces (@classmethod)")

    if lines[46].startswith('        '):  # Line 47: def from_dict
        lines[46] = lines[46][4:]  # Remove 4 leading spaces
        print(f"   ✅ Fixed line 47: Reduced indent from 8 to 4 spaces (def from_dict)")

    # Write back
    fixed_content = '\n'.join(lines)
    file_path.write_text(fixed_content, encoding='utf-8')

    print(f"✅ Fixed: {file_path}")
    return True


if __name__ == "__main__":
    print("🔧 Fixing async_monitoring.py\n")
    fix_async_monitoring()
    print("\n✅ Done! You can now run Pylint to verify the fix.")
