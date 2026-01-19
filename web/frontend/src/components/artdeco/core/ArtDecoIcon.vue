<template>
  <component
    :is="iconComponent"
    class="artdeco-icon"
    :class="[`artdeco-icon--${size}`, { 'artdeco-icon--spin': spin }]"
    :style="{ color: computedColor }"
    v-bind="iconProps"
  />
</template>

<script setup lang="ts">
import { computed, h } from 'vue'

/**
 * ArtDecoIcon - ArtDeco风格SVG图标组件
 *
 * 替换emoji图标，提供专业的金融/数据图标
 *
 * @example
 * <ArtDecoIcon name="Market" size="md" />
 * <ArtDecoIcon name="Realtime" color="#D4AF37" />
 */

// Props定义
interface Props {
  /** 图标名称（从ICON_MAP中选择） */
  name: string
  /** 图标尺寸 */
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  /** 图标颜色（CSS颜色值或ArtDeco颜色变量） */
  color?: string
  /** 是否旋转动画 */
  spin?: boolean
  /** 图标变体风格 */
  variant?: 'outline' | 'filled' | 'duotone' | 'decorative'
  /** 图标线条粗细 */
  weight?: 'light' | 'regular' | 'bold'
  /** 是否添加ArtDeco风格的动画 */
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  color: undefined,
  spin: false,
  variant: 'outline', // Default to outline
  weight: 'regular',  // Default to regular
  animated: false
})

// 计算颜色
const computedColor = computed(() => {
  if (!props.color) {
    return 'var(--artdeco-gold-primary, #D4AF37)'
  }
  return props.color
})

