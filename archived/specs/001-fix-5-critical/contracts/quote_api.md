# Stock Quote API Contract

**Feature**: Fix 5 Critical Issues in OpenStock Demo
**API Version**: 1.0
**Base URL**: `http://localhost:8000/api`
**Authentication**: Required (JWT Bearer token)

## Overview

Real-time stock quote retrieval with automatic exchange suffix detection for Chinese A-share stocks.

---

## Endpoint

### GET /stock-search/quote/{stock_code}

**Purpose**: Fetch real-time market quote for a specific stock

**Authentication**: Required

**Path Parameters**:
- `stock_code` (string, required): 6-digit stock code with or without exchange suffix
  - Examples: `600519`, `600519.SH`, `000858`, `300750.SZ`

**Query Parameters**:
- `market` (string, optional): Market type filter
  - Values: `auto`, `cn`, `hk`
  - Default: `auto`
  - `cn`: Chinese A-share only (Shanghai + Shenzhen)
  - `hk`: Hong Kong H-share only
  - `auto`: Auto-detect based on stock code

**Request**:
```http
GET /api/stock-search/quote/600519?market=cn HTTP/1.1
Host: localhost:8000
Authorization: Bearer <JWT_TOKEN>
```

**Response** (200 OK):
```json
{
  "symbol": "600519.SH",
  "name": "贵州茅台",
  "current": 1850.50,
  "change": 25.30,
  "change_percent": 1.39,
  "high": 1865.00,
  "low": 1840.00,
  "open": 1845.00,
  "previous_close": 1825.20,
  "volume": 2500000,
  "amount": 4625000000.0,
  "timestamp": 1737025200,
  "trading_status": "trading"
}
```

**Error Responses**:

1. **404 Not Found** - Stock not found in market data
   ```json
   {
     "detail": "未找到股票报价: 股票代码 600999 不存在或数据源暂未提供报价"
   }
   ```

2. **400 Bad Request** - Invalid stock code format
   ```json
   {
     "detail": "无效的股票代码格式。预期格式: 6位数字，可选 .SH/.SZ/.HK 后缀"
   }
   ```

3. **401 Unauthorized** - Missing or invalid JWT token
   ```json
   {
     "detail": "Not authenticated"
   }
   ```

4. **500 Internal Server Error** - AKShare API failure
   ```json
   {
     "detail": "数据源暂时不可用，请稍后重试"
   }
   ```

5. **503 Service Unavailable** - AKShare timeout (> 10 seconds)
   ```json
   {
     "detail": "数据源响应超时，请稍后重试"
   }
   ```

---

## Stock Code Normalization

### Auto-Detection Rules

The API automatically detects and adds the appropriate exchange suffix if not provided:

| Input Code | Detected Exchange | Normalized Code | Reasoning |
|------------|-------------------|-----------------|-----------|
| `600519` | Shanghai (SH) | `600519.SH` | 600xxx-603xxx → SH |
| `601318` | Shanghai (SH) | `601318.SH` | 600xxx-603xxx → SH |
| `688001` | Shanghai STAR (SH) | `688001.SH` | 688xxx → SH STAR Market |
| `000858` | Shenzhen (SZ) | `000858.SZ` | 000xxx-003xxx → SZ Main |
| `002415` | Shenzhen (SZ) | `002415.SZ` | 002xxx → SZ SME Board |
| `300750` | Shenzhen (SZ) | `300750.SZ` | 300xxx-301xxx → SZ ChiNext |
| `600519.SH` | (Already normalized) | `600519.SH` | Pass-through |

### Validation Rules

1. **Length**: Must be exactly 6 digits (excluding exchange suffix)
2. **Format**: `^\d{6}(\.(SH|SZ|HK))?$`
3. **Characters**: Only digits and optional exchange suffix
4. **Case Insensitive**: `.sh` normalized to `.SH`, `.sz` to `.SZ`

### Edge Cases

- **Non-existent codes**: Return 404 with clear message (e.g., "股票代码 600999 不存在")
- **Suspended stocks**: Return last available quote with `trading_status: "halted"`
- **After-hours**: Return quote from market close with `trading_status: "closed"`
- **Invalid format**: Return 400 before querying data source

---

