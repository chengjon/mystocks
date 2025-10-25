# K-Line Chart API Contract

**Feature**: Fix 5 Critical Issues in OpenStock Demo
**API Version**: 1.0
**Base URL**: `http://localhost:8000/api`
**Authentication**: Required (JWT Bearer token)

## Overview

Historical K-line (candlestick) data retrieval for technical analysis and chart visualization.

---

## Endpoint

### GET /market/kline

**Purpose**: Fetch historical K-line (OHLCV) data for a stock

**Authentication**: Required

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| stock_code | string | Yes | N/A | 6-digit code with optional exchange suffix (e.g., "600519", "600519.SH") |
| period | string | No | "daily" | Time period: "daily", "weekly", "monthly" |
| adjust | string | No | "qfq" | Adjustment type: "qfq" (forward), "hfq" (backward), "" (none) |
| start_date | string | No | 60 days ago | Start date in YYYY-MM-DD format |
| end_date | string | No | Today | End date in YYYY-MM-DD format |

**Request**:
```http
GET /api/market/kline?stock_code=600519&period=daily&adjust=qfq HTTP/1.1
Host: localhost:8000
Authorization: Bearer <JWT_TOKEN>
```

**Response** (200 OK):
```json
{
  "stock_code": "600519.SH",
  "stock_name": "贵州茅台",
  "period": "daily",
  "adjust": "qfq",
  "data": [
    {
      "date": "2025-01-20",
      "timestamp": 1737331200,
      "open": 1845.00,
      "high": 1865.00,
      "low": 1840.00,
      "close": 1850.50,
      "volume": 2500000,
      "amount": 4625000000.0,
      "amplitude": 1.37,
      "change_percent": 1.39
    },
    {
      "date": "2025-01-17",
      "timestamp": 1737072000,
      "open": 1820.00,
      "high": 1830.00,
      "low": 1815.00,
      "close": 1825.20,
      "volume": 1800000,
      "amount": 3283600000.0,
      "amplitude": 0.82,
      "change_percent": 0.29
    }
    // ... (58 more trading days)
  ],
  "count": 60
}
```

**Error Responses**:

1. **400 Bad Request** - Invalid parameters
   ```json
   {
     "detail": "无效的股票代码格式"
   }
   ```
   ```json
   {
     "detail": "无效的时间周期。支持的值: daily, weekly, monthly"
   }
   ```
   ```json
   {
     "detail": "无效的日期格式。请使用 YYYY-MM-DD 格式"
   }
   ```

2. **404 Not Found** - Stock or data not found
   ```json
   {
     "detail": "股票代码 600999 不存在或暂无K线数据"
   }
   ```

3. **422 Unprocessable Entity** - Insufficient data
   ```json
   {
     "detail": "该股票历史数据不足10个交易日，无法生成K线图"
   }
   ```

4. **401 Unauthorized** - Missing/invalid JWT
   ```json
   {
     "detail": "Not authenticated"
   }
   ```

5. **500 Internal Server Error** - AKShare failure
   ```json
   {
     "detail": "数据源暂时不可用，请稍后重试"
   }
   ```

---

## Query Parameters Detail

### stock_code (Required)

**Format**: 6-digit number with optional exchange suffix

**Examples**:
- `600519` (auto-detected as `600519.SH`)
- `600519.SH` (explicit Shanghai)
- `000858.SZ` (explicit Shenzhen)

**Validation**:
- Must match pattern: `^\d{6}(\.(SH|SZ|HK))?$`
- Auto-normalized using same logic as quote API

---

### period (Optional, default: "daily")

**Supported Values**:

| Value | Description | Typical Use Case |
|-------|-------------|------------------|
| `daily` | Daily K-line (1 day per candle) | Short-term analysis (1-3 months) |
| `weekly` | Weekly K-line (1 week per candle) | Medium-term analysis (3-12 months) |
| `monthly` | Monthly K-line (1 month per candle) | Long-term analysis (1-5 years) |

**Chinese Names**:
- `daily` = 日K
- `weekly` = 周K
- `monthly` = 月K

**Data Points Returned**:
- `daily`: Up to 250 trading days (1 year)
- `weekly`: Up to 52 weeks (1 year)
- `monthly`: Up to 60 months (5 years)

---

### adjust (Optional, default: "qfq")

**Supported Values**:

