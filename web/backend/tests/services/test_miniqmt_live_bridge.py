from web.backend.app.services.miniqmt_live_bridge import (
    BRIDGE_RESULT_PAYLOAD,
    BRIDGE_RESULT_TIMEOUT,
    BRIDGE_SUBMISSION_RECEIPT,
    MiniQMTLiveBridgeClient,
)


class _BridgeAdapterStub:
    def __init__(self, *, receipt=None, results=None):
        self.receipt = receipt or {}
        self.results = list(results or [])
        self.last_endpoint = None
        self.last_params = None
        self.result_calls = 0

    def get_data(self, endpoint, params=None):
        self.last_endpoint = endpoint
        self.last_params = params
        return self.receipt

    def get_task_result(self, provider_name, task_id):
        self.result_calls += 1
        if self.results:
            return self.results.pop(0)
        return {"status": "running", "task_id": task_id}


def test_submit_order_normalizes_canonical_live_receipt():
    bridge_adapter = _BridgeAdapterStub(
        receipt={
            "status": "success",
            "task_id": "bridge-task-0101",
            "timestamp": "2026-04-29T10:00:00+00:00",
            "source": "qmt",
            "bridge_contract_version": "1",
        }
    )
    client = MiniQMTLiveBridgeClient(bridge_adapter)

    receipt = client.submit_order({"client_order_id": "submission-0101", "symbol": "000001"})

    assert receipt["contract_state"] == BRIDGE_SUBMISSION_RECEIPT
    assert receipt["provider"] == "qmt"
    assert receipt["method"] == "submit_order"
    assert receipt["task_id"] == "bridge-task-0101"
    assert receipt["receipt_timestamp"] == "2026-04-29T10:00:00+00:00"
    assert bridge_adapter.last_endpoint == "qmt/submit_order"


def test_poll_task_result_returns_canonical_bridge_payload():
    bridge_adapter = _BridgeAdapterStub(
        results=[
            {"status": "running", "task_id": "bridge-task-0102", "bridge_contract_version": "1"},
            {
                "status": "completed",
                "task_id": "bridge-task-0102",
                "bridge_contract_version": "1",
                "result": {
                    "status": "accepted",
                    "updated_at": "2026-04-29T10:01:00+00:00",
                    "client_order_id": "submission-0102",
                    "account_scope": "sim-account-0102",
                    "event_id": "evt-0102",
                    "entrust_no": "broker-order-0102",
                    "sequence_no": "seq-0102",
                },
            },
        ]
    )
    sleeps = []
    times = iter([0.0, 0.1, 0.2])
    client = MiniQMTLiveBridgeClient(
        bridge_adapter,
        time_fn=lambda: next(times),
        sleep_fn=lambda seconds: sleeps.append(seconds),
        poll_interval_seconds=0.01,
    )

    result = client.poll_task_result("bridge-task-0102")

    assert result["contract_state"] == BRIDGE_RESULT_PAYLOAD
    assert result["task_id"] == "bridge-task-0102"
    assert result["broker_event_type"] == "acknowledgement"
    assert result["local_submission_id"] == "submission-0102"
    assert result["account_scope"] == "sim-account-0102"
    assert result["event_id"] == "evt-0102"
    assert result["external_order_id"] == "broker-order-0102"
    assert result["sequence_id"] == "seq-0102"
    assert result["bridge_contract_version"] == "1"
    assert sleeps == [0.01]


def test_poll_task_result_times_out_when_bridge_never_reaches_terminal_state():
    bridge_adapter = _BridgeAdapterStub(
        results=[
            {"status": "running", "task_id": "bridge-task-0103", "bridge_contract_version": "1"},
            {"status": "running", "task_id": "bridge-task-0103", "bridge_contract_version": "1"},
        ]
    )
    times = iter([0.0, 0.05, 0.15])
    client = MiniQMTLiveBridgeClient(
        bridge_adapter,
        time_fn=lambda: next(times),
        sleep_fn=lambda seconds: None,
        timeout_seconds=0.1,
        poll_interval_seconds=0.01,
    )

    result = client.poll_task_result("bridge-task-0103")

    assert result["contract_state"] == BRIDGE_RESULT_TIMEOUT
    assert result["task_id"] == "bridge-task-0103"
    assert result["reason_code"] == "bridge_result_timeout"


def test_submit_order_surfaces_authenticated_contract_failure_state():
    bridge_adapter = _BridgeAdapterStub(
        receipt={
            "status": "error",
            "task_id": "bridge-task-auth-0104",
            "reason_code": "live_bridge_auth_failed",
            "reason_detail": "missing bearer token",
            "failure_class": "live_bridge_auth_failed",
            "bridge_contract_version": "1",
        }
    )
    client = MiniQMTLiveBridgeClient(bridge_adapter)

    receipt = client.submit_order({"client_order_id": "submission-0104", "symbol": "000001"})

    assert receipt["contract_state"] == "bridge_submission_auth_failed"
    assert receipt["task_id"] == "bridge-task-auth-0104"
    assert receipt["reason_code"] == "live_bridge_auth_failed"
    assert receipt["bridge_contract_version"] == "1"


def test_fetch_task_result_surfaces_contract_version_mismatch():
    bridge_adapter = _BridgeAdapterStub(
        results=[
            {
                "status": "error",
                "task_id": "bridge-task-version-0105",
                "reason_code": "live_bridge_unsupported_contract_version",
                "reason_detail": "agent only supports contract version 2",
                "bridge_contract_version": "2",
            }
        ]
    )
    client = MiniQMTLiveBridgeClient(bridge_adapter)

    result = client.fetch_task_result("bridge-task-version-0105")

    assert result["contract_state"] == "bridge_result_unsupported_contract_version"
    assert result["reason_code"] == "live_bridge_unsupported_contract_version"
    assert result["bridge_contract_version"] == "2"