## Response Fields

### StockQuote Model

```typescript
interface StockQuote {
  symbol: string;          // Normalized stock code with exchange (e.g., "600519.SH")
  name: string;            // Stock name in Chinese (e.g., "贵州茅台")
  current: number;         // Current price (RMB)
  change: number;          // Absolute price change from previous close (RMB)
  change_percent: number;  // Percentage change (e.g., 1.39 = +1.39%)
  high: number;            // Day's highest price (RMB)
  low: number;             // Day's lowest price (RMB)
  open: number;            // Opening price (RMB)
  previous_close: number;  // Previous trading day's closing price (RMB)
  volume: number;          // Trading volume (shares)
  amount: number;          // Trading amount (RMB)
  timestamp: number;       // Unix timestamp (seconds since epoch)
  trading_status: string;  // "trading" | "halted" | "closed" | "pre_market" | "after_hours"
}
```

### Field Details

| Field | Type | Unit | Range | Notes |
|-------|------|------|-------|-------|
| symbol | string | N/A | 6 digits + suffix | Always includes exchange suffix |
| name | string | N/A | 1-100 chars | Chinese characters supported |
| current | float | RMB | > 0 | Latest traded price |
| change | float | RMB | Any | Positive = up, Negative = down |
| change_percent | float | % | Any | Calculated: (current - previous_close) / previous_close × 100 |
| high | float | RMB | >= current | May equal current if reached just now |
| low | float | RMB | <= current | May equal current if reached just now |
| open | float | RMB | > 0 | Opening auction price |
| previous_close | float | RMB | > 0 | Used for change calculation |
| volume | integer | shares | >= 0 | Cumulative since market open |
| amount | float | RMB | >= 0 | Cumulative trading value |
| timestamp | integer | seconds | Unix epoch | Time of last update |
| trading_status | string | N/A | Enum | Current trading state |

### Trading Status Values

- `"trading"`: Market open, active trading
- `"halted"`: Trading temporarily suspended (e.g., major news announcement)
- `"closed"`: Market closed, showing last quote from previous session
- `"pre_market"`: Before market open (9:15-9:25 AM call auction)
- `"after_hours"`: After market close (3:00-3:30 PM closing auction for Shenzhen)

---

## Data Source

### AKShare Integration

**Function**: `akshare.stock_zh_a_spot_em()`

**Update Frequency**: Real-time during trading hours (9:30 AM - 3:00 PM CST, Monday-Friday)

**Data Latency**: Typically < 3 seconds from actual trade

**Coverage**:
- Shanghai Stock Exchange (SSE): All A-share stocks
- Shenzhen Stock Exchange (SZSE): All A-share stocks (Main, SME, ChiNext)
- Excluded: B-shares, Hong Kong H-shares (requires different endpoint)

**Reliability**: 99.5% uptime during trading hours (based on AKShare historical data)

---

## Performance

### Response Time SLA

| Scenario | Typical | p95 | p99 | Max |
|----------|---------|-----|-----|-----|
| Cache hit | N/A | N/A | N/A | N/A |
| Cache miss (AKShare call) | 1.5s | 3s | 5s | 10s |
| Invalid code (no external call) | 50ms | 100ms | 150ms | 200ms |
| Stock not found | 1.5s | 3s | 5s | 10s |

**Note**: Currently no caching implemented (each request queries AKShare). Future enhancement: 30-second TTL cache.

### Timeout Handling

- **AKShare call timeout**: 10 seconds
- **Total request timeout**: 15 seconds (FastAPI default)
- **Retry strategy**: No automatic retries (fail-fast for demo)

---

## Security

1. **Authentication**: JWT token required (extracted from `Authorization` header)
2. **Rate Limiting**: None (consider adding if production deployment)
3. **Input Validation**: Stock code validated before external API call
4. **Error Masking**: Internal errors logged but not exposed to client

---

## Monitoring & Observability

### Logged Events

1. **Quote Request**: Log stock_code, user_id, market parameter
2. **Normalization**: Log original code → normalized code
3. **AKShare Call**: Log duration, success/failure
4. **Errors**: Log full error details (type, message, stack trace)

### Metrics to Track