// SVG图标映射（使用Heroicons/Lucide风格的路径）
const ICON_MAP: Record<string, { path: string; viewBox?: string; decorative?: boolean }> = {
  // ========== 市场行情 ==========
  Market: {
    path: 'M3 3v18h18 M3 13l4-4 4 4 6-6 4 4',
    viewBox: '0 0 24 24',
    decorative: true // Mark as decorative to allow special rendering
  },
  Realtime: {
    path: 'M13 2L3 14h9l-1 8 10-12h-9l1-8z',
    viewBox: '0 0 24 24',
    decorative: true
  },
  Technical: {
    path: 'M3 3v18h18 M18 9l-5 5-4-4-3 3',
    viewBox: '0 0 24 24'
  },
  FundFlow: {
    path: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6',
    viewBox: '0 0 24 24'
  },
  ETF: {
    path: 'M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5',
    viewBox: '0 0 24 24'
  },
  Concept: {
    path: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z',
    viewBox: '0 0 24 24'
  },
  Auction: {
    path: 'M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z',
    viewBox: '0 0 24 24'
  },
  LongHuBang: {
    path: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
    viewBox: '0 0 24 24'
  },
  Institution: {
    path: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
    viewBox: '0 0 24 24'
  },
  Wencai: {
    path: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z',
    viewBox: '0 0 24 24'
  },
  Screener: {
    path: 'M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z',
    viewBox: '0 0 24 24'
  },

  // ========== 股票管理 ==========
  StockManagement: {
    path: 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z',
    viewBox: '0 0 24 24'
  },
  Portfolio: {
    path: 'M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z M13 7v6h8a9 9 0 11-8-8z',
    viewBox: '0 0 24 24'
  },
  Watchlist: {
    path: 'M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z',
    viewBox: '0 0 24 24'
  },
  Activity: {
    path: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
    viewBox: '0 0 24 24'
  },
  StrategySelection: {
    path: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01',
    viewBox: '0 0 24 24'
  },
  IndustrySelection: {
    path: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
    viewBox: '0 0 24 24'
  },
  ConceptSelection: {
    path: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
    viewBox: '0 0 24 24'
  },

  // ========== 投资分析 ==========
  Analysis: {
    path: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z M10 7l3 3 3-3',
    viewBox: '0 0 24 24'
  },
  TechnicalAnalysis: {
    path: 'M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z',
    viewBox: '0 0 24 24'
  },
  Fundamental: {
    path: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    viewBox: '0 0 24 24'
  },
  Indicator: {
    path: 'M12 2a10 10 0 1010 10A10 10 0 0012 2zm0 18a8 8 0 118-8 8 8 0 01-8 8zm1-13h-2v6l5.2 3.2.8-1.3-4-2.4V7z',
    viewBox: '0 0 24 24'
  },
  CustomIndicator: {
    path: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
    viewBox: '0 0 24 24'
  },
  StockAnalysis: {
    path: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
    viewBox: '0 0 24 24'
  },
  ListAnalysis: {
    path: 'M4 6h16M4 10h16M4 14h16M4 18h16',
    viewBox: '0 0 24 24'
  },

  // ========== 风险管理 ==========
  RiskManagement: {
    path: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
    viewBox: '0 0 24 24'
  },
  Alert: {
    path: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9',
    viewBox: '0 0 24 24'
  },
  RiskIndicators: {
    path: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
    viewBox: '0 0 24 24'
  },
  Sentiment: {
    path: 'M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z',
    viewBox: '0 0 24 24'
  },
  PositionRisk: {
    path: 'M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z',
    viewBox: '0 0 24 24'
  },
  FactorAnalysis: {
    path: 'M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z M13 7v6h8',
    viewBox: '0 0 24 24'
  },

  // ========== 策略和交易管理 ==========
  StrategyTrading: {
    path: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6',
    viewBox: '0 0 24 24'
  },
  StrategyDesign: {
    path: 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z',
    viewBox: '0 0 24 24'
  },
  StrategyManagement: {
    path: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
    viewBox: '0 0 24 24'
  },
  Backtest: {
    path: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
    viewBox: '0 0 24 24'
  },
  GPUBacktest: {
    path: 'M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z',
    viewBox: '0 0 24 24'
  },
  Signals: {
    path: 'M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0',
    viewBox: '0 0 24 24'
  },
  TradeHistory: {
    path: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
    viewBox: '0 0 24 24'
  },
  Positions: {
    path: 'M4 6h16M4 10h16M4 14h16M4 18h16',
    viewBox: '0 0 24 24'
  },
  Attribution: {
    path: 'M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z',
    viewBox: '0 0 24 24'
  },

  // ========== 系统监控 ==========
  SystemMonitoring: {
    path: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
    viewBox: '0 0 24 24'
  },
  Monitoring: {
    path: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
    viewBox: '0 0 24 24'
  },
  Settings: {
    path: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
    viewBox: '0 0 24 24'
  },
  DataUpdate: {
    path: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15',
    viewBox: '0 0 24 24'
  },
  DataQuality: {
    path: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    viewBox: '0 0 24 24'
  },
  APIHealth: {
    path: 'M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01',
    viewBox: '0 0 24 24'
  },

  // ========== 通用图标 ==========
  Home: {
    path: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
    viewBox: '0 0 24 24'
  },
  ChevronRight: {
    path: 'M9 5l7 7-7 7',
    viewBox: '0 0 24 24'
  },
  ChevronDown: {
    path: 'M19 9l-7 7-7-7',
    viewBox: '0 0 24 24'
  },
  ChevronUp: {
    path: 'M5 15l7-7 7 7',
    viewBox: '0 0 24 24'
  },
  Search: {
    path: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z',
    viewBox: '0 0 24 24'
  },
  Bell: {
    path: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9',
    viewBox: '0 0 24 24'
  },
  User: {
    path: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
    viewBox: '0 0 24 24'
  },
  Logout: {
    path: 'M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1',
    viewBox: '0 0 24 24'
  }
}

