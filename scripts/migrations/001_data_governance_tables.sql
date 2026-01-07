-- Migration: Create data governance tables
-- Run this script to create tables for data lineage tracking and asset management
-- Database: PostgreSQL
-- Version: 1.0

-- Create data lineage nodes table
CREATE TABLE IF NOT EXISTS data_lineage_nodes (
    node_id VARCHAR(255) PRIMARY KEY,
    node_type VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create data lineage edges table
CREATE TABLE IF NOT EXISTS data_lineage_edges (
    id SERIAL PRIMARY KEY,
    from_node VARCHAR(255) NOT NULL REFERENCES data_lineage_nodes(node_id),
    to_node VARCHAR(255) NOT NULL REFERENCES data_lineage_nodes(node_id),
    operation VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    CONSTRAINT unique_edge UNIQUE (from_node, to_node, operation, timestamp)
);

-- Create data assets table
CREATE TABLE IF NOT EXISTS data_assets (
    asset_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(50) NOT NULL,
    source VARCHAR(255) NOT NULL,
    schema JSONB DEFAULT '{}',
    description TEXT,
    owner VARCHAR(255),
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP WITH TIME ZONE,
    access_count INTEGER DEFAULT 0,
    quality_score DECIMAL(5,2),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_lineage_nodes_type ON data_lineage_nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_lineage_edges_from ON data_lineage_edges(from_node);
CREATE INDEX IF NOT EXISTS idx_lineage_edges_to ON data_lineage_edges(to_node);
CREATE INDEX IF NOT EXISTS idx_lineage_edges_operation ON data_lineage_edges(operation);
CREATE INDEX IF NOT EXISTS idx_assets_type ON data_assets(asset_type);
CREATE INDEX IF NOT EXISTS idx_assets_source ON data_assets(source);
CREATE INDEX IF NOT EXISTS idx_assets_updated ON data_assets(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_assets_access_count ON data_assets(access_count DESC);

-- Add foreign key constraints for lineage edges
ALTER TABLE data_lineage_edges
DROP CONSTRAINT IF EXISTS fk_from_node;
ALTER TABLE data_lineage_edges
ADD CONSTRAINT fk_from_node
FOREIGN KEY (from_node) REFERENCES data_lineage_nodes(node_id)
ON DELETE CASCADE;

ALTER TABLE data_lineage_edges
DROP CONSTRAINT IF EXISTS fk_to_node;
ALTER TABLE data_lineage_edges
ADD CONSTRAINT fk_to_node
FOREIGN KEY (to_node) REFERENCES data_lineage_nodes(node_id)
ON DELETE CASCADE;

-- Comments for documentation
COMMENT ON TABLE data_lineage_nodes IS 'Stores nodes in the data lineage graph (data sources, datasets, APIs, storage)';
COMMENT ON TABLE data_lineage_edges IS 'Stores edges connecting nodes in the data lineage graph';
COMMENT ON TABLE data_assets IS 'Stores metadata for all data assets in the system';
COMMENT ON COLUMN data_lineage_nodes.node_type IS 'Type of node: datasource, dataset, api, storage, transform';
COMMENT ON COLUMN data_lineage_edges.operation IS 'Type of operation: fetch, transform, store, serve';
COMMENT ON COLUMN data_assets.asset_type IS 'Type of asset: dataset, table, view, api, model, report';