| Value | Chinese | Description | When to Use |
|-------|---------|-------------|-------------|
| `qfq` | 前复权 | Forward-adjusted | **Recommended default**. Adjusts historical prices forward to current level. Best for price continuity. |
| `hfq` | 后复权 | Backward-adjusted | Adjusts current price backward to historical level. Useful for relative comparisons. |
| `""` (empty) | 不复权 | Unadjusted | Raw prices without adjustment. Use when analyzing absolute price levels. |

**Adjustment Events**:
- Stock splits (e.g., 10-for-1)
- Dividends (e.g., 5 RMB per share)
- Rights offerings

**Example**:
If a stock had a 10-for-1 split on 2024-06-01:
- `qfq`: Pre-split prices divided by 10 (e.g., 1000 → 100)
- `hfq`: Post-split prices multiplied by 10 (e.g., 100 → 1000)
- `""`: Pre-split = 1000, Post-split = 100 (discontinuity)

---

### start_date & end_date (Optional)

**Format**: `YYYY-MM-DD` (ISO 8601 date only)

**Examples**:
- `2024-01-01` (Valid)
- `2025-01-20` (Valid)
- `2025/01/20` (Invalid - wrong separator)
- `01-20-2025` (Invalid - wrong order)

**Default Behavior**:
- If both omitted: Last 60 trading days
- If only `start_date`: From start_date to today
- If only `end_date`: Last 60 days before end_date
- If both provided: Specific range (max 250 days for daily)

**Validation**:
- `start_date` must be <= `end_date`
- Range must not exceed 250 trading days (for daily period)
- Cannot request future dates (> today)

---

## Response Fields

### Response Wrapper

```typescript
interface KLineResponse {
  stock_code: string;       // Normalized code with exchange (e.g., "600519.SH")
  stock_name: string;       // Stock name (e.g., "贵州茅台")
  period: string;           // "daily" | "weekly" | "monthly"
  adjust: string;           // "qfq" | "hfq" | ""
  data: KLineDataPoint[];   // Array of candlesticks (newest first)
  count: number;            // Number of data points returned
}
```

### KLineDataPoint Model

```typescript
interface KLineDataPoint {
  date: string;             // Trading date in YYYY-MM-DD format
  timestamp: number;        // Unix timestamp (seconds) for frontend charting
  open: number;             // Opening price (RMB)
  high: number;             // Highest price (RMB)
  low: number;              // Lowest price (RMB)
  close: number;            // Closing price (RMB)
  volume: number;           // Trading volume (shares)
  amount: number;           // Trading amount (RMB)
  amplitude: number;        // Price amplitude: (high - low) / previous_close × 100 (%)
  change_percent: number;   // Day-over-day change: (close - previous_close) / previous_close × 100 (%)
}
```

### Field Constraints

| Field | Type | Range | Validation |
|-------|------|-------|------------|
| date | string | Valid trading day | No weekends, no holidays |
| timestamp | integer | Unix epoch | Midnight CST of trading day |
| open | float | > 0 | Must be within [low, high] |
| high | float | > 0 | >= max(open, close) |
| low | float | > 0 | <= min(open, close) |
| close | float | > 0 | Must be within [low, high] |
| volume | integer | >= 0 | Can be 0 for suspended trading |
| amount | float | >= 0 | Can be 0 for suspended trading |
| amplitude | float | >= 0 | Percentage (e.g., 1.37 = 1.37%) |
| change_percent | float | Any | Positive = up, Negative = down |

---

## Data Source

### AKShare Integration

**Function**: `akshare.stock_zh_a_hist()`

**Parameters Mapping**:
```python
df = ak.stock_zh_a_hist(
    symbol=stock_code.split('.')[0],  # Remove exchange suffix
    period=period,                    # "daily", "weekly", "monthly"
    start_date=start_date,            # "20240101"
    end_date=end_date,                # "20250120"
    adjust=adjust                     # "qfq", "hfq", ""
)
```

**Data Quality**:
- **Completeness**: 99.9% of trading days available
- **Accuracy**: Matches official exchange data (SSE/SZSE)
- **Latency**: Previous day's data available by 9:00 AM next day
- **Historical Depth**: Up to IPO date (varies by stock)

---

## Performance

### Response Time SLA

