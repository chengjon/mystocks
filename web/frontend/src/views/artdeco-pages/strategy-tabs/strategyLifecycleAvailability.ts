export type StrategyLifecycleAction = "start" | "pause" | "resume" | "stop"

export function supportsStrategyLifecycleAction(_action: StrategyLifecycleAction): boolean {
  return false
}
