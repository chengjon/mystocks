# MyStocks Authentication - Quick Reference Guide

## Quick Authentication Flow

```
User Login Form
    ↓
authStore.login(username, password)
    ↓
POST /api/auth/login (form-data: username=xxx&password=yyy)
    ↓
Backend: authenticate_user() → verify_password() → bcrypt
    ↓
Check MFA → generate JWT token
    ↓
Return: {access_token, token_type, expires_in, mfa_required}
    ↓
Store in localStorage: token, user
    ↓
Add to all requests: Authorization: Bearer <token>
    ↓
Protected routes accessible ✓
```

## Key Files

| Component | File | Purpose |
|-----------|------|---------|
| **Frontend UI** | `web/frontend/src/views/Login.vue` | Login form with validation |
| **State Management** | `web/frontend/src/stores/auth.js` | Token/user storage (Pinia) |
| **HTTP Client** | `web/frontend/src/api/index.js` | Axios with interceptors |
| **Route Guards** | `web/frontend/src/router/index.js` | Protected route enforcement |
| **Auth Endpoints** | `web/backend/app/api/auth.py` | Login, logout, refresh, me endpoints |
| **Security Logic** | `web/backend/app/core/security.py` | Password hashing, JWT generation |
| **Database Models** | `web/backend/app/models/user.py` | User, MFA, OAuth2, audit tables |
| **Config** | `web/backend/app/core/config.py` | JWT settings, database connection |

## Test Credentials

```
Username: admin      Password: admin123
Username: user       Password: user123
```

## API Endpoints

### Authentication

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/api/auth/login` | No | Login with username/password |
| POST | `/api/auth/logout` | Bearer | Logout current user |
| GET | `/api/auth/me` | Bearer | Get current user info |
| POST | `/api/auth/refresh` | Bearer | Refresh access token |
| GET | `/api/auth/users` | Bearer (admin) | List all users |

### OAuth2 (Optional)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/auth/oauth2/{provider}` | Redirect to OAuth2 provider |
| GET | `/api/auth/oauth2/{provider}/callback` | OAuth2 provider callback |
| GET | `/api/auth/oauth2/available-providers` | List available providers |

## Token Structure

**JWT Header**:
```json
{"alg": "HS256", "typ": "JWT"}
```

**JWT Payload**:
```json
{
  "sub": "username",
  "user_id": 1,
  "role": "admin",
  "mfa_pending": false,
  "exp": 1730306400,
  "iat": 1730304600
}
```

**Configuration**:
- Algorithm: HS256
- Secret Key: `your-secret-key-change-in-production`
- Expiration: 30 minutes (configurable)
- MFA Token Expiration: 5 minutes

## Password Security

**Algorithm**: bcrypt with cost factor 12

**Pre-computed Hashes**:
- `admin123` → `$2b$12$JzXL46bSlDVnMJlDvkV7q.u5gY6pVEYNV18otWdH8FwHD3uRcV1ia`
- `user123` → `$2b$12$8aBh8ytBXEX0B0okxvYqPO428xzvnJlnA6c.q/ua6BS6z33ZP3WnK`

**Verification**:
```python
bcrypt.checkpw(password.encode()[:72], hash.encode())
```

## Database Tables

### users
```sql
id, username, email, hashed_password, role, is_active,
email_verified, email_verified_at,
mfa_enabled, mfa_method,
created_at, updated_at, last_login, last_login_ip,
full_name, avatar_url,
failed_login_attempts, locked_until,
password_changed_at, preferences, deletion_requested_at
```

### mfa_secrets
```sql
id, user_id, method (totp/email/sms), secret, backup_codes,
verified, enabled, created_at, verified_at, config
```

### login_audit_logs
```sql
id, user_id, username, success, failure_reason,
ip_address, user_agent, mfa_passed, created_at
```

### oauth2_accounts
```sql
id, user_id, provider, provider_user_id,
access_token, refresh_token, token_type, token_expires_at,
provider_email, provider_name, provider_avatar,
created_at, updated_at, last_used_at
```

## Frontend Storage

**localStorage Keys**:
```javascript
// Token (JWT)
localStorage.token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

// User Info (JSON)
localStorage.user = {
  "username": "admin",
  "email": "admin@mystocks.com",
  "role": "admin",
  "is_active": true
}
```

## MFA Implementation

### TOTP (Time-based One-Time Password)
- Library: `pyotp`
- QR Code: base64-encoded PNG (data URI)
- Backup Codes: 10 codes, XXXX-XXXX format
- Time Window: ±30 seconds

### Email OTP
- Code Length: 6 digits
- Expiration: 10 minutes
- Delivery: SMTP (configured in environment)

### SMS
- Code Length: 6 digits
- Expiration: 10 minutes
- Delivery: SMS service provider (future implementation)

## Graceful Degradation