| Scenario | Typical | p95 | p99 | Max |
|----------|---------|-----|-----|-----|
| 60 days daily | 1.5s | 3s | 5s | 10s |
| 250 days daily | 2s | 4s | 6s | 10s |
| 52 weeks weekly | 1s | 2s | 4s | 10s |
| Invalid code (no external call) | 50ms | 100ms | 150ms | 200ms |

### Data Size

| Period | Days | Avg Response Size | Max Response Size |
|--------|------|-------------------|-------------------|
| daily (60 days) | 60 | ~5 KB | ~10 KB |
| daily (250 days) | 250 | ~20 KB | ~40 KB |
| weekly (52 weeks) | 52 | ~4 KB | ~8 KB |
| monthly (60 months) | 60 | ~5 KB | ~10 KB |

**Calculation**: 1 data point ≈ 200 bytes JSON (10 fields × 20 bytes avg)

### Timeout Handling

- **AKShare call timeout**: 10 seconds
- **Total request timeout**: 15 seconds
- **Retry strategy**: None (fail-fast)

---

## Security

1. **Authentication**: JWT token required
2. **Input Validation**: All parameters validated before external call
3. **Rate Limiting**: None (consider adding if heavy usage)
4. **Data Sanitization**: No user-generated content (all data from AKShare)

---

## Frontend Integration

### ECharts Configuration

**Sample Frontend Code**:
```javascript
import * as echarts from 'echarts';

async function loadKLineChart(stockCode) {
  const response = await fetch(
    `/api/market/kline?stock_code=${stockCode}&period=daily&adjust=qfq`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  const klineData = await response.json();

  const chart = echarts.init(document.getElementById('kline-chart'));

  const option = {
    title: { text: `${klineData.stock_name} (${klineData.stock_code})` },
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    grid: [
      { left: '5%', right: '5%', height: '50%' },  // Price chart
      { left: '5%', right: '5%', top: '70%', height: '15%' }  // Volume chart
    ],
    xAxis: [
      { type: 'category', data: klineData.data.map(d => d.date.slice(5)) },  // MM-DD
      { type: 'category', data: klineData.data.map(d => d.date.slice(5)), gridIndex: 1 }
    ],
    yAxis: [
      { type: 'value', scale: true },  // Price axis
      { type: 'value', scale: true, gridIndex: 1 }  // Volume axis
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: klineData.data.map(d => [d.open, d.close, d.low, d.high]),
        itemStyle: {
          color: '#ef5350',      // Red = rising (Chinese convention)
          color0: '#26a69a',     // Green = falling
          borderColor: '#ef5350',
          borderColor0: '#26a69a'
        }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: klineData.data.map((d, i) => ({
          value: d.volume,
          itemStyle: {
            color: i === 0 || d.close >= klineData.data[i + 1]?.close
              ? '#ef5350'  // Red if price up
              : '#26a69a'  // Green if price down
          }
        }))
      }
    ]
  };

  chart.setOption(option);
}
```

### Color Convention (Chinese Market)

**IMPORTANT**: Chinese markets use opposite color convention from Western markets:
- 🔴 **Red**: Price increase (bullish)
- 🟢 **Green**: Price decrease (bearish)

This is the OPPOSITE of US markets (where green = up, red = down).

---

## Testing

### Test Cases

#### 1. Happy Path - Default Parameters
```bash
curl -X GET "http://localhost:8000/api/market/kline?stock_code=600519" \
  -H "Authorization: Bearer <token>"

Expected: 200 OK with 60 daily candles, qfq adjustment
```

#### 2. Happy Path - Custom Date Range
```bash
curl -X GET "http://localhost:8000/api/market/kline?stock_code=600519&start_date=2024-01-01&end_date=2024-12-31" \
  -H "Authorization: Bearer <token>"

Expected: 200 OK with ~244 trading days from 2024
```

#### 3. Happy Path - Weekly Period
```bash
curl -X GET "http://localhost:8000/api/market/kline?stock_code=000858&period=weekly&adjust=hfq" \
  -H "Authorization: Bearer <token>"

Expected: 200 OK with ~52 weekly candles
```

#### 4. Error - Invalid Stock Code
```bash
curl -X GET "http://localhost:8000/api/market/kline?stock_code=ABC123" \
  -H "Authorization: Bearer <token>"

Expected: 400 Bad Request
```

