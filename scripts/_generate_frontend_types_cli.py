"""CLI workflow helpers for ``generate_frontend_types``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate TypeScript types from Pydantic models")
    parser.add_argument("--domain", "-d", help="Generate types for specific domain only")
    parser.add_argument(
        "--openapi-spec",
        help="Path to generated OpenAPI spec artifact for contract-first CI validation",
    )
    parser.add_argument("--all", action="store_true", help="Generate multi-file output (default)")
    parser.add_argument(
        "--single",
        action="store_true",
        help="Generate single file (backward compatible)",
    )
    parser.add_argument("--watch", "-w", action="store_true", help="Watch mode (not implemented)")
    return parser


def generate_index_file(domains: list[str], output_dir: Path) -> str:
    lines = [
        "// Auto-generated index file for TypeScript types",
        "",
    ]

    for domain in sorted(domains):
        domain_file = output_dir / f"{domain}.ts"
        if domain_file.exists():
            lines.append(f"// {domain.title()} domain types")
            lines.append(f"export * from './{domain}';")
            lines.append("")

    return "\n".join(lines)


def _scan_directories(project_root: Path) -> list[Path]:
    return [
        project_root / "web" / "backend" / "app" / "schemas",
        project_root / "web" / "backend" / "app" / "schema",
        project_root / "web" / "backend" / "app" / "api" / "v1",
        project_root / "web" / "backend" / "app" / "models",
    ]


def _extract_models(project_root: Path, extractor: Any) -> None:
    for scan_dir in _scan_directories(project_root):
        if not scan_dir.exists():
            print(f"  ⚠️  Directory not found: {scan_dir}")
            continue

        print(f"  📂 Scanning {scan_dir.relative_to(project_root)}...")
        for py_file in scan_dir.rglob("*.py"):
            if py_file.name != "__init__.py":
                extractor.extract_from_file(py_file)


def _write_single_file_output(generator: Any, extractor: Any, output_dir: Path) -> None:
    ts_code = generator.generate(extractor.models)
    output_file = output_dir / "generated-types.ts"
    output_file.write_text(ts_code, encoding="utf-8")
    print(f"✅ Generated single file: {output_file}")


def _collect_common_models(extractor: Any, non_common_used_models: set[str]) -> dict[str, dict[str, Any]]:
    common_models: dict[str, dict[str, Any]] = dict(extractor.domain_models.get("common", {}))
    for name, info in extractor.models.items():
        if name not in non_common_used_models:
            common_models.setdefault(name, info)
    return common_models


def _write_multi_file_output(generator: Any, extractor: Any, output_dir: Path) -> None:
    domains = set(extractor.domain_models.keys())
    generated_domains: list[str] = []
    non_common_used_models: set[str] = set()

    for domain in sorted(domains):
        if domain == "common":
            continue
        models = extractor.domain_models[domain]
        if models:
            ts_code = generator.generate_domain(domain, models)
            domain_file = output_dir / f"{domain}.ts"
            domain_file.write_text(ts_code, encoding="utf-8")
            print(f"  ✅ Generated {domain}.ts ({len(models)} models)")
            generated_domains.append(domain)
            non_common_used_models.update(models.keys())

    common_models = _collect_common_models(extractor, non_common_used_models)
    if common_models:
        chunk_count = generator.write_common_split_files(common_models, output_dir)
        print(f"  ✅ Generated common.ts + common/index.ts + {chunk_count} chunk files")
        generated_domains.append("common")

    index_code = generate_index_file(generated_domains, output_dir)
    (output_dir / "index.ts").write_text(index_code, encoding="utf-8")
    print("  ✅ Generated index.ts")

    generator.write_generated_types_compat_barrel(output_dir)
    print("  ✅ Generated generated-types.ts (compatibility barrel)")
    print("\n📊 Summary:")
    print(f"   Total models: {len(extractor.models)}")
    print(f"   Domains: {', '.join(generated_domains)}")


def _report_generation_results(extractor: Any, config: Any, output_dir: Path) -> None:
    if extractor.fixed_conflicts:
        print(f"\n✅ {len(extractor.fixed_conflicts)} conflicts auto-fixed:")
        for fix in extractor.fixed_conflicts[:10]:
            print(f"    • {fix}")
        if len(extractor.fixed_conflicts) > 10:
            print(f"    • ... and {len(extractor.fixed_conflicts) - 10} more fixes")

    if extractor.warnings:
        max_warnings = config.get_max_warnings()
        print(f"\n⚠️  {len(extractor.warnings)} warnings detected:")
        for warning in extractor.warnings[:max_warnings]:
            print(f"    • {warning}")
        if len(extractor.warnings) > max_warnings:
            print(f"    • ... and {len(extractor.warnings) - max_warnings} more warnings (limited by config)")

    if extractor.type_conflicts and config.should_warn_on_conflicts():
        print(f"\n🚨 {len(extractor.type_conflicts)} type conflicts detected:")
        for name, conflicts in extractor.type_conflicts.items():
            print(f"    • {name}: {len(conflicts)} conflicting definitions")

    if config.is_strict_mode() and (extractor.warnings or extractor.type_conflicts):
        print("\n❌ Strict mode enabled - exiting with error due to conflicts/warnings")
        sys.exit(1)

    print(f"\n📁 Output directory: {output_dir}")


def run_generation(
    args: argparse.Namespace,
    *,
    project_root: Path,
    output_dir: Path,
    config_factory: Any,
    extractor_factory: Any,
    generator_factory: Any,
) -> None:
    print("🔄 Generating TypeScript types from Pydantic models...")
    if args.openapi_spec:
        openapi_spec_path = Path(args.openapi_spec)
        if not openapi_spec_path.exists():
            raise FileNotFoundError(f"OpenAPI spec artifact not found: {openapi_spec_path}")
        print(f"📄 Using OpenAPI contract artifact: {openapi_spec_path}")

    config = config_factory()
    extractor = extractor_factory(config)
    _extract_models(project_root, extractor)

    generator = generator_factory()
    if args.single:
        _write_single_file_output(generator, extractor, output_dir)
    else:
        _write_multi_file_output(generator, extractor, output_dir)

    _report_generation_results(extractor, config, output_dir)