- **Request Count**: Total requests per minute/hour
- **Error Rate**: Percentage of 404/500 responses
- **Response Time**: p50, p95, p99 latencies
- **AKShare Availability**: Success rate of external API calls

---

## Testing

### Test Cases

#### 1. Happy Path - Valid Code Without Suffix
```bash
curl -X GET "http://localhost:8000/api/stock-search/quote/600519?market=cn" \
  -H "Authorization: Bearer <token>"

Expected: 200 OK with complete quote data, symbol = "600519.SH"
```

#### 2. Happy Path - Valid Code With Suffix
```bash
curl -X GET "http://localhost:8000/api/stock-search/quote/000858.SZ?market=cn" \
  -H "Authorization: Bearer <token>"

Expected: 200 OK with complete quote data, symbol = "000858.SZ"
```

#### 3. Error - Invalid Code Format
```bash
curl -X GET "http://localhost:8000/api/stock-search/quote/ABC123?market=cn" \
  -H "Authorization: Bearer <token>"

Expected: 400 Bad Request with error message
```

#### 4. Error - Non-Existent Code
```bash
curl -X GET "http://localhost:8000/api/stock-search/quote/600999?market=cn" \
  -H "Authorization: Bearer <token>"

Expected: 404 Not Found with "未找到股票报价" message
```

#### 5. Error - Missing Authentication
```bash
curl -X GET "http://localhost:8000/api/stock-search/quote/600519?market=cn"

Expected: 401 Unauthorized
```

#### 6. Edge Case - After Trading Hours
```bash
# Execute at 5:00 PM (after market close)
curl -X GET "http://localhost:8000/api/stock-search/quote/600519?market=cn" \
  -H "Authorization: Bearer <token>"

Expected: 200 OK with trading_status = "closed", timestamp = last market close time
```

### Sample Test Data

**Valid A-share codes**:
- `600519` - 贵州茅台 (Large-cap, high liquidity)
- `000858` - 五粮液 (Shenzhen main board)
- `300750` - 宁德时代 (ChiNext, new energy)
- `601318` - 中国平安 (Financial sector)
- `688981` - 中芯国际 (STAR market)

**Invalid codes for testing**:
- `600999` - Non-existent
- `ABC123` - Invalid format
- `12345` - Wrong length
- `6005191` - Too many digits

---

## Migration Notes

### Existing Behavior vs. New Behavior

| Scenario | Before Fix | After Fix |
|----------|------------|-----------|
| Code without suffix (e.g., `300892`) | 404 "未找到股票报价" | 200 OK with auto-detected suffix |
| Code with suffix (e.g., `300892.SZ`) | 200 OK | 200 OK (unchanged) |
| Invalid code format | 500 Internal Server Error | 400 Bad Request (fail-fast) |
| AKShare unavailable | Unhandled exception | 503 Service Unavailable with retry message |

### Backward Compatibility

- ✅ Fully backward compatible (existing calls with exchange suffix work unchanged)
- ✅ New functionality is additive (auto-detection for codes without suffix)
- ✅ Error responses improved (clearer messages, proper status codes)

---

## Future Enhancements (Out of Scope)

1. **Caching**: Add 30-second TTL cache keyed by normalized stock code
2. **Batch Quotes**: Support multiple stock codes in single request (e.g., `/quote?symbols=600519,000858,300750`)
3. **WebSocket Streaming**: Real-time push updates for subscribed stocks
4. **Historical Intraday**: Add minute-level quote history endpoint
5. **Extended Hours Data**: Pre-market (9:15-9:30) and after-hours quotes
6. **H-share Support**: Integrate separate AKShare endpoint for Hong Kong stocks

---

## Dependencies

- **akshare**: Python library for Chinese stock market data (version >= 1.11.0)
- **pandas**: Data manipulation (akshare returns DataFrames)
- **psycopg2**: PostgreSQL driver (for user authentication, not quote storage)
- **FastAPI**: Web framework
- **pydantic**: Data validation and serialization

---

## Contact & Support

For issues related to:
- **Stock code not found**: Verify code exists on Shanghai/Shenzhen exchanges
- **Slow responses**: Check AKShare service status (https://github.com/akfamily/akshare)
- **Data accuracy**: Compare with official exchange websites (SSE/SZSE)
