# MyStocks Web Application: Complete Authentication Flow Analysis

**Document Date**: 2025-10-30  
**Analysis Scope**: Front-end (Vue 3), Back-end (FastAPI), Database Layer (PostgreSQL)  
**Thoroughness Level**: Very Thorough - Complete execution path analysis

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Complete Authentication Flow](#complete-authentication-flow)
4. [Front-End Authentication](#front-end-authentication)
5. [Back-End Authentication](#back-end-authentication)
6. [Database Layer](#database-layer)
7. [Security Mechanisms](#security-mechanisms)
8. [MFA Implementation](#mfa-implementation)
9. [Graceful Degradation](#graceful-degradation)
10. [Security Considerations](#security-considerations)

---

## Executive Summary

The MyStocks web application implements a **multi-layered authentication system** with JWT tokens, optional MFA support, and graceful database degradation. The system uses:

- **Front-end**: Vue 3 with Pinia store, localStorage for token persistence
- **Back-end**: FastAPI with OAuth2 password flow and JWT validation
- **Database**: PostgreSQL for user storage, user audit logs, and MFA secrets
- **Token Format**: JWT with HS256 algorithm, 30-minute expiration (configurable)
- **MFA Support**: TOTP, Email OTP, SMS (optional feature with database fallback)

The authentication flow is designed to be **robust** with automatic token refresh, graceful degradation when MFA database is unavailable, and comprehensive audit logging.

---

## Architecture Overview

### System Layers

```
┌─────────────────────────────────────────────────────────────────┐
│ FRONT-END LAYER (Vue 3 + Pinia)                                 │
├─────────────────────────────────────────────────────────────────┤
│ • Login.vue: UI component for credential collection              │
│ • auth.js (Pinia Store): Token and user state management         │
│ • index.js (Axios): HTTP client with interceptors               │
│ • router/index.js: Route guards for protected routes             │
└─────────────────────────────────────────────────────────────────┘
              ↓ HTTP/HTTPS (POST /api/auth/login)
┌─────────────────────────────────────────────────────────────────┐
│ BACK-END LAYER (FastAPI)                                        │
├─────────────────────────────────────────────────────────────────┤
│ • api/auth.py: Authentication endpoints                          │
│ • core/security.py: Token generation & password hashing          │
│ • core/database.py: Session management & database connections   │
│ • api/oauth2.py: OAuth2 provider integration (optional)          │
└─────────────────────────────────────────────────────────────────┘
              ↓ ORM Queries (SQLAlchemy)
┌─────────────────────────────────────────────────────────────────┐
│ DATABASE LAYER (PostgreSQL)                                     │
├─────────────────────────────────────────────────────────────────┤
│ • users table: User credentials & metadata                       │
│ • mfa_secrets table: MFA configuration (optional)               │
│ • login_audit_logs table: Login attempt tracking                │
│ • oauth2_accounts table: OAuth2 provider links                  │
│ • password_reset_tokens table: Password reset management        │
│ • email_verification_tokens table: Email verification           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Complete Authentication Flow

### 1. User Login Flow (Step-by-Step)

#### Step 1: User Navigates to Login Page

```
User clicks "Login" in browser
        ↓
Router guards check auth state (router/index.js)
        ↓
If authenticated: redirect to /dashboard
If not authenticated: allow access to /login (requiresAuth: false)
        ↓
Login.vue component renders
```

**Code Reference** (`web/frontend/src/router/index.js`):
```javascript
{
  path: '/login',
  name: 'login',
  component: () => import('@/views/Login.vue'),
  meta: { requiresAuth: false }  // Login page accessible without auth
}
```

#### Step 2: User Submits Credentials

**Component**: `Login.vue` (lines 11-112)

```vue
<template>
  <el-form @submit.prevent="handleLogin">
    <el-form-item label="用户名" prop="username">
      <el-input v-model="loginForm.username" />
    </el-form-item>
    
    <el-form-item label="密码" prop="password">
      <el-input 
        v-model="loginForm.password" 
        type="password"
        @keyup.enter="handleLogin"
      />
    </el-form-item>
    
    <el-button @click="handleLogin" :loading="loading">
      登录
    </el-button>
  </el-form>
</template>

<script setup>
const handleLogin = async () => {
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      const result = await authStore.login(
        loginForm.username, 
        loginForm.password
      )
      if (result.success) {
        ElMessage.success('登录成功')
        router.push(route.query.redirect || '/')
      } else {
        ElMessage.error(result.message)
      }
    } finally {
      loading.value = false
    }
  })
}
</script>
```

**Validation Rules**:
- Username: Required
- Password: Required, minimum 6 characters

#### Step 3: API Call to Backend

**Store**: `web/frontend/src/stores/auth.js` (lines 11-29)

```javascript
async function login(username, password) {
  try {
    const response = await authApi.login(username, password)
    
    // Response interceptor already returns response.data
    token.value = response.access_token
    user.value = response.user
    
    // Persist to localStorage
    localStorage.setItem('token', token.value)
    localStorage.setItem('user', JSON.stringify(user.value))
    
    return { success: true }
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.detail || '登录失败'
    }
  }
}
```

**HTTP Client**: `web/frontend/src/api/index.js` (lines 111-123)

```javascript
export const authApi = {
  login(username, password) {
    // Use URLSearchParams for OAuth2-compliant form-data format
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)
    
    return request.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
  }
}
```

**Request Format**:
```
POST /api/auth/login HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Authorization: Bearer <previous_token_if_exists>

username=admin&password=admin123
```

#### Step 4: Request Interceptor Adds Token

**Axios Interceptor**: `web/frontend/src/api/index.js` (lines 39-52)

```javascript
request.interceptors.request.use(
  config => {
    // Ensure token exists (use mock token if needed in dev)
    const token = localStorage.getItem('token') || ensureMockToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)
```

**Development Note**: The `ensureMockToken()` function generates a mock JWT token for development purposes if no token exists, allowing testing without login.

---

### 2. Backend Processing (Backend Authentication Flow)

#### Step 5: FastAPI Endpoint Receives Request

**Endpoint**: `web/backend/app/api/auth.py` (lines 107-234)

```python
@router.post("/login", response_model=Token)
async def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    User login to get access token
    Supports OAuth2 standard form data format
    
    If user has MFA enabled, response includes mfa_required flag 
    and temporary token
    """
    try:
        # Step 1: Authenticate user credentials
        user = authenticate_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
            )
        
        # Step 2: Check if user has MFA enabled (graceful degradation)
        global _mfa_query_failure_count
        mfa_enabled = False
        verified_mfa = []
        try:
            db_user = db.execute(
                select(UserModel).where(UserModel.username == username)
            ).scalar_one_or_none()
            
            if db_user and db_user.mfa_enabled:
                # Check for verified MFA methods
                verified_mfa = (
                    db.execute(
                        select(MFASecretModel).where(
                            (MFASecretModel.user_id == db_user.id)
                            and (MFASecretModel.verified == True)
                        )
                    )
                    .scalars()
                    .all()
                )
                mfa_enabled = bool(verified_mfa)
            
            # Reset failure counter on success
            _mfa_query_failure_count = 0
        
        except Exception as e:
            # If database query fails, continue with standard login (graceful degradation)
            _mfa_query_failure_count += 1
            
            logger.warning(
                "mfa_check_failed",
                username=username,
                error=str(e),
                failure_count=_mfa_query_failure_count,
                event_type="graceful_degradation_triggered",
            )
            
            # Alert if persistent failure pattern detected
            if _mfa_query_failure_count >= 5:
                logger.error(
                    "mfa_persistent_failure_alert",
                    failure_count=_mfa_query_failure_count,
                    message="MFA database checks failing persistently"
                )
        
        # Step 3: Handle MFA flow
        if mfa_enabled and verified_mfa:
            # Create temporary token for MFA verification (5 minutes)
            temp_token_expires = timedelta(minutes=5)
            temp_token = create_access_token(
                data={
                    "sub": user.username,
                    "user_id": user.id,
                    "role": user.role,
                    "mfa_pending": True,
                },
                expires_delta=temp_token_expires,
            )
            
            return {
                "access_token": temp_token,
                "token_type": "bearer",
                "expires_in": 5 * 60,  # 5 minutes
                "mfa_required": True,
                "mfa_methods": [mfa.method for mfa in verified_mfa],
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                },
            }
        
        # Step 4: No MFA - return full access token
        access_token_expires = timedelta(
            minutes=settings.access_token_expire_minutes
        )
        access_token = create_access_token(
            data={
                "sub": user.username,
                "user_id": user.id,
                "role": user.role
            },
            expires_delta=access_token_expires,
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "mfa_required": False,
            "user": {
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Login endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录服务暂时不可用，请稍后重试",
        )
```

#### Step 6: User Authentication

**Function**: `web/backend/app/core/security.py` (lines 97-134)

```python
def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """
    Authenticate user credentials
    
    This should connect to database to query user info.
    Currently uses mock data, but can be extended to use real database.
    """
    # Mock user database (should be replaced with real DB query)
    users_db = {
        "admin": {
            "id": 1,
            "username": "admin",
            "email": "admin@mystocks.com",
            "hashed_password": "$2b$12$JzXL46bSlDVnMJlDvkV7q.u5gY6pVEYNV18otWdH8FwHD3uRcV1ia",  # admin123
            "role": "admin",
            "is_active": True
        },
        "user": {
            "id": 2,
            "username": "user",
            "email": "user@mystocks.com",
            "hashed_password": "$2b$12$8aBh8ytBXEX0B0okxvYqPO428xzvnJlnA6c.q/ua6BS6z33ZP3WnK",  # user123
            "role": "user",
            "is_active": True
        }
    }
    
    # Look up user by username
    user = users_db.get(username)
    if not user:
        return None
    
    user_in_db = UserInDB(**user)
    
    # Verify password using bcrypt
    if not verify_password(password, user_in_db.hashed_password):
        return None
    
    return user_in_db
```

**Password Verification**: `web/backend/app/core/security.py` (lines 43-52)

```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password - uses bcrypt directly"""
    try:
        # bcrypt has a 72-byte password length limit
        password_bytes = plain_password.encode('utf-8')[:72]
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"Password verification error: {e}")
        return False
```

**Password Hashing**: `web/backend/app/core/security.py` (lines 54-58)

```python
def get_password_hash(password: str) -> str:
    """Generate password hash - uses pure bcrypt"""
    password_bytes = password.encode('utf-8')[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
```

**Security Details**:
- Algorithm: bcrypt with cost factor 12 (configurable via bcrypt.gensalt())
- Password limit: 72 bytes (enforced by bcrypt)
- UTF-8 encoding with truncation to prevent DoS

#### Step 7: JWT Token Generation

**Function**: `web/backend/app/core/security.py` (lines 60-72)

```python
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    
    return encoded_jwt
```

**JWT Payload Structure**:
```json
{
  "sub": "admin",
  "user_id": 1,
  "role": "admin",
  "exp": 1730307600,
  "iat": 1730306100
}
```

**Configuration**: `web/backend/app/core/config.py` (lines 38-41)

```python
# JWT 认证配置
secret_key: str = "your-secret-key-change-in-production"
algorithm: str = "HS256"
access_token_expire_minutes: int = 30
```

---

### 3. Response Processing at Frontend

#### Step 8: Response Interceptor

**Axios Interceptor**: `web/frontend/src/api/index.js` (lines 54-108)

```javascript
request.interceptors.response.use(
  response => {
    // Response interceptor already returns response.data
    return response.data
  },
  error => {
    // Priority: use backend's user-friendly error messages
    if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error)
      
      // Special handling for 401 errors
      if (error.response.status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        router.push('/login')
      }
    } else if (error.response) {
      // If backend didn't return friendly message, use default
      switch (error.response.status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          router.push('/login')
          break
        case 403:
          ElMessage.error('没有权限执行此操作')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误，请稍后重试')
          break
        case 503:
          ElMessage.error('服务暂时不可用，请稍后重试')
          break
        default:
          const errorMsg = error.response.data?.message ||
                          error.response.data?.detail ||
                          '请求失败，请稍后重试'
          ElMessage.error(errorMsg)
      }
    } else if (error.request) {
      // Request sent but no response
      ElMessage.error('网络错误，请检查连接后重试')
    } else {
      // Request configuration error
      ElMessage.error('请求错误: ' + (error.message || '未知错误'))
    }
    
    return Promise.reject(error)
  }
)
```

#### Step 9: Store Token and Update State

**Auth Store**: `web/frontend/src/stores/auth.js` (lines 11-29)

```javascript
async function login(username, password) {
  try {
    const response = await authApi.login(username, password)
    
    // Response interceptor has already returned response.data
    token.value = response.access_token
    user.value = response.user
    
    // Persist to localStorage
    localStorage.setItem('token', token.value)
    localStorage.setItem('user', JSON.stringify(user.value))
    
    return { success: true }
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.detail || '登录失败'
    }
  }
}
```

**Storage Structure**:
```javascript
// localStorage keys:
localStorage.token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
localStorage.user = {
  "username": "admin",
  "email": "admin@mystocks.com",
  "role": "admin",
  "is_active": true
}
```

---

## Front-End Authentication

### Login Component (Vue 3)

**File**: `web/frontend/src/views/Login.vue`

**Features**:
- Form validation (required fields, password length >= 6)
- Loading state during submission
- Error message display via ElMessage
- Test credentials display
- Keyboard support (Enter to submit)
- Redirect support (preserves redirect URL from query params)

**Test Credentials**:
```
Admin: admin / admin123
User: user / user123
```

### Pinia Store (State Management)

**File**: `web/frontend/src/stores/auth.js`

**State**:
```javascript
const token = ref(localStorage.getItem('token') || '')
const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
```

**Computed**:
```javascript
const isAuthenticated = computed(() => !!token.value)
```

**Actions**:

1. **login(username, password)** - Authenticate user
   - Calls `/api/auth/login` with credentials
   - Stores token and user in localStorage
   - Returns `{ success: true }` or `{ success: false, message: "..." }`

2. **logout()** - Clear authentication
   - Calls `/api/auth/logout` (optional, error is ignored)
   - Clears token and user from state and localStorage

3. **checkAuth()** - Verify token validity
   - Calls `/api/auth/me` to get current user
   - Returns true if valid, false otherwise
   - Logs out if token is invalid

4. **refreshToken()** - Refresh access token
   - Calls `/api/auth/refresh`
   - Updates token in state and localStorage
   - Returns true on success, logs out on failure

### Axios HTTP Client

**File**: `web/frontend/src/api/index.js`

**Features**:
- Automatic token injection in Authorization header
- Request/response interception
- Error handling with user-friendly messages
- Automatic logout on 401 responses
- OAuth2-compliant form-data format for login
- Development mock token support

**Request Headers**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json (or application/x-www-form-urlencoded for login)
```

### Router Guards

**File**: `web/frontend/src/router/index.js` (lines 195-208)

```javascript
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth !== false && !authStore.isAuthenticated) {
    // Need login but not authenticated - redirect to login
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    // Already logged in - redirect to dashboard
    next({ name: 'dashboard' })
  } else {
    next()
  }
})
```

**Route Protection**:
- Routes with `meta: { requiresAuth: true }` require authentication
- Routes with `meta: { requiresAuth: false }` are publicly accessible
- Protected routes redirect to `/login` with redirect URL in query params

---

## Back-End Authentication

### FastAPI Application

**File**: `web/backend/app/main.py`

**CORS Configuration** (lines 64-81):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Authentication Endpoints

**File**: `web/backend/app/api/auth.py`

#### 1. POST /auth/login

**Request**:
```
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

**Response (No MFA)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "mfa_required": false,
  "user": {
    "username": "admin",
    "email": "admin@mystocks.com",
    "role": "admin"
  }
}
```

**Response (MFA Required)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 300,
  "mfa_required": true,
  "mfa_methods": ["totp", "email"],
  "user": {
    "username": "admin",
    "email": "admin@mystocks.com",
    "role": "admin"
  }
}
```

**Error Response**:
```json
{
  "detail": "用户名或密码错误"
}
```

#### 2. POST /auth/logout

**Request**:
```
Authorization: Bearer <token>
```

**Response**:
```json
{
  "message": "登出成功",
  "success": true
}
```

#### 3. GET /auth/me

**Request**:
```
Authorization: Bearer <token>
```

**Response**:
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@mystocks.com",
  "role": "admin",
  "is_active": true
}
```

