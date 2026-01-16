# Type Safety Generation Specification

## ADDED Requirements

### Requirement: Pydantic Model to TypeScript Generation

**Requirement**: Backend Pydantic models MUST automatically generate TypeScript types.

#### Scenario: Model Definition
**GIVEN** a Pydantic model is defined in the backend
**WHEN** the type generation script runs
**THEN** a corresponding TypeScript interface MUST be generated:

```python
# Backend: web/backend/app/schemas/market_schemas.py
class MarketIndexData(BaseModel):
    name: str
    current: float
    change: float
    change_percent: float
    volume: Optional[float] = None
```

```typescript
// Generated: web/frontend/src/api/types.ts
export interface MarketIndexData {
  name: string
  current: number
  change: number
  change_percent: number
  volume?: number | null
}
```

### Requirement: Type Naming Convention

**Requirement**: Generated TypeScript types MUST follow consistent naming conventions.

#### Scenario: PascalCase Conversion
**GIVEN** a Python class name in PascalCase
**WHEN** generating TypeScript types
**THEN** the TypeScript interface SHALL use the same PascalCase name:
- `MarketOverviewResponse` → `MarketOverviewResponse`
- `FundFlowItem` → `FundFlowItem`
- `StockSearchResult` → `StockSearchResult`

#### Scenario: Snake Case to CamelCase
**GIVEN** Python fields in snake_case
**WHEN** generating TypeScript types
**THEN** the TypeScript properties SHALL be in camelCase:
- `market_index` → `marketIndex`
- `change_percent` → `changePercent`
- `trade_date` → `tradeDate`

### Requirement: Type Mapping Rules

**Requirement**: Python types MUST be correctly mapped to TypeScript types.

#### Scenario: Primitive Types
**GIVEN** Python primitive types
**WHEN** generating TypeScript types
**THEN** they SHALL map as follows:
- `str` → `string`
- `int` → `number`
- `float` → `number`
- `bool` → `boolean`
- `None` → `null`

#### Scenario: Complex Types
**GIVEN** Python complex types
**WHEN** generating TypeScript types
**THEN** they SHALL map as follows:
- `List[T]` → `T[]`
- `Optional[T]` → `T | null`
- `Union[T, U]` → `T | U`
- `Dict[K, V]` → `Record<K, V>`
- `datetime` → `string` (ISO 8601)
- `date` → `string` (ISO 8601 date)
- `Decimal` → `string` (to preserve precision)

### Requirement: Nested Type Generation

**Requirement**: Nested Pydantic models MUST generate nested TypeScript interfaces.

#### Scenario: Nested Model
**GIVEN** a Pydantic model with nested models
**WHEN** generating TypeScript types
**THEN** nested interfaces SHALL be generated separately:

```python
class OrderResponse(BaseModel):
    order_id: str
    symbol: str
    status: OrderStatus
    details: OrderDetails

class OrderDetails(BaseModel):
    price: float
    quantity: int
    side: str
```

```typescript
export interface OrderResponse {
  order_id: string
  symbol: string
  status: OrderStatus
  details: OrderDetails
}

export interface OrderDetails {
  price: number
  quantity: number
  side: string
}
```

### Requirement: Enum Generation

**Requirement**: Python enums MUST generate TypeScript string literal unions.

#### Scenario: Enum Definition
**GIVEN** a Python Enum class
**WHEN** generating TypeScript types
**THEN** a string literal union MUST be generated:

```python
class OrderStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
```

```typescript
export type OrderStatus = "pending" | "filled" | "cancelled" | "rejected"
```

### Requirement: API Response Type Generation

**Requirement**: API response wrapper types MUST be generated for all endpoints.

#### Scenario: Response Wrapper
**GIVEN** an API endpoint with a Pydantic response model
**WHEN** generating TypeScript types
**THEN** a wrapped response type MUST be generated:

```python
@router.get("/market/overview", response_model=APIResponse[MarketOverviewResponse])
async def get_market_overview():
    pass
```

```typescript
export interface MarketOverviewResponseWrapper {
  success: boolean
  code: number
  message: string
  data?: MarketOverviewResponse
  request_id: string
  timestamp: string
}
```

### Requirement: Type Generation Pipeline

**Requirement**: Type generation MUST be automated and integrated into the build process.

#### Scenario: CI/CD Integration
**GIVEN** a change to Pydantic models
**WHEN** the CI pipeline runs
**THEN** TypeScript types MUST be automatically regenerated
**AND** the build SHALL fail if type generation fails.

#### Scenario: Development Workflow
**GIVEN** a developer modifies a Pydantic model
**WHEN** they run the dev server
**THEN** TypeScript types MUST be automatically regenerated
**AND** type errors MUST be immediately visible in the IDE.
