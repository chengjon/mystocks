# Task 2.1: User Authentication System Enhancement Plan

**Status**: In Progress
**Priority**: High (Priority 2)
**Estimated Effort**: 15 hours
**Date Started**: 2025-10-28

## Overview

Enhance the existing authentication system from in-memory user data to a production-ready system with:
- Database-backed user management (PostgreSQL)
- OAuth2 provider integration (Google, GitHub)
- Multi-Factor Authentication (MFA) support
- Comprehensive API documentation and testing

## Current State Analysis

### Existing Implementation
- ✅ Basic JWT token generation and validation
- ✅ BCrypt password hashing
- ✅ In-memory user storage (2 test users: admin, user)
- ✅ Simple role-based access control (admin, user)
- ✅ Basic API endpoints (login, logout, refresh, me)

### Gaps Identified
- ❌ No persistent user storage (in-memory only)
- ❌ No user registration endpoint
- ❌ No OAuth2 provider integration
- ❌ No MFA/2FA support
- ❌ No token blacklist/revocation mechanism
- ❌ No password reset functionality
- ❌ No user session management
- ❌ Incomplete RBAC implementation
- ❌ No audit logging for authentication events

## Implementation Plan

### Phase 1: Database-Backed User Management (5 hours)

#### 1.1 Create User Model and Database Schema
**Files to Create/Modify**:
- `web/backend/app/models/user.py` - SQLAlchemy User model
- `db_manager/migrations/user_schema.sql` - User table schema

**Requirements**:
- User table with fields: id, username, email, hashed_password, role, is_active, created_at, updated_at
- Unique constraints on username and email
- Password history for security

**Tasks**:
1. Create User SQLAlchemy ORM model
2. Create database migration script
3. Add support for user registration

#### 1.2 Implement Database-Backed Authentication
**Files to Modify**:
- `web/backend/app/core/security.py` - Authentication functions
- `web/backend/app/api/auth.py` - Auth endpoints

**Requirements**:
- Migrate `authenticate_user()` to database query
- Migrate `get_current_user()` to database query
- Add user registration endpoint with validation
- Implement password reset flow

**Tasks**:
1. Refactor security.py to use database instead of in-memory
2. Add registration validation (email format, password strength)
3. Add password reset token generation
4. Add email verification for registration

### Phase 2: OAuth2 Provider Integration (5 hours)

#### 2.1 OAuth2 Infrastructure
**Files to Create**:
- `web/backend/app/core/oauth2_providers.py` - OAuth2 provider implementations
- `web/backend/app/api/oauth2.py` - OAuth2 endpoints

**Providers to Support**:
- Google OAuth2
- GitHub OAuth2

**Requirements**:
- OAuth2 provider configuration
- Access token exchange
- User profile retrieval
- Automatic user creation on first login

**Tasks**:
1. Implement OAuth2 base class for provider abstraction
2. Create Google OAuth2 provider implementation
3. Create GitHub OAuth2 provider implementation
4. Add OAuth2 callback endpoints
5. Store OAuth2 linked accounts in database

#### 2.2 OAuth2 Endpoints
**Endpoints to Create**:
- `GET /api/auth/oauth2/google` - Google OAuth2 login redirect
- `GET /api/auth/oauth2/google/callback` - Google OAuth2 callback
- `GET /api/auth/oauth2/github` - GitHub OAuth2 login redirect
- `GET /api/auth/oauth2/github/callback` - GitHub OAuth2 callback

### Phase 3: Multi-Factor Authentication (5 hours)

#### 3.1 MFA Methods Support
**Methods to Implement**:
1. TOTP (Time-based One-Time Password) - Authenticator apps
2. Email verification - One-time code via email
3. SMS verification - One-time code via SMS

**Files to Create**:
- `web/backend/app/core/mfa.py` - MFA implementations
- `web/backend/app/api/mfa.py` - MFA endpoints

#### 3.2 TOTP Implementation
**Requirements**:
- Generate TOTP secrets for users
- QR code generation for authenticator apps
- TOTP verification
- Backup codes generation

**Tasks**:
1. Implement TOTP secret generation
2. Implement TOTP verification
3. Generate backup codes for account recovery
4. Add QR code generation endpoint

#### 3.3 Email Verification Implementation
**Requirements**:
- Send verification code via email
- Verify code validity and expiration
- Resend verification code

**Tasks**:
1. Implement email verification code generation
2. Add email sending via SMTP
3. Implement code verification endpoint

#### 3.4 SMS Verification Implementation (Optional)
**Requirements**:
- Integration with SMS provider (Twilio, Nexmo)
- Send verification code via SMS
- Verify code validity

### Phase 4: Testing and Documentation (2 hours)

#### 4.1 Unit Tests
**Files to Create**:
- `tests/unit/test_authentication.py` - Authentication logic tests
- `tests/unit/test_mfa.py` - MFA logic tests

**Test Coverage**:
- User registration validation
- Password hashing and verification
- JWT token generation and validation
- OAuth2 provider integration (mocked)
- MFA verification logic

#### 4.2 Integration Tests
**Files to Create**:
- `tests/integration/test_auth_flow.py` - End-to-end auth flows

**Test Scenarios**:
- Complete registration and login flow
- Password reset flow
- OAuth2 login flow
- MFA setup and verification
- Token refresh and expiration

#### 4.3 API Documentation
**Files to Create**:
- `docs/AUTHENTICATION_API.md` - Complete API documentation
- `docs/AUTHENTICATION_EXAMPLES.md` - Usage examples

