from __future__ import annotations

from scripts.runtime.export_collab_snapshots import render_task_report_markdown


def test_task_report_prefers_live_graphiti_projection_when_provided() -> None:
    markdown = render_task_report_markdown(
        work_item={
            "work_item_id": "MT-200A",
            "title": "Graphiti live projection",
            "owner_cli": "cli-2",
            "status": "in_progress",
        },
        updates=[],
        requests=[],
        status_view=None,
        events=[
            {
                "event_type": "automation.graphiti_preflight_checked",
                "created_at": "2026-03-20T08:00:00+00:00",
                "payload": {
                    "server_status": "ok",
                    "ingest_status": "warming",
                    "search_summary": "nodes hit=1, facts hit=2, waited 60s",
                },
            }
        ],
        graphiti_projection={
            "server_status": "ok",
            "ingest_status": "completed",
            "search_summary": "nodes hit=1, facts hit=2, waited 60s",
        },
    )

    assert "ingest_status: `completed`" in markdown
    assert "ingest_status: `warming`" not in markdown


def test_task_report_renders_graphiti_projection_from_latest_event() -> None:
    markdown = render_task_report_markdown(
        work_item={
            "work_item_id": "MT-200",
            "title": "Graphiti projection",
            "owner_cli": "cli-2",
            "status": "in_progress",
        },
        updates=[],
        requests=[],
        status_view=None,
        events=[
            {
                "event_type": "automation.graphiti_preflight_checked",
                "created_at": "2026-03-20T08:00:00+00:00",
                "payload": {
                    "server_status": "ok",
                    "ingest_status": "warming",
                    "search_summary": "nodes hit=1, facts hit=2, waited 60s",
                },
            }
        ],
    )

    assert "## Graphiti" in markdown
    assert "server_status: `ok`" in markdown
    assert "ingest_status: `warming`" in markdown
    assert "search_summary: `nodes hit=1, facts hit=2, waited 60s`" in markdown


def test_task_report_renders_empty_graphiti_projection_when_no_event_exists() -> None:
    markdown = render_task_report_markdown(
        work_item={
            "work_item_id": "MT-201",
            "title": "Graphiti projection missing",
            "owner_cli": "cli-2",
            "status": "in_progress",
        },
        updates=[],
        requests=[],
        status_view=None,
        events=[],
    )

    assert "## Graphiti" in markdown
    assert "server_status: `(none)`" in markdown
    assert "ingest_status: `(none)`" in markdown
    assert "search_summary: `(none)`" in markdown


def test_task_report_renders_transcript_summary_without_inlining_full_body() -> None:
    markdown = render_task_report_markdown(
        work_item={
            "work_item_id": "MT-202",
            "title": "Transcript summary",
            "owner_cli": "cli-2",
            "status": "in_progress",
        },
        updates=[],
        requests=[],
        status_view=None,
        events=[],
        transcripts=[
            {
                "session_id": "sess-202",
                "actor_cli": "cli-2",
                "transcript_kind": "MANUAL",
                "started_at": "2026-04-03T00:00:00+00:00",
                "hot_body_available": False,
                "archive_locator": "archive/MT-202/sess-202/transcript.txt",
                "content": "this should not be inlined",
            }
        ],
    )

    assert "## Transcripts" in markdown
    assert "sess-202" in markdown
    assert "archive/MT-202/sess-202/transcript.txt" in markdown
    assert "this should not be inlined" not in markdown
