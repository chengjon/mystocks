import type { NormalizedDataSourceConfigItem } from "./dataManagementData"

interface DataSourceConfigBatchUpdate {
  operations: Array<{
    action: "update"
    endpoint_name: string
    updates: {
      status: "active" | "maintenance"
    }
  }>
}

export function supportsDataSourceConfigWrite(): boolean {
  return true
}

export function buildDataSourceConfigBatchRequest(
  currentItems: NormalizedDataSourceConfigItem[],
  originalItems: NormalizedDataSourceConfigItem[],
): DataSourceConfigBatchUpdate {
  const originalByEndpoint = new Map(originalItems.map((item) => [item.endpointName, item]))

  const operations = currentItems.flatMap((item) => {
    const original = originalByEndpoint.get(item.endpointName)
    if (!original || original.enabled === item.enabled) {
      return []
    }

    return [{
      action: "update" as const,
      endpoint_name: item.endpointName,
      updates: {
        status: item.enabled ? "active" as const : "maintenance" as const,
      },
    }]
  })

  return { operations }
}
