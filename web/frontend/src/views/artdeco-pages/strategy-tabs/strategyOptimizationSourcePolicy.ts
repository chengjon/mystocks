export type OptimizationDataSource = "real" | "mock" | "unavailable"

export function shouldUseOptimizationMockFallback(isEmbedded: boolean): boolean {
  return isEmbedded
}

export function canWritebackOptimizationRow(source: OptimizationDataSource): boolean {
  return source === "real"
}

export function formatOptimizationSourceLabel(source: OptimizationDataSource): string {
  if (source === "mock") {
    return "EMBEDDED-MOCK"
  }

  if (source === "unavailable") {
    return "REAL-OFFLINE"
  }

  return "REAL"
}
