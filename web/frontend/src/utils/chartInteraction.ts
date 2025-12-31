/**
 * Chart Interaction Utilities
 *
 * Provides utilities for managing chart interactions including crosshairs,
 * zooming, and other interactive features.
 */

import type { Chart, Coordinate, Point } from '@/types/klinecharts'

/**
 * Crosshair information
 */
export interface CrosshairInfo {
  x: number
  y: number
  visible: boolean
  timestamp?: number
  price?: number
}

/**
 * Chart interaction configuration
 */
export interface ChartInteractionConfig {
  enableCrosshair: boolean
  enableZoom: boolean
  enableScroll: boolean
  crosshairColor?: string
  crosshairWidth?: number
}

/**
 * Default configuration
 */
export const DEFAULT_CONFIG: ChartInteractionConfig = {
  enableCrosshair: true,
  enableZoom: true,
  enableScroll: true,
  crosshairColor: '#888888',
  crosshairWidth: 1,
}

/**
 * Chart Interaction Manager
 */
export class ChartInteractionManager {
  private chart: Chart | null = null
  private config: ChartInteractionConfig

  constructor(config: ChartInteractionConfig = DEFAULT_CONFIG) {
    this.config = { ...DEFAULT_CONFIG, ...config }
  }

  setChart(chart: Chart): void {
    this.chart = chart
  }

  getChart(): Chart | null {
    return this.chart
  }

  destroy(): void {
    this.chart = null
  }
}

/**
 * Crosshair Manager
 */
export class CrosshairManager {
  private chart: Chart | null = null
  private info: CrosshairInfo = {
    x: 0,
    y: 0,
    visible: false,
  }

  constructor(chart?: Chart) {
    if (chart) {
      this.chart = chart
    }
  }

  setChart(chart: Chart): void {
    this.chart = chart
  }

  update(info: Partial<CrosshairInfo>): void {
    this.info = { ...this.info, ...info }
  }

  getCrosshairInfo(): CrosshairInfo {
    return { ...this.info }
  }

  show(): void {
    this.info.visible = true
  }

  hide(): void {
    this.info.visible = false
  }

  isVisible(): boolean {
    return this.info.visible
  }
}

/**
 * Create chart interaction manager
 */
export function createChartInteraction(
  config?: ChartInteractionConfig
): ChartInteractionManager {
  return new ChartInteractionManager(config)
}

/**
 * Create crosshair manager
 */
export function createCrosshairManager(chart?: Chart): CrosshairManager {
  return new CrosshairManager(chart)
}