// 计算图标组件和属性
const iconComponent = computed(() => {
  const icon = ICON_MAP[props.name]
  if (!icon) {
    console.warn(`ArtDecoIcon: Icon "${props.name}" not found`)
    return null
  }

  // Stroke Width based on weight
  let strokeWidth = '2'
  if (props.weight === 'light') {
    strokeWidth = '1.5'
  } else if (props.weight === 'bold') {
    strokeWidth = '2.5'
  }

  // Stroke Linecap and Linejoin for Art Deco aesthetic
  let strokeLinecap: 'round' | 'square' | 'butt' = 'square'
  let strokeLinejoin: 'round' | 'miter' | 'bevel' = 'miter'

  // SVG filters for glow effect
  const filters: any[] = []
  if (props.animated || props.variant === 'decorative') {
    filters.push(h('filter', { id: 'gold-glow' }, [
      h('feGaussianBlur', { stdDeviation: '1.5', result: 'blur' }),
      h('feFlood', { floodColor: 'var(--artdeco-gold-primary)', result: 'color' }),
      h('feComposite', { in: 'color', in2: 'blur', operator: 'in', result: 'shadow' }),
      h('feComposite', { in: 'SourceGraphic', in2: 'shadow', operator: 'over' })
    ]))
  }

  // Decorative variant specific rendering
  if (props.variant === 'decorative' && icon.decorative) {
    return {
      render() {
        return h('svg', {
          viewBox: icon.viewBox || '0 0 24 24',
          fill: 'none',
          stroke: 'currentColor', // Main path color
          'stroke-width': strokeWidth,
          'stroke-linecap': strokeLinecap,
          'stroke-linejoin': strokeLinejoin,
          class: { 'artdeco-icon--animated': props.animated },
          filter: props.animated ? 'url(#gold-glow)' : undefined
        }, [
          h('defs', filters),
          h('rect', {
            x: '2', y: '2', width: '20', height: '20',
            fill: 'none',
            stroke: 'var(--artdeco-gold-primary)',
            'stroke-width': '0.5',
            'stroke-dasharray': '2 2',
            opacity: '0.5'
          }),
          h('path', {
            d: icon.path,
            stroke: 'currentColor',
            filter: props.animated ? 'url(#gold-glow)' : undefined // Apply glow to path as well
          }),
          // Decorative circles
          h('circle', { cx: '7', cy: '9', r: '1', fill: 'var(--artdeco-gold-primary)' }),
          h('circle', { cx: '11', cy: '13', r: '1', fill: 'var(--artdeco-gold-primary)' }),
          h('circle', { cx: '15', cy: '17', r: '1', fill: 'var(--artdeco-gold-primary)' })
        ])
      }
    }
  }

  return {
    render() {
      return h('svg', {
        viewBox: icon.viewBox || '0 0 24 24',
        fill: props.variant === 'filled' ? 'currentColor' : 'none',
        stroke: props.variant === 'filled' ? 'none' : 'currentColor',
        'stroke-width': strokeWidth,
        'stroke-linecap': strokeLinecap,
        'stroke-linejoin': strokeLinejoin,
        class: { 'artdeco-icon--animated': props.animated },
        filter: props.animated ? 'url(#gold-glow)' : undefined
      }, [
        h('defs', filters),
        h('path', {
          d: icon.path
        })
      ])
    }
  }
})

const iconProps = computed(() => {
  const icon = ICON_MAP[props.name]
  return {
    viewBox: icon?.viewBox || '0 0 24 24'
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.artdeco-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  // SVG样式
  svg {
    width: 100%;
    height: 100%;
    stroke: currentColor;
  }

  // 尺寸变体
  &--xs {
    width: 14px;
    height: 14px;
  }

  &--sm {
    width: 16px;
    height: 16px;
  }

  &--md {
    width: 20px;
    height: 20px;
  }

  &--lg {
    width: 24px;
    height: 24px;
  }

  &--xl {
    width: 32px;
    height: 32px;
  }

  // 旋转动画
  &--spin {
    animation: artdeco-icon-spin 1s linear infinite;
  }

  // 悬停效果
  &:hover {
    opacity: 0.8;
    transition: opacity 150ms ease;
  }
}

@keyframes artdeco-icon-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
