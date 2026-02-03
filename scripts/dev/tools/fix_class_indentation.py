#!/usr/bin/env python3
"""
Fix class method indentation for monitoring files.

Issues:
- performance_monitor.py: def __init__ at line 41 missing 4-space indent
- data_source_metrics.py: class methods missing proper indentation
- alert_notifier.py: class methods missing proper indentation
"""

from pathlib import Path


def fix_performance_monitor():
    """Fix performance_monitor.py - add 4-space indent to all class methods."""
    file_path = Path("src/domain/monitoring/performance_monitor.py")

    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Lines 41-end need 4-space indent for class methods
    # Class starts at line 26
    # Methods start at line 41 (def __init__)
    # We need to add 4 spaces to lines 41 onwards (excluding module-level code at end)

    fixed_lines = []
    for i, line in enumerate(lines):
        line_num = i + 1  # 1-indexed

        if line_num >= 41:
            # Check if this is module-level code (test code at end)
            # Usually starts with "if __name__ == '__main__':" or similar
            if line.startswith('if __name__'):
                # Start of module-level code, stop adding indent
                fixed_lines.append(line)
            elif line.strip() and not line.startswith(' '):
                # Non-empty line with no indent starting at line 41+
                # This is likely a method definition missing indent
                if line_num >= 41 and not line.startswith('#'):
                    # Add 4 spaces
                    fixed_lines.append('    ' + line)
                else:
                    fixed_lines.append(line)
            else:
                # Line already has some indent or is empty
                fixed_lines.append(line)
        else:
            # Lines before 41, keep as is
            fixed_lines.append(line)

    # Write back
    fixed_content = '\n'.join(fixed_lines)
    file_path.write_text(fixed_content, encoding='utf-8')
    print(f"   ✅ Fixed: performance_monitor.py (added indent to methods)")
    return True


def fix_data_source_metrics():
    """Fix data_source_metrics.py - fix singleton class methods."""
    file_path = Path("src/domain/monitoring/data_source_metrics.py")

    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Line 111: def __new__ - should be at 4 spaces
    # Line 116: @classmethod - should be at 4 spaces (we tried to fix but it's still wrong)
    # Line 117: def get_instance - should be at 4 spaces
    # Line 123: def __init__ - should be at 4 spaces

    # The issue is that these methods are inside the class but missing proper indent
    # Let's check lines 105-130

    # Actually, looking at the output, line 116 still has the error
    # Let me read the file to see the current state
    for i in range(105, min(130, len(lines))):
        line_num = i + 1
        if i >= len(lines):
            break
        prefix = ">>>" if line_num in [111, 116, 117, 123] else "   "
        print(f"   {prefix} Line {line_num}: {repr(lines[i])}")

    # Based on what I see, I need to fix the indentation properly
    # Line 111: def __new__(cls): - should be 4 spaces
    if len(lines) > 110 and 'def __new__' in lines[110]:
        if not lines[110].startswith('    def __new__'):
            lines[110] = '    ' + lines[110].lstrip()
            print(f"   ✅ Fixed line 111: def __new__")

    # Line 116-117: @classmethod and def get_instance - should be 4 spaces each
    if len(lines) > 115 and lines[115].startswith('        @classmethod'):
        lines[115] = lines[115][4:]  # Remove 4 spaces
        print(f"   ✅ Fixed line 116: @classmethod (8→4 spaces)")

    if len(lines) > 116 and lines[116].startswith('        def get_instance'):
        lines[116] = lines[116][4:]  # Remove 4 spaces
        print(f"   ✅ Fixed line 117: def get_instance (8→4 spaces)")

    # Line 123+: def __init__ and beyond - should be 4 spaces
    if len(lines) > 122 and 'def __init__' in lines[122]:
        if not lines[122].startswith('    def __init__'):
            lines[122] = '    ' + lines[122].lstrip()
            print(f"   ✅ Fixed line 124: def __init__ (0→4 spaces)")

    # Write back
    fixed_content = '\n'.join(lines)
    file_path.write_text(fixed_content, encoding='utf-8')
    print(f"   ✅ Fixed: data_source_metrics.py")
    return True


def fix_alert_notifier():
    """Fix alert_notifier.py - fix base class methods."""
    file_path = Path("src/domain/monitoring/alert_notifier.py")

    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Line 106: def __init__ - should be at 4 spaces
    # Line 112: @abstractmethod - should be at 4 spaces
    # Line 113: async def send - should be at 4 spaces
    # Line 114: docstring - should be at 8 spaces

    # Line 106
    if len(lines) > 105 and 'def __init__' in lines[105]:
        if not lines[105].startswith('    def __init__'):
            lines[105] = '    ' + lines[105].lstrip()
            print(f"   ✅ Fixed line 106: def __init__ (0→4 spaces)")

    # Lines 112-114
    if len(lines) > 111 and lines[111].startswith('        @abstractmethod'):
        lines[111] = lines[111][4:]  # Remove 4 spaces
        print(f"   ✅ Fixed line 112: @abstractmethod (8→4 spaces)")

    if len(lines) > 112 and lines[112].startswith('        async def send'):
        lines[112] = lines[112][4:]  # Remove 4 spaces
        print(f"   ✅ Fixed line 113: async def send (8→4 spaces)")

    if len(lines) > 113 and lines[113] == '    """Send notification via this channel"""':
        lines[113] = '        """Send notification via this channel"""'
        print(f"   ✅ Fixed line 114: docstring (4→8 spaces)")

    # Write back
    fixed_content = '\n'.join(lines)
    file_path.write_text(fixed_content, encoding='utf-8')
    print(f"   ✅ Fixed: alert_notifier.py")
    return True


def fix_decoupled_monitoring():
    """Fix decoupled_monitoring.py - line 127 has unexpected unindent."""
    file_path = Path("src/domain/monitoring/decoupled_monitoring.py")

    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Check lines 122-132
    for i in range(121, min(132, len(lines))):
        line_num = i + 1
        prefix = ">>>" if line_num == 127 else "   "
        print(f"   {prefix} Line {line_num}: {repr(lines[i])}")

    # Line 127 is the problem
    # The error says "unexpected unindent" which means the indent is wrong
    # Let me check if line 126 and 127 need to be swapped or fixed

    # Actually, based on the previous fix, we fixed line 122, 127, 132
    # But line 127 still has an error. Let's see what it is.

    # Write back (no changes for now, just inspecting)
    print(f"   ⚠️  decoupled_monitoring.py: Needs more investigation")
    return False


def main():
    """Main entry point."""
    print("🔧 Day 6 (Round 2): Fixing class method indentation\n")

    # Fix performance_monitor
    print("1. performance_monitor.py:")
    fix_performance_monitor()
    print()

    # Fix data_source_metrics
    print("2. data_source_metrics.py:")
    fix_data_source_metrics()
    print()

    # Fix alert_notifier
    print("3. alert_notifier.py:")
    fix_alert_notifier()
    print()

    # Check decoupled_monitoring
    print("4. decoupled_monitoring.py:")
    fix_decoupled_monitoring()
    print()

    print("=" * 60)
    print("✅ Fixes applied. Run Pylint to verify.")


if __name__ == "__main__":
    main()
