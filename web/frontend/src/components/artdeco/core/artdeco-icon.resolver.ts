export interface ArtDecoIconDefinition {
  path: string
  viewBox?: string
  decorative?: boolean
}

type ArtDecoIconMap = Record<string, ArtDecoIconDefinition>

const ICON_ALIASES: Record<string, string> = {
  activity: 'Activity',
  'alert-circle': 'Alert',
  'bar-chart-3': 'BarChart3',
  bookmark: 'Bookmark',
  briefcase: 'Briefcase',
  'chevron-left': 'ChevronLeft',
  clock: 'Clock',
  'dollar-sign': 'DollarSign',
  refresh: 'Refresh',
  trophy: 'Trophy',
  'trending-up': 'TrendingUp',
  'wifi-off': 'WifiOff',
}

const missingIconWarnings = new Set<string>()

export const FALLBACK_ICON_NAME = 'Alert'

const toPascalCase = (name: string): string =>
  name
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
    .join('')

export const resolveArtDecoIconKey = (iconMap: ArtDecoIconMap, rawName: string): string => {
  if (iconMap[rawName]) {
    return rawName
  }

  const normalized = rawName.trim().toLowerCase()
  const alias = ICON_ALIASES[normalized]
  if (alias && iconMap[alias]) {
    return alias
  }

  const pascal = toPascalCase(rawName)
  if (iconMap[pascal]) {
    return pascal
  }

  if (!missingIconWarnings.has(rawName)) {
    console.warn(`ArtDecoIcon: Icon "${rawName}" not found, fallback to "${FALLBACK_ICON_NAME}"`)
    missingIconWarnings.add(rawName)
  }

  return FALLBACK_ICON_NAME
}