### MFA Database Unavailable
```
1. Try MFA query
2. Catch exception → increment failure counter
3. If < 5 failures:
   - Log warning
   - Continue login without MFA
4. If >= 5 failures:
   - Log error alert
   - Message: "MFA database checks have failed persistently"
   - Notify operators
```

**Result**: User can still login, MFA is bypassed

## Security Features

| Feature | Status | Details |
|---------|--------|---------|
| Password Hashing | ✅ | bcrypt cost 12 (~80ms) |
| JWT Tokens | ✅ | HS256, 30-min expiration |
| Role-Based Access | ✅ | user < admin hierarchy |
| MFA Support | ✅ | TOTP, Email OTP, SMS |
| CORS Protection | ✅ | Configured origins only |
| HTTPBearer Auth | ✅ | Authorization header |
| Audit Logging | ✅ | login_audit_logs table |
| CSRF Protection | ⚠️ | Not explicitly implemented |
| Rate Limiting | ⚠️ | Not implemented |
| Account Lockout | ⚠️ | Not implemented |
| HttpOnly Cookies | ⚠️ | Using localStorage instead |
| HTTPS | ⚠️ | HTTP in dev, should use HTTPS in prod |

## Error Responses

### 401 Unauthorized
```json
{"detail": "Could not validate credentials"}
{"detail": "用户名或密码错误"}
```
**Action**: Clear token, redirect to /login

### 403 Forbidden
```json
{"detail": "权限不足"}
```
**Action**: Show error, don't logout

### 404 Not Found
```json
{"detail": "请求的资源不存在"}
```
**Action**: Show error

### 500 Server Error
```json
{"detail": "登录服务暂时不可用，请稍后重试"}
```
**Action**: Show error, don't logout

### 503 Service Unavailable
```json
{"detail": "服务暂时不可用，请稍后重试"}
```
**Action**: Show error, don't logout

## Configuration (Environment Variables)

```bash
# JWT Settings
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
POSTGRESQL_HOST=192.168.123.104
POSTGRESQL_PORT=5438
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=***
POSTGRESQL_DATABASE=mystocks

# OAuth2 (Optional)
OAUTH2_GOOGLE_CLIENT_ID=***
OAUTH2_GOOGLE_CLIENT_SECRET=***
OAUTH2_GITHUB_CLIENT_ID=***
OAUTH2_GITHUB_CLIENT_SECRET=***

# Email (For OTP)
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=***
EMAIL_SMTP_PASSWORD=***

# MFA Settings
MFA_TOTP_ISSUER=MyStocks
MFA_EMAIL_CODE_LENGTH=6
MFA_EMAIL_CODE_EXPIRES_MINUTES=10
```

## Common Issues & Solutions

### Issue: 401 on protected routes
**Cause**: Token missing/invalid/expired  
**Solution**: Check localStorage, verify token hasn't expired, login again

### Issue: CORS error
**Cause**: Frontend origin not in CORS allow list  
**Solution**: Add origin to `app.add_middleware(CORSMiddleware, allow_origins=[...])`

### Issue: MFA database down but login works
**Cause**: Graceful degradation triggered  
**Solution**: MFA is bypassed, system continues operating, check database health

### Issue: Password hashing fails
**Cause**: Password > 72 bytes or bcrypt library issue  
**Solution**: Truncate password to 72 bytes (handled automatically)

### Issue: Token refresh fails
**Cause**: Old token fully expired  
**Solution**: User must re-login

## Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| bcrypt password verify | ~80ms | Cost 12, single verification |
| JWT token generation | <1ms | HS256 signature |
| JWT token verification | <1ms | Signature + exp check |
| Database query (user lookup) | ~1-5ms | With index on username |
| MFA database query | ~1-5ms | With index on user_id |
| Complete login flow | ~200-500ms | End-to-end (80ms bcrypt + DB + JWT) |

## Monitoring Recommendations

**Log Metrics**:
- Login success/failure rate
- Failed password attempts
- MFA verification attempts
- Token validation failures
- Account lockouts
- Unusual geographic locations
- Rapid login attempts from same IP

**Alerts**:
- MFA database failures (5+ in a row)
- Multiple failed logins (brute force detection)
- Token signature errors
- CORS violations

## Next Steps for Production

1. [ ] Change `SECRET_KEY` to secure random value
2. [ ] Enable HTTPS (SSL/TLS certificate)
3. [ ] Implement rate limiting on `/auth/login`
4. [ ] Implement account lockout after N failed attempts
5. [ ] Add CSRF protection
6. [ ] Switch token storage to HttpOnly cookies
7. [ ] Enable comprehensive audit logging
8. [ ] Set up monitoring and alerting
9. [ ] Implement password reset flow
10. [ ] Implement email verification flow
11. [ ] Deploy MFA to production
12. [ ] Configure OAuth2 providers

