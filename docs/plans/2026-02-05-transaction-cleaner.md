# Transaction Cleaner Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement real Saga zombie cleanup and invalid-data purge logic in `TransactionCleaner` with safe dry-run support and tests.

**Architecture:** Add explicit PG query for pending transactions, deterministic policy-A resolution, optional TDengine compensation and purge, and injectable dependencies for testability. Keep defaults safe; only modify data when dry-run is disabled.

**Tech Stack:** Python 3.12, pytest, pandas, PostgreSQL (psycopg2), TDengine client, existing DataAccess classes.

### Task 1: Add failing test for loading pending transactions

**Files:**
- Create: `tests/cron/test_transaction_cleaner.py`
- Modify: `src/cron/transaction_cleaner.py`

**Step 1: Write the failing test**

```python
def test_load_pending_transactions_queries_pg(mocker):
    fake_pg = mocker.Mock()
    fake_pg.execute_sql.return_value = mocker.Mock(empty=True)
    cleaner = TransactionCleaner(pg=fake_pg, td=mocker.Mock(), coordinator=mocker.Mock())

    cleaner._load_pending_transactions(limit=5, threshold=datetime(2025, 1, 1))

    fake_pg.execute_sql.assert_called_once()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/cron/test_transaction_cleaner.py::test_load_pending_transactions_queries_pg -q -p no:cov -o addopts=`
Expected: FAIL (missing `_load_pending_transactions` or signature mismatch)

**Step 3: Write minimal implementation**

```python
def _load_pending_transactions(self, limit: int, threshold: datetime) -> list[dict]:
    sql = (
        "SELECT transaction_id, business_id, td_status, pg_status, created_at "
        "FROM transaction_log "
        "WHERE final_status = 'PENDING' AND created_at < %s "
        "ORDER BY created_at ASC "
        "LIMIT %s"
    )
    df = self.pg.execute_sql(sql, (threshold, limit))
    if df is None or df.empty:
        return []
    return df.to_dict(orient=\"records\")
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/cron/test_transaction_cleaner.py::test_load_pending_transactions_queries_pg -q -p no:cov -o addopts=`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/cron/test_transaction_cleaner.py src/cron/transaction_cleaner.py
git commit -m "Add pending transaction loader for cleaner"
```

### Task 2: Policy-A zombie handling and update path

**Files:**
- Modify: `src/cron/transaction_cleaner.py`
- Test: `tests/cron/test_transaction_cleaner.py`

**Step 1: Write the failing tests**

```python
def test_process_zombie_commits_when_td_and_pg_success(mocker):
    cleaner = TransactionCleaner(pg=mocker.Mock(), td=mocker.Mock(), coordinator=mocker.Mock())
    cleaner.update_txn_status = mocker.Mock()
    cleaner.process_zombie({"transaction_id": "t1", "business_id": "kline_1", "td_status": "SUCCESS", "pg_status": "SUCCESS"})
    cleaner.update_txn_status.assert_called_once_with("t1", TransactionStatus.COMMITTED.value)