## Database Schema

### User Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_method VARCHAR(20), -- 'totp', 'email', 'sms'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_username ON users(username);
CREATE INDEX idx_email ON users(email);
```

### OAuth2 Linked Accounts Table
```sql
CREATE TABLE oauth2_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50), -- 'google', 'github'
    provider_user_id VARCHAR(255),
    access_token VARCHAR(1000),
    refresh_token VARCHAR(1000),
    token_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider, provider_user_id)
);
```

### MFA Secrets Table
```sql
CREATE TABLE mfa_secrets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    method VARCHAR(20), -- 'totp', 'email', 'sms'
    secret VARCHAR(255),
    backup_codes TEXT[], -- Array of backup codes
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP,
    UNIQUE(user_id, method)
);

CREATE INDEX idx_user_mfa ON mfa_secrets(user_id);
```

## API Endpoints

### Authentication Endpoints

#### 1. User Registration
```
POST /api/auth/register
Content-Type: application/json

{
    "username": "newuser",
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "password_confirm": "SecurePassword123!"
}

Response:
{
    "id": 3,
    "username": "newuser",
    "email": "user@example.com",
    "role": "user",
    "message": "Registration successful. Please verify your email."
}
```

#### 2. Email Verification
```
POST /api/auth/verify-email
Content-Type: application/json

{
    "token": "verification_token_from_email"
}

Response:
{
    "success": true,
    "message": "Email verified successfully"
}
```

#### 3. Login
```
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=user&password=password123

Response:
{
    "access_token": "jwt_token",
    "token_type": "bearer",
    "expires_in": 3600,
    "mfa_required": true,  // If MFA is enabled
    "mfa_methods": ["totp", "email"],
    "user": {...}
}
```

#### 4. MFA Verification
```
POST /api/auth/mfa/verify
Content-Type: application/json
Authorization: Bearer jwt_token

{
    "method": "totp",
    "code": "123456"
}

Response:
{
    "success": true,
    "access_token": "full_jwt_token",
    "token_type": "bearer"
}
```

#### 5. MFA Setup
```
POST /api/auth/mfa/setup
Content-Type: application/json
Authorization: Bearer jwt_token

{
    "method": "totp"
}

Response:
{
    "qr_code": "data:image/png;base64,...",
    "secret": "JBSWY3DPEBLW64TMMQ======",
    "backup_codes": ["XXXX-XXXX", "XXXX-XXXX", ...]
}
```

#### 6. OAuth2 Login
```
GET /api/auth/oauth2/{provider}
Query params: redirect_uri=http://localhost:3000/auth/callback

Response: 302 redirect to OAuth2 provider
```

#### 7. Password Reset
```
POST /api/auth/password-reset/request
Content-Type: application/json

{
    "email": "user@example.com"
}

Response:
{
    "message": "Password reset instructions sent to email"
}

POST /api/auth/password-reset/confirm
Content-Type: application/json

{
    "token": "reset_token_from_email",
    "password": "NewPassword123!",
    "password_confirm": "NewPassword123!"
}

Response:
{
    "success": true,
    "message": "Password reset successfully"
}
```

## Success Criteria

### Functionality
- ✅ User registration with email verification
- ✅ Database-backed user storage
- ✅ OAuth2 login with Google and GitHub
- ✅ MFA setup and verification (TOTP minimum)
- ✅ Password reset flow
- ✅ Token refresh mechanism
- ✅ User session management

### Testing
- ✅ 30+ unit tests for authentication logic
- ✅ 15+ integration tests for auth flows
- ✅ 95%+ code coverage for auth module
- ✅ All tests passing

### Documentation
- ✅ Complete API documentation
- ✅ Usage examples for each endpoint
- ✅ OAuth2 provider setup guide
- ✅ MFA setup instructions

### Performance
- ✅ Authentication endpoint response time < 200ms
- ✅ Password hashing time < 500ms
- ✅ OAuth2 callback < 500ms
- ✅ MFA verification < 100ms

## Dependencies Required

```python
# Core
fastapi>=0.104.0
sqlalchemy>=2.0.0
pydantic>=2.0.0

# Authentication
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
bcrypt>=4.0.0
PyJWT>=2.8.0

# OAuth2
authlib>=1.2.0
httpx>=0.24.0

# MFA
pyotp>=2.9.0
qrcode>=7.4.0
Pillow>=10.0.0

# Email
aiosmtplib>=3.0.0
email-validator>=2.0.0

# SMS (Optional)
twilio>=8.0.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
```

## Timeline

| Phase | Duration | Start | End |
|-------|----------|-------|-----|
| Phase 1: Database | 5 hours | 2025-10-28 | 2025-10-28 |
| Phase 2: OAuth2 | 5 hours | 2025-10-28 | 2025-10-29 |
| Phase 3: MFA | 5 hours | 2025-10-29 | 2025-10-29 |
| Phase 4: Testing | 2 hours | 2025-10-29 | 2025-10-29 |
| **Total** | **17 hours** | | |

## Next Steps

1. Create User SQLAlchemy model
2. Create database migration
3. Implement database-backed authentication
4. Add user registration endpoint
5. Implement OAuth2 providers
6. Add MFA support
7. Create comprehensive tests
8. Document API endpoints

---

**Created**: 2025-10-28
**Status**: In Progress
**Owner**: Claude Code
