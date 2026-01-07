-- PostgreSQL Transaction Log Table Creation
-- 用于 Saga 模式分布式事务协调

CREATE TABLE IF NOT EXISTS transaction_log (
    transaction_id VARCHAR(64) PRIMARY KEY,
    business_type VARCHAR(32) NOT NULL,      -- E.g., 'KLINE_SYNC'
    business_id VARCHAR(128) NOT NULL,       -- E.g., '600000.SH_DAILY_20240101'

    -- 阶段 1: TDengine 写入状态
    td_status VARCHAR(16) DEFAULT 'INIT',    -- INIT, SUCCESS, FAIL, UNKNOWN
    td_write_time TIMESTAMP,

    -- 阶段 2: PG 元数据更新状态
    pg_status VARCHAR(16) DEFAULT 'INIT',    -- INIT, SUCCESS, FAIL
    pg_update_time TIMESTAMP,

    -- 整体事务状态
    final_status VARCHAR(16) DEFAULT 'PENDING', -- PENDING, COMMITTED, ROLLED_BACK

    retry_count INT DEFAULT 0,
    error_msg TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_trans_status ON transaction_log(final_status);
CREATE INDEX IF NOT EXISTS idx_trans_biz_id ON transaction_log(business_id);
CREATE INDEX IF NOT EXISTS idx_trans_created_at ON transaction_log(created_at);

-- Comment
COMMENT ON TABLE transaction_log IS '分布式事务 Saga 模式状态追踪表';
