#!/usr/bin/env python3
"""Expand local route decorator paths into full runtime URLs.

Resolves prefix layers from router_registry.py registrations and
APIRouter declarations to produce a full-path route table.

Outputs JSON + Markdown with full-path and local-decorator duplicate reports.

Usage:
    cd web/backend && python3 ../../scripts/dev/backend_audit_fullpath_routes.py
"""

import ast
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

os.chdir(Path(__file__).resolve().parent.parent.parent / "web/backend")

API_DIR = "app/api"
REGISTRY_FILE = "app/router_registry.py"


def extract_routes(filepath):
    """Extract @router.get/post/... decorators via AST."""
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
            routes.append((method, path, node.name))
    return routes


def get_router_prefix(filepath):
    """Get prefix from APIRouter() in file."""
    try:
        tree = ast.parse(open(filepath).read())
    except Exception:
        return ""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not isinstance(node.value, ast.Call):
            continue
        func = getattr(node.value, "func", None)
        if not isinstance(func, ast.Name) or func.id != "APIRouter":
            continue
        for kw in node.value.keywords:
            if kw.arg == "prefix" and isinstance(kw.value, ast.Constant):
                return kw.value.value
    return ""


def parse_version_mapping():
    """Parse VERSION_MAPPING.py."""
    mapping = {}
    try:
        tree = ast.parse(open("app/api/VERSION_MAPPING.py").read())
    except Exception:
        return mapping
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "VERSION_MAPPING":
                if isinstance(node.value, ast.Dict):
                    for k, v in zip(node.value.keys, node.value.values):
                        if isinstance(k, ast.Constant) and isinstance(v, ast.Dict):
                            domain = k.value
                            for dk, dv in zip(v.keys, v.values):
                                if isinstance(dk, ast.Constant) and dk.value == "prefix":
                                    if isinstance(dv, ast.Constant):
                                        mapping[domain] = dv.value
    return mapping


def normalize(p):
    """Normalize URL path."""
    while "//" in p:
        p = p.replace("//", "/")
    if not p.startswith("/"):
        p = "/" + p
    return p


def compose(reg_prefix, router_prefix, local_path):
    """Compose full path from three layers."""
    parts = []
    for p in [reg_prefix, router_prefix, local_path]:
        p = p.strip("/")
        if p:
            parts.append(p)
    return normalize("/" + "/".join(parts)) if parts else "/"


def module_to_file(mod_name):
    """Check if import name resolves to a flat file or package."""
    flat = f"app/api/{mod_name}.py"
    pkg = f"app/api/{mod_name}/__init__.py"
    if os.path.exists(flat) and os.path.exists(pkg):
        # Both exist — the flat file shadows the package in most cases,
        # but router_registry uses `from .api import X` which resolves to package.
        # Return both so we can track the ambiguity.
        return flat, pkg
    if os.path.exists(flat):
        return flat, None
    if os.path.exists(pkg):
        return None, pkg
    return None, None


def find_route_files_for_module(mod_name):
    """Find all .py files that contribute routes for a module.

    For packages: the __init__.py re-exports from submodules.
    We need to find where the actual router is defined.
    """
    flat, pkg = module_to_file(mod_name)
    files = []

    if pkg:
        # Package: find the file that defines the exported router
        pkg_dir = f"app/api/{mod_name}"
        for root, dirs, fnames in os.walk(pkg_dir):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in fnames:
                if f.endswith(".py"):
                    files.append(os.path.join(root, f))
    elif flat:
        files.append(flat)

    return files


