from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

import scripts.market_data.run_miniqmt_controlled_evidence as cli_module
from src.adapters.miniqmt_market_data import (
    MarketDatasetEvidenceLedger,
    MarketDatasetEvidenceRecord,
    MiniQmtBundleError,
    MiniQmtControlledEvidenceService,
    MiniQmtMarketDataReleaseClient,
)


REQUIRED_BUNDLE_FILES = [
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


def _write_bundle(tmp_path: Path, *, dataset_version: str = "kline_daily_20260518_v1") -> Path:
    bundle = tmp_path / "bundle"
    artifact = bundle / "artifacts" / "kline_daily.json"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "symbol": "000001.SZ",
            "trade_date": "2026-05-18",
            "open": 10.0,
            "high": 10.5,
            "low": 9.8,
            "close": 10.2,
            "volume": 100000,
        },
        {
            "symbol": "600000.SH",
            "trade_date": "2026-05-18",
            "open": 8.0,
            "high": 8.4,
            "low": 7.9,
            "close": 8.1,
            "volume": 200000,
        },
    ]
    artifact.write_text(json.dumps({"rows": rows}, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    artifact_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()

    manifest = {
        "dataset_version": dataset_version,
        "lineage_id": f"lin_{dataset_version}",
        "payload_hash": "payload-sha256",
        "rows_hash": "rows-sha256",
        "schema_version": "market-data.kline-daily.v1",
        "quality_status": "validated",
        "maturity": "validated",
        "artifacts": [
            {
                "type": "json",
                "uri": "artifacts/kline_daily.json",
                "hash": artifact_hash,
            }
        ],
    }
    manifest_path = bundle / "dataset_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    bundle.mkdir(exist_ok=True)
    for name in REQUIRED_BUNDLE_FILES:
        path = bundle / name
        if name == "bundle_manifest.json":
            path.write_text(
                json.dumps(
                    {
                        "dataset_version": dataset_version,
                        "manifest_file": "dataset_manifest.json",
                        "required_files": REQUIRED_BUNDLE_FILES,
                    },
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
        elif name.endswith(".json"):
            path.write_text("{}", encoding="utf-8")
        else:
            path.write_text("fixture\n", encoding="utf-8")
    return bundle


def _write_published_parquet_dataset(tmp_path: Path) -> tuple[Path, Path, str]:
    pd = pytest.importorskip("pandas")
    pytest.importorskip("pyarrow")

    artifact = tmp_path / "exports" / "kline_daily" / "kline_daily_20260518_v1.parquet"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "data_domain": "kline_daily",
                "symbol": "600000.SH",
                "open": 9.08,
                "high": 9.11,
                "low": 9.02,
                "close": 9.03,
                "volume": 77714000.0,
                "amount": 703348399.0,
                "adjustment": "forward",
                "source_system": "xtdata",
                "trade_date": "2026-05-12",
                "adjustment_factor": 1.0,
            },
            {
                "data_domain": "kline_daily",
                "symbol": "600000.SH",
                "open": 9.04,
                "high": 9.07,
                "low": 9.01,
                "close": 9.03,
                "volume": 84264300.0,
                "amount": 760849230.0,
                "adjustment": "forward",
                "source_system": "xtdata",
                "trade_date": "2026-05-13",
                "adjustment_factor": 1.0,
            },
        ]
    ).to_parquet(artifact, index=False)
    artifact_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()

    manifest = {
        "dataset_version": "kline_daily_20260518_v1",
        "lineage_id": "lin_kline_daily_20260518_v1",
        "payload_hash": "61eedd9cd029f6c0a3324b3e66be0d9b83402279cbd0aed75885459822ec13d1",
        "rows_hash": "0efbcdd407ff0461c8d3f06a4dc6ac315c6b6ec177f783705ce8f57c233c1152",
        "row_count": 2,
        "schema_version": "v1",
        "quality_status": "raw",
        "maturity": "candidate",
        "artifacts": [
            {
                "type": "parquet",
                "uri": "file:///D:/MyCode3/miniQMT/logs/mystocks_evidence_dataset_registry_20260518/exports/kline_daily/kline_daily_20260518_v1.parquet",
                "hash": artifact_hash,
                "hash_algorithm": "sha256",
                "row_count": 2,
                "rows_hash": "0efbcdd407ff0461c8d3f06a4dc6ac315c6b6ec177f783705ce8f57c233c1152",
            }
        ],
    }
    manifest_path = tmp_path / "manifests" / "kline_daily_20260518_v1.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return manifest_path, artifact, artifact_hash


def _load_manifest(bundle: Path) -> dict[str, object]:
    return json.loads((bundle / "dataset_manifest.json").read_text(encoding="utf-8"))


def _write_manifest(bundle: Path, manifest: dict[str, object]) -> None:
    (bundle / "dataset_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _replace_artifact_rows(bundle: Path, rows: list[dict[str, object]]) -> None:
    artifact = bundle / "artifacts" / "kline_daily.json"
    artifact.write_text(json.dumps({"rows": rows}, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    artifact_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()
    manifest = _load_manifest(bundle)
    manifest["artifacts"] = [{"type": "json", "uri": "artifacts/kline_daily.json", "hash": artifact_hash}]
    _write_manifest(bundle, manifest)


def test_release_client_requires_explicit_dataset_version(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path)
    client = MiniQmtMarketDataReleaseClient(bundle)

    with pytest.raises(MiniQmtBundleError, match="dataset_version is required"):
        client.load_bundle("")

    with pytest.raises(MiniQmtBundleError, match="implicit latest"):
        client.load_bundle("latest")


def test_release_client_requires_upstream_bundle_manifest(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path)
    (bundle / "bundle_manifest.json").unlink()

    with pytest.raises(MiniQmtBundleError, match="bundle_manifest.json"):
        MiniQmtMarketDataReleaseClient(bundle).load_bundle("kline_daily_20260518_v1")


def test_release_client_requires_manifest_identity_fields(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path)
    manifest = _load_manifest(bundle)
    manifest.pop("lineage_id")
    _write_manifest(bundle, manifest)

    with pytest.raises(MiniQmtBundleError, match="lineage_id"):
        MiniQmtMarketDataReleaseClient(bundle).load_bundle("kline_daily_20260518_v1")


def test_release_client_verifies_artifact_hash(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path)
    artifact = bundle / "artifacts" / "kline_daily.json"
    artifact.write_text('{"rows": []}', encoding="utf-8")

    with pytest.raises(MiniQmtBundleError, match="artifact hash mismatch"):
        MiniQmtMarketDataReleaseClient(bundle).load_bundle("kline_daily_20260518_v1")


def test_release_client_rejects_internal_artifact_paths(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path)
    manifest = _load_manifest(bundle)
    manifest["artifacts"] = [{"type": "json", "uri": "raw/kline_daily.json", "hash": "sha256"}]
    _write_manifest(bundle, manifest)

    with pytest.raises(MiniQmtBundleError, match="internal state"):
        MiniQmtMarketDataReleaseClient(bundle).load_bundle("kline_daily_20260518_v1")


def test_release_client_rejects_missing_and_unsupported_artifacts(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path)
    (bundle / "artifacts" / "kline_daily.json").unlink()

    with pytest.raises(MiniQmtBundleError, match="artifact file is missing"):
        MiniQmtMarketDataReleaseClient(bundle).load_bundle("kline_daily_20260518_v1")

    bundle = _write_bundle(tmp_path)
    manifest = _load_manifest(bundle)
    manifest["artifacts"] = [{"type": "xml", "uri": "artifacts/kline_daily.xml", "hash": "sha256"}]
    _write_manifest(bundle, manifest)

    with pytest.raises(MiniQmtBundleError, match="supported parquet/json/csv"):
        MiniQmtMarketDataReleaseClient(bundle).load_bundle("kline_daily_20260518_v1")


def test_release_client_loads_manifest_and_artifact_through_http_fetcher() -> None:
    artifact_payload = json.dumps({"rows": [{"symbol": "000001.SZ", "trade_date": "2026-05-18"}]}, sort_keys=True)
    artifact_bytes = artifact_payload.encode("utf-8")
    artifact_hash = hashlib.sha256(artifact_bytes).hexdigest()
    manifest = {
        "dataset_version": "kline_daily_20260518_v1",
        "lineage_id": "lin_kline_daily_20260518_v1",
        "payload_hash": "payload-sha256",
        "rows_hash": "rows-sha256",
        "schema_version": "market-data.kline-daily.v1",
        "quality_status": "validated",
        "maturity": "validated",
        "artifacts": [{"type": "json", "uri": "https://miniqmt.example/artifacts/kline_daily.json", "hash": artifact_hash}],
    }
    manifest_url = "https://miniqmt.example/api/v1/market-data/datasets/kline_daily_20260518_v1/manifest"
    fetched = {
        manifest_url: json.dumps(manifest).encode("utf-8"),
        "https://miniqmt.example/artifacts/kline_daily.json": artifact_bytes,
    }

    release = MiniQmtMarketDataReleaseClient.load_http(
        "kline_daily_20260518_v1",
        manifest_url,
        fetch_bytes=lambda url: fetched[url],
    )

    assert release.dataset_version == "kline_daily_20260518_v1"
    assert release.artifact.actual_hash == artifact_hash
    assert release.artifact.byte_count == len(artifact_bytes)


def test_release_client_loads_published_manifest_and_parquet_artifact(tmp_path: Path) -> None:
    manifest_path, artifact_path, artifact_hash = _write_published_parquet_dataset(tmp_path)

    release = MiniQmtMarketDataReleaseClient.load_manifest_file(
        "kline_daily_20260518_v1",
        manifest_path,
        artifact_path=artifact_path,
    )
    result = MiniQmtControlledEvidenceService().run_release(
        release=release,
        output_dir=tmp_path / "evidence",
        source_command="python scripts/market_data/run_miniqmt_controlled_evidence.py --manifest-path ...",
        run_at=datetime(2026, 5, 18, 10, 0, tzinfo=timezone.utc),
    )
    evidence = json.loads(result.evidence_path.read_text(encoding="utf-8"))
    raw_report = json.loads(result.raw_report_path.read_text(encoding="utf-8"))

    assert release.payload_hash == "61eedd9cd029f6c0a3324b3e66be0d9b83402279cbd0aed75885459822ec13d1"
    assert release.rows_hash == "0efbcdd407ff0461c8d3f06a4dc6ac315c6b6ec177f783705ce8f57c233c1152"
    assert release.quality_status == "raw"
    assert release.maturity == "candidate"
    assert release.artifact.actual_hash == artifact_hash
    assert release.artifact.artifact_type == "parquet"
    assert evidence["payload_hash"] == release.payload_hash
    assert evidence["result_summary"]["row_count"] == 2
    assert evidence["result_summary"]["dry_run"]["artifact_sha256_verified"] is True
    assert evidence["hash_or_size"]["artifact_sha256"] == artifact_hash
    assert raw_report["artifact"]["type"] == "parquet"
    assert raw_report["dry_run"]["sample_symbols"] == ["600000.SH"]
    assert raw_report["dry_run"]["sample_dates"] == ["2026-05-12", "2026-05-13"]


def test_cli_supports_manifest_url_without_live_http(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle = _write_bundle(tmp_path)
    release = MiniQmtMarketDataReleaseClient(bundle).load_bundle("kline_daily_20260518_v1")
    output_dir = tmp_path / "http-output"
    monkeypatch.setattr(
        cli_module.MiniQmtMarketDataReleaseClient,
        "load_http",
        staticmethod(lambda dataset_version, manifest_url: release),
    )

    exit_code = cli_module.main(
        [
            "--dataset-version",
            "kline_daily_20260518_v1",
            "--manifest-url",
            "https://miniqmt.example/manifest",
            "--output-dir",
            str(output_dir),
        ]
    )

    summary = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert summary["status"] == "passed"
    assert summary["row_count"] == 2


def test_cli_supports_manifest_path_and_artifact_path(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    manifest_path, artifact_path, artifact_hash = _write_published_parquet_dataset(tmp_path)
    output_dir = tmp_path / "published-output"

    exit_code = cli_module.main(
        [
            "--dataset-version",
            "kline_daily_20260518_v1",
            "--manifest-path",
            str(manifest_path),
            "--artifact-path",
            str(artifact_path),
            "--output-dir",
            str(output_dir),
        ]
    )

    summary = json.loads(capsys.readouterr().out)
    evidence = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    assert exit_code == 0
    assert summary["status"] == "passed"
    assert summary["row_count"] == 2
    assert evidence["lineage_id"] == "lin_kline_daily_20260518_v1"
    assert evidence["payload_hash"] == "61eedd9cd029f6c0a3324b3e66be0d9b83402279cbd0aed75885459822ec13d1"
    assert evidence["hash_or_size"]["artifact_sha256"] == artifact_hash


def test_controlled_evidence_service_rejects_empty_artifact_rows(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path)
    _replace_artifact_rows(bundle, [])

    with pytest.raises(MiniQmtBundleError, match="at least one real artifact row"):
        MiniQmtControlledEvidenceService().run_bundle(
            dataset_version="kline_daily_20260518_v1",
            bundle_path=bundle,
            output_dir=tmp_path / "evidence",
            source_command="test command",
        )


def test_controlled_evidence_service_rejects_placeholder_identity_values(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path)
    manifest = _load_manifest(bundle)
    manifest["payload_hash"] = "<payload_hash_from_manifest>"
    _write_manifest(bundle, manifest)

    with pytest.raises(MiniQmtBundleError, match="placeholder"):
        MiniQmtControlledEvidenceService().run_bundle(
            dataset_version="kline_daily_20260518_v1",
            bundle_path=bundle,
            output_dir=tmp_path / "evidence",
            source_command="test command",
        )


def test_controlled_evidence_service_rejects_basic_ohlc_quality_failures(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path)
    _replace_artifact_rows(
        bundle,
        [
            {
                "symbol": "000001.SZ",
                "trade_date": "2026-05-18",
                "open": 10.0,
                "high": 9.5,
                "low": 10.2,
                "close": 10.1,
                "volume": 100000,
            }
        ],
    )

    with pytest.raises(MiniQmtBundleError, match="data quality checks failed"):
        MiniQmtControlledEvidenceService().run_bundle(
            dataset_version="kline_daily_20260518_v1",
            bundle_path=bundle,
            output_dir=tmp_path / "evidence",
            source_command="test command",
        )


def test_controlled_evidence_service_generates_validator_compatible_evidence(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path)
    output_dir = tmp_path / "evidence"
    run_at = datetime(2026, 5, 18, 9, 30, tzinfo=timezone.utc)

    result = MiniQmtControlledEvidenceService().run_bundle(
        dataset_version="kline_daily_20260518_v1",
        bundle_path=bundle,
        output_dir=output_dir,
        source_command="python scripts/market_data/run_miniqmt_controlled_evidence.py --dataset-version kline_daily_20260518_v1",
        run_at=run_at,
    )

    evidence = json.loads(result.evidence_path.read_text(encoding="utf-8"))
    raw_report = json.loads(result.raw_report_path.read_text(encoding="utf-8"))

    assert evidence["schema_version"] == "evidence.v1"
    assert evidence["evidence_key"] == "mystocks_dry_run"
    assert evidence["consumer_system"] == "mystocks_spec"
    assert evidence["dataset_version"] == "kline_daily_20260518_v1"
    assert evidence["lineage_id"] == "lin_kline_daily_20260518_v1"
    assert evidence["payload_hash"] == "payload-sha256"
    assert evidence["related_function_tree_node"] == "FUNCTION_TREE.md#8.1 Market Data M1 authoritative-ready 缺口"
    assert evidence["retention_decision"] == "keep_minimal_evidence"
    assert evidence["raw_source_file"] == "logs/mystocks_dry_run_kline_daily_20260518_v1.json"
    assert evidence["environment"]["consumer_system"] == "mystocks_spec"
    assert evidence["environment"]["field_mapping_version"] == "miniqmt.kline_daily.v1"
    assert evidence["hash_or_size"]["artifact_sha256"] == raw_report["artifact"]["hash"]
    assert evidence["hash_or_size"]["raw_report_sha256"] == result.raw_report_sha256
    assert evidence["hash_or_size"][evidence["raw_source_file"]]["sha256"] == result.raw_report_sha256
    assert evidence["hash_or_size"][evidence["raw_source_file"]]["byte_count"] == result.raw_report_size
    result_summary = evidence["result_summary"]
    assert result_summary["evidence_type"] == "promotion_consumer_dry_run"
    assert result_summary["consumer_system"] == "mystocks_spec"
    assert result_summary["dataset_version"] == "kline_daily_20260518_v1"
    assert result_summary["lineage_id"] == "lin_kline_daily_20260518_v1"
    assert result_summary["payload_hash"] == "payload-sha256"
    assert result_summary["row_count"] == 2
    assert result_summary["field_mapping_version"] == "miniqmt.kline_daily.v1"
    assert result_summary["database_target"] == "dry-run-only"
    assert result_summary["writes_performed"] is False
    assert result_summary["dry_run"]["passed"] is True
    assert result_summary["dry_run"]["failed_checks"] == []
    assert result_summary["dry_run"]["artifact_sha256_verified"] is True
    assert result_summary["dry_run"]["placeholder_count"] == 0
    assert raw_report["dry_run"]["mapped_classification"] == "daily_kline"
    assert raw_report["dry_run"]["failed_checks"] == []
    assert raw_report["dry_run"]["artifact_sha256_verified"] is True
    assert raw_report["dry_run"]["placeholder_count"] == 0


def test_controlled_evidence_service_supports_forward_output_suffix(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path)
    output_dir = tmp_path / "forward-evidence"
    run_at = datetime(2026, 5, 19, 9, 30, tzinfo=timezone.utc)

    result = MiniQmtControlledEvidenceService().run_bundle(
        dataset_version="kline_daily_20260518_v1",
        bundle_path=bundle,
        output_dir=output_dir,
        source_command="python scripts/market_data/run_miniqmt_controlled_evidence.py --dataset-version kline_daily_20260518_v1 --output-suffix forward",
        run_at=run_at,
        output_suffix="forward",
    )

    evidence = json.loads(result.evidence_path.read_text(encoding="utf-8"))
    raw_report = json.loads(result.raw_report_path.read_text(encoding="utf-8"))

    assert result.evidence_path.name == "2026-05-19-kline_daily_20260518_v1-mystocks-dry-run-forward.evidence.json"
    assert result.raw_report_path.name == "mystocks_dry_run_kline_daily_20260518_v1_forward.json"
    assert evidence["raw_source_file"] == "logs/mystocks_dry_run_kline_daily_20260518_v1_forward.json"
    assert evidence["result_summary"]["evidence_type"] == "promotion_consumer_dry_run"
    assert raw_report["dataset_version"] == "kline_daily_20260518_v1"


def test_controlled_evidence_service_rejects_template_artifact_rows(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path)
    artifact = bundle / "artifacts" / "kline_daily.json"
    artifact.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "symbol": "<symbol>",
                        "trade_date": "2026-05-18",
                        "open": 10.0,
                        "high": 10.5,
                        "low": 9.8,
                        "close": 10.2,
                        "volume": 100000,
                    }
                ]
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    manifest_path = bundle / "dataset_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifacts"][0]["hash"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    with pytest.raises(MiniQmtBundleError, match="raw report contains placeholder values"):
        MiniQmtControlledEvidenceService().run_bundle(
            dataset_version="kline_daily_20260518_v1",
            bundle_path=bundle,
            output_dir=tmp_path / "evidence",
            source_command="test command",
        )


def test_cli_writes_evidence_and_prints_machine_readable_summary(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    bundle = _write_bundle(tmp_path)
    output_dir = tmp_path / "cli-output"

    exit_code = cli_module.main(
        [
            "--dataset-version",
            "kline_daily_20260518_v1",
            "--bundle-path",
            str(bundle),
            "--output-dir",
            str(output_dir),
            "--output-suffix",
            "forward",
        ]
    )

    captured = capsys.readouterr()
    summary = json.loads(captured.out)
    assert exit_code == 0
    assert summary["status"] == "passed"
    assert summary["dataset_version"] == "kline_daily_20260518_v1"
    assert summary["row_count"] == 2
    assert summary["field_mapping_version"] == "miniqmt.kline_daily.v1"
    assert Path(summary["evidence_path"]).exists()
    assert Path(summary["raw_report_path"]).exists()
    assert Path(summary["evidence_path"]).name.endswith("-mystocks-dry-run-forward.evidence.json")
    assert Path(summary["raw_report_path"]).name.endswith("_forward.json")


def test_cli_can_insert_evidence_ledger_when_postgres_dsn_is_provided(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle = _write_bundle(tmp_path)
    output_dir = tmp_path / "cli-output"
    inserted_records: list[MarketDatasetEvidenceRecord] = []

    class FakeLedger:
        def insert_run(self, record: MarketDatasetEvidenceRecord) -> int:
            inserted_records.append(record)
            return 17

    monkeypatch.setattr(cli_module, "connect_postgres_ledger", lambda dsn: FakeLedger())

    exit_code = cli_module.main(
        [
            "--dataset-version",
            "kline_daily_20260518_v1",
            "--bundle-path",
            str(bundle),
            "--output-dir",
            str(output_dir),
            "--postgres-dsn",
            "postgresql://example.invalid/mystocks",
        ]
    )

    summary = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert summary["ledger_id"] == 17
    assert len(inserted_records) == 1
    assert inserted_records[0].dataset_version == "kline_daily_20260518_v1"
    assert inserted_records[0].dry_run_status == "passed"


def test_evidence_ledger_inserts_controlled_evidence_metadata(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path)
    output_dir = tmp_path / "evidence"
    result = MiniQmtControlledEvidenceService().run_bundle(
        dataset_version="kline_daily_20260518_v1",
        bundle_path=bundle,
        output_dir=output_dir,
        source_command="test command",
        run_at=datetime(2026, 5, 18, 9, 30, tzinfo=timezone.utc),
    )
    evidence = json.loads(result.evidence_path.read_text(encoding="utf-8"))
    raw_report = json.loads(result.raw_report_path.read_text(encoding="utf-8"))
    record = MarketDatasetEvidenceRecord.from_run_result(result, evidence=evidence, raw_report=raw_report)
    connection = _FakeConnection()

    inserted_id = MarketDatasetEvidenceLedger(connection).insert_run(record)

    assert inserted_id == 17
    assert connection.committed is True
    assert connection.cursor_obj.sql is not None
    assert "INSERT INTO market_dataset_evidence_runs" in connection.cursor_obj.sql
    assert "ON CONFLICT" in connection.cursor_obj.sql
    assert record.dataset_version in connection.cursor_obj.params
    assert record.lineage_id in connection.cursor_obj.params
    assert result.raw_report_sha256 in connection.cursor_obj.params
    assert result.evidence_sha256 in connection.cursor_obj.params


def test_evidence_ledger_updates_operator_supplied_miniqmt_status() -> None:
    connection = _FakeConnection()

    updated_id = MarketDatasetEvidenceLedger(connection).update_miniqmt_status(
        dataset_version="kline_daily_20260518_v1",
        evidence_key="mystocks_dry_run",
        evidence_type="promotion_consumer_dry_run",
        validation_status="passed",
        preview_status="passed",
        apply_status="not_submitted",
        operator_notes="miniQMT preview succeeded",
    )

    assert updated_id == 17
    assert connection.committed is True
    assert connection.cursor_obj.sql is not None
    assert "UPDATE market_dataset_evidence_runs" in connection.cursor_obj.sql
    assert "miniqmt_preview_status" in connection.cursor_obj.sql
    assert "miniQMT preview succeeded" in connection.cursor_obj.params


class _FakeCursor:
    def __init__(self) -> None:
        self.sql: str | None = None
        self.params: tuple[object, ...] = ()

    def execute(self, sql: str, params: tuple[object, ...]) -> None:
        self.sql = sql
        self.params = params

    def fetchone(self) -> tuple[int]:
        return (17,)


class _FakeConnection:
    def __init__(self) -> None:
        self.cursor_obj = _FakeCursor()
        self.committed = False

    def cursor(self) -> _FakeCursor:
        return self.cursor_obj

    def commit(self) -> None:
        self.committed = True
