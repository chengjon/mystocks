-- Database Migration for User Authentication System
-- Task 2.1: User Authentication System Enhancement
-- Created: 2025-10-28

-- Enable UUID extension if needed (optional, for future use)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. Users Table - Main user account storage
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),  -- NULL for OAuth2-only users

    -- User attributes
    role VARCHAR(50) DEFAULT 'user' NOT NULL,  -- user, analyst, trader, admin
    is_active BOOLEAN DEFAULT TRUE NOT NULL,

    -- Email verification
    email_verified BOOLEAN DEFAULT FALSE NOT NULL,
    email_verified_at TIMESTAMP NULL,

    -- MFA/2FA
    mfa_enabled BOOLEAN DEFAULT FALSE NOT NULL,
    mfa_method VARCHAR(20),  -- 'totp', 'email', 'sms'

    -- User details
    full_name VARCHAR(100),
    avatar_url VARCHAR(500),

    -- Account security
    failed_login_attempts INTEGER DEFAULT 0 NOT NULL,
    locked_until TIMESTAMP NULL,  -- Account lock time
    password_changed_at TIMESTAMP NULL,

    -- User preferences (JSON format)
    preferences TEXT,

    -- Account deletion
    deletion_requested_at TIMESTAMP NULL,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login TIMESTAMP NULL,
    last_login_ip VARCHAR(45)  -- IPv4 or IPv6
);

-- Create indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- ============================================================================
-- 2. OAuth2 Accounts Table - Third-party OAuth2 provider accounts
-- ============================================================================
CREATE TABLE IF NOT EXISTS oauth2_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- OAuth2 provider information
    provider VARCHAR(50) NOT NULL,  -- 'google', 'github', 'microsoft', etc.
    provider_user_id VARCHAR(255) NOT NULL,  -- User ID from OAuth2 provider

    -- OAuth2 tokens
    access_token VARCHAR(1000),
    refresh_token VARCHAR(1000),
    token_type VARCHAR(50) DEFAULT 'Bearer' NOT NULL,
    token_expires_at TIMESTAMP NULL,

    -- Provider user information
    provider_email VARCHAR(100),
    provider_name VARCHAR(100),
    provider_avatar VARCHAR(500),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_used_at TIMESTAMP NULL,

    -- Unique constraint to prevent duplicate OAuth2 accounts
    CONSTRAINT uq_oauth2_provider_user UNIQUE(provider, provider_user_id)
);

-- Create indexes for oauth2_accounts table
CREATE INDEX IF NOT EXISTS idx_oauth2_user_id ON oauth2_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_oauth2_provider ON oauth2_accounts(provider);
CREATE INDEX IF NOT EXISTS idx_oauth2_provider_user_id ON oauth2_accounts(provider_user_id);

-- ============================================================================
-- 3. MFA Secrets Table - Multi-Factor Authentication configuration
-- ============================================================================
CREATE TABLE IF NOT EXISTS mfa_secrets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- MFA method
    method VARCHAR(20) NOT NULL,  -- 'totp', 'email', 'sms'

    -- MFA credentials/secrets
    secret VARCHAR(255) NOT NULL,  -- TOTP secret or other credentials
    backup_codes TEXT,  -- JSON format backup codes

    -- Status
    verified BOOLEAN DEFAULT FALSE NOT NULL,
    enabled BOOLEAN DEFAULT FALSE NOT NULL,

    -- Configuration metadata (JSON format)
    config TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    verified_at TIMESTAMP NULL,

    -- Unique constraint to prevent duplicate MFA methods per user
    CONSTRAINT uq_mfa_user_method UNIQUE(user_id, method)
);

-- Create indexes for mfa_secrets table
CREATE INDEX IF NOT EXISTS idx_mfa_user_id ON mfa_secrets(user_id);
CREATE INDEX IF NOT EXISTS idx_mfa_method ON mfa_secrets(method);

-- ============================================================================
-- 4. Password Reset Tokens Table - Password reset requests
-- ============================================================================
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Token information
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,

    -- Usage status
    used BOOLEAN DEFAULT FALSE NOT NULL,
    used_at TIMESTAMP NULL,

    -- Security audit
    request_ip VARCHAR(45),

    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for password_reset_tokens table
CREATE INDEX IF NOT EXISTS idx_pwd_reset_user_id ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_pwd_reset_token ON password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_pwd_reset_used ON password_reset_tokens(used);

-- ============================================================================
-- 5. Email Verification Tokens Table - Email verification requests
-- ============================================================================
CREATE TABLE IF NOT EXISTS email_verification_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    email VARCHAR(100) NOT NULL,  -- Email to be verified

    -- Token information
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,

    -- Usage status
    used BOOLEAN DEFAULT FALSE NOT NULL,
    used_at TIMESTAMP NULL,

    -- Security audit
    request_ip VARCHAR(45),
    attempt_count INTEGER DEFAULT 0 NOT NULL,

    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for email_verification_tokens table
