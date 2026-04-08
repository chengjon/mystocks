from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TAXONOMY_PATH = PROJECT_ROOT / "config" / "governance" / "documentation-taxonomy.yaml"
REQUIRED_TAXONOMY_KEYS = {
    "metadata",
    "scan_roots",
    "decision_statuses",
    "lifecycle_classes",
    "archive_targets",
    "delete_gate_requirements",
    "trunks",
    "protected_doc_families",
    "families",
}


def normalize_path(path_value: str | Path) -> str:
    return Path(path_value).as_posix().strip("/")


def load_taxonomy(taxonomy_path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(taxonomy_path.read_text(encoding="utf-8")) or {}
    missing_keys = sorted(REQUIRED_TAXONOMY_KEYS - payload.keys())
    if missing_keys:
        raise ValueError(f"Taxonomy missing required keys: {', '.join(missing_keys)}")
    return payload


def discover_markdown_files(project_root: Path, scan_roots: list[str], paths: list[str] | None = None) -> list[str]:
    if paths:
        discovered = []
        for raw_path in paths:
            normalized = normalize_path(raw_path)
            target = project_root / normalized
            if target.is_file() and target.suffix == ".md":
                discovered.append(normalized)
        return sorted(set(discovered))

    discovered: list[str] = []
    for scan_root in scan_roots:
        target = project_root / normalize_path(scan_root)
        if not target.exists():
            continue
        if target.is_file() and target.suffix == ".md":
            discovered.append(normalize_path(target.relative_to(project_root)))
            continue
        for path in target.rglob("*.md"):
            discovered.append(normalize_path(path.relative_to(project_root)))
    return sorted(set(discovered))


def path_matches(path_value: str, patterns: list[str] | None) -> bool:
    if not patterns:
        return False
    return any(fnmatch(path_value, pattern) for pattern in patterns)


def trunk_by_id(taxonomy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in taxonomy["trunks"]}


def trunk_by_path(taxonomy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        normalize_path(item["path"]): item
        for item in taxonomy["trunks"]
        if item.get("path_kind", "file") == "file"
    }


def rule_specificity(rule: dict[str, Any]) -> tuple[int, int]:
    patterns = rule.get("match_paths", [])
    if not patterns:
        return (0, 0)
    longest = max(len(pattern) for pattern in patterns)
    wildcard_count = min(pattern.count("*") for pattern in patterns)
    return (longest, -wildcard_count)


def classify_path(path_value: str, taxonomy: dict[str, Any]) -> dict[str, Any] | None:
    normalized_path = normalize_path(path_value)
    exact_trunks = trunk_by_path(taxonomy)
    if normalized_path in exact_trunks:
        trunk = exact_trunks[normalized_path]
        return {
            "path": normalized_path,
            "source": "trunk",
            "id": trunk["id"],
            "concern": trunk["concern"],
            "lifecycle": trunk["lifecycle"],
            "canonical_trunk_id": trunk["id"],
            "current_truth": trunk.get("current_truth", False),
            "protected": trunk.get("protected", False),
            "decision_status": "keep-canonical",
        }

    for family in taxonomy.get("protected_doc_families", []):
        if path_matches(normalized_path, family.get("match_paths")) and not path_matches(
            normalized_path, family.get("exclude_paths")
        ):
            return {
                "path": normalized_path,
                "source": "protected_doc_family",
                "id": family["id"],
                "concern": family["concern"],
                "lifecycle": family["lifecycle"],
                "canonical_trunk_id": family["canonical_trunk_id"],
                "current_truth": family["lifecycle"] == "canonical",
                "protected": family.get("delete_protected", False),
                "decision_status": "keep-canonical" if family["lifecycle"] == "canonical" else "keep-supporting",
            }

    families = sorted(taxonomy.get("families", []), key=rule_specificity, reverse=True)
    for family in families:
        if not path_matches(normalized_path, family.get("match_paths")):
            continue
        if path_matches(normalized_path, family.get("exclude_paths")):
            continue
        lifecycle = family["lifecycle"]
        lifecycle_definition = taxonomy["lifecycle_classes"].get(lifecycle, {})
        delete_gate = family.get("delete_gate", {})
        return {
            "path": normalized_path,
            "source": "family",
            "id": family["id"],
            "concern": family["concern"],
            "lifecycle": lifecycle,
            "canonical_trunk_id": family["canonical_trunk_id"],
            "current_truth": lifecycle_definition.get("current_truth_allowed", False),
            "protected": family.get("delete_protected", False),
            "decision_status": family.get("decision_status"),
            "archive_target": family.get("archive_target"),
            "canonical_replacement": family.get("canonical_replacement"),
            "delete_gate": delete_gate,
        }

    return None


def detect_duplicate_truths(taxonomy: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for trunk in taxonomy["trunks"]:
        if trunk.get("lifecycle") != "canonical":
            continue
        if not trunk.get("current_truth", False):
            continue
        grouped[trunk["concern"]].append(trunk)

    findings = []
    for concern, items in sorted(grouped.items()):
        if len(items) < 2:
            continue
        findings.append(
            {
                "concern": concern,
                "message": f"Multiple canonical current-truth trunks declared for concern '{concern}'",
                "trunks": [{"id": item["id"], "path": item["path"]} for item in items],
            }
        )
    return findings


def validate_delete_candidate(classification: dict[str, Any], trunk_index: dict[str, dict[str, Any]]) -> list[str]:
    issues = []
    trunk_id = classification.get("canonical_trunk_id")
    if not trunk_id:
        issues.append("missing canonical_trunk_id")
    elif trunk_id not in trunk_index:
        issues.append(f"unknown canonical_trunk_id '{trunk_id}'")

    if not classification.get("canonical_replacement"):
        issues.append("missing canonical_replacement")

    delete_gate = classification.get("delete_gate") or {}
    inbound_links = delete_gate.get("inbound_links")
    retention_duty = delete_gate.get("retention_duty")
    decision_status = delete_gate.get("decision_status")

    if not inbound_links:
        issues.append("missing delete_gate.inbound_links")
    elif inbound_links != "clean":
        issues.append(f"delete_gate.inbound_links={inbound_links}")

    if retention_duty is None:
        issues.append("missing delete_gate.retention_duty")
    elif retention_duty != "none":
        issues.append(f"delete_gate.retention_duty={retention_duty}")

    if not decision_status:
        issues.append("missing delete_gate.decision_status")
    elif decision_status != "delete":
        issues.append(f"delete_gate.decision_status={decision_status}")

    return issues


def build_report(
    project_root: Path,
    taxonomy_path: Path = DEFAULT_TAXONOMY_PATH,
    paths: list[str] | None = None,
) -> dict[str, Any]:
    taxonomy = load_taxonomy(taxonomy_path)
    discovered_paths = discover_markdown_files(project_root, taxonomy["scan_roots"], paths)
    classifications: list[dict[str, Any]] = []
    unclassified: list[dict[str, Any]] = []
    blocked_delete_candidates: list[dict[str, Any]] = []

    trunk_index = trunk_by_id(taxonomy)
    lifecycle_counter: Counter[str] = Counter()

    for path_value in discovered_paths:
        classification = classify_path(path_value, taxonomy)
        if classification is None:
            unclassified.append({"path": path_value, "message": "No taxonomy rule matched this markdown path"})
            continue

        classifications.append(classification)
        lifecycle_counter[classification["lifecycle"]] += 1
        if classification["lifecycle"] == "delete_candidate":
            issues = validate_delete_candidate(classification, trunk_index)
            if issues:
                blocked_delete_candidates.append(
                    {
                        "path": classification["path"],
                        "family_id": classification["id"],
                        "canonical_trunk_id": classification.get("canonical_trunk_id"),
                        "issues": issues,
                    }
                )

    duplicate_truths = detect_duplicate_truths(taxonomy)

    return {
        "project_root": str(project_root),
        "taxonomy_path": str(taxonomy_path),
        "scanned_files": len(discovered_paths),
        "classified_files": len(classifications),
        "taxonomy_summary": {
            "trunks": len(taxonomy["trunks"]),
            "protected_doc_families": len(taxonomy["protected_doc_families"]),
            "families": len(taxonomy["families"]),
        },
        "summary": {
            "by_lifecycle": dict(sorted(lifecycle_counter.items())),
            "unclassified": len(unclassified),
            "duplicate_truths": len(duplicate_truths),
            "blocked_delete_candidates": len(blocked_delete_candidates),
        },
        "classifications": classifications,
        "findings": {
            "unclassified": unclassified,
            "duplicate_truths": duplicate_truths,
            "blocked_delete_candidates": blocked_delete_candidates,
        },
    }


def print_report(report: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    print("Documentation Governance Audit")
    print("==============================")
    print(f"scanned_files: {report['scanned_files']}")
    print(f"classified_files: {report['classified_files']}")
    print(f"unclassified: {report['summary']['unclassified']}")
    print(f"duplicate_truths: {report['summary']['duplicate_truths']}")
    print(f"blocked_delete_candidates: {report['summary']['blocked_delete_candidates']}")
    print(f"taxonomy: {report['taxonomy_path']}")

    if report["summary"]["by_lifecycle"]:
        print("\nLifecycle Summary:")
        for lifecycle, count in report["summary"]["by_lifecycle"].items():
            print(f"  - {lifecycle}: {count}")

    for section in ("duplicate_truths", "blocked_delete_candidates", "unclassified"):
        items = report["findings"][section]
        if not items:
            continue
        print(f"\n{section}:")
        for item in items:
            print(f"  - {json.dumps(item, ensure_ascii=False)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit documentation taxonomy coverage and delete-gate readiness")
    parser.add_argument("--root-dir", default=str(PROJECT_ROOT))
    parser.add_argument("--taxonomy", default=str(DEFAULT_TAXONOMY_PATH))
    parser.add_argument("--path", action="append")
    parser.add_argument("filenames", nargs="*")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    root_dir = Path(args.root_dir).resolve()
    taxonomy_path = Path(args.taxonomy).resolve()
    merged_paths = [*(args.path or []), *args.filenames]
    report = build_report(root_dir, taxonomy_path=taxonomy_path, paths=merged_paths or None)
    print_report(report, args.format)
    return 1 if report["summary"]["duplicate_truths"] or report["summary"]["blocked_delete_candidates"] else 0


if __name__ == "__main__":
    sys.exit(main())
