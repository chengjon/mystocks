#!/usr/bin/env python3
"""
Day 7: Fix MonitoringReporter class indentation.

Fix lines 615-640 to add 4-space indent to all class methods.
"""

from pathlib import Path


def fix_monitoring_reporter():
    """Fix MonitoringReporter class in decoupled_monitoring.py."""
    file_path = Path("src/domain/monitoring/decoupled_monitoring.py")

    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Fix lines 615-640 (0-indexed: 614-639)
    # Add 4 spaces to all class methods
    for i in range(614, min(640, len(lines))):
        line = lines[i]
        # Skip if empty or already properly indented
        if not line.strip():
            continue
        if line.startswith('    '):  # Already has 4+ spaces
            continue
        if line.startswith('class '):
            continue
        if line.startswith('@dataclass'):
            continue

        # Check if this is a method definition or class attribute
        if (line.startswith('def ') or
            line.startswith('    def ') or
            'self.' in line or
            line.strip().startswith('"""') or
            line.strip().startswith("'")):

            # Add 4 spaces if not already present
            if not line.startswith('    '):
                lines[i] = '    ' + line
                print(f"   ✅ Fixed line {i+1}: Added 4-space indent")

    # Write back
    fixed_content = '\n'.join(lines)
    file_path.write_text(fixed_content, encoding='utf-8')
    print(f"✅ Fixed: MonitoringReporter class in decoupled_monitoring.py")
    return True


if __name__ == "__main__":
    print("🔧 Day 7 Part 1: Fixing MonitoringReporter class\n")
    fix_monitoring_reporter()
    print("\n🎯 Next: Run Pylint to verify 0 syntax-error")
