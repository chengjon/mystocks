#!/usr/bin/env python3
"""
Fix YAML indentation issues in data_sources_registry.yaml
"""


def fix_indentation():
    with open("config/data_sources_registry.yaml", "r", encoding="utf-8") as f:
        lines = f.readlines()

    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()

        # Look for patterns that need fixing
        if (
            stripped.endswith("table_name:")
            or stripped.endswith("endpoint_name:")
            or stripped.endswith("call_method:")
        ):
            # This is a correctly indented line, check the next few lines
            fixed_lines.append(line)
            i += 1

            # Check next lines for incorrectly indented parameters/test_parameters/quality_rules
            while i < len(lines):
                next_line = lines[i]
                next_stripped = next_line.strip()

                if next_stripped.startswith("#"):
                    # Comment, keep as is
                    fixed_lines.append(next_line)
                    i += 1
                elif next_stripped in [
                    "parameters:",
                    "test_parameters:",
                    "quality_rules:",
                ]:
                    # Check current indentation
                    current_indent = len(next_line) - len(next_line.lstrip())
                    if current_indent == 2:
                        # Fix to 4 spaces
                        fixed_line = "    " + next_stripped + "\n"
                        fixed_lines.append(fixed_line)
                        print(f"Fixed line {i + 1}: {next_stripped}")
                    else:
                        fixed_lines.append(next_line)
                    i += 1
                    break
                elif next_stripped == "" or len(next_stripped) == 0:
                    # Empty line, keep
                    fixed_lines.append(next_line)
                    i += 1
                else:
                    # Some other content, stop checking
                    break
        else:
            fixed_lines.append(line)
            i += 1

    # Write back
    with open("config/data_sources_registry.yaml", "w", encoding="utf-8") as f:
        f.writelines(fixed_lines)


if __name__ == "__main__":
    fix_indentation()
