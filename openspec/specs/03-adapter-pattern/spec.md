# 03-adapter-pattern Specification

## Purpose
TBD - created by archiving change implement-api-web-alignment. Update Purpose after archive.
## Requirements
### Requirement: Data Adapter Interface

**Requirement**: All data transformations between API and UI MUST use adapter classes.

#### Scenario: Data Transformation
**GIVEN** raw API response data (DTO)
**WHEN** preparing data for UI components
**THEN** it MUST be transformed through an adapter:

```typescript
// WRONG: Direct transformation in component
const data = await api.getMarketOverview()
const uiData = {
  indices: data.market_index.map(item => ({
    name: item.name,
    value: item.current,
    change: item.change_percent + '%'
  }))
}

// RIGHT: Using adapter
const rawData = await api.getMarketOverview()
const uiData = DataAdapter.toMarketOverviewVM(rawData)
```

### Requirement: ViewModel Interface Definition

**Requirement**: Each UI component MUST have a corresponding ViewModel interface.

#### Scenario: Component Props
**GIVEN** a Vue component receives data
**WHEN** defining its props
**THEN** it MUST use a ViewModel type, not the API type:

```typescript
// ViewModel type for UI consumption
export interface MarketOverviewVM {
  indices: IndexItemVM[]
  sectors: SectorItemVM[]
  marketSentiment: 'bullish' | 'bearish' | 'neutral'
  lastUpdate: string
}

// API type (DO NOT use directly in components)
export interface MarketOverviewResponse {
  market_index: MarketIndexData[]
  hot_sectors: SectorData[]
  market_metrics: MarketMetrics
}
```

### Requirement: Adapter Method Naming Convention

**Requirement**: Adapter methods MUST follow consistent naming conventions.

#### Scenario: Method Naming
**GIVEN** an adapter class
**WHEN** defining transformation methods
**THEN** they SHALL be named `to[ViewModelName]`:
- `toMarketOverviewVM()`
- `toFundFlowChart()`
- `toKLineData()`
- `toStrategyListItemVM()`

#### Scenario: Static vs Instance
**GIVEN** stateless transformation logic
**WHEN** implementing adapters
**THEN** methods SHOULD be static to avoid unnecessary instantiation:

```typescript
export class DataAdapter {
  static toMarketOverviewVM(data: MarketOverviewResponse): MarketOverviewVM {
    // Stateless transformation
  }
}
```

### Requirement: Data Formatting Rules

**Requirement**: Common data formatting MUST be centralized in adapters.

#### Scenario: Number Formatting
**GIVEN** numerical data needs formatting
**WHEN** transforming in adapters
**THEN** use standardized formatting methods:

```typescript
private static formatPercent(value: number): string {
  return `${(value * 100).toFixed(2)}%`
}

private static formatVolume(value: number): string {
  if (value >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`
  } else if (value >= 10000) {
    return `${(value / 10000).toFixed(2)}万`
  }
  return value.toString()
}
```

#### Scenario: Date Formatting
**GIVEN** date/time data
**WHEN** transforming for UI
**THEN** consistent date formats MUST be used:
- Display dates: `YYYY-MM-DD HH:mm:ss`
- Chart dates: `YYYY-MM-DD`
- Relative times: "2小时前", "刚刚"

### Requirement: Error Handling in Adapters

**Requirement**: Adapters MUST handle missing or invalid data gracefully.

#### Scenario: Missing Fields
**GIVEN** API response with optional fields
**WHEN** transforming in adapter
**THEN** default values MUST be provided:

```typescript
static toStockItem(data: StockData): StockItemVM {
  return {
    symbol: data.symbol || '',
    name: data.name || '未知',
    price: data.current_price || 0,
    change: data.change || 0,
    // Provide defaults for all fields
    trend: data.change > 0 ? 'up' : data.change < 0 ? 'down' : 'flat',
    volume: data.volume ? this.formatVolume(data.volume) : '--'
  }
}
```

### Requirement: Adapter Composition

**Requirement**: Complex transformations MUST use adapter composition for maintainability.

#### Scenario: Composite Data
**GIVEN** data from multiple API endpoints
**WHEN** creating a composite ViewModel
**THEN** use adapter composition:

```typescript
class DashboardAdapter {
  static toDashboardVM(
    marketData: MarketResponse,
    portfolioData: PortfolioResponse,
    alertData: AlertResponse
  ): DashboardVM {
    return {
      market: DataAdapter.toMarketOverviewVM(marketData),
      portfolio: PortfolioAdapter.toPortfolioVM(portfolioData),
      alerts: AlertAdapter.toAlertListVM(alertData),
      lastUpdate: new Date().toISOString()
    }
  }
}
```

### Requirement: Performance Optimization

**Requirement**: Adapters MUST be optimized for performance.

#### Scenario: Large Data Sets
**GIVEN** large datasets to transform
**WHEN** implementing adapters
**THEN** use efficient transformation methods:
- Use `Array.map()` instead of `for` loops
- Avoid unnecessary object creation
- Memoize expensive calculations

```typescript
// Memoization for expensive transformations
private static priceFormatter = new Intl.NumberFormat('zh-CN', {
  style: 'currency',
  currency: 'CNY'
})

static toPrice(value: number): string {
  return this.priceFormatter.format(value)
}
```

### Requirement: Test Coverage

**Requirement**: All adapter methods MUST have unit tests.

#### Scenario: Unit Testing
**GIVEN** an adapter method
**WHEN** writing tests
**THEN** test cases MUST cover:
- Normal data transformation
- Edge cases (null, undefined, empty values)
- Format validation
- Performance with large datasets

```typescript
describe('DataAdapter', () => {
  it('should transform market overview correctly', () => {
    const mockData = { /* mock API response */ }
    const result = DataAdapter.toMarketOverviewVM(mockData)

    expect(result.indices).toHaveLength(mockData.market_index.length)
    expect(result.marketSentiment).toBe('bullish')
  })

  it('should handle missing data gracefully', () => {
    const incompleteData = { market_index: [] }
    const result = DataAdapter.toMarketOverviewVM(incompleteData)

    expect(result.indices).toEqual([])
    expect(result.marketSentiment).toBe('neutral')
  })
})
```