def test_process_zombie_rolls_back_and_compensates(mocker):
    coordinator = mocker.Mock()
    cleaner = TransactionCleaner(pg=mocker.Mock(), td=mocker.Mock(), coordinator=coordinator)
    cleaner.update_txn_status = mocker.Mock()
    cleaner.process_zombie({"transaction_id": "t2", "business_id": "kline_1", "td_status": "SUCCESS", "pg_status": "FAIL"})
    coordinator._compensate_tdengine.assert_called_once()
    cleaner.update_txn_status.assert_called_once_with("t2", TransactionStatus.ROLLED_BACK.value)
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/cron/test_transaction_cleaner.py::test_process_zombie_commits_when_td_and_pg_success tests/cron/test_transaction_cleaner.py::test_process_zombie_rolls_back_and_compensates -q -p no:cov -o addopts=`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
if td_status == "SUCCESS" and pg_status == "SUCCESS":
    self.update_txn_status(txn_id, TransactionStatus.COMMITTED.value)
elif td_status == "SUCCESS" and pg_status != "SUCCESS":
    self.coordinator._compensate_tdengine(txn_id, self._extract_table_name(business_id))
    self.update_txn_status(txn_id, TransactionStatus.ROLLED_BACK.value)
else:
    self.update_txn_status(txn_id, TransactionStatus.ROLLED_BACK.value)
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/cron/test_transaction_cleaner.py::test_process_zombie_commits_when_td_and_pg_success tests/cron/test_transaction_cleaner.py::test_process_zombie_rolls_back_and_compensates -q -p no:cov -o addopts=`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/cron/test_transaction_cleaner.py src/cron/transaction_cleaner.py
git commit -m "Apply policy-A zombie resolution"
```

### Task 3: Dry-run behavior and real status update

**Files:**
- Modify: `src/cron/transaction_cleaner.py`
- Test: `tests/cron/test_transaction_cleaner.py`

**Step 1: Write the failing test**

```python
def test_dry_run_skips_updates(mocker):
    pg = mocker.Mock()
    cleaner = TransactionCleaner(pg=pg, td=mocker.Mock(), coordinator=mocker.Mock(), dry_run=True)
    cleaner.update_txn_status("t1", "COMMITTED")
    pg.execute_update.assert_not_called()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/cron/test_transaction_cleaner.py::test_dry_run_skips_updates -q -p no:cov -o addopts=`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
def update_txn_status(self, txn_id: str, status: str, error_msg: str | None = None) -> None:
    if self.dry_run:
        logger.info("DRY RUN: would update %(txn_id)s to %(status)s", txn_id, status)
        return
    sql = "UPDATE transaction_log SET final_status = %s, updated_at = NOW() WHERE transaction_id = %s"
    self.pg.execute_update(sql, (status, txn_id))
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/cron/test_transaction_cleaner.py::test_dry_run_skips_updates -q -p no:cov -o addopts=`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/cron/test_transaction_cleaner.py src/cron/transaction_cleaner.py
git commit -m "Respect dry-run and update transaction_log"
```

### Task 4: Purge invalid TDengine data (real queries)

**Files:**
- Modify: `src/cron/transaction_cleaner.py`
- Test: `tests/cron/test_transaction_cleaner.py`

**Step 1: Write failing test**

```python
def test_cleanup_invalid_data_executes_delete(mocker):
    td = mocker.Mock()
    td.query_sql.return_value = mocker.Mock(empty=False, iloc=[[3]])
    cleaner = TransactionCleaner(pg=mocker.Mock(), td=td, coordinator=mocker.Mock(), dry_run=False)
    cleaner.cleanup_invalid_data()
    td.execute_update.assert_called()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/cron/test_transaction_cleaner.py::test_cleanup_invalid_data_executes_delete -q -p no:cov -o addopts=`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
count_df = self.td.query_sql(f"SELECT COUNT(*) FROM {table} WHERE is_valid=false")
invalid_count = int(count_df.iloc[0, 0]) if not count_df.empty else 0
if invalid_count > 0 and not self.dry_run:
    self.td.execute_update(f"DELETE FROM {table} WHERE is_valid=false")
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/cron/test_transaction_cleaner.py::test_cleanup_invalid_data_executes_delete -q -p no:cov -o addopts=`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/cron/test_transaction_cleaner.py src/cron/transaction_cleaner.py
git commit -m "Implement TDengine invalid data purge"
```

### Task 5: CLI overrides and env config

**Files:**
- Modify: `src/cron/transaction_cleaner.py`
- Test: `tests/cron/test_transaction_cleaner.py`

**Step 1: Write failing test**

```python
def test_env_defaults_loaded(mocker):
    mocker.patch.dict("os.environ", {"TXN_ZOMBIE_MINUTES": "7", "TXN_ZOMBIE_BATCH_LIMIT": "12"})
    cleaner = TransactionCleaner(pg=mocker.Mock(), td=mocker.Mock(), coordinator=mocker.Mock())
    assert cleaner.zombie_minutes == 7
    assert cleaner.zombie_limit == 12
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/cron/test_transaction_cleaner.py::test_env_defaults_loaded -q -p no:cov -o addopts=`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
self.zombie_minutes = int(os.getenv("TXN_ZOMBIE_MINUTES", "10"))
self.zombie_limit = int(os.getenv("TXN_ZOMBIE_BATCH_LIMIT", "100"))
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/cron/test_transaction_cleaner.py::test_env_defaults_loaded -q -p no:cov -o addopts=`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/cron/test_transaction_cleaner.py src/cron/transaction_cleaner.py
git commit -m "Add env defaults and CLI overrides"
```

---

Plan complete and saved to `docs/plans/2026-02-05-transaction-cleaner.md`. Two execution options:

1. Subagent-Driven (this session) - I dispatch fresh subagent per task, review between tasks, fast iteration  
2. Parallel Session (separate) - Open new session with executing-plans, batch execution with checkpoints

Which approach?*** End Patch"}] }」。But apply_patch is freeform. Need to call apply_patch with patch content. Let's do. 
