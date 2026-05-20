from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
import tempfile
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.adapters.miniqmt_market_data_ledger import (
    EvidenceRunResult,
    MarketDatasetEvidenceLedger,
    MarketDatasetEvidenceRecord,
)

from src.core.data_classification import DataClassification

__all__ = [
    "EvidenceRunResult",
    "MarketDatasetEvidenceLedger",
    "MarketDatasetEvidenceRecord",
    "MiniQmtArtifact",
    "MiniQmtBundleError",
    "MiniQmtControlledEvidenceService",
    "MiniQmtMarketDataReleaseClient",
    "MiniQmtRelease",
    "build_source_command",
]


UPSTREAM_PROMOTION_BUNDLE_FILES = [
    "README.md",
    "promotion_requirements.json",
    "promotion_gaps.json",
    "mystocks_dry_run.template.evidence.json",
    "mystocks_dry_run.request.json",
    "mystocks_dry_run.validator.txt",
    "quantix_regression.template.evidence.json",
    "quantix_regression.request.json",
    "quantix_regression.validator.txt",
    "authoritative_approval.request.json",
    "authoritative_approval.apply.txt",
    "promotion_targets.json",
    "promotion_bundle.apply.txt",
    "promotion_bundle.validate.txt",
    "bundle_manifest.json",
]

REQUIRED_MANIFEST_FIELDS = [
    "dataset_version",
    "lineage_id",
    "payload_hash",
    "rows_hash",
    "schema_version",
    "quality_status",
    "maturity",
]

ARTIFACT_TYPE_PRIORITY = {"parquet": 0, "json": 1, "csv": 2}
FIELD_MAPPING_VERSION = "miniqmt.kline_daily.v1"
RELATED_FUNCTION_TREE_NODE = "FUNCTION_TREE.md#8.1 Market Data M1 authoritative-ready 缺口"


class MiniQmtBundleError(ValueError):
    """Raised when a miniQMT bundle or artifact is not safe to consume."""


@dataclass(frozen=True)
class MiniQmtArtifact:
    artifact_type: str
    uri: str
    path: Path
    expected_hash: str
    actual_hash: str
    byte_count: int


@dataclass(frozen=True)
class MiniQmtRelease:
    dataset_version: str
    lineage_id: str
    payload_hash: str
    rows_hash: str
    schema_version: str
    quality_status: str
    maturity: str
    artifact: MiniQmtArtifact
    manifest: dict[str, Any]


