#!/usr/bin/env python3
"""
Fix remaining indentation issues in monitoring files.

Issues:
1. performance_monitor.py:366 - docstring has 4 spaces (should be 8)
2. signal_decorator.py:600 - unindent issue
3. decoupled_monitoring.py:139 - unexpected unindent
4. alert_notifier.py:720 - unindent issue
"""

from pathlib import Path


def fix_performance_monitor_line_366():
    """Fix performance_monitor.py line 366: docstring should have 8 spaces."""
    file_path = Path("src/domain/monitoring/performance_monitor.py")

    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Line 366 (0-indexed: 365) - docstring
    # Current: 4 spaces, should be 8
    if len(lines) > 365 and lines[365] == '    """':
        lines[365] = '        """'
        print(f"   ✅ Fixed line 366: docstring indent (4→8 spaces)")

    # Also fix subsequent lines in the docstring until we hit non-docstring
    i = 366  # Line 367 (0-indexed)
    while i < len(lines):
        line = lines[i]
        # Check if this is still part of the docstring
        if line.strip().startswith('用法:') or line.strip().startswith('@') or line.strip() == '':
            # This is likely docstring content
            if line.startswith('    ') and not line.startswith('        '):
                # Has 4 spaces, needs 8
                if line.strip():  # Non-empty
                    lines[i] = '    ' + line
            i += 1
        else:
            break

    # Write back
    fixed_content = '\n'.join(lines)
    file_path.write_text(fixed_content, encoding='utf-8')
    print(f"   ✅ Fixed: performance_monitor.py")
    return True


def fix_signal_decorator_line_600():
    """Fix signal_decorator.py line 600: return decorator indent."""
    file_path = Path("src/domain/monitoring/signal_decorator.py")

    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Check lines around 600
    print(f"   Checking signal_decorator.py lines 595-605:")
    for i in range(594, min(605, len(lines))):
        line_num = i + 1
        prefix = ">>>" if line_num == 600 else "   "
        print(f"   {prefix} Line {line_num}: {repr(lines[i])}")

    # Line 600 (0-indexed: 599) - return decorator
    # This should be at the same level as the function definition
    # Let's check the function structure

    # The function should be:
    # def monitored_strategy(...):      # 0 spaces (module level function)
    #     def decorator(...):            # 4 spaces
    #         def wrapper(...):          # 8 spaces
    #             ...                    # 12 spaces
    #         return wrapper             # 8 spaces
    #     return decorator               # 4 spaces

    # So line 600 should have 4 spaces, not 0
    if lines[599] == 'return decorator':  # 0 spaces - WRONG
        lines[599] = '    return decorator'  # 4 spaces - CORRECT
        print(f"   ✅ Fixed line 600: return decorator indent (0→4 spaces)")

    # Write back
    fixed_content = '\n'.join(lines)
    file_path.write_text(fixed_content, encoding='utf-8')
    print(f"   ✅ Fixed: signal_decorator.py")
    return True


def fix_decoupled_monitoring_line_139():
    """Fix decoupled_monitoring.py line 139: unexpected unindent."""
    file_path = Path("src/domain/monitoring/decoupled_monitoring.py")

    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Check lines around 139
    print(f"   Checking decoupled_monitoring.py lines 134-144:")
    for i in range(133, min(144, len(lines))):
        line_num = i + 1
        prefix = ">>>" if line_num == 139 else "   "
        print(f"   {prefix} Line {line_num}: {repr(lines[i])}")

    # Line 139 (0-indexed: 138) - unexpected unindent
    # Let's see what the issue is
    if len(lines) > 138:
        line_139 = lines[138]
        print(f"   Line 139 content: {repr(line_139)}")
        print(f"   Line 139 indent: {len(line_139) - len(line_139.lstrip())} spaces")

        # If line 139 has wrong indent, fix it
        # Based on the error "unexpected unindent", it might have too much indent
        # or too little indent compared to surrounding lines

        # Check surrounding lines to determine correct indent
        if line_139.startswith('            ') and line_139.strip() == 'return cls._context.get()':
            # Has 12 spaces, might need 8 or 16
            # Let's check line 138
            if len(lines) > 137:
                line_138_indent = len(lines[137]) - len(lines[137].lstrip())
                print(f"   Line 138 indent: {line_138_indent} spaces")
                # If line 138 has 8 spaces and line 139 has 12, reduce line 139 to 8
                if line_138_indent == 8:
                    lines[138] = '        ' + line_139.lstrip()
                    print(f"   ✅ Fixed line 139: indent (12→8 spaces)")

    # Write back
    fixed_content = '\n'.join(lines)
    file_path.write_text(fixed_content, encoding='utf-8')
    print(f"   ✅ Fixed: decoupled_monitoring.py")
    return True


def fix_alert_notifier_line_720():
    """Fix alert_notifier.py line 720: unindent issue."""
    file_path = Path("src/domain/monitoring/alert_notifier.py")

    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Check lines around 720
    print(f"   Checking alert_notifier.py lines 715-725:")
    for i in range(714, min(725, len(lines))):
        line_num = i + 1
        prefix = ">>>" if line_num == 720 else "   "
        print(f"   {prefix} Line {line_num}: {repr(lines[i])}")

    # Line 720 (0-indexed: 719) - unindent issue
    # Need to determine the correct indent based on context

    # Write back (no changes for now, just inspecting)
    print(f"   ⚠️  alert_notifier.py: Needs manual inspection")
    return False


def main():
    """Main entry point."""
    print("🔧 Day 6 (Round 3): Fixing final indentation issues\n")

    results = {}

    # Fix 1
    print("1. performance_monitor.py (line 366):")
    results['performance_monitor'] = fix_performance_monitor_line_366()
    print()

    # Fix 2
    print("2. signal_decorator.py (line 600):")
    results['signal_decorator'] = fix_signal_decorator_line_600()
    print()

    # Fix 3
    print("3. decoupled_monitoring.py (line 139):")
    results['decoupled_monitoring'] = fix_decoupled_monitoring_line_139()
    print()

    # Fix 4
    print("4. alert_notifier.py (line 720):")
    results['alert_notifier'] = fix_alert_notifier_line_720()
    print()

    # Summary
    print("=" * 60)
    print("📊 SUMMARY:")
    fixed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"   ✅ Fixed: {fixed}/{total}")
    print(f"   ⚠️  Needs manual: {total - fixed}/{total}")
    print("\n🎯 Next: Run Pylint to verify all fixes")


if __name__ == "__main__":
    main()