#### 5. Error - Invalid Period
```bash
curl -X GET "http://localhost:8000/api/market/kline?stock_code=600519&period=hourly" \
  -H "Authorization: Bearer <token>"

Expected: 400 Bad Request (hourly not supported)
```

#### 6. Error - Date Range Too Large
```bash
curl -X GET "http://localhost:8000/api/market/kline?stock_code=600519&start_date=2020-01-01&end_date=2025-01-01" \
  -H "Authorization: Bearer <token>"

Expected: 400 Bad Request (exceeds 250 trading days)
```

#### 7. Edge Case - Newly Listed Stock
```bash
# Stock listed only 30 days ago
curl -X GET "http://localhost:8000/api/market/kline?stock_code=688XXX" \
  -H "Authorization: Bearer <token>"

Expected: 200 OK with ~30 candles (all available data)
```

#### 8. Edge Case - Suspended Trading Days
```bash
# Stock with trading suspension periods
curl -X GET "http://localhost:8000/api/market/kline?stock_code=600519&start_date=2024-06-01&end_date=2024-06-30" \
  -H "Authorization: Bearer <token>"

Expected: 200 OK with gaps in dates (suspended days omitted)
```

### Sample Test Data

**Recommended test stocks**:
- `600519` (贵州茅台): Large-cap, long history, high liquidity
- `000858` (五粮液): Shenzhen main board
- `300750` (宁德时代): ChiNext, newer listing
- `601318` (中国平安): Financial sector

**Edge case stocks**:
- Newly listed stocks (< 60 trading days)
- Stocks with historical trading suspensions
- Stocks with multiple splits/dividends (test adjustment)

---

## Business Rules

### Trading Day Exclusions

K-line data ONLY includes trading days. Excluded:
1. **Weekends**: Saturdays and Sundays
2. **Public Holidays**: Chinese national holidays (e.g., Spring Festival, National Day)
3. **Market Closures**: Emergency closures (rare)
4. **Stock Suspensions**: Individual stock trading halts

**Important**: Date ranges are specified in calendar days, but returned data only includes trading days.

Example:
```
Request: start_date=2025-01-15, end_date=2025-01-20 (6 calendar days)
Response: 4 data points (Jan 17, 20 are weekend, excluded)
```

### Adjustment Event Handling

When a stock undergoes adjustment events (split, dividend):

**With Adjustment** (`qfq` or `hfq`):
- Historical prices modified to maintain price continuity
- Chart shows smooth line across event date
- Use for technical analysis

**Without Adjustment** (empty string):
- Historical prices unchanged (actual traded prices)
- Chart shows sudden gap on event date
- Use for absolute price history

---

## Future Enhancements (Out of Scope)

1. **Minute-Level Data**: Add `period="1min"` for intraday analysis
2. **Caching**: Cache daily K-line data (updates once per day after market close)
3. **Batch Requests**: Support multiple stock codes in single request
4. **Technical Indicators**: Pre-calculate MACD, RSI, Bollinger Bands server-side
5. **Real-Time Updates**: WebSocket for live candlestick updates during trading
6. **Export Formats**: Support CSV/Excel download
7. **Historical Comparison**: Overlay multiple stocks on single chart

---

## Dependencies

- **akshare**: Historical market data (version >= 1.11.0)
- **pandas**: DataFrame processing
- **FastAPI**: Web framework
- **pydantic**: Data validation

---

## Migration Notes

### Existing Behavior vs. New Behavior

| Before | After |
|--------|-------|
| Endpoint not implemented | New endpoint `/api/market/kline` |
| Frontend shows "接口未实现" | Frontend can load K-line charts |
| N/A | Auto-detects exchange suffix |
| N/A | Supports 3 time periods (daily, weekly, monthly) |
| N/A | Supports 3 adjustment types (qfq, hfq, none) |

### Backward Compatibility

- ✅ No breaking changes (new endpoint)
- ✅ Follows existing API conventions (auth, error format)
- ✅ Uses same stock code normalization as quote API

---

## Support & Contact

For issues:
- **Insufficient data**: Stock may be newly listed or data not available from AKShare
- **Slow responses**: Check AKShare service status
- **Chart rendering issues**: Verify frontend ECharts configuration
- **Date gaps**: Verify dates fall on trading days (use stock_zh_a_trade_date_ths() to check)
