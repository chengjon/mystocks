# API Endpoint Contracts

**Feature**: Fix All Broken Web Features
**Date**: 2025-10-25

## Overview

This document defines API contracts for endpoints being fixed or newly created as part of this feature.

---

## 1. Fund Flow API (资金流向)

### GET /api/market/fund-flow

**Description**: Retrieve capital flow data by industry or stock

**Query Parameters**:
```json
{
  "type": "string, required, one of: 'industry', 'stock'",
  "date": "string, optional, format: YYYY-MM-DD, default: latest trading day",
  "limit": "integer, optional, default: 50, max: 500",
  "sort_by": "string, optional, one of: 'net_inflow', 'main_net_inflow', default: 'net_inflow'",
  "order": "string, optional, one of: 'asc', 'desc', default: 'desc'"
}
```

**Response (200 OK)**:
```json
{
  "code": 200,
  "data": [
    {
      "trade_date": "2025-10-24",
      "industry_code": "BK0001",
      "industry_name": "电子信息",
      "net_inflow": 12.35,
      "main_net_inflow": 8.20,
      "retail_net_inflow": 4.15
    }
  ],
  "meta": {
    "total": 150,
    "page": 1,
    "per_page": 50
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid parameters
- `500 Internal Server Error`: Database connection failed (user-friendly message)

---

## 2. Dashboard Data API

### GET /api/data/dashboard/summary

**Description**: Get complete dashboard data including favorites, strategies, and market overview

**Query Parameters**:
```json
{
  "include": "string[], optional, one of: ['favorites', 'strategies', 'industry', 'concept', 'fund_flow']"
}
```

**Response (200 OK)**:
```json
{
  "code": 200,
  "data": {
    "favorites": [
      {
        "stock_code": "600519",
        "stock_name": "贵州茅台",
        "current_price": 1755.50,
        "change_pct": 1.23,
        "volume": 15680000,
        "last_updated": "2025-10-24T15:00:00Z"
      }
    ],
    "strategies": [
      {
        "strategy_name": "MACD金叉",
        "matched_stocks": 23,
        "top_stocks": [
          {"stock_code": "000001", "stock_name": "平安银行", "score": 8.5}
        ]
      }
    ],
    "fund_flow": {
      "top_inflow_industries": [
        {"industry_name": "电子信息", "net_inflow": 12.35}
      ]
    }
  },
  "timestamp": "2025-10-24T15:30:00Z"
}
```

---

## 3. Indicator Configuration API

### POST /api/indicators/configs

**Description**: Save custom indicator configuration

**Request Body**:
```json
{
  "indicator_name": "MACD",
  "display_name": "My Custom MACD",
  "parameters": {
    "fast_period": 12,
    "slow_period": 26,
    "signal_period": 9
  },
  "description": "Custom MACD for short-term trading",
  "is_public": false
}
```

**Response (201 Created)**:
```json
{
  "code": 201,
  "data": {
    "id": 123,
    "indicator_name": "MACD",
    "display_name": "My Custom MACD",
    "parameters": {...},
    "created_at": "2025-10-24T15:30:00Z"
  },
  "message": "Indicator configuration saved successfully"
}
```

### GET /api/indicators/configs

**Description**: Retrieve user's saved indicator configurations

**Query Parameters**:
```json
{
  "indicator_name": "string, optional, filter by indicator type",
  "include_public": "boolean, optional, include public configs, default: false"
}
```

**Response (200 OK)**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 123,
      "indicator_name": "MACD",
      "display_name": "My Custom MACD",
      "parameters": {...},
      "is_public": false,
      "created_at": "2025-10-24T15:30:00Z"
    }
  ]
}
```

---

## 4. Authentication Refresh API

### POST /api/auth/refresh

**Description**: Refresh access token using refresh token

**Request Body**:
```json
{
  "refresh_token": "string, required"
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or expired refresh token
- `400 Bad Request`: Missing refresh token

---

## 5. ETF Data API

### GET /api/market/etf-data

**Description**: Retrieve ETF data including NAV, premium rate, and performance metrics

**Query Parameters**:
```json
{
  "etf_code": "string, optional, filter by ETF code",
  "date": "string, optional, format: YYYY-MM-DD",
  "sort_by": "string, optional, one of: 'premium_rate', 'turnover', 'close_price'",
  "limit": "integer, optional, default: 100"
}
```

**Response (200 OK)**:
```json
{
  "code": 200,
  "data": [
    {
      "etf_code": "510300",
      "etf_name": "沪深300ETF",
      "trade_date": "2025-10-24",
      "nav": 4.235,
      "close_price": 4.240,
      "premium_rate": 0.12,
      "volume": 125680000,
      "pe_ratio": 13.5,
      "pb_ratio": 1.42
    }
  ]
}
```

---

## Error Handling Standard

All endpoints follow this error response format:

```json
{
  "error": "User-friendly error message",
  "request_id": "uuid-v4-request-id",
  "timestamp": "2025-10-24T15:30:00Z"
}
```

**Status Codes**:
- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required or failed
- `403 Forbidden`: Authenticated but not authorized
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error (logged, user sees friendly message)

**User-Friendly Messages**:
- Database errors: "Unable to load data. Please try again in a moment."
- Authentication errors: "Your session has expired. Please log in again."
- Validation errors: "Please check your input and try again."
- Generic errors: "Something went wrong. Our team has been notified."
