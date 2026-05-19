from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.adapters.miniqmt_market_data import (
    MarketDatasetEvidenceLedger,
    MarketDatasetEvidenceRecord,
    MiniQmtBundleError,
    MiniQmtControlledEvidenceService,
    MiniQmtMarketDataReleaseClient,
    build_source_command,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate MyStocks miniQMT controlled dry-run evidence.")
    parser.add_argument("--dataset-version", required=True)
    parser.add_argument("--bundle-path", type=Path)
    parser.add_argument("--manifest-url")
    parser.add_argument("--manifest-path", type=Path)
    parser.add_argument("--artifact-path", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("docs/reports/evidence/miniqmt"))
    parser.add_argument("--database-target", default="dry-run-only", choices=["dry-run-only"])
    parser.add_argument("--postgres-dsn")
    return parser


def connect_postgres_ledger(dsn: str) -> MarketDatasetEvidenceLedger:
    import psycopg2

    return MarketDatasetEvidenceLedger(psycopg2.connect(dsn))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source_command = build_source_command(argv)
    service = MiniQmtControlledEvidenceService()
    if args.bundle_path:
        result = service.run_bundle(
            dataset_version=args.dataset_version,
            bundle_path=args.bundle_path,
            output_dir=args.output_dir,
            source_command=source_command,
        )
    elif args.manifest_url:
        release = MiniQmtMarketDataReleaseClient.load_http(args.dataset_version, args.manifest_url)
        result = service.run_release(
            release=release,
            output_dir=args.output_dir,
            source_command=source_command,
        )
    elif args.manifest_path:
        release = MiniQmtMarketDataReleaseClient.load_manifest_file(
            args.dataset_version,
            args.manifest_path,
            artifact_path=args.artifact_path,
        )
        result = service.run_release(
            release=release,
            output_dir=args.output_dir,
            source_command=source_command,
        )
    else:
        raise MiniQmtBundleError("one of --bundle-path, --manifest-url, or --manifest-path is required")
    summary = {
        "status": result.status,
        "dataset_version": result.dataset_version,
        "row_count": result.row_count,
        "field_mapping_version": result.field_mapping_version,
        "evidence_path": str(result.evidence_path),
        "raw_report_path": str(result.raw_report_path),
        "evidence_sha256": result.evidence_sha256,
        "raw_report_sha256": result.raw_report_sha256,
    }
    if args.postgres_dsn:
        evidence = json.loads(result.evidence_path.read_text(encoding="utf-8"))
        raw_report = json.loads(result.raw_report_path.read_text(encoding="utf-8"))
        record = MarketDatasetEvidenceRecord.from_run_result(result, evidence=evidence, raw_report=raw_report)
        summary["ledger_id"] = connect_postgres_ledger(args.postgres_dsn).insert_run(record)

    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except MiniQmtBundleError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from exc