def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "docs/reports/quality/generated"
    os.makedirs(output_dir, exist_ok=True)

    vm = parse_version_mapping()

    # Parse router_registry.py
    content = open(REGISTRY_FILE).read()

    # Build import_name -> module_name mapping (handles multi-line import blocks)
    import_map = {}
    in_block = False
    for line in content.splitlines():
        stripped = line.strip()
        # Multi-line block start: from .api import (
        if stripped.startswith("from .api import ("):
            in_block = True
            rest = stripped[len("from .api import ("):]
            if ")" in rest:
                for n in rest.rstrip(")").split(","):
                    n = n.strip().split(" as ")[0].strip()
                    if n:
                        import_map[n] = n
                in_block = False
            continue
        if in_block:
            if ")" in stripped:
                rest = stripped.rstrip(")").strip()
                if rest:
                    import_map[rest] = rest
                in_block = False
            else:
                n = stripped.rstrip(",").strip()
                if n:
                    import_map[n] = n
            continue
        # Single-line imports from .api
        m = re.match(r"from\s+\.api\s+import\s+(\w+)", stripped)
        if m:
            import_map[m.group(1)] = m.group(1)
        # Sub-directory imports
        m = re.match(r"from\s+\.api\.(\S+)\s+import\s+(\w+)", stripped)
        if m:
            import_map[m.group(2)] = f"{m.group(1)}.{m.group(2)}"

    # Extract all app.include_router registrations
    # Format: (module_var, attr, prefix)
    registrations = []

    lines = content.splitlines()
    i = 0
    while i < len(lines):
        full_line = lines[i]
        while full_line.count("(") > full_line.count(")") and i + 1 < len(lines):
            i += 1
            full_line += " " + lines[i].strip()

        if "app.include_router(" not in full_line:
            i += 1
            continue

        # Extract module.var
        mod_match = re.search(r"app\.include_router\(\s*(\w+)(?:\.\w+)?", full_line)
        if not mod_match:
            i += 1
            continue
        var_name = mod_match.group(1)

        # Extract prefix
        prefix = ""
        pm = re.search(r'prefix\s*=\s*["\']([^"\']+)["\']', full_line)
        if pm:
            prefix = pm.group(1)

        # Check VERSION_MAPPING reference
        vm_match = re.search(r'VERSION_MAPPING\["(\w+)"\]\["prefix"\]', full_line)
        if vm_match:
            prefix = vm.get(vm_match.group(1), prefix)

        registrations.append((var_name, prefix))
        i += 1

    # Also parse router_modules dict + VERSION_MAPPING loop (lines 65-83)
    # These are: for key, config in VERSION_MAPPING.items():
    #                app.include_router(router_modules[key], prefix=config["prefix"])
    try:
        block_start = content.index("router_modules = {")
        block_end = content.index("}", block_start) + 1
        block = content[block_start:block_end]
        for m in re.finditer(r'"(\w+)":\s*(\w+)\.\w+', block):
            vm_key = m.group(1)
            var_name = m.group(2)
            vm_prefix = vm.get(vm_key, "")
            if vm_prefix:
                registrations.append((var_name, vm_prefix))
    except ValueError:
        pass

    # For each registration, find the actual file(s) and expand routes
    all_routes = []

    for var_name, reg_prefix in registrations:
        mod_name = import_map.get(var_name, var_name)

        # Special case: mystocks_v1_router -> app/api/v1/router.py
        if var_name == "mystocks_v1_router":
            # This is the v1 aggregation router with prefix /api/v1
            # Its sub-routers are composed in v1/router.py
            expand_v1_aggregation(all_routes, reg_prefix)
            continue

        # Special case: auth_compat
        if var_name == "auth_compat":
            filepath = "app/api/auth_compat.py"
            if os.path.exists(filepath):
                expand_single_file(all_routes, filepath, reg_prefix)
            continue

        # Standard module
        files = find_route_files_for_module(mod_name)
        if not files:
            continue

        # For flat files: direct expansion
        flat = f"app/api/{mod_name}.py"
        if flat in files and os.path.exists(flat):
            expand_single_file(all_routes, flat, reg_prefix)

        # For packages: the __init__.py re-exports the router
        # Find which sub-file actually defines the router
        pkg_init = f"app/api/{mod_name}/__init__.py"
        if os.path.exists(pkg_init):
            # Read __init__.py to find which submodule exports the router
            try:
                init_content = open(pkg_init).read()
            except Exception:
                continue
            # Check if it imports router from a submodule
            sub_match = re.search(r"from\s+\.(\w+)\s+import\s+.*router", init_content)
            if sub_match:
                sub_file = f"app/api/{mod_name}/{sub_match.group(1)}.py"
                if os.path.exists(sub_file):
                    expand_single_file(all_routes, sub_file, reg_prefix)
            else:
                # Router defined directly in __init__.py
                expand_single_file(all_routes, pkg_init, reg_prefix)

            # Also scan for other submodules that might have their own routers
            # (included via router.include_router in __init__.py or in the main router file)
            pkg_dir = f"app/api/{mod_name}"
            for root, dirs, fnames in os.walk(pkg_dir):
                dirs[:] = [d for d in dirs if d != "__pycache__"]
                for f in fnames:
                    if f.endswith(".py") and f != "__init__.py":
                        subpath = os.path.join(root, f)
                        if subpath not in [r["_source"] for r in all_routes]:
                            # Check if this file's routes are included via
                            # router.include_router in the main file
                            sub_routes = extract_routes(subpath)
                            if sub_routes:
                                # These are sub-router routes; their prefix
                                # comes from include_router call, not from app-level
                                sub_prefix = get_router_prefix(subpath)
                                for method, path, func in sub_routes:
                                    full = compose(reg_prefix, sub_prefix, path)
                                    all_routes.append({
                                        "_source": subpath,
                                        "method": method,
                                        "local_path": path,
                                        "function": func,
                                        "full_path": full,
                                        "reg_prefix": reg_prefix,
                                        "router_prefix": sub_prefix,
                                    })

    # Scan for orphan files (not in any registration)
    registered_sources = set(r["_source"] for r in all_routes)
    all_api_files = set()
    for root, dirs, files in os.walk(API_DIR):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if f.endswith(".py") and f not in ("__init__.py", "VERSION_MAPPING.py"):
                all_api_files.add(os.path.join(root, f))

    orphan_files = sorted(all_api_files - registered_sources)
    for filepath in orphan_files:
        rp = get_router_prefix(filepath)
        for method, path, func in extract_routes(filepath):
            full = compose("", rp, path)
            all_routes.append({
                "_source": filepath,
                "method": method,
                "local_path": path,
                "function": func,
                "full_path": full,
                "reg_prefix": "",
                "router_prefix": rp,
                "orphan": True,
            })

    # Compute duplicates
    fp_map = defaultdict(list)
    for r in all_routes:
        fp_map[(r["method"], r["full_path"])].append(r)

    fp_dups = {k: v for k, v in fp_map.items() if len(v) > 1}

    lp_map = defaultdict(list)
    for r in all_routes:
        lp_map[(r["method"], r["local_path"])].append({"source": r["_source"], "function": r["function"]})
    lp_dups = {k: v for k, v in lp_map.items() if len(v) > 1}

    orphan_routes = [r for r in all_routes if r.get("orphan")]

    # Build JSON output
    result = {
        "generated_at": datetime.now().isoformat(),
        "git_branch": os.popen("git branch --show-current").read().strip(),
        "git_head": os.popen("git log --oneline -1").read().strip(),
        "summary": {
            "total_routes": len(all_routes),
            "registered_routes": len(all_routes) - len(orphan_routes),
            "orphan_routes": len(orphan_routes),
            "unique_files": len(set(r["_source"] for r in all_routes)),
            "local_decorator_duplicate_groups": len(lp_dups),
            "full_path_duplicate_groups": len(fp_dups),
        },
        "full_path_duplicates": [
            {
                "method": k[0],
                "full_path": k[1],
                "handler_count": len(v),
                "handlers": [{"source": r["_source"], "function": r["function"]} for r in v],
            }
            for k, v in sorted(fp_dups.items(), key=lambda x: -len(x[1]))
        ],
        "local_decorator_duplicates_count": len(lp_dups),
        "orphan_files": sorted(set(r["_source"] for r in orphan_routes)),
    }

    json_path = os.path.join(output_dir, "backend-fullpath-route-table.json")
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Write Markdown
    md_lines = []
    md_lines.append("# MyStocks Backend Full-Path Route Table (P3-0.5)\n")
    md_lines.append(f"> **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    md_lines.append(f"> **Branch**: `{result['git_branch']}`")
    md_lines.append(f"> **HEAD**: `{result['git_head']}`\n")
    md_lines.append("## Summary\n")
    md_lines.append("| Metric | Value |")
    md_lines.append("|--------|-------|")
    for k, v in result["summary"].items():
        md_lines.append(f"| {k.replace('_', ' ').title()} | {v} |")

    # Full-path duplicates
    md_lines.append("\n## Full-Path Duplicates (same method + final URL)\n")
    if result["full_path_duplicates"]:
        md_lines.append(f"**{len(result['full_path_duplicates'])} groups** where multiple handlers serve the same final URL.\n")
        md_lines.append("| # | Method | Full Path | Handlers |")
        md_lines.append("|---|--------|-----------|----------|")
        for i, dup in enumerate(result["full_path_duplicates"], 1):
            h_str = "<br>".join(
                f"`{h['function']}` ({h['source']})" for h in dup["handlers"][:4]
            )
            extra = f" (+{dup['handler_count'] - 4} more)" if dup["handler_count"] > 4 else ""
            md_lines.append(f"| {i} | {dup['method']} | `{dup['full_path']}` | {h_str}{extra} |")
    else:
        md_lines.append("No full-path duplicates found.")

    md_lines.append(f"\n## Local Decorator Duplicates: {result['local_decorator_duplicates_count']} groups\n")
    md_lines.append("These share the same method+local_path but may resolve to different full URLs.")
    md_lines.append("See the baseline document for the detailed breakdown.\n")

    if result["orphan_files"]:
        md_lines.append(f"## Orphan Route Files ({len(result['orphan_files'])} files)\n")
        md_lines.append("Not directly registered in `router_registry.py`. May be sub-routers or dead code.\n")
        for fp in result["orphan_files"]:
            md_lines.append(f"- `{fp}`")

    md_path = os.path.join(output_dir, "backend-fullpath-route-table.md")
    with open(md_path, "w") as f:
        f.write("\n".join(md_lines) + "\n")

    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    print(f"\nSummary:")
    for k, v in result["summary"].items():
        print(f"  {k}: {v}")


def expand_single_file(all_routes, filepath, reg_prefix):
    """Expand all routes from a single file with given registration prefix."""
    router_prefix = get_router_prefix(filepath)
    for method, path, func in extract_routes(filepath):
        full = compose(reg_prefix, router_prefix, path)
        all_routes.append({
            "_source": filepath,
            "method": method,
            "local_path": path,
            "function": func,
            "full_path": full,
            "reg_prefix": reg_prefix,
            "router_prefix": router_prefix,
        })


def expand_v1_aggregation(all_routes, reg_prefix):
    """Expand the v1 aggregation router (app/api/v1/router.py).

    This router has prefix="/api/v1" and includes sub-routers.
    """
    v1_dir = "app/api/v1"
    router_file = f"{v1_dir}/router.py"
    v1_prefix = "/api/v1"  # From APIRouter declaration

    # Parse v1/router.py to find sub-router includes
    try:
        content = open(router_file).read()
    except Exception:
        return

    # The sub-routers are imported from submodules
    # Each include_router adds the sub-router's own prefix
    sub_router_files = []
    for root, dirs, files in os.walk(v1_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if f.endswith(".py") and f not in ("__init__.py", "router.py"):
                sub_router_files.append(os.path.join(root, f))

    for filepath in sub_router_files:
        rp = get_router_prefix(filepath)
        # Full prefix = v1_prefix + sub_router_prefix
        for method, path, func in extract_routes(filepath):
            full = compose(v1_prefix, rp, path)
            all_routes.append({
                "_source": filepath,
                "method": method,
                "local_path": path,
                "function": func,
                "full_path": full,
                "reg_prefix": v1_prefix,
                "router_prefix": rp,
            })


if __name__ == "__main__":
    main()
