-- src/storage/schema/indicator_registry.sql

-- 1. Create Indicator Registry Table
CREATE TABLE IF NOT EXISTS indicator_registry (
    id SERIAL PRIMARY KEY,

    -- Basic Information
    indicator_name VARCHAR(50) NOT NULL,        -- e.g., SMA, RSI
    indicator_type VARCHAR(20) NOT NULL,        -- trend/momentum/volatility/volume
    indicator_id VARCHAR(100) UNIQUE NOT NULL,   -- e.g., sma.20, rsi.14

    -- Implementation Details
    implementation_type VARCHAR(20),            -- python/talib/numba/gpu
    class_name VARCHAR(100),                    -- Python class name
    module_path TEXT,                           -- Python module path
    dependencies TEXT[],                        -- List of dependent indicator IDs

    -- Classification & Usage
    indicator_category VARCHAR(50) NOT NULL,    -- trend_indicators/etc.
    use_case VARCHAR(20) NOT NULL,             -- backtest/realtime/batch
    supported_backends TEXT[],                  -- Array: [cpu, gpu, numba]
    supports_streaming BOOLEAN DEFAULT FALSE,   -- Streaming support flag

    -- Safety Flags
    is_lagging BOOLEAN DEFAULT TRUE,            -- Is it a lagging indicator?
    lookahead_bias BOOLEAN DEFAULT FALSE,       -- Does it use future data?

    -- Metadata
    description TEXT,
    formula TEXT,                               -- LaTeX formula
    parameters JSONB,                           -- Parameter definitions
    required_columns TEXT[],                    -- Required input columns
    output_columns TEXT[],                      -- Output column names

    -- Performance Stats
    performance_score FLOAT DEFAULT 8.0,        -- 0-10 score
    avg_calculation_time FLOAT DEFAULT 0,       -- ms
    benchmark_rows INT DEFAULT 1000,            -- Rows used for benchmark

    -- Quality Stats
    accuracy_score FLOAT DEFAULT 8.0,           -- vs TA-Lib
    stability_score FLOAT DEFAULT 8.0,
    test_coverage FLOAT DEFAULT 0.0,

    -- Monitoring
    last_test_time TIMESTAMP,
    last_test_success BOOLEAN,
    total_calculations INT DEFAULT 0,
    failed_calculations INT DEFAULT 0,
    consecutive_failures INT DEFAULT 0,

    -- Status
    status VARCHAR(20) DEFAULT 'active',       -- active/deprecated/experimental
    tags TEXT[],

    -- Management
    owner VARCHAR(50) DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_status CHECK (status IN ('active', 'deprecated', 'experimental')),
    CONSTRAINT chk_performance_score CHECK (performance_score >= 0 AND performance_score <= 10)
);

-- 2. Create Indexes
CREATE INDEX IF NOT EXISTS idx_ir_category ON indicator_registry(indicator_category);
CREATE INDEX IF NOT EXISTS idx_ir_type ON indicator_registry(indicator_type, status);
CREATE INDEX IF NOT EXISTS idx_ir_name ON indicator_registry(indicator_name);
CREATE INDEX IF NOT EXISTS idx_ir_performance ON indicator_registry(performance_score DESC);

-- 3. Create Calculation History Table (For Monitoring)
CREATE TABLE IF NOT EXISTS indicator_calculation_history (
    id BIGSERIAL PRIMARY KEY,
    indicator_id VARCHAR(100) NOT NULL,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Context
    parameters JSONB,
    mode VARCHAR(20),                          -- batch/streaming

    -- Results
    success BOOLEAN NOT NULL,
    duration_ms FLOAT,                         -- Calculation duration
    row_count INT,                             -- Rows processed

    -- Diagnostics
    error_message TEXT,
    backend_used VARCHAR(20),                  -- cpu/gpu/numba/talib

    CONSTRAINT fk_indicator FOREIGN KEY (indicator_id)
        REFERENCES indicator_registry(indicator_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ich_time ON indicator_calculation_history(calculation_time DESC);
CREATE INDEX IF NOT EXISTS idx_ich_indicator ON indicator_calculation_history(indicator_id, calculation_time DESC);
