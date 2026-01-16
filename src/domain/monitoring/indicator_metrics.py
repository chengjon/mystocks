from prometheus_client import Histogram, Counter, Gauge

# Labels used: indicator_id, backend (cpu/numba/gpu)

# 1. Batch Calculation Latency
CALCULATION_LATENCY = Histogram(
    "indicator_batch_latency_seconds",
    "Time spent calculating indicators in batch mode",
    ["indicator_id", "backend"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# 2. Streaming Update Latency (Microsecond resolution)
STREAMING_LATENCY = Histogram(
    "indicator_streaming_latency_seconds",
    "Time spent updating indicators in streaming mode",
    ["indicator_id"],
    buckets=(0.000001, 0.000005, 0.00001, 0.000025, 0.00005, 0.0001, 0.001),
)

# 3. Request Counters
CALCULATION_REQUESTS = Counter(
    "indicator_requests_total",
    "Total number of indicator calculation requests",
    # mode: batch/streaming, status: success/error
    ["indicator_id", "mode", "status"],
)

# 4. Data Alignment Errors
ALIGNMENT_ERRORS = Counter(
    "indicator_alignment_errors_total", "Number of times output index did not align with input", ["indicator_id"]
)
