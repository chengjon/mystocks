import { dataApi } from '@/api/index.ts'

import type { CachedData, DataRoute } from './TradingApiManager.types.ts'
import { DataClassification } from './TradingApiManager.types.ts'

type SaveBatchDataOptions = {
  database: 'tdengine' | 'postgresql'
  useExecuteValues?: boolean
  compression?: boolean
  useUpsert?: boolean
  conflictColumns?: string[]
  updateColumns?: string[]
}

type SaveBatchDataResult = { success: boolean }
type DataApiCompat = typeof dataApi & {
  saveBatchData?: (table: string, data: unknown, options: SaveBatchDataOptions) => Promise<SaveBatchDataResult>
  queryTimeSeries?: (table: string, filters: unknown) => Promise<unknown>
  queryRelational?: (table: string, filters: unknown) => Promise<unknown>
}

const dataApiCompat = dataApi as DataApiCompat

const realtimeService = {
  connect(channel: string, _callback: Function): void {
    console.warn(`[TradingApiManager.data-flow] realtimeService unavailable for channel: ${channel}`)
  },
  disconnect(_channel: string): void {
    // No-op fallback while realtime service is absent from the current API surface.
  },
}

function isRecordArray(data: unknown): data is Array<Record<string, unknown>> {
  return Array.isArray(data) && data.every((item) => typeof item === 'object' && item !== null)
}

export class DataFlowManager {
  private cache = new Map<string, CachedData>()
  private realtimeConnections = new Set<string>()

  async saveData(classification: DataClassification, data: unknown): Promise<boolean> {
    const route = this.getDataRoute(classification)
    return await this.saveToDatabase(route.database, data, route.table)
  }

  async loadData(classification: DataClassification, filters: Record<string, unknown> = {}): Promise<unknown> {
    const route = this.getDataRoute(classification)
    const cacheKey = `${classification}-${JSON.stringify(filters)}`
    const cached = this.cache.get(cacheKey)

    if (cached && !this.isExpired(cached)) {
      return cached.data
    }

    const data = await this.loadFromDatabase(route.database, route.table, filters)

    this.cache.set(cacheKey, {
      data,
      timestamp: Date.now(),
      ttl: 300000
    })

    return data
  }

  private getDataRoute(classification: DataClassification): DataRoute {
    const routes: Record<DataClassification, DataRoute> = {
      [DataClassification.TICK_DATA]: { database: 'tdengine', table: 'tick_data' },
      [DataClassification.MINUTE_KLINE]: { database: 'tdengine', table: 'minute_kline' },
      [DataClassification.DAILY_KLINE]: { database: 'postgresql', table: 'daily_kline' },
      [DataClassification.SYMBOLS_INFO]: { database: 'postgresql', table: 'symbols_info' },
      [DataClassification.INDUSTRY_CLASS]: { database: 'postgresql', table: 'industry_class' },
      [DataClassification.CONCEPT_CLASS]: { database: 'postgresql', table: 'concept_class' },
      [DataClassification.TECHNICAL_INDICATORS]: { database: 'postgresql', table: 'technical_indicators' },
      [DataClassification.QUANT_FACTORS]: { database: 'postgresql', table: 'quant_factors' },
      [DataClassification.TRADE_SIGNALS]: { database: 'postgresql', table: 'trade_signals' },
      [DataClassification.ORDER_RECORDS]: { database: 'postgresql', table: 'order_records' },
      [DataClassification.TRADE_RECORDS]: { database: 'postgresql', table: 'trade_records' },
      [DataClassification.POSITION_HISTORY]: { database: 'postgresql', table: 'position_history' },
      [DataClassification.USER_CONFIG]: { database: 'postgresql', table: 'user_config' },
      [DataClassification.SYSTEM_CONFIG]: { database: 'postgresql', table: 'system_config' },
      [DataClassification.DATA_QUALITY_METRICS]: { database: 'postgresql', table: 'data_quality_metrics' },
      [DataClassification.STRATEGY_PARAMS]: { database: 'postgresql', table: 'strategy_params' }
    }

    return routes[classification] || { database: 'postgresql', table: 'default' }
  }

  private async saveToDatabase(database: string, data: unknown, table: string): Promise<boolean> {
    try {
      if (database === 'tdengine') {
        return await this.saveToTDengine(data, table)
      }

      return await this.saveToPostgreSQL(data, table)
    } catch (error) {
      console.error(`Failed to save to ${database}:`, error)
      return false
    }
  }

  private async loadFromDatabase(database: string, table: string, filters: unknown): Promise<unknown> {
    if (database === 'tdengine') {
      return await this.loadFromTDengine(table, filters)
    }

    return await this.loadFromPostgreSQL(table, filters)
  }

  private async saveToTDengine(data: unknown, table: string): Promise<boolean> {
    if (!dataApiCompat.saveBatchData) {
      console.warn(`[TradingApiManager.data-flow] saveBatchData unavailable for TDengine table: ${table}`)
      return false
    }

    const result = await dataApiCompat.saveBatchData(table, data, {
      database: 'tdengine',
      useExecuteValues: true,
      compression: true
    })

    return result.success
  }

  private async saveToPostgreSQL(data: unknown, table: string): Promise<boolean> {
    if (!dataApiCompat.saveBatchData) {
      console.warn(`[TradingApiManager.data-flow] saveBatchData unavailable for PostgreSQL table: ${table}`)
      return false
    }

    const updateColumns = isRecordArray(data)
      ? Object.keys(data[0] ?? {}).filter((key) => key !== 'id')
      : []

    const result = await dataApiCompat.saveBatchData(table, data, {
      database: 'postgresql',
      useUpsert: true,
      conflictColumns: ['id'],
      updateColumns
    })

    return result.success
  }

  private async loadFromTDengine(table: string, filters: unknown): Promise<unknown> {
    if (!dataApiCompat.queryTimeSeries) {
      console.warn(`[TradingApiManager.data-flow] queryTimeSeries unavailable for table: ${table}`)
      return []
    }

    return await dataApiCompat.queryTimeSeries(table, filters)
  }

  private async loadFromPostgreSQL(table: string, filters: unknown): Promise<unknown> {
    if (!dataApiCompat.queryRelational) {
      console.warn(`[TradingApiManager.data-flow] queryRelational unavailable for table: ${table}`)
      return []
    }

    return await dataApiCompat.queryRelational(table, filters)
  }

  private isExpired(cached: CachedData): boolean {
    return Date.now() - cached.timestamp > cached.ttl
  }

  setupRealtimeUpdates(channel: string, callback: Function): () => void {
    if (!this.realtimeConnections.has(channel)) {
      realtimeService.connect(channel, callback)
      this.realtimeConnections.add(channel)
    }

    return () => {
      realtimeService.disconnect(channel)
      this.realtimeConnections.delete(channel)
    }
  }
}
