#!/usr/bin/env python3
"""
Fix YAML indentation by parsing and re-serializing
"""

import yaml
import sys


def fix_yaml():
    try:
        with open("config/data_sources_registry.yaml", "r", encoding="utf-8") as f:
            content = f.read()

        # Try to load and immediately dump to fix formatting
        config = yaml.safe_load(content)

        # Write back with consistent formatting
        with open("config/data_sources_registry.yaml", "w", encoding="utf-8") as f:
            yaml.dump(
                config,
                f,
                default_flow_style=False,
                allow_unicode=True,
                indent=4,
                sort_keys=False,
            )

        print("YAML reformatted successfully")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    fix_yaml()
