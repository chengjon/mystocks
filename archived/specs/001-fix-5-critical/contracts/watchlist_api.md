# Watchlist API Contract

**Feature**: Fix 5 Critical Issues in OpenStock Demo
**API Version**: 1.0
**Base URL**: `http://localhost:8000/api`
**Authentication**: Required (JWT Bearer token)

## Overview

Watchlist management endpoints for creating groups, adding stocks, and organizing user watchlists.

---

## Endpoints

### 1. GET /watchlist/groups

**Purpose**: Retrieve all watchlist groups for the authenticated user

**Authentication**: Required

**Request**:
```http
GET /api/watchlist/groups HTTP/1.1
Host: localhost:8000
Authorization: Bearer <JWT_TOKEN>
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "group_name": "默认分组",
    "created_at": "2025-01-15T10:30:00Z",
    "sort_order": 0,
    "stock_count": 5
  },
  {
    "id": 2,
    "group_name": "科技股",
    "created_at": "2025-01-16T14:20:00Z",
    "sort_order": 1,
    "stock_count": 3
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT token
- `500 Internal Server Error`: Database connection failure

**Performance**: < 100ms (typical), < 500ms (p95)

**Notes**:
- Results ordered by `sort_order` ASC, then `created_at` ASC
- `stock_count` is denormalized (cached) for performance

---

### 2. POST /watchlist/groups

**Purpose**: Create a new watchlist group

**Authentication**: Required

**Request**:
```http
POST /api/watchlist/groups HTTP/1.1
Host: localhost:8000
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "group_name": "价值股"
}
```

**Response** (201 Created):
```json
{
  "id": 3,
  "group_name": "价值股",
  "created_at": "2025-01-20T09:15:00Z",
  "sort_order": 2,
  "stock_count": 0
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input (see details below)
  ```json
  {
    "detail": "Group name must be 1-100 characters"
  }
  ```
- `409 Conflict`: Duplicate group name
  ```json
  {
    "detail": "Group '价值股' already exists"
  }
  ```
- `401 Unauthorized`: Missing or invalid JWT token
- `500 Internal Server Error`: Database error

**Validation Rules**:
1. `group_name` required, 1-100 characters after trimming
2. `group_name` cannot contain only whitespace
3. `group_name` must be unique per user

**Performance**: < 200ms (typical)

---

### 3. PUT /watchlist/groups/{group_id}

**Purpose**: Update watchlist group name or sort order

**Authentication**: Required

**Request**:
```http
PUT /api/watchlist/groups/3 HTTP/1.1
Host: localhost:8000
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "group_name": "价值投资",
  "sort_order": 1
}
```

**Response** (200 OK):
```json
{
  "id": 3,
  "group_name": "价值投资",
  "created_at": "2025-01-20T09:15:00Z",
  "sort_order": 1,
  "stock_count": 0
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input
- `404 Not Found`: Group does not exist or belongs to different user
- `409 Conflict`: New name conflicts with existing group
- `401 Unauthorized`: Missing or invalid JWT token

**Notes**:
- At least one field (group_name or sort_order) must be provided
- User can only update their own groups (ownership verified)

---

### 4. DELETE /watchlist/groups/{group_id}

**Purpose**: Delete a watchlist group and all its stocks

**Authentication**: Required

**Request**:
```http
DELETE /api/watchlist/groups/3 HTTP/1.1
Host: localhost:8000
Authorization: Bearer <JWT_TOKEN>
```

**Response** (204 No Content):
```
(empty body)
```

**Error Responses**:
- `404 Not Found`: Group does not exist or belongs to different user
- `403 Forbidden`: Cannot delete default group with stocks
  ```json
  {
    "detail": "Cannot delete default group while it contains stocks. Move stocks to another group first."
  }
  ```
- `401 Unauthorized`: Missing or invalid JWT token

**Notes**:
- Deleting a group CASCADE deletes all watchlist items in that group
- Default group ("默认分组") can only be deleted if empty

---

### 5. GET /watchlist/groups/{group_id}/stocks

**Purpose**: Get all stocks in a specific group

**Authentication**: Required

**Request**:
```http
GET /api/watchlist/groups/1/stocks HTTP/1.1
Host: localhost:8000
Authorization: Bearer <JWT_TOKEN>
```

**Response** (200 OK):
```json
[
  {
    "id": 101,
    "stock_code": "600519.SH",
    "stock_name": "贵州茅台",
    "added_at": "2025-01-15T11:00:00Z",
    "notes": "白酒龙头"
  },
  {
    "id": 102,
    "stock_code": "000858.SZ",
    "stock_name": "五粮液",
    "added_at": "2025-01-16T14:30:00Z",
    "notes": null
  }
]
```

**Error Responses**:
- `404 Not Found`: Group does not exist or belongs to different user
- `401 Unauthorized`: Missing or invalid JWT token

**Performance**: < 100ms for groups with < 100 stocks

**Notes**:
- Results ordered by `added_at` DESC (newest first)
- Returns empty array if group has no stocks

---

### 6. POST /watchlist/groups/{group_id}/stocks

**Purpose**: Add a stock to a watchlist group

**Authentication**: Required

**Request**:
```http
POST /api/watchlist/groups/1/stocks HTTP/1.1
Host: localhost:8000
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "stock_code": "600519",
  "stock_name": "贵州茅台",
  "notes": "白酒龙头"
}
```

**Response** (201 Created):
```json
{
  "id": 103,
  "stock_code": "600519.SH",
  "stock_name": "贵州茅台",
  "added_at": "2025-01-20T10:05:00Z",
  "notes": "白酒龙头"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid stock code format
  ```json
  {
    "detail": "Invalid stock code format. Expected 6 digits optionally followed by .SH/.SZ/.HK"
  }
  ```
- `409 Conflict`: Stock already exists in this group
  ```json
  {
    "detail": "Stock 600519.SH is already in this group"
  }
  ```
- `404 Not Found`: Group does not exist
- `401 Unauthorized`: Missing or invalid JWT token

**Validation Rules**:
1. `stock_code` required, must match pattern `^\d{6}(\.(SH|SZ|HK))?$`
2. `stock_code` automatically normalized with exchange suffix
3. `stock_name` optional, max 100 characters
4. `notes` optional, max 1000 characters

**Performance**: < 200ms (typical)

**Notes**:
- If stock_code lacks exchange suffix, it's auto-detected based on first digit
- Same stock can exist in multiple groups (different group_id values)

---

### 7. PUT /watchlist/stocks/{stock_id}

**Purpose**: Update notes for a watchlist item

**Authentication**: Required

**Request**:
```http
PUT /api/watchlist/stocks/103 HTTP/1.1
Host: localhost:8000
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "notes": "长期持有，分红稳定"
}
```

**Response** (200 OK):
```json
{
  "id": 103,
  "stock_code": "600519.SH",
  "stock_name": "贵州茅台",
  "added_at": "2025-01-20T10:05:00Z",
  "notes": "长期持有，分红稳定"
}
```

**Error Responses**:
- `404 Not Found`: Stock does not exist or belongs to different user
- `400 Bad Request`: Notes exceed 1000 characters
- `401 Unauthorized`: Missing or invalid JWT token

---

### 8. DELETE /watchlist/stocks/{stock_id}

**Purpose**: Remove a stock from watchlist

**Authentication**: Required

**Request**:
```http
DELETE /api/watchlist/stocks/103 HTTP/1.1
Host: localhost:8000
Authorization: Bearer <JWT_TOKEN>
```

**Response** (204 No Content):
```
(empty body)
```

**Error Responses**:
- `404 Not Found`: Stock does not exist or belongs to different user
- `401 Unauthorized`: Missing or invalid JWT token

**Notes**:
- Deleting a stock decrements the group's `stock_count` via database trigger

---

## Data Models

### WatchlistGroup

```typescript
interface WatchlistGroup {
  id: number;
  group_name: string;
  created_at: string;  // ISO 8601 datetime
  sort_order: number;
  stock_count: number;
}
```

### WatchlistStock

```typescript
interface WatchlistStock {
  id: number;
  stock_code: string;
  stock_name: string | null;
  added_at: string;  // ISO 8601 datetime
  notes: string | null;
}
```

---

## Stock Code Normalization

### Input Formats Accepted

- `600519` → Normalized to `600519.SH`
- `000858` → Normalized to `000858.SZ`
- `300750` → Normalized to `300750.SZ`
- `600519.SH` → Returned as-is (already normalized)

### Detection Rules

| Code Pattern | Exchange | Example |
|--------------|----------|---------|
| 600xxx-603xxx | Shanghai (SH) | 600519 → 600519.SH |
| 688xxx | Shanghai STAR (SH) | 688001 → 688001.SH |
| 000xxx-003xxx | Shenzhen Main (SZ) | 000858 → 000858.SZ |
| 300xxx-301xxx | Shenzhen ChiNext (SZ) | 300750 → 300750.SZ |
| 6xxxxx (other) | Shanghai (SH) | 601318 → 601318.SH |
| 0xxxxx, 3xxxxx (other) | Shenzhen (SZ) | 002415 → 002415.SZ |

---

## Error Handling

### Standard Error Response Format

```json
{
  "detail": "Human-readable error message"
}
```

### HTTP Status Codes

- `200 OK`: Successful GET/PUT request
- `201 Created`: Successful POST request
- `204 No Content`: Successful DELETE request
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Operation not allowed
- `404 Not Found`: Resource does not exist
- `409 Conflict`: Duplicate entry
- `500 Internal Server Error`: Server-side error

---

## Security

1. **Authentication**: All endpoints require valid JWT token in `Authorization: Bearer <token>` header
2. **Authorization**: Users can only access their own watchlist data (filtered by user_id from JWT)
3. **SQL Injection Prevention**: All queries use parameterized statements
4. **Input Sanitization**: Group names and notes are escaped to prevent XSS

---

## Performance SLAs

| Endpoint | Typical | p95 | p99 |
|----------|---------|-----|-----|
| GET /groups | 50ms | 100ms | 200ms |
| POST /groups | 100ms | 200ms | 500ms |
| PUT /groups/{id} | 80ms | 150ms | 300ms |
| DELETE /groups/{id} | 100ms | 200ms | 500ms |
| GET /groups/{id}/stocks | 50ms | 150ms | 300ms |
| POST /groups/{id}/stocks | 100ms | 200ms | 500ms |
| PUT /stocks/{id} | 80ms | 150ms | 300ms |
| DELETE /stocks/{id} | 100ms | 200ms | 500ms |

**Assumptions**: < 100 stocks per user, PostgreSQL on localhost, no network latency

---

## Testing

### Integration Test Scenarios

1. **Happy Path**: Create group → Add stock → Update notes → Remove stock → Delete group
2. **Duplicate Prevention**: Try to create group with existing name → Expect 409
3. **Stock Code Normalization**: Add stock without suffix → Verify suffix added
4. **Authorization**: Try to access another user's group → Expect 404
5. **Cascade Delete**: Delete group with stocks → Verify all stocks removed
6. **Default Group Protection**: Try to delete "默认分组" with stocks → Expect 403

### Sample Test Data

```python
# User 1 (admin)
user_1_id = 1
default_group_id = 1  # "默认分组"
tech_group_id = 2     # "科技股"

# Sample stocks
stock_1 = {"stock_code": "600519", "stock_name": "贵州茅台"}
stock_2 = {"stock_code": "000858", "stock_name": "五粮液"}
stock_3 = {"stock_code": "300750", "stock_name": "宁德时代"}
```