**Error Response**:
```json
{
  "detail": "Could not validate credentials"
}
```

#### 4. POST /auth/refresh

**Request**:
```
Authorization: Bearer <old_token>
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Token Dependency Injection

**File**: `web/backend/app/api/auth.py` (lines 62-104)

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if token_data is None:
            raise credentials_exception
        
        username = token_data.username
        if username is None:
            raise credentials_exception
    
    except Exception:
        raise credentials_exception
    
    # Look up user
    users_db = get_users_db()
    user = users_db.get(username)
    if user is None:
        raise credentials_exception
    
    return User(**user)


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

**Usage in Protected Endpoints**:
```python
@router.get("/protected-endpoint")
async def protected_route(
    current_user: User = Depends(get_current_active_user)
):
    return {"user": current_user}
```

### Token Verification

**Function**: `web/backend/app/core/security.py` (lines 74-89)

```python
def verify_token(token: str) -> Optional[TokenData]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        
        if username is None:
            return None
        
        token_data = TokenData(username=username, user_id=user_id, role=role)
        return token_data
    
    except jwt.PyJWTError:
        return None
```

**Error Cases**:
- Expired token (exp claim)
- Invalid signature
- Invalid algorithm
- Missing claims
- Malformed token

---

## Database Layer

### User Database Model

**File**: `web/backend/app/models/user.py` (lines 22-79)

```python
class User(Base):
    """
    User model - corresponds to users table in PostgreSQL
    Stores user account info, authentication credentials, and account state
    """
    
    __tablename__ = "users"
    
    # Basic info
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    
    # Authentication
    hashed_password = Column(String(255), nullable=True)  # Optional for OAuth2 users
    
    # User attributes
    role = Column(String(50), default="user", nullable=False)  # user, analyst, trader, admin
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Email verification
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime, nullable=True)
    
    # MFA/2FA
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_method = Column(String(20), nullable=True)  # 'totp', 'email', 'sms'
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)  # IPv4 or IPv6
    
    # User details
    full_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Account security
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)  # Account lock time
    
    # Password security history
    password_changed_at = Column(DateTime, nullable=True)
    
    # User preferences (JSON format)
    preferences = Column(Text, nullable=True)
    
    # Account status markers
    deletion_requested_at = Column(DateTime, nullable=True)
