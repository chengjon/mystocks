export type StrategyLifecycleAction = "start" | "pause" | "resume" | "stop"

const SUPPORTED_STRATEGY_LIFECYCLE_ACTIONS = new Set<StrategyLifecycleAction>([
  "start",
  "pause",
  "resume",
  "stop",
])

export function supportsStrategyLifecycleAction(action: StrategyLifecycleAction): boolean {
  return SUPPORTED_STRATEGY_LIFECYCLE_ACTIONS.has(action)
}
