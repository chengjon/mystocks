-- Migration: Add category column to watchlist_groups table
-- Feature: 005-ui User Story 3 - Watchlist Tabs Refactoring
-- Task: T004 [BLOCKING]
-- Date: 2025-10-26
-- Author: Claude Code

-- ============================================================================
-- Purpose: Add category field to support 4-tab watchlist layout
-- ============================================================================

BEGIN;

-- Step 1: Add category column with default value
-- Values: 'user', 'system', 'strategy', 'monitor'
ALTER TABLE watchlist_groups
ADD COLUMN category VARCHAR(20) DEFAULT 'user' NOT NULL;

-- Step 2: Create index for category queries (performance optimization)
CREATE INDEX idx_watchlist_groups_category
ON watchlist_groups(category);

-- Step 3: Update existing data
-- Mark all existing groups as 'user' category (default behavior)
UPDATE watchlist_groups
SET category = 'user'
WHERE category IS NULL OR category = '';

-- Step 4: Add check constraint for valid categories
ALTER TABLE watchlist_groups
ADD CONSTRAINT chk_watchlist_groups_category
CHECK (category IN ('user', 'system', 'strategy', 'monitor'));

COMMIT;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Verify column was added
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'watchlist_groups' AND column_name = 'category';

-- Verify index was created
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'watchlist_groups' AND indexname = 'idx_watchlist_groups_category';

-- Check distinct categories
SELECT category, COUNT(*) as count
FROM watchlist_groups
GROUP BY category;

-- ============================================================================
-- Rollback Script (if needed)
-- ============================================================================

-- BEGIN;
-- DROP INDEX IF EXISTS idx_watchlist_groups_category;
-- ALTER TABLE watchlist_groups DROP CONSTRAINT IF EXISTS chk_watchlist_groups_category;
-- ALTER TABLE watchlist_groups DROP COLUMN IF EXISTS category;
-- COMMIT;
