#!/usr/bin/env python3
"""Backend audit fact baseline generator.

Outputs Markdown and JSON artifacts for Phase 3 issue tracking.
Usage: python3 scripts/dev/backend_audit_baseline.py [--output-dir docs/reports/quality]
"""

import ast
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Ensure we run from web/backend/
os.chdir(Path(__file__).resolve().parent.parent.parent / "web/backend")


def count_python_files(directory, exclude_dunder=True, exclude_private_prefix=False):
    """Count .py files in a directory tree."""
    count = 0
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if not f.endswith(".py"):
                continue
            if exclude_dunder and f == "__init__.py":
                continue
            if exclude_private_prefix and f.startswith("_"):
                continue
            count += 1
    return count


def count_lines(directory):
    """Count total lines in .py files."""
    total = 0
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if f.endswith(".py"):
                total += sum(1 for _ in open(os.path.join(root, f)))
    return total


def extract_routes(filepath):
    """Extract route decorators from a Python file using AST."""
    routes = []
    try:
        tree = ast.parse(open(filepath).read())
    except Exception:
        return routes
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for deco in node.decorator_list:
            if not isinstance(deco, ast.Call):
                continue
            func = deco.func
            if not isinstance(func, ast.Attribute):
                continue
            method = func.attr.upper()
            if method not in ("GET", "POST", "PUT", "DELETE", "PATCH"):
                continue
            path = ""
            if deco.args and isinstance(deco.args[0], ast.Constant):
                path = deco.args[0].value
            routes.append({"method": method, "path": path, "function": node.name})
    return routes


