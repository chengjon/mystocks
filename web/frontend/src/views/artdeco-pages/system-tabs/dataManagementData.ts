interface DataSourceConfigItemLike {
  description?: unknown
  endpoint_name?: unknown
  name?: unknown
  source_name?: unknown
  enabled?: unknown
  status?: unknown
  endpoint?: unknown
  url?: unknown
}

export interface NormalizedDataSourceConfigItem {
  endpointName: string
  name: string
  enabled: boolean
  endpoint: string
  status: string
}

function toItem(item: DataSourceConfigItemLike): NormalizedDataSourceConfigItem {
  const status = typeof item.status === "string" && item.status ? item.status : item.enabled === false ? "maintenance" : "active"
  return {
    endpointName:
      (typeof item.endpoint_name === "string" && item.endpoint_name) ||
      (typeof item.name === "string" && item.name) ||
      (typeof item.source_name === "string" && item.source_name) ||
      "unknown.endpoint",
    name:
      (typeof item.name === "string" && item.name) ||
      (typeof item.description === "string" && item.description) ||
      (typeof item.source_name === "string" && item.source_name) ||
      "Unknown",
    enabled: status === "active",
    endpoint:
      (typeof item.endpoint === "string" && item.endpoint) ||
      (typeof item.url === "string" && item.url) ||
      (typeof item.endpoint_name === "string" && item.endpoint_name) ||
      "N/A",
    status,
  }
}

export function extractDataSourceConfigItems(payload: unknown): NormalizedDataSourceConfigItem[] {
  if (Array.isArray(payload)) {
    return payload.map((item) => toItem((item ?? {}) as DataSourceConfigItemLike))
  }

  if (payload && typeof payload === "object") {
    const candidate = payload as {
      data?: unknown
      endpoints?: unknown
    }

    if (Array.isArray(candidate.data)) {
      return candidate.data.map((item) => toItem((item ?? {}) as DataSourceConfigItemLike))
    }

    if (Array.isArray(candidate.endpoints)) {
      return candidate.endpoints.map((item) => toItem((item ?? {}) as DataSourceConfigItemLike))
    }
  }

  return []
}