CREATE INDEX IF NOT EXISTS idx_email_verify_user_id ON email_verification_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_email_verify_token ON email_verification_tokens(token);
CREATE INDEX IF NOT EXISTS idx_email_verify_used ON email_verification_tokens(used);

-- ============================================================================
-- 6. Login Audit Logs Table - Authentication audit trail
-- ============================================================================
CREATE TABLE IF NOT EXISTS login_audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    username VARCHAR(50) NOT NULL,  -- Record attempted username

    -- Login result
    success BOOLEAN NOT NULL,
    failure_reason VARCHAR(100),  -- 'invalid_password', 'user_not_found', 'account_locked', etc.

    -- Request information
    ip_address VARCHAR(45) NOT NULL,
    user_agent VARCHAR(500),

    -- MFA information
    mfa_passed BOOLEAN,  -- NULL if MFA not required

    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for login_audit_logs table
CREATE INDEX IF NOT EXISTS idx_login_audit_user_id ON login_audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_login_audit_username ON login_audit_logs(username);
CREATE INDEX IF NOT EXISTS idx_login_audit_success ON login_audit_logs(success);
CREATE INDEX IF NOT EXISTS idx_login_audit_created_at ON login_audit_logs(created_at);

-- ============================================================================
-- 7. Create Initial Admin User
-- ============================================================================
-- NOTE: These are test users, should be removed in production
-- Password: admin123 (bcrypt hash)
INSERT INTO users (username, email, hashed_password, role, is_active, email_verified)
VALUES
    ('admin', 'admin@mystocks.com', '$2b$12$JzXL46bSlDVnMJlDvkV7q.u5gY6pVEYNV18otWdH8FwHD3uRcV1ia', 'admin', TRUE, TRUE),
    ('user', 'user@mystocks.com', '$2b$12$8aBh8ytBXEX0B0okxvYqPO428xzvnJlnA6c.q/ua6BS6z33ZP3WnK', 'user', TRUE, TRUE)
ON CONFLICT (username) DO NOTHING;

-- ============================================================================
-- 8. Create Role-Based Permission Tables (Optional - for RBAC)
-- ============================================================================
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255),
    resource VARCHAR(50) NOT NULL,  -- e.g., 'user', 'stock', 'portfolio'
    action VARCHAR(50) NOT NULL,  -- e.g., 'create', 'read', 'update', 'delete'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (role_id, permission_id)
);

-- ============================================================================
-- 9. Insert Default Roles (Optional)
-- ============================================================================
INSERT INTO roles (name, description) VALUES
    ('user', 'Regular user with basic access'),
    ('analyst', 'Analyst with advanced analysis capabilities'),
    ('trader', 'Trader with trading execution capabilities'),
    ('admin', 'Administrator with full system access')
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- 10. Insert Default Permissions (Sample)
-- ============================================================================
INSERT INTO permissions (name, description, resource, action) VALUES
    ('view_stocks', 'View stock data', 'stock', 'read'),
    ('view_portfolio', 'View user portfolio', 'portfolio', 'read'),
    ('create_portfolio', 'Create new portfolio', 'portfolio', 'create'),
    ('edit_portfolio', 'Edit portfolio', 'portfolio', 'update'),
    ('delete_portfolio', 'Delete portfolio', 'portfolio', 'delete'),
    ('manage_users', 'Manage user accounts', 'user', 'update'),
    ('view_audit_logs', 'View audit logs', 'audit', 'read')
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- 11. Assign Permissions to Roles (Sample)
-- ============================================================================
-- Admin role gets all permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p WHERE r.name = 'admin'
ON CONFLICT DO NOTHING;

-- Analyst role gets view/create/edit permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.name = 'analyst' AND p.name IN ('view_stocks', 'view_portfolio', 'create_portfolio', 'edit_portfolio', 'view_audit_logs')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 12. Create View for User Role Information
-- ============================================================================
CREATE OR REPLACE VIEW v_user_roles AS
SELECT
    u.id,
    u.username,
    u.email,
    u.role,
    u.is_active,
    u.created_at,
    COALESCE(string_agg(DISTINCT r.name, ', '), 'none') as role_names
FROM users u
LEFT JOIN roles r ON LOWER(r.name) = LOWER(u.role)
GROUP BY u.id, u.username, u.email, u.role, u.is_active, u.created_at;

-- ============================================================================
-- Summary
-- ============================================================================
-- Tables created:
-- 1. users - Main user account storage
-- 2. oauth2_accounts - OAuth2 provider associations
-- 3. mfa_secrets - MFA configuration and secrets
-- 4. password_reset_tokens - Password reset token tracking
-- 5. email_verification_tokens - Email verification token tracking
-- 6. login_audit_logs - Login attempt audit trail
-- 7. roles - User roles definition
-- 8. permissions - System permissions
-- 9. role_permissions - Role-permission mapping
--
-- Two test users created (admin/admin123 and user/user123)
-- Default roles and sample permissions configured
-- ============================================================================