def scan_singletons(directory):
    """Scan for global _xxx singleton pattern."""
    results = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if not f.endswith(".py"):
                continue
            fpath = os.path.join(root, f)
            try:
                content = open(fpath).read()
            except Exception:
                continue
            for line_no, line in enumerate(content.splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("global ") and "_globals" not in stripped:
                    import re
                    match = re.match(r"global\s+(_\w+)", stripped)
                    if match:
                        var_name = match.group(1)
                        results.append({
                            "file": os.path.relpath(fpath, directory),
                            "line": line_no,
                            "variable": var_name,
                        })
    return results


def scan_api_flat_vs_package(api_dir):
    """Identify flat files, package dirs, and overlaps."""
    flat = set()
    pkgs = set()

    for f in os.listdir(api_dir):
        fp = os.path.join(api_dir, f)
        if os.path.isfile(fp) and f.endswith(".py"):
            if f in ("__init__.py", "VERSION_MAPPING.py"):
                continue
            name = f.replace(".py", "")
            if not name.startswith("_"):
                flat.add(name)
        elif os.path.isdir(fp) and not f.startswith("__"):
            init = os.path.join(fp, "__init__.py")
            if os.path.exists(init):
                pkgs.add(f)

    return {
        "flat_files": sorted(flat),
        "package_dirs": sorted(pkgs),
        "overlap": sorted(flat & pkgs),
        "flat_only": sorted(flat - pkgs),
        "pkg_only": sorted(pkgs - flat),
    }


def scan_health_routes(api_dir):
    """Classify health endpoints into canonical/fragmented/excluded."""
    canonical = []
    fragmented = []
    excluded = []
    all_health = []

    for root, dirs, files in os.walk(api_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if not f.endswith(".py") or f == "__init__.py":
                continue
            fpath = os.path.join(root, f)
            rel = os.path.relpath(fpath, api_dir)
            routes = extract_routes(fpath)
            for r in routes:
                is_health = (
                    "health" in r["path"].lower()
                    or "health" in r["function"].lower()
                )
                if not is_health:
                    continue
                entry = {**r, "source": rel}
                all_health.append(entry)

                if rel == "health.py":
                    canonical.append(entry)
                elif "old" in rel or "test_" in rel or "example" in rel:
                    excluded.append(entry)
                else:
                    fragmented.append(entry)

    return {
        "canonical": canonical,
        "fragmented": fragmented,
        "excluded": excluded,
        "total": len(all_health),
    }


def scan_residual_files(app_dir):
    """Find _new.py, .bak, .backup, .old.py, monitoring_old."""
    residual = {"new_py": [], "bak": [], "monitoring_old": None, "auth_compat": None}

    for root, dirs, files in os.walk(app_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            fpath = os.path.join(root, f)
            rel = os.path.relpath(fpath, app_dir)
            if f.endswith("_new.py"):
                residual["new_py"].append(rel)
            if f.endswith((".bak", ".backup", ".old.py")):
                residual["bak"].append(rel)
            if f == "auth_compat.py":
                residual["auth_compat"] = rel

    old_dir = os.path.join(app_dir, "api", "monitoring_old")
    if os.path.isdir(old_dir):
        residual["monitoring_old"] = os.path.relpath(old_dir, app_dir)

    return residual


def find_duplicate_routes(api_dir):
    """Find routes with same method+path across different modules."""
    route_map = defaultdict(list)

    for root, dirs, files in os.walk(api_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if not f.endswith(".py") or f == "__init__.py":
                continue
            fpath = os.path.join(root, f)
            rel = os.path.relpath(fpath, api_dir)
            routes = extract_routes(fpath)
            for r in routes:
                key = (r["method"], r["path"])
                route_map[key].append({"source": rel, "function": r["function"]})

    return {k: v for k, v in route_map.items() if len(v) > 1}


def generate_baseline():
    """Generate complete baseline data."""
    baseline = {
        "generated_at": datetime.now().isoformat(),
        "git_branch": os.popen("git branch --show-current").read().strip(),
        "git_head": os.popen("git log --oneline -1").read().strip(),
    }

    # Core
    baseline["core"] = {
        "python_files": count_python_files("app/core", exclude_dunder=False),
        "total_lines": count_lines("app/core"),
    }

    # Singleton
    singletons = scan_singletons("app")
    unique_vars = list(set(s["variable"] for s in singletons))
    by_layer = defaultdict(int)
    for s in singletons:
        layer = s["file"].split("/")[0] if "/" in s["file"] else "root"
        by_layer[layer] += 1
    baseline["singleton"] = {
        "total_statements": len(singletons),
        "unique_variables": len(unique_vars),
        "by_layer": dict(by_layer),
        "top_variables": sorted(
            [(v, sum(1 for s in singletons if s["variable"] == v)) for v in unique_vars],
            key=lambda x: -x[1],
        )[:15],
    }

    # API
    api_state = scan_api_flat_vs_package("app/api")
    baseline["api"] = {
        "flat_count": len(api_state["flat_files"]),
        "package_count": len(api_state["package_dirs"]),
        "overlap_domains": len(api_state["overlap"]),
        "overlap_list": api_state["overlap"],
        "flat_only": api_state["flat_only"],
        "pkg_only": api_state["pkg_only"],
    }

    # Routes
    all_routes = []
    route_count_by_module = defaultdict(int)
    for root, dirs, files in os.walk("app/api"):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if not f.endswith(".py") or f in ("__init__.py", "VERSION_MAPPING.py"):
                continue
            fpath = os.path.join(root, f)
            rel = os.path.relpath(fpath, "app/api")
            mod = rel.replace(".py", "").replace("/", ".")
            routes = extract_routes(fpath)
            route_count_by_module[mod] = len(routes)
            all_routes.extend(routes)
    baseline["routes"] = {
        "total_decorators": len(all_routes),
        "modules": len(route_count_by_module),
        "by_module": dict(sorted(route_count_by_module.items(), key=lambda x: -x[1])[:20]),
    }

    # Duplicates
    dups = find_duplicate_routes("app/api")
    baseline["duplicates"] = {
        "total_duplicate_groups": len(dups),
        "health_duplicate_count": sum(
            1 for (m, p), v in dups.items() if "health" in p.lower()
        ),
    }

    # Health
    health = scan_health_routes("app/api")
    baseline["health"] = {
        "canonical_count": len(health["canonical"]),
        "fragmented_count": len(health["fragmented"]),
        "excluded_count": len(health["excluded"]),
        "total_health_routes": health["total"],
    }

    # Residual
    baseline["residual"] = scan_residual_files("app")

    return baseline


def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(output_dir, exist_ok=True)

    baseline = generate_baseline()

    # JSON output
    json_path = os.path.join(output_dir, "backend-audit-baseline.json")
    with open(json_path, "w") as f:
        json.dump(baseline, f, indent=2, ensure_ascii=False)
    print(f"JSON: {json_path}")

    # Summary
    print(f"\nCore: {baseline['core']['python_files']} files, {baseline['core']['total_lines']} lines")
    print(f"Singleton: {baseline['singleton']['total_statements']} statements, {baseline['singleton']['unique_variables']} unique")
    print(f"API: {baseline['api']['flat_count']} flat, {baseline['api']['package_count']} packages, {baseline['api']['overlap_domains']} overlaps")
    print(f"Routes: {baseline['routes']['total_decorators']} total, {baseline['duplicates']['total_duplicate_groups']} duplicate groups")
    print(f"Health: {baseline['health']['canonical_count']} canonical, {baseline['health']['fragmented_count']} fragmented, {baseline['health']['excluded_count']} excluded")
    print(f"Residual _new.py: {len(baseline['residual']['new_py'])}")


if __name__ == "__main__":
    main()
