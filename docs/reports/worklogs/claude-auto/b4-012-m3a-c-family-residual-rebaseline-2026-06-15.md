# B4.012-M3a-C family residual rebaseline

Date: 2026-06-15
HEAD: `29b080886b105485c24d10306a155424c0bade83`

## Goal

Rebaseline the remaining `B4.012-M3a-C` tracked adapter/data-source test candidates after the closure of `C1`, `C2`, and `C3`, without touching source/runtime/OpenSpec/external dirty files.

## Scope Check

Original refined `M3a-C` tracked candidate set: 25 files.

Closed in prior subpackages:

- `C1`: 3 files
- `C2`: 4 files
- `C3`: 1 file

Covered total: 8 files.

Remaining in the original tracked set: 17 files.

All 17 remaining candidates are currently modified and should be split into family batches.

## Residual Families

### C4 - Akshare adapter family

Residual files:

- `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part1.py`
- `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part2.py`
- `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part3.py`
- `tests/test_akshare_adapter.py`
- `tests/unit/adapters/test_akshare_adapter.py`
- `tests/unit/adapters/test_akshare_adapter_real.py`
- `tests/adapters/test_akshare_adapter/helpers.py`

Signals:

- Largest concentration of edits.
- `ruff` already flags `PT009` in `helpers.py` and `part1.py` on current dirty content.
- `tests/test_akshare_adapter.py` still carries TODO/marker cleanup edits.

Risk: medium-high. This family is the most likely to require coordinated test hygiene and contract alignment.

### C5 - Other adapter compatibility family

Residual files:

- `tests/unit/adapters/test_baostock_adapter_real.py`
- `tests/unit/adapters/test_byapi_adapter_basic.py`
- `tests/unit/adapters/test_customer_adapter_basic.py`
- `tests/unit/adapters/test_financial_adapter_real.py`
- `tests/unit/adapters/test_financial_adapter_simple.py`
- `tests/unit/adapters/test_tdx_connection_manager.py`
- `tests/unit/adapters/test_tushare_adapter_basic.py`

Signals:

- Edits are small and mostly metadata / assertion cleanup.
- `py_compile` passes on the residual set.

Risk: medium-low. Suitable for a compact batch after Akshare is isolated.

### C6 - DataSourceManager family

Residual files:

- `tests/unit/adapters/test_data_source_manager.py`
- `tests/unit/adapters/test_data_source_manager_basic.py`
- `tests/unit/adapters/test_data_source_manager_fixed.py`

Signals:

- Narrow and cohesive manager-regression surface.
- `py_compile` passes on the residual set.

Risk: medium-low. Best handled as one small follow-up batch.

## Explicit Exclusions

These do not belong to the `C` family and remain governed by their own packages:

- API overlap: `M3a-B1/B2`
- backend overlap: `M3a-B3`
- generated/tooling overlap: `tests/generated/test_new_market_data_adapter_new_feature.py`
- untracked data-source provenance candidate: `tests/unit/data_source/test_data_source_client_contract.py`

## Static Checks on Remaining Dirty Set

- `python -m py_compile` on the 17 remaining modified tracked candidates: passed
- `python -m ruff check` on the 17 remaining modified tracked candidates: failed on pre-existing dirty content in `tests/adapters/test_akshare_adapter/helpers.py` and `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part1.py` with `PT009`

## Recommended Next Batches

1. `C4` Akshare adapter family
2. `C5` other adapter compatibility family
3. `C6` DataSourceManager family

## Conclusion

`B4.012-M3a-C` is not closed yet. The parent split still has 17 modified tracked files remaining, grouped cleanly into three follow-up families.
