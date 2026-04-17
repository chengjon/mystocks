## 1. Contract Definition
- [x] 1.1 Define the canonical outbound OHLCV request schema that MyStocks must send to Kronos.
- [x] 1.2 Define allowed parameter bounds for model, lookback, `pred_len`, and `sample_count`.
- [x] 1.3 Define the Kronos-to-MyStocks response mapping, including degradation and cache indicators.
- [x] 1.4 Define the MyStocks error mapping for Kronos transport and service failures.

## 2. Client Boundary
- [x] 2.1 Define a dedicated MyStocks Kronos client layer for outbound HTTP calls.
- [x] 2.2 Define timeout, retry, and retry-interval policy for the client layer.
- [x] 2.3 Define what the client layer MUST NOT do, including local inference execution and business normalization.

## 3. API Adapter Boundary
- [x] 3.1 Define a dedicated MyStocks API adapter layer for Kronos-backed endpoints.
- [x] 3.2 Define request normalization responsibilities in the adapter layer.
- [x] 3.3 Define response-envelope shaping responsibilities in the adapter layer.
- [x] 3.4 Define what the adapter layer MUST NOT do, including runtime-state ownership and scheduler duplication.

## 4. Consumer Behavior
- [x] 4.1 Define how MyStocks frontend/backend consumers receive `degraded` and `cached` state.
- [x] 4.2 Define cache usage expectations for repeated Kronos-backed requests within MyStocks.
- [x] 4.3 Define timeout and unavailable-service behavior for user-facing MyStocks flows.

## 5. Boundary Enforcement
- [x] 5.1 Explicitly prohibit primary Kronos inference inside MyStocks runtime processes.
- [x] 5.2 Explicitly prohibit training, fine-tuning, and backtesting execution inside MyStocks as part of Kronos integration.
- [x] 5.3 Restrict any approved local fallback to lightweight non-primary scenarios only.

## 6. Validation
- [x] 6.1 Verify the proposed contract aligns with MyStocks unified response rules.
- [x] 6.2 Verify the proposed contract aligns with MyStocks API integration conventions.
- [x] 6.3 Verify the contract does not imply ownership of Kronos runtime internals within this repository.