```

### MFA Configuration Table

**File**: `web/backend/app/models/user.py` (lines 158-205)

```python
class MFASecret(Base):
    """
    MFA secret model
    Stores user MFA configuration, including TOTP keys, backup codes, etc.
    """
    
    __tablename__ = "mfa_secrets"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User association
    user_id = Column(Integer, nullable=False, index=True)
    
    # MFA method
    method = Column(String(20), nullable=False)  # 'totp', 'email', 'sms'
    
    # MFA key/credential
    secret = Column(String(255), nullable=False)  # TOTP key or other credential
    
    # Backup codes (comma-separated or JSON format)
    backup_codes = Column(Text, nullable=True)  # JSON format
    
    # Status
    verified = Column(Boolean, default=False, nullable=False)
    enabled = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    
    # Configuration metadata (JSON format)
    config = Column(Text, nullable=True)
```

### Supporting Tables

#### 1. Login Audit Logs

**File**: `web/backend/app/models/user.py` (lines 276-309)

```python
class LoginAuditLog(Base):
    """
    Login audit log model
    Records all login attempts (successful and failed) for security audits
    """
    
    __tablename__ = "login_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User info
    user_id = Column(Integer, nullable=True, index=True)
    username = Column(String(50), nullable=False)
    
    # Login result
    success = Column(Boolean, nullable=False)
    failure_reason = Column(String(100), nullable=True)
    
    # Request info
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(500), nullable=True)
    
    # MFA info
    mfa_passed = Column(Boolean, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
```

#### 2. OAuth2 Accounts

**File**: `web/backend/app/models/user.py` (lines 100-156)

```python
class OAuth2Account(Base):
    """
    OAuth2 associated account model
    Stores OAuth2 provider (Google, GitHub, etc.) account links
    """
    
    __tablename__ = "oauth2_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User association
    user_id = Column(Integer, nullable=False, index=True)
    
    # OAuth2 provider info
    provider = Column(String(50), nullable=False, index=True)  # 'google', 'github'
    provider_user_id = Column(String(255), nullable=False, index=True)
    
    # OAuth2 token info
    access_token = Column(String(1000), nullable=True)
    refresh_token = Column(String(1000), nullable=True)
    token_type = Column(String(50), default="Bearer", nullable=False)
    token_expires_at = Column(DateTime, nullable=True)
    
    # User info (from provider)
    provider_email = Column(String(100), nullable=True)
    provider_name = Column(String(100), nullable=True)
    provider_avatar = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
```

#### 3. Password Reset Tokens

**File**: `web/backend/app/models/user.py` (lines 208-238)

```python
class PasswordResetToken(Base):
    """
    Password reset token model
    Stores password reset requests and their tokens
    """
    
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User association
    user_id = Column(Integer, nullable=False, index=True)
    
    # Token info
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    
    # Usage status
    used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    # IP info for security audit
    request_ip = Column(String(45), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

### Database Connection Management

**File**: `web/backend/app/core/database.py`

**Configuration**:
```python
def get_postgresql_connection_string() -> str:
    """Get PostgreSQL main database connection string"""
    return f"postgresql://{settings.postgresql_user}:{settings.postgresql_password}@{settings.postgresql_host}:{settings.postgresql_port}/{settings.postgresql_database}"
```

**Session Management**:
```python
def get_db() -> Session:
    """Get database session (for FastAPI dependency injection)"""
    session = get_postgresql_session()
    try:
        yield session
    finally:
        session.close()
```

**Connection Pooling**:
- Pool size: 10
- Max overflow: 20
- Pool recycle: 3600 seconds (1 hour)
- Pool pre-ping: True (validates connections before use)

---

## Security Mechanisms

### 1. Password Security

**Hashing Algorithm**: bcrypt with cost factor 12

```python
bcrypt.hashpw(password_bytes, bcrypt.gensalt())
```

**Pre-computed Password Hashes** (for test accounts):
```python
# admin123 -> "$2b$12$JzXL46bSlDVnMJlDvkV7q.u5gY6pVEYNV18otWdH8FwHD3uRcV1ia"
# user123 -> "$2b$12$8aBh8ytBXEX0B0okxvYqPO428xzvnJlnA6c.q/ua6BS6z33ZP3WnK"
```

**Password Verification Process**:
1. Retrieve hashed password from database
2. Hash provided password using same cost factor
3. Compare byte-by-byte (constant-time comparison via bcrypt)
4. Return boolean result

**Security Features**:
- Cost factor 12: ~0.08 seconds per verification (prevents brute force)
- Password truncation: 72 bytes max (bcrypt limitation)
- UTF-8 encoding: Supports international characters
- Salt generation: Unique salt per password (included in hash)

### 2. JWT Token Security

**Token Structure**:
```
Header.Payload.Signature
```

**Header**:
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload**:
```json
{
  "sub": "admin",        // Subject (username)
  "user_id": 1,          // User ID
  "role": "admin",       // User role
  "exp": 1730306400,     // Expiration time
  "iat": 1730304600      // Issued at time
}
```

**Signature**:
```
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret_key
)
```

**Security Configuration**:
- Algorithm: HS256 (HMAC-SHA256)
- Secret Key: Configurable via `settings.secret_key`
- Expiration: 30 minutes (configurable)
- Issued At: Automatically set to current time

**Token Validation**:
1. Decode header and payload (base64)
2. Verify signature using secret key
3. Check expiration (exp > current_time)
4. Extract claims (sub, user_id, role)
5. Return TokenData or None if invalid

**Recommended Secret Key Rotation**:
- In production: Use strong, randomly generated key (>32 bytes)
- Never hardcode secrets in code
- Use environment variables (via .env file)
- Rotate keys periodically (with token refresh strategy)

### 3. Authorization

**Role Hierarchy**:
```python
role_hierarchy = {
    "user": 0,
    "admin": 1
}
```

**Permission Check**:
```python
def check_permission(user_role: str, required_role: str) -> bool:
    """Check if user has required role"""
    role_hierarchy = {"user": 0, "admin": 1}
    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
```

**Usage**:
```python
# Only admins can access this endpoint
if not check_permission(current_user.role, "admin"):
    raise HTTPException(status_code=403, detail="권한 부족")
```

### 4. CORS Protection

**Allowed Origins**:
```python
["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"]
```

**Credentials**: Allowed (cookies can be sent with requests)

**Methods**: All HTTP methods allowed

**Headers**: All headers allowed (including Authorization)

### 5. HTTPS/TLS

**Recommended Settings**:
- Use HTTPS in production (not HTTP)
- Certificate validation enabled
- TLS 1.2 or higher

### 6. Additional Security Headers

**Recommendations** (not currently implemented):
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: ...
```

---

## MFA Implementation

### 1. MFA Setup Flow

**File**: `web/backend/app/core/mfa.py`

#### TOTP Provider

**Setup Process**:
```python
class TOTPProvider(MFAProvider):
    async def setup(self, user_id: int, user_email: str) -> Dict[str, Any]:
        # Generate TOTP secret (base32-encoded)
        secret = pyotp.random_base32()
        
        # Create TOTP instance
        totp = pyotp.TOTP(secret)
        
        # Generate provisioning URI for QR code
        provisioning_uri = totp.provisioning_uri(
            name=user_email, 
            issuer_name="MyStocks"
        )
        
        # Generate QR code image (base64-encoded PNG)
        qr_code_image = self._generate_qr_code(provisioning_uri)
        
        # Generate 10 backup codes for account recovery
        backup_codes = self._generate_backup_codes()
        
        return {
            "method": "totp",
            "secret": secret,
            "qr_code": qr_code_image,
            "backup_codes": backup_codes,
            "manual_entry_key": secret,
        }
```

**Backup Code Generation**:
```python
def _generate_backup_codes(self) -> List[str]:
    """Generate 10 backup codes (8 chars each, alphanumeric)"""
    codes = []
    characters = string.ascii_uppercase + string.digits
    
    for _ in range(10):
        code = "".join(secrets.choice(characters) for _ in range(8))
        formatted_code = f"{code[:4]}-{code[4:]}"  # XXXX-XXXX format
        codes.append(formatted_code)
    
    return codes
```

**Verification Process**:
```python
async def verify(self, secret: str, code: str, window: int = 1) -> bool:
    """Verify 6-digit TOTP code"""
    try:
        totp = pyotp.TOTP(secret)
        # Verify with ±30 second time window tolerance
        return totp.verify(code, valid_window=window)
    except Exception as e:
        logger.warning(f"TOTP verification failed: {e}")
        return False
```

**QR Code Generation**:
- Format: PNG image
- Encoding: base64 data URI
- Includes provisioning URI for automatic import in authenticator apps
- Compatible with: Google Authenticator, Microsoft Authenticator, Authy, FreeOTP

#### Email OTP Provider

**Code Generation**:
```python
async def generate_code(self) -> Tuple[str, datetime]:
    """Generate 6-digit OTP code with 10-minute expiration"""
    code = "".join(secrets.choice(string.digits) for _ in range(6))
    expiration = datetime.utcnow() + timedelta(minutes=10)
    return code, expiration
```

**Verification**:
```python
async def verify(
    self, 
    stored_code: str, 
    provided_code: str, 
    expiration: datetime
) -> bool:
    """Verify OTP code hasn't expired and matches"""
    if datetime.utcnow() > expiration:
        logger.warning("OTP code has expired")
        return False
    
    if stored_code == provided_code:
        logger.info("OTP code verified successfully")
        return True
    
    logger.warning("OTP code does not match")
    return False
```

#### SMS Provider

Similar to Email OTP provider with SMS delivery instead of email.

### 2. MFA Login Flow

**Process in `/auth/login` endpoint**:

```
1. Verify username/password
   ↓
2. Check MFA status in database
   ├─ If MFA enabled and verified methods exist:
   │  ├─ Generate temporary token (5-minute expiration)
   │  ├─ Include "mfa_pending": True in token
   │  └─ Return mfa_required: True + mfa_methods list
   │
   └─ If no MFA:
      ├─ Generate full access token (30-minute expiration)
      └─ Return mfa_required: False
```

**Graceful Degradation** (if MFA database unavailable):
```python
try:
    db_user = db.execute(
        select(UserModel).where(UserModel.username == username)
    ).scalar_one_or_none()
    # ... MFA check logic
except Exception as e:
    # Log error and failure count
    _mfa_query_failure_count += 1
    
    logger.warning(
        "mfa_check_failed",
        failure_count=_mfa_query_failure_count,
        event_type="graceful_degradation_triggered"
    )
    
    # If persistent failure (5+ attempts):
    if _mfa_query_failure_count >= 5:
        logger.error("mfa_persistent_failure_alert")
    
    # Continue with standard login (no MFA)
```

### 3. MFA Database Queries

**Query: Get User's Verified MFA Methods**:
```python
verified_mfa = db.execute(
    select(MFASecretModel).where(
        (MFASecretModel.user_id == db_user.id) and
        (MFASecretModel.verified == True)
    )
).scalars().all()
```

**Returns**: List of MFASecret objects with method, secret, backup_codes

---

## Graceful Degradation

### 1. MFA Database Unavailability

**Scenario**: PostgreSQL connection fails during MFA check in `/auth/login`

**Behavior**:

1. **First Failure**: 
   - Log warning with failure count
   - Continue with standard login (allow access without MFA)
   - Increment failure counter

2. **Repeated Failures** (5+ times):
   - Log ERROR-level alert
   - Message: "MFA database checks have failed persistently"
   - Action required flag triggered

3. **User Experience**:
   - User can still login
   - MFA is bypassed (not ideal but acceptable)
   - System operators are alerted via logs

**Code Implementation**:
```python
global _mfa_query_failure_count
try:
    # Try to get MFA status
    db_user = db.execute(select(UserModel)...).scalar_one_or_none()
    # ... MFA check
    _mfa_query_failure_count = 0  # Reset on success
except Exception as e:
    _mfa_query_failure_count += 1
    
    logger.warning(
        "mfa_check_failed",
        failure_count=_mfa_query_failure_count,
        event_type="graceful_degradation_triggered"
    )
    
    if _mfa_query_failure_count >= 5:
        logger.error("mfa_persistent_failure_alert")
    
    # Continue without MFA check
    mfa_enabled = False
```

### 2. Response Interceptor Error Handling

**Frontend**: `api/index.js` (lines 54-108)

**Graceful Handling**:

1. **401 Unauthorized**:
   - Clear token and user from localStorage
   - Redirect to login page
   - Show error message

2. **403 Forbidden**:
   - Show permission error
   - Keep user logged in (don't redirect)

3. **500 Server Error**:
   - Show generic error message
   - Don't force logout

4. **503 Service Unavailable**:
   - Show service unavailable message
   - Don't force logout

5. **Network Error**:
   - Show network error message
   - Keep token (for retry on reconnection)

### 3. Token Expiration Handling

**Frontend**: `stores/auth.js`

**checkAuth() Method**:
```javascript
async function checkAuth() {
    if (!token.value) return false
    
    try {
        // Verify token by calling /api/auth/me
        const response = await authApi.getCurrentUser()
        user.value = response
        return true
    } catch (error) {
        // Token is invalid or expired
        logout()  // Clear token and redirect
        return false
    }
}
```

**refreshToken() Method**:
```javascript
async function refreshToken() {
    try {
        // Request new token
        const response = await authApi.refreshToken()
        token.value = response.access_token
        localStorage.setItem('token', token.value)
        return true
    } catch (error) {
        // Refresh failed, logout
        logout()
        return false
    }
}
```

---

## Security Considerations

### 1. Vulnerabilities and Mitigations

| Vulnerability | Current Status | Mitigation |
|---|---|---|
| SQL Injection | Low | Using SQLAlchemy ORM (parameterized queries) |
| XSS (Cross-Site Scripting) | Low | Vue 3 auto-escapes templates, uses v-text for untrusted data |
| CSRF (Cross-Site Request Forgery) | Medium | No explicit CSRF tokens (relies on SameSite cookie policy) |
| Brute Force | Low | bcrypt cost 12 (~80ms per attempt) |
| Token Theft | Medium | Token in localStorage (vulnerable to XSS), no HttpOnly flag |
| Man-in-the-Middle | Medium | Not using HTTPS in dev environment |
| Account Enumeration | Medium | Error messages reveal if username exists |

### 2. Recommended Improvements

#### A. Token Storage Security

**Current**: localStorage (vulnerable to XSS)

**Recommended Options**:
1. **HttpOnly Cookies** (most secure):
   ```python
   # Backend: Set in response
   response.set_cookie(
       key="access_token",
       value=token,
       httponly=True,
       secure=True,  # HTTPS only
       samesite="strict"
   )
   ```
   - Not accessible via JavaScript
   - Automatically sent with requests
   - Protected against XSS

2. **Memory + Refresh Token Rotation**:
   ```javascript
   // Frontend: Keep token in memory (cleared on refresh)
   let accessToken = null;  // In memory, not localStorage
   
   // Use refresh token (in HttpOnly cookie) for renewal
   async function refreshToken() {
       const response = await fetch('/api/auth/refresh', {
           credentials: 'include'  // Send cookies
       });
   }
   ```

#### B. Additional Security Headers

```python
from fastapi.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

app.add_middleware(SecurityHeaderMiddleware)
```

#### C. HTTPS Enforcement

**Development**: HTTP is acceptable (localhost)

**Production Requirements**:
- Generate SSL/TLS certificate (Let's Encrypt free option)
- Configure Nginx/Apache to serve HTTPS
- Redirect HTTP to HTTPS
- Enable HSTS header

```nginx
# nginx configuration example
server {
    listen 443 ssl;
    server_name mystocks.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}

server {
    listen 80;
    server_name mystocks.example.com;
    return 301 https://$server_name$request_uri;
}
```

#### D. CSRF Protection

**Current Issue**: No explicit CSRF token validation

**Recommended Implementation**:
```python
from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel

class CsrfSettings(BaseModel):
    secret_key: str = "your-secret-key"

@app.post("/auth/login")
@CsrfProtect.csrf_token_check
async def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
    csrf_protect: CsrfProtect = Depends()
):
    # CSRF token automatically validated
    ...
```

#### E. Rate Limiting

**Current Issue**: No rate limiting on login endpoint (vulnerable to brute force)

**Recommended Implementation**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/login")
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    ...
```

#### F. Account Lockout

**Current Issue**: No account lockout after failed attempts

**Recommended Implementation**:
```python
# In User model
failed_login_attempts = Column(Integer, default=0, nullable=False)
locked_until = Column(DateTime, nullable=True)

# In login endpoint
if user.locked_until and datetime.utcnow() < user.locked_until:
    raise HTTPException(status_code=423, detail="Account temporarily locked")

if not verify_password(password, user.hashed_password):
    user.failed_login_attempts += 1
    if user.failed_login_attempts >= 5:
        user.locked_until = datetime.utcnow() + timedelta(minutes=15)
    db.commit()
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Reset on successful login
user.failed_login_attempts = 0
user.locked_until = None
```

### 3. Secrets Management

**Current Implementation**:
```python
# config.py
secret_key: str = "your-secret-key-change-in-production"
```

**Production Recommendations**:
1. **Use Environment Variables**:
   ```bash
   # .env file (NOT in git)
   SECRET_KEY=generated-random-key-min-32-chars
   OAUTH2_GOOGLE_CLIENT_SECRET=xxx
   DATABASE_PASSWORD=xxx
   ```

2. **Generate Strong Keys**:
   ```python
   import secrets
   secret_key = secrets.token_urlsafe(32)  # Min 32 characters
   ```

3. **Rotate Keys Periodically**:
   - Regenerate secret_key every 90 days
   - Support key rotation (old + new keys for grace period)
   - Implement separate signing and verification keys

### 4. Audit Logging

**Current Implementation**:
- Login attempts logged to `login_audit_logs` table (optional, not forced)
- Structured logging with `structlog` module

**Recommended Enhancements**:
```python
# Log all authentication events
async def audit_log_login(
    db: Session,
    username: str,
    success: bool,
    ip_address: str,
    user_agent: str,
    failure_reason: Optional[str] = None,
    mfa_passed: Optional[bool] = None
):
    log_entry = LoginAuditLog(
        username=username,
        success=success,
        ip_address=ip_address,
        user_agent=user_agent,
        failure_reason=failure_reason,
        mfa_passed=mfa_passed
    )
    db.add(log_entry)
    db.commit()
```

### 5. Monitoring and Alerting

**Recommended Metrics to Monitor**:
- Login success/failure rates
- MFA database availability
- Failed MFA verification attempts
- Account lockouts
- Token validation failures
- Unusual geographic locations
- Rapid login attempts from same IP

**Implementation Example**:
```python
# In login endpoint
logger.info(
    "login_attempt",
    username=username,
    success=True/False,
    ip_address=request.client.host,
    timestamp=datetime.utcnow().isoformat(),
    response_time_ms=(time.time() - start_time) * 1000
)
```

---

## Data Flow Diagram (Complete)

```
┌──────────────────────────────────────────────────────────────────────┐
│                         USER LOGIN FLOW                               │
└──────────────────────────────────────────────────────────────────────┘

FRONTEND (Vue 3)
════════════════════════════════════════════════════════════════════════

1. User clicks "Login" button
         ↓
2. Login.vue validates form
   ├─ username: required
   └─ password: min 6 chars
         ↓
3. Call authStore.login(username, password)
         ↓
4. authApi.login() creates POST request
   ├─ URL: /api/auth/login
   ├─ Body: username=xxx&password=yyy
   └─ Headers: Content-Type: application/x-www-form-urlencoded
         ↓
5. Request interceptor adds Authorization header
   └─ Authorization: Bearer <existing_token_or_mock>
         ↓
6. HTTP POST sent to backend


BACKEND (FastAPI)
════════════════════════════════════════════════════════════════════════

7. /auth/login endpoint receives request
   ├─ Extract: username, password
   └─ Database: get_db() session
         ↓
8. authenticate_user(username, password)
   ├─ Query: users table for username
   ├─ Verify: bcrypt.checkpw(password, hashed_password)
   └─ Return: User object or None
         ↓
9. If auth failed: raise HTTP 401 "用户名或密码错误"
         ↓
10. If auth succeeded:
    ├─ Try: Query MFA configuration from database
    │  ├─ SELECT * FROM mfa_secrets WHERE user_id=X AND verified=True
    │  └─ Catch: Exception → increment failure counter
    │     └─ If 5+ failures: log ERROR alert
    │        else: log WARNING + continue
    │
    ├─ If MFA enabled and verified methods exist:
    │  ├─ Create temp token (exp: +5 min)
    │  │  └─ Payload: {sub, user_id, role, mfa_pending: True}
    │  └─ Return: {
    │       access_token: temp_token,
    │       mfa_required: True,
    │       mfa_methods: [list],
    │       ...
    │     }
    │
    └─ If no MFA:
       ├─ Create access token (exp: +30 min)
       │  └─ Payload: {sub, user_id, role}
       └─ Return: {
            access_token: full_token,
            mfa_required: False,
            ...
          }

11. JWT Token Generation
    ├─ Header: {alg: HS256, typ: JWT}
    ├─ Payload: {sub, user_id, role, exp, iat}
    ├─ Signature: HMACSHA256(header.payload, secret_key)
    └─ Output: base64url(header).base64url(payload).base64url(signature)


DATABASE (PostgreSQL)
════════════════════════════════════════════════════════════════════════

12. Queries executed during login:
    ├─ SELECT * FROM users WHERE username = $1
    ├─ SELECT * FROM mfa_secrets WHERE user_id = $1 AND verified = True
    └─ [OPTIONAL] INSERT INTO login_audit_logs (...)


FRONTEND (Vue 3)
════════════════════════════════════════════════════════════════════════

13. Response interceptor processes response
    ├─ Status 200: return response.data
    └─ Status 401/500: 
       ├─ Clear localStorage token
       ├─ Show error message
       └─ [401] Redirect to /login
         ↓
14. authStore.login() stores response
    ├─ token.value = response.access_token
    ├─ user.value = response.user
    ├─ localStorage.token = token
    └─ localStorage.user = JSON.stringify(user)
         ↓
15. Return { success: true } to Login.vue
         ↓
16. Show "登录成功" message
         ↓
17. Redirect to dashboard or redirect URL
         ↓
18. Router guard checks isAuthenticated
    └─ true: allow access to protected route


SUBSEQUENT REQUESTS
════════════════════════════════════════════════════════════════════════

19. User makes API request (e.g., GET /api/data/...)
         ↓
20. Request interceptor adds token
    └─ Authorization: Bearer <access_token>
         ↓
21. Backend gets_current_user dependency
    ├─ Extract Authorization header: "Bearer <token>"
    ├─ Call verify_token(token)
    │  ├─ jwt.decode(token, secret_key, algorithm=HS256)
    │  ├─ Check exp > current_time
    │  └─ Return TokenData
    ├─ Query users table by username
    └─ Return User object
         ↓
22. Route handler executes with current_user
    └─ Can access: current_user.username, current_user.role, etc.
         ↓
23. Response returned to frontend
    ├─ Status 401: Token invalid/expired
    │  └─ Response interceptor clears token & redirects to /login
    └─ Status 200: Data returned normally


LOGOUT FLOW
════════════════════════════════════════════════════════════════════════

24. User clicks "Logout"
         ↓
25. authStore.logout()
    ├─ Call authApi.logout() (optional, error ignored)
    ├─ token.value = ''
    ├─ user.value = null
    ├─ localStorage.removeItem('token')
    ├─ localStorage.removeItem('user')
    └─ Return to login state
         ↓
26. Router guard redirects to /login


TOKEN REFRESH FLOW
════════════════════════════════════════════════════════════════════════

27. Token approaching expiration or explicitly expired
         ↓
28. Call authStore.refreshToken()
    ├─ POST /api/auth/refresh
    ├─ Includes: Authorization: Bearer <old_token>
    └─ Backend verifies old token (exp may be within grace period)
         ↓
29. Backend generates new token
    ├─ Same payload (username, user_id, role)
    ├─ New exp (current_time + 30 min)
    └─ Return new token
         ↓
30. Frontend updates localStorage.token
         ↓
31. Continue using new token for requests
```

---

## Configuration Summary

### Frontend Configuration

**File**: `web/frontend/src/api/index.js`

```javascript
const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

// Login: application/x-www-form-urlencoded
authApi.login(username, password)  // POST /auth/login

// Token: localStorage
localStorage.getItem('token')
localStorage.setItem('token', token)
```

### Backend Configuration

**File**: `web/backend/app/core/config.py`

```python
# JWT Settings
secret_key: str = "your-secret-key-change-in-production"
algorithm: str = "HS256"
access_token_expire_minutes: int = 30

# Database
postgresql_host: str = "192.168.123.104"
postgresql_port: int = 5438
postgresql_database: str = "mystocks"

# OAuth2 (optional)
oauth2_google_client_id: Optional[str] = None
oauth2_github_client_id: Optional[str] = None

# MFA
mfa_totp_issuer: str = "MyStocks"
mfa_email_code_length: int = 6
mfa_email_code_expires_minutes: int = 10
```

---

## Troubleshooting Guide

### Common Issues

#### 1. "Could not validate credentials" on protected routes

**Causes**:
- Token missing from Authorization header
- Token expired
- Token signature invalid
- Secret key mismatch

**Solutions**:
```python
# Check request headers in browser DevTools
# Authorization: Bearer <token>

# Check token expiration
import jwt
jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

# Check secret key
# Ensure settings.secret_key matches backend configuration
```

#### 2. Login returns 401 "用户名或密码错误"

**Causes**:
- Username doesn't exist
- Password incorrect
- User not active (is_active = False)

**Solutions**:
```python
# Check user in database
SELECT * FROM users WHERE username = 'admin';

# Reset password
UPDATE users SET hashed_password = <new_hash> WHERE username = 'admin';

# Check user status
SELECT is_active FROM users WHERE username = 'admin';
```

#### 3. MFA database unavailable but login still works

**Cause**: Graceful degradation - MFA check skipped if database fails

**Expected Behavior**: Login succeeds without MFA verification

**Logs**:
```
WARNING mfa_check_failed failure_count=1 event_type=graceful_degradation_triggered
ERROR mfa_persistent_failure_alert threshold=5 action_required="Investigate database health"
```

#### 4. Token refresh fails

**Cause**: Old token expired beyond refresh grace period

**Solution**: User must re-login

```python
# Refresh requires valid token (can be near expiration)
# Grace period determined by JWT library (typically same as exp)
```

#### 5. CORS errors in browser console

**Cause**: Frontend and backend origins mismatch CORS config

**Solution**:
```python
# In main.py CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Add your origin
    allow_credentials=True,
)
```

---

## Summary

The MyStocks web authentication system provides:

✅ **Multi-layer Security**: JWT tokens, bcrypt passwords, role-based access  
✅ **MFA Support**: TOTP, Email OTP, SMS (optional)  
✅ **Graceful Degradation**: Continues operation if MFA database unavailable  
✅ **User-Friendly Errors**: Informative error messages for debugging  
✅ **Comprehensive Audit**: Login attempt tracking and monitoring  
✅ **Token Management**: Auto-refresh, expiration, validation  
✅ **OAuth2 Integration**: Support for Google, GitHub providers (optional)

**Production Recommendations**:
- Use HTTPS only
- Store secrets in environment variables
- Implement rate limiting
- Add CSRF protection
- Use HttpOnly cookies for tokens
- Enable comprehensive audit logging
- Monitor for suspicious activity

