#!/usr/bin/env python3
"""
Fix YAML indentation issues in data_sources_registry.yaml
"""

import re


def fix_yaml_indentation():
    with open("config/data_sources_registry.yaml", "r", encoding="utf-8") as f:
        lines = f.readlines()

    fixed_lines = []
    in_data_source = False
    current_indent_level = 0

    for i, line in enumerate(lines):
        stripped = line.rstrip()
        if not stripped or stripped.startswith("#"):
            fixed_lines.append(line)
            continue

        # Check indentation
        indent = len(line) - len(line.lstrip())
        content = line.strip()

        # Track when we're in a data source block
        if content.startswith("data_sources:"):
            in_data_source = True
            current_indent_level = indent
        elif in_data_source and indent == current_indent_level + 4 and ":" in content:
            # This is a data source name
            pass
        elif in_data_source and indent == current_indent_level + 8:
            # This should be a top-level key under data source (description, update_frequency, etc.)
            # Some are incorrectly indented with 2 spaces instead of 4
            if content in ["parameters:", "test_parameters:", "quality_rules:"]:
                # This should be at level current_indent_level + 8, which is correct
                pass
            else:
                # This is content under parameters/test_parameters/quality_rules
                pass
        elif in_data_source and indent == current_indent_level + 4:
            # This might be incorrectly indented - should be +8 for top-level keys
            if content in ["parameters:", "test_parameters:", "quality_rules:"]:
                # Fix: change from 4 spaces to 8 spaces
                fixed_line = "        " + content + "\n"
                fixed_lines.append(fixed_line)
                continue

        fixed_lines.append(line)

    # Write back
    with open("config/data_sources_registry.yaml", "w", encoding="utf-8") as f:
        f.writelines(fixed_lines)

    print("Fixed indentation issues")


if __name__ == "__main__":
    fix_yaml_indentation()