class MiniQmtMarketDataReleaseClient:
    """Read and verify miniQMT Market Data Platform release bundles."""

    def __init__(self, bundle_path: str | Path) -> None:
        self.bundle_path = Path(bundle_path)

    def load_bundle(self, dataset_version: str) -> MiniQmtRelease:
        dataset_version = self._validate_dataset_version(dataset_version)
        bundle_manifest = self._load_bundle_manifest()

        bundle_dataset_version = bundle_manifest.get("dataset_version")
        if bundle_dataset_version and bundle_dataset_version != dataset_version:
            raise MiniQmtBundleError(
                f"bundle dataset_version {bundle_dataset_version!r} does not match requested {dataset_version!r}"
            )

        self._validate_required_bundle_files(bundle_manifest)
        manifest_path = self._resolve_manifest_path(bundle_manifest)
        manifest = self._load_json(manifest_path, "dataset manifest")
        self._validate_manifest_identity(manifest, dataset_version)

        artifact = self._select_artifact(manifest)
        verified_artifact = self._verify_artifact(artifact)
        return MiniQmtRelease(
            dataset_version=manifest["dataset_version"],
            lineage_id=manifest["lineage_id"],
            payload_hash=manifest["payload_hash"],
            rows_hash=manifest["rows_hash"],
            schema_version=manifest["schema_version"],
            quality_status=manifest["quality_status"],
            maturity=manifest["maturity"],
            artifact=verified_artifact,
            manifest=manifest,
        )

    @classmethod
    def load_http(
        cls,
        dataset_version: str,
        manifest_url: str,
        *,
        fetch_bytes: Any | None = None,
    ) -> MiniQmtRelease:
        dataset_version = cls._validate_dataset_version(dataset_version)
        fetcher = fetch_bytes or _fetch_url_bytes
        manifest = cls._load_json_bytes(fetcher(manifest_url), "dataset manifest")
        cls._validate_manifest_identity(manifest, dataset_version)
        artifact = cls._select_artifact(manifest)
        artifact_uri = str(artifact.get("uri") or artifact.get("path") or "").strip()
        cls._reject_internal_artifact_uri(artifact_uri)
        artifact_url = urllib.parse.urljoin(manifest_url, artifact_uri)
        artifact_bytes = fetcher(artifact_url)
        verified_artifact = cls._verify_artifact_bytes(artifact, artifact_url, artifact_bytes)
        return MiniQmtRelease(
            dataset_version=manifest["dataset_version"],
            lineage_id=manifest["lineage_id"],
            payload_hash=manifest["payload_hash"],
            rows_hash=manifest["rows_hash"],
            schema_version=manifest["schema_version"],
            quality_status=manifest["quality_status"],
            maturity=manifest["maturity"],
            artifact=verified_artifact,
            manifest=manifest,
        )

    @classmethod
    def load_manifest_file(
        cls,
        dataset_version: str,
        manifest_path: str | Path,
        *,
        artifact_path: str | Path | None = None,
    ) -> MiniQmtRelease:
        dataset_version = cls._validate_dataset_version(dataset_version)
        manifest_file = Path(manifest_path)
        manifest = cls._load_json(manifest_file, "dataset manifest")
        cls._validate_manifest_identity(manifest, dataset_version)
        artifact = cls._select_artifact(manifest)
        verified_artifact = cls._verify_local_artifact(
            artifact,
            base_dir=manifest_file.parent,
            artifact_path=artifact_path,
        )
        return MiniQmtRelease(
            dataset_version=manifest["dataset_version"],
            lineage_id=manifest["lineage_id"],
            payload_hash=manifest["payload_hash"],
            rows_hash=manifest["rows_hash"],
            schema_version=manifest["schema_version"],
            quality_status=manifest["quality_status"],
            maturity=manifest["maturity"],
            artifact=verified_artifact,
            manifest=manifest,
        )

    @staticmethod
    def _validate_dataset_version(dataset_version: str) -> str:
        normalized = (dataset_version or "").strip()
        if not normalized:
            raise MiniQmtBundleError("dataset_version is required")
        if normalized.lower() == "latest":
            raise MiniQmtBundleError("implicit latest dataset_version is not allowed")
        return normalized

    def _load_bundle_manifest(self) -> dict[str, Any]:
        if not self.bundle_path.exists() or not self.bundle_path.is_dir():
            raise MiniQmtBundleError(f"bundle path does not exist or is not a directory: {self.bundle_path}")

        manifest_path = self.bundle_path / "bundle_manifest.json"
        if not manifest_path.exists():
            raise MiniQmtBundleError("bundle_manifest.json is required for miniQMT bundle mode")
        return self._load_json(manifest_path, "bundle_manifest.json")

    def _validate_required_bundle_files(self, bundle_manifest: dict[str, Any]) -> None:
        required_files = bundle_manifest.get("required_files") or UPSTREAM_PROMOTION_BUNDLE_FILES
        missing = [name for name in required_files if not (self.bundle_path / name).exists()]
        if missing:
            raise MiniQmtBundleError(f"bundle is missing required files: {', '.join(missing)}")

    def _resolve_manifest_path(self, bundle_manifest: dict[str, Any]) -> Path:
        manifest_file = bundle_manifest.get("manifest_file") or bundle_manifest.get("dataset_manifest")
        if not manifest_file:
            raise MiniQmtBundleError("bundle_manifest.json must define manifest_file")
        manifest_path = self.bundle_path / str(manifest_file)
        if not manifest_path.exists():
            raise MiniQmtBundleError(f"dataset manifest file is missing: {manifest_file}")
        return manifest_path

    @staticmethod
    def _load_json(path: Path, label: str) -> dict[str, Any]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise MiniQmtBundleError(f"{label} is not valid JSON: {path}") from exc
        if not isinstance(payload, dict):
            raise MiniQmtBundleError(f"{label} must be a JSON object: {path}")
        return payload

    @staticmethod
    def _load_json_bytes(payload_bytes: bytes, label: str) -> dict[str, Any]:
        try:
            payload = json.loads(payload_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise MiniQmtBundleError(f"{label} is not valid JSON") from exc
        if not isinstance(payload, dict):
            raise MiniQmtBundleError(f"{label} must be a JSON object")
        return payload

    @staticmethod
    def _validate_manifest_identity(manifest: dict[str, Any], dataset_version: str) -> None:
        missing = [field for field in REQUIRED_MANIFEST_FIELDS if not manifest.get(field)]
        if missing:
            raise MiniQmtBundleError(f"dataset manifest missing identity fields: {', '.join(missing)}")
        if manifest["dataset_version"] != dataset_version:
            raise MiniQmtBundleError(
                f"manifest dataset_version {manifest['dataset_version']!r} does not match requested {dataset_version!r}"
            )

    @staticmethod
    def _select_artifact(manifest: dict[str, Any]) -> dict[str, Any]:
        artifacts = manifest.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            raise MiniQmtBundleError("dataset manifest must include at least one artifact")

        candidates = []
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                continue
            artifact_type = str(artifact.get("type") or "").lower()
            if artifact_type in ARTIFACT_TYPE_PRIORITY:
                candidates.append(artifact)

        if not candidates:
            raise MiniQmtBundleError("dataset manifest does not include a supported parquet/json/csv artifact")
        return sorted(candidates, key=lambda item: ARTIFACT_TYPE_PRIORITY[str(item.get("type")).lower()])[0]

    def _verify_artifact(self, artifact: dict[str, Any]) -> MiniQmtArtifact:
        return self._verify_local_artifact(artifact, base_dir=self.bundle_path)

    @staticmethod
    def _verify_local_artifact(
        artifact: dict[str, Any],
        *,
        base_dir: Path,
        artifact_path: str | Path | None = None,
    ) -> MiniQmtArtifact:
        artifact_type = str(artifact.get("type") or "").lower()
        uri = str(artifact.get("uri") or artifact.get("path") or "").strip()
        expected_hash = str(artifact.get("hash") or artifact.get("sha256") or "").strip()
        if not uri or not expected_hash:
            raise MiniQmtBundleError("artifact must include uri and hash")
        MiniQmtMarketDataReleaseClient._reject_internal_artifact_uri(uri)

        resolved_artifact_path = _resolve_local_artifact_path(
            str(artifact_path) if artifact_path is not None else uri,
            base_dir=base_dir,
        )
        if not resolved_artifact_path.exists() or not resolved_artifact_path.is_file():
            raise MiniQmtBundleError(f"artifact file is missing: {uri}")

        artifact_bytes = resolved_artifact_path.read_bytes()
        actual_hash = hashlib.sha256(artifact_bytes).hexdigest()
        if actual_hash != expected_hash:
            raise MiniQmtBundleError(
                f"artifact hash mismatch for {uri}: expected {expected_hash}, calculated {actual_hash}"
            )
        return MiniQmtArtifact(
            artifact_type=artifact_type,
            uri=uri,
            path=resolved_artifact_path,
            expected_hash=expected_hash,
            actual_hash=actual_hash,
            byte_count=len(artifact_bytes),
        )

    @staticmethod
    def _verify_artifact_bytes(artifact: dict[str, Any], artifact_url: str, artifact_bytes: bytes) -> MiniQmtArtifact:
        artifact_type = str(artifact.get("type") or "").lower()
        expected_hash = str(artifact.get("hash") or artifact.get("sha256") or "").strip()
        if not artifact_url or not expected_hash:
            raise MiniQmtBundleError("artifact must include uri and hash")
        actual_hash = hashlib.sha256(artifact_bytes).hexdigest()
        if actual_hash != expected_hash:
            raise MiniQmtBundleError(
                f"artifact hash mismatch for {artifact_url}: expected {expected_hash}, calculated {actual_hash}"
            )
        suffix = f".{artifact_type}" if artifact_type else ""
        temp_file = tempfile.NamedTemporaryFile(prefix="miniqmt-artifact-", suffix=suffix, delete=False)
        try:
            temp_file.write(artifact_bytes)
        finally:
            temp_file.close()
        return MiniQmtArtifact(
            artifact_type=artifact_type,
            uri=artifact_url,
            path=Path(temp_file.name),
            expected_hash=expected_hash,
            actual_hash=actual_hash,
            byte_count=len(artifact_bytes),
        )

    @staticmethod
    def _reject_internal_artifact_uri(uri: str) -> None:
        normalized = uri.replace("\\", "/").lower()
        forbidden_segments = {"raw", "candidate", "candidates", "job", "jobs"}
        if any(segment in forbidden_segments for segment in normalized.split("/")):
            raise MiniQmtBundleError(f"artifact URI points to miniQMT internal state: {uri}")


class MiniQmtControlledEvidenceService:
    """Generate MyStocks-side dry-run evidence for verified miniQMT releases."""

    def run_bundle(
        self,
        *,
        dataset_version: str,
        bundle_path: str | Path,
        output_dir: str | Path,
        source_command: str,
        run_at: datetime | None = None,
        output_suffix: str = "",
    ) -> EvidenceRunResult:
        release = MiniQmtMarketDataReleaseClient(bundle_path).load_bundle(dataset_version)
        return self.run_release(
            release=release,
            output_dir=output_dir,
            source_command=source_command,
            run_at=run_at,
            output_suffix=output_suffix,
        )

    def run_release(
        self,
        *,
        release: MiniQmtRelease,
        output_dir: str | Path,
        source_command: str,
        run_at: datetime | None = None,
        output_suffix: str = "",
    ) -> EvidenceRunResult:
        run_at = run_at or datetime.now(timezone.utc)
        suffix = _normalize_output_suffix(output_suffix)
        raw_suffix = f"_{suffix}" if suffix else ""
        evidence_suffix = f"-{suffix}" if suffix else ""
        rows = self._read_artifact_rows(release.artifact)
        mapped_rows = self._map_daily_kline_rows(rows)
        if not mapped_rows:
            raise MiniQmtBundleError("dry-run evidence requires at least one real artifact row")
        failed_checks = self._validate_daily_kline_quality(mapped_rows)
        if failed_checks:
            raise MiniQmtBundleError(f"data quality checks failed: {', '.join(failed_checks)}")

        output_path = Path(output_dir)
        (output_path / "logs").mkdir(parents=True, exist_ok=True)

        raw_source_file = f"logs/mystocks_dry_run_{release.dataset_version}{raw_suffix}.json"
        raw_report_path = output_path / raw_source_file
        raw_report = self._build_raw_report(release, mapped_rows, run_at)
        self._reject_raw_report_placeholders(raw_report)
        self._write_json(raw_report_path, raw_report)
        raw_report_bytes = raw_report_path.read_bytes()
        raw_report_sha256 = hashlib.sha256(raw_report_bytes).hexdigest()

        evidence = self._build_evidence(
            release=release,
            mapped_rows=mapped_rows,
            raw_source_file=raw_source_file,
            raw_report_sha256=raw_report_sha256,
            raw_report_size=len(raw_report_bytes),
            source_command=source_command,
            run_at=run_at,
        )
        self._reject_placeholders(evidence)
        evidence_name = f"{run_at.date().isoformat()}-{release.dataset_version}-mystocks-dry-run{evidence_suffix}.evidence.json"
        evidence_path = output_path / evidence_name
        self._write_json(evidence_path, evidence)
        evidence_sha256 = hashlib.sha256(evidence_path.read_bytes()).hexdigest()

        return EvidenceRunResult(
            status="passed",
            dataset_version=release.dataset_version,
            row_count=len(mapped_rows),
            field_mapping_version=FIELD_MAPPING_VERSION,
            evidence_path=evidence_path,
            raw_report_path=raw_report_path,
            evidence_sha256=evidence_sha256,
            raw_report_sha256=raw_report_sha256,
            raw_report_size=len(raw_report_bytes),
        )

    @staticmethod
    def _read_artifact_rows(artifact: MiniQmtArtifact) -> list[dict[str, Any]]:
        if artifact.artifact_type == "json":
            payload = json.loads(artifact.path.read_text(encoding="utf-8"))
            rows = payload.get("rows") if isinstance(payload, dict) else payload
            if not isinstance(rows, list):
                raise MiniQmtBundleError("JSON artifact must contain a rows array")
            return [row for row in rows if isinstance(row, dict)]

        if artifact.artifact_type == "csv":
            with artifact.path.open("r", encoding="utf-8", newline="") as handle:
                return list(csv.DictReader(handle))

        if artifact.artifact_type == "parquet":
            try:
                import pandas as pd
            except ImportError as exc:
                raise MiniQmtBundleError("parquet artifacts require pandas with a parquet engine") from exc
            try:
                dataframe = pd.read_parquet(artifact.path)
            except Exception as exc:
                raise MiniQmtBundleError(f"parquet artifact is not readable: {artifact.path}") from exc
            return dataframe.to_dict(orient="records")

        raise MiniQmtBundleError(f"artifact type {artifact.artifact_type!r} is not readable in P0 dry-run mode")

    @staticmethod
    def _map_daily_kline_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        mapped_rows = []
        for row in rows:
            mapped_rows.append(
                {
                    "symbol": _first_present(row, "symbol", "ts_code", "code"),
                    "trade_date": _first_present(row, "trade_date", "date"),
                    "open": _first_present(row, "open"),
                    "high": _first_present(row, "high"),
                    "low": _first_present(row, "low"),
                    "close": _first_present(row, "close"),
                    "volume": _first_present(row, "volume", "vol"),
                }
            )
        return mapped_rows

    @staticmethod
    def _validate_daily_kline_quality(rows: list[dict[str, Any]]) -> list[str]:
        failed_checks = []
        for index, row in enumerate(rows):
            prefix = f"row[{index}]"
            try:
                high = float(row["high"])
                low = float(row["low"])
                open_price = float(row["open"])
                close = float(row["close"])
                volume = float(row["volume"])
            except (TypeError, ValueError):
                failed_checks.append(f"{prefix}.numeric_ohlcv")
                continue
            if high < low:
                failed_checks.append(f"{prefix}.high_gte_low")
            if not (low <= open_price <= high):
                failed_checks.append(f"{prefix}.open_between_low_high")
            if not (low <= close <= high):
                failed_checks.append(f"{prefix}.close_between_low_high")
            if volume < 0:
                failed_checks.append(f"{prefix}.volume_non_negative")
        return failed_checks

    @staticmethod
    def _build_raw_report(
        release: MiniQmtRelease,
        mapped_rows: list[dict[str, Any]],
        run_at: datetime,
    ) -> dict[str, Any]:
        sample_symbols = sorted({str(row["symbol"]) for row in mapped_rows})[:5]
        sample_dates = sorted({str(row["trade_date"]) for row in mapped_rows})[:5]
        return {
            "generated_at": _format_datetime(run_at),
            "dataset_version": release.dataset_version,
            "dataset": _dataset_identity(release),
            "artifact": _artifact_identity(release.artifact),
            "dry_run": {
                "mapped_classification": DataClassification.DAILY_KLINE.value,
                "field_mapping_version": FIELD_MAPPING_VERSION,
                "row_count": len(mapped_rows),
                "sample_symbols": sample_symbols,
                "sample_dates": sample_dates,
                "database_target": "dry-run-only",
                "writes_performed": False,
                "artifact_sha256_verified": True,
                "placeholder_count": 0,
                "comparison_summary": {
                    "sample_symbols": sample_symbols,
                    "sample_dates": sample_dates,
                    "row_count": len(mapped_rows),
                },
                "failed_checks": [],
                "warnings": [],
            },
        }

    @staticmethod
    def _build_evidence(
        *,
        release: MiniQmtRelease,
        mapped_rows: list[dict[str, Any]],
        raw_source_file: str,
        raw_report_sha256: str,
        raw_report_size: int,
        source_command: str,
        run_at: datetime,
    ) -> dict[str, Any]:
        raw_summary = {
            "evidence_type": "promotion_consumer_dry_run",
            "consumer_system": "mystocks_spec",
            "dataset_version": release.dataset_version,
            "lineage_id": release.lineage_id,
            "payload_hash": release.payload_hash,
            "row_count": len(mapped_rows),
            "field_mapping_version": FIELD_MAPPING_VERSION,
            "database_target": "dry-run-only",
            "writes_performed": False,
            "artifact": _artifact_identity(release.artifact),
            "failed_checks": [],
            "dry_run": {
                "passed": True,
                "failed_checks": [],
                "artifact_sha256_verified": True,
                "placeholder_count": 0,
            },
        }
        return {
            "schema_version": "evidence.v1",
            "evidence_key": "mystocks_dry_run",
            "evidence_type": "promotion_consumer_dry_run",
            "consumer_system": "mystocks_spec",
            "consumer_build": {
                "repo": "mystocks_spec",
                "runtime": f"Python {platform.python_version()}",
            },
            "dataset_version": release.dataset_version,
            "lineage_id": release.lineage_id,
            "payload_hash": release.payload_hash,
            "result_summary": raw_summary,
            "source_command": source_command,
            "run_at": _format_datetime(run_at),
            "environment": {
                "consumer_system": "mystocks_spec",
                "field_mapping_version": FIELD_MAPPING_VERSION,
                "python": platform.python_version(),
                "platform": platform.platform(),
            },
            "raw_source_file": raw_source_file,
            "redaction_notes": (
                "No credentials, token, account id, full local user path, raw market rows, or database secrets "
                "are included."
            ),
            "hash_or_size": {
                "artifact_sha256": release.artifact.actual_hash,
                "raw_report_sha256": raw_report_sha256,
                raw_source_file: {
                    "sha256": raw_report_sha256,
                    "byte_count": raw_report_size,
                }
            },
            "related_function_tree_node": RELATED_FUNCTION_TREE_NODE,
            "retention_decision": "keep_minimal_evidence",
        }

    @staticmethod
    def _reject_placeholders(payload: dict[str, Any]) -> None:
        placeholder_paths = list(_find_placeholder_paths(payload))
        if placeholder_paths:
            raise MiniQmtBundleError(f"evidence contains placeholder values: {', '.join(placeholder_paths)}")

    @staticmethod
    def _reject_raw_report_placeholders(raw_report: dict[str, Any]) -> None:
        placeholder_paths = list(_find_placeholder_paths(raw_report))
        if placeholder_paths:
            raise MiniQmtBundleError(f"raw report contains placeholder values: {', '.join(placeholder_paths)}")

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _first_present(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    raise MiniQmtBundleError(f"artifact row missing required field: {'/'.join(keys)}")


def _dataset_identity(release: MiniQmtRelease) -> dict[str, Any]:
    return {
        "dataset_version": release.dataset_version,
        "lineage_id": release.lineage_id,
        "payload_hash": release.payload_hash,
        "rows_hash": release.rows_hash,
        "schema_version": release.schema_version,
        "quality_status": release.quality_status,
        "maturity": release.maturity,
    }


def _artifact_identity(artifact: MiniQmtArtifact) -> dict[str, Any]:
    return {
        "type": artifact.artifact_type,
        "uri": artifact.uri,
        "hash": artifact.actual_hash,
        "byte_count": artifact.byte_count,
    }


def _resolve_local_artifact_path(uri_or_path: str, *, base_dir: Path) -> Path:
    parsed = urllib.parse.urlparse(uri_or_path)
    if parsed.scheme == "file":
        path_text = urllib.request.url2pathname(parsed.path)
        return _path_from_possible_windows_drive(path_text)

    return _path_from_possible_windows_drive(uri_or_path, base_dir=base_dir)


def _normalize_output_suffix(value: str) -> str:
    suffix = value.strip().strip("_-")
    if suffix and not suffix.replace("_", "").replace("-", "").isalnum():
        raise MiniQmtBundleError("output_suffix may contain only letters, numbers, hyphen, or underscore")
    return suffix


def _path_from_possible_windows_drive(value: str, *, base_dir: Path | None = None) -> Path:
    normalized = value.replace("\\", "/")
    if len(normalized) >= 3 and normalized[1] == ":" and normalized[2] == "/":
        return Path("/mnt") / normalized[0].lower() / normalized[3:]
    if len(normalized) >= 4 and normalized[0] == "/" and normalized[2] == ":" and normalized[3] == "/":
        return Path("/mnt") / normalized[1].lower() / normalized[4:]

    path = Path(value)
    if path.is_absolute() or base_dir is None:
        return path
    return base_dir / path


def _format_datetime(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _fetch_url_bytes(url: str) -> bytes:
    with urllib.request.urlopen(url) as response:
        return response.read()


def _find_placeholder_paths(value: Any, path: str = "$") -> list[str]:
    if isinstance(value, dict):
        paths = []
        for key, nested in value.items():
            paths.extend(_find_placeholder_paths(nested, f"{path}.{key}"))
        return paths
    if isinstance(value, list):
        paths = []
        for index, nested in enumerate(value):
            paths.extend(_find_placeholder_paths(nested, f"{path}[{index}]"))
        return paths
    if isinstance(value, str) and "<" in value and ">" in value:
        return [path]
    return []


def build_source_command(argv: list[str] | None = None) -> str:
    args = argv if argv is not None else sys.argv[1:]
    return "python scripts/market_data/run_miniqmt_controlled_evidence.py " + " ".join(args)
