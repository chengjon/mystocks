-- ========================================
-- Watchlist Tables Migration
-- Version: 1.2
-- Date: 2025-01-20
-- Purpose: Create watchlist_groups and migrate user_watchlist to new schema
-- ========================================

BEGIN;

-- Step 1: Create watchlist_groups table
CREATE TABLE IF NOT EXISTS watchlist_groups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    group_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sort_order INTEGER DEFAULT 0,
    stock_count INTEGER DEFAULT 0,
    UNIQUE(user_id, group_name)
);

-- Step 2: Create index for watchlist_groups
CREATE INDEX IF NOT EXISTS idx_watchlist_groups_user
    ON watchlist_groups(user_id);

-- Step 3: Check if user_watchlist needs migration
-- If it has 'symbol' column (old schema), we need to migrate
DO $$
DECLARE
    has_old_schema BOOLEAN;
BEGIN
    -- Check if user_watchlist has the old 'symbol' column
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'user_watchlist'
        AND column_name = 'symbol'
    ) INTO has_old_schema;

    IF has_old_schema THEN
        -- Old schema detected, perform migration
        RAISE NOTICE 'Old user_watchlist schema detected, performing migration...';

        -- First, create default groups for all users in the existing watchlist
        INSERT INTO watchlist_groups (user_id, group_name, created_at)
        SELECT DISTINCT user_id, '默认分组', CURRENT_TIMESTAMP
        FROM user_watchlist
        ON CONFLICT (user_id, group_name) DO NOTHING;

        -- Create temporary backup table
        CREATE TEMP TABLE user_watchlist_backup AS
        SELECT * FROM user_watchlist;

        -- Drop old table
        DROP TABLE user_watchlist CASCADE;

        -- Create new table with correct schema
        CREATE TABLE user_watchlist (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL REFERENCES watchlist_groups(id) ON DELETE CASCADE,
            stock_code VARCHAR(20) NOT NULL,
            stock_name VARCHAR(100),
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            UNIQUE(user_id, group_id, stock_code)
        );

        -- Migrate data from backup to new table
        -- Assign all stocks to the default group for each user
        INSERT INTO user_watchlist (user_id, group_id, stock_code, stock_name, added_at, notes)
        SELECT
            b.user_id,
            g.id as group_id,  -- Use default group id
            b.symbol as stock_code,  -- Rename symbol to stock_code
            b.display_name as stock_name,  -- Rename display_name to stock_name
            b.added_at,
            b.notes
        FROM user_watchlist_backup b
        JOIN watchlist_groups g ON g.user_id = b.user_id AND g.group_name = '默认分组'
        ON CONFLICT (user_id, group_id, stock_code) DO NOTHING;

        RAISE NOTICE 'Migration completed: % rows migrated', (SELECT COUNT(*) FROM user_watchlist);

    ELSE
        -- New schema already exists or table doesn't exist
        -- Create table if it doesn't exist
        CREATE TABLE IF NOT EXISTS user_watchlist (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL REFERENCES watchlist_groups(id) ON DELETE CASCADE,
            stock_code VARCHAR(20) NOT NULL,
            stock_name VARCHAR(100),
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            UNIQUE(user_id, group_id, stock_code)
        );

        RAISE NOTICE 'user_watchlist table ready (no migration needed)';
    END IF;
END $$;

-- Step 4: Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_watchlist_user_group
    ON user_watchlist(user_id, group_id);

CREATE INDEX IF NOT EXISTS idx_user_watchlist_stock_code
    ON user_watchlist(stock_code);

-- Step 5: Create trigger function for stock_count maintenance
CREATE OR REPLACE FUNCTION update_group_stock_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE watchlist_groups
        SET stock_count = stock_count + 1
        WHERE id = NEW.group_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE watchlist_groups
        SET stock_count = stock_count - 1
        WHERE id = OLD.group_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Step 6: Create trigger
DROP TRIGGER IF EXISTS trg_update_stock_count ON user_watchlist;
CREATE TRIGGER trg_update_stock_count
    AFTER INSERT OR DELETE ON user_watchlist
    FOR EACH ROW
    EXECUTE FUNCTION update_group_stock_count();

-- Step 7: Update stock_count for existing groups
UPDATE watchlist_groups g
SET stock_count = (
    SELECT COUNT(*)
    FROM user_watchlist w
    WHERE w.group_id = g.id
);

COMMIT;

-- Migration completed successfully
-- Tables created/migrated: watchlist_groups, user_watchlist
-- Triggers created: trg_update_stock_count
-- Default groups created for users with existing watchlist data
