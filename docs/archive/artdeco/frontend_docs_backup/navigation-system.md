# Advanced Navigation System Documentation

## Overview

The MyStocks frontend implements a comprehensive navigation system with domain-driven routing, responsive design, and accessibility features. This document covers the navigation architecture, components, and usage guidelines.

## Architecture

### Domain-Driven Navigation Structure

```
Frontend Navigation System
├── Layout Layer
│   ├── ArtDecoBaseLayout.vue (Base layout with navigation)
│   ├── TradingLayout.vue (Trading domain)
│   ├── RiskLayout.vue (Risk management domain)
│   ├── SettingsLayout.vue (System settings domain)
│   └── MainLayout.vue (General pages)
├── Navigation Components
│   ├── BreadcrumbNav.vue (Breadcrumb navigation)
│   ├── DynamicSidebar.vue (Domain-based sidebar)
│   └── CommandPalette.vue (Ctrl+K search)
└── State Management
    ├── Sidebar collapse/expand
    ├── Mobile overlay handling
    └── Keyboard navigation
```

### Supported Domains

| Domain | Layout | Routes | Features |
|--------|--------|--------|----------|
| **Trading** | TradingLayout | `/trading/*` | Order management, positions, execution |
| **Risk** | RiskLayout | `/risk/*` | Risk monitoring, alerts, portfolio risk |
| **Settings** | SettingsLayout | `/settings/*` | General, theme, notifications, security |
| **Market** | MainLayout | `/market/*` | Real-time quotes, technical analysis |
| **Stocks** | MainLayout | `/stocks/*` | Watchlists, portfolios, screener |
| **Strategy** | StrategyLayout | `/strategy/*` | Backtesting, strategy management |

## Components

### ArtDecoBaseLayout

The foundation layout component that provides:

- **Top Bar**: Page title, breadcrumb navigation, search, notifications, user menu
- **Sidebar**: Domain-specific navigation menu with collapse/expand
- **Main Content**: Router-view for page content
- **Mobile Overlay**: Touch-friendly navigation on mobile devices

#### Props

```typescript
interface ArtDecoBaseLayoutProps {
  pageTitle?: string        // Page title in header
  menuItems: MenuItem[]     // Navigation menu items
}

interface MenuItem {
  path: string              // Route path
  label: string             // Display label
  icon: string              // Icon emoji/identifier
  badge?: string | number   // Optional badge
}
```

#### Features

- **Responsive Design**: Adapts from mobile (320px) to 4K displays
- **Keyboard Navigation**: Ctrl+B (sidebar), Ctrl+K (search), Escape (close)
- **Analytics Integration**: Google Analytics event tracking
- **Error Handling**: Graceful fallbacks for navigation errors
- **Performance**: Memoized computed properties, lazy loading

### BreadcrumbNav

Automatic breadcrumb generation from Vue Router paths.

```vue
<template>
  <BreadcrumbNav :items="breadcrumbItems" />
</template>
```

#### Features

- **Auto-generation**: Creates breadcrumbs from route segments
- **Custom Labels**: Supports route meta `breadcrumb` property
- **Accessibility**: Proper ARIA labels and semantic HTML
- **Error Recovery**: Fallback to basic navigation on errors

### DynamicSidebar

Domain-aware sidebar with module switching.

```vue
<template>
  <DynamicSidebar />
</template>
```

#### Features

- **Module Switching**: Switch between domains (Market, Stocks, etc.)
- **Context Awareness**: Shows relevant menu items per domain
- **State Persistence**: Remembers collapse/expand state
- **TypeScript Support**: Full type safety with Vue 3 Composition API

### CommandPalette

Global search and navigation (Ctrl+K).

#### Features

- **Fuzzy Search**: Fast search through all navigation items
- **Keyboard Navigation**: Arrow keys, Enter to navigate
- **Recent Commands**: History of recently used commands
- **Analytics**: Tracks search and navigation events

## Usage Guidelines

### Adding New Routes

1. **Choose Domain Layout**: Select appropriate layout based on functionality
2. **Add Route Configuration**: Update `router/index.ts` with proper meta
3. **Update Menu Config**: Add to domain-specific menu configuration
4. **Test Navigation**: Verify breadcrumbs and sidebar behavior

```typescript
// Example: Adding trading route
{
  path: '/trading/orders',
  component: () => import('@/views/trading/Orders.vue'),
  meta: {
    title: 'Order Management',
    icon: '📋',
    breadcrumb: 'Orders'  // Custom breadcrumb label
  }
}
```

### Menu Configuration

Update `MenuConfig.ts` for domain-specific menus:

```typescript
export const TRADING_MENU_ITEMS = [
  { path: '/trading/orders', label: 'Orders', icon: '📋' },
  { path: '/trading/positions', label: 'Positions', icon: '📊' },
  { path: '/trading/history', label: 'History', icon: '📈' }
]
```

### Responsive Breakpoints

| Breakpoint | Behavior |
|------------|----------|
| `< 768px` | Mobile overlay, full sidebar width |
| `768px - 1024px` | Tablet overlay, adaptive sidebar |
| `> 1024px` | Desktop inline, collapsible sidebar |
| `> 1920px` | Large screen, expanded sidebar |

## Keyboard Shortcuts

| Shortcut | Action | Context |
|----------|--------|---------|
| `Ctrl+B` / `Cmd+B` | Toggle sidebar | Global |
| `Ctrl+K` / `Cmd+K` | Open command palette | Global |
| `Escape` | Close mobile sidebar | Mobile only |
| `↑/↓` | Navigate palette items | Command palette |
| `Enter` | Select palette item | Command palette |

## Accessibility

### WCAG 2.1 AA Compliance

- **Keyboard Navigation**: All interactive elements keyboard accessible
- **Screen Readers**: Proper ARIA labels and semantic HTML
- **Focus Management**: Logical tab order and focus indicators
- **Color Contrast**: Minimum 4.5:1 contrast ratio
- **Touch Targets**: Minimum 44px touch targets on mobile

### ARIA Implementation

```vue
<!-- Breadcrumb navigation -->
<nav class="breadcrumb-nav" aria-label="Breadcrumb">
  <ol class="breadcrumb-list">
    <li class="breadcrumb-item">
      <router-link :to="item.path" class="breadcrumb-link">
        {{ item.label }}
      </router-link>
    </li>
  </ol>
</nav>

<!-- Sidebar toggle -->
<button
  class="sidebar-toggle"
  @click="toggleSidebar"
  :aria-expanded="!sidebarCollapsed"
  aria-label="Toggle sidebar"
>
  ☰
</button>
```

## Performance Optimizations

### Memoization

```typescript
const breadcrumbItems = computed(() => {
  // Expensive breadcrumb generation
  // Result cached until dependencies change
  return generateBreadcrumbs(route.path)
})
```

### Lazy Loading

```typescript
const commandItems = computed(() => {
  // Lazy evaluation of command items
  return menuItems.value.map(item => ({
    ...item,
    action: () => router.push(item.path)
  }))
})
```

### Error Boundaries

```typescript
const breadcrumbItems = computed(() => {
  try {
    return generateBreadcrumbs(route.path)
  } catch (error) {
    console.warn('Breadcrumb error:', error)
    return [{ label: 'Home', path: '/' }] // Fallback
  }
})
```

## Analytics Integration

### Event Tracking

```typescript
const onCommandPaletteOpen = () => {
  // Google Analytics event
  gtag('event', 'command_palette_open', {
    event_category: 'navigation',
    event_label: pageTitle
  })
}
```

### Error Tracking

```typescript
const handleNavigationError = (error: Error) => {
  // Error reporting
  console.error('Navigation error:', error)

  // Analytics error event
  gtag('event', 'navigation_error', {
    event_category: 'error',
    event_label: error.message
  })
}
```

## Testing

### Unit Tests

```typescript
describe('ArtDecoBaseLayout', () => {
  it('toggles sidebar on Ctrl+B', () => {
    // Test keyboard navigation
  })

  it('generates breadcrumbs from route', () => {
    // Test breadcrumb generation
  })

  it('closes sidebar on mobile overlay click', () => {
    // Test mobile interaction
  })
})
```

### E2E Tests

```typescript
test('navigation flow', async ({ page }) => {
  await page.goto('/trading/orders')
  await page.keyboard.press('Control+b') // Toggle sidebar
  await expect(page.locator('.sidebar')).toHaveClass('collapsed')
})
```

## Troubleshooting

### Common Issues

**Sidebar not collapsing:**
- Check `toggleSidebar()` method is called
- Verify CSS transitions are applied
- Check for JavaScript errors in console

**Breadcrumb not updating:**
- Ensure route has proper path segments
- Check for route meta `breadcrumb` property
- Verify `breadcrumbItems` computed property

**Mobile overlay not working:**
- Confirm viewport width detection
- Check CSS media queries
- Verify overlay click handler

**Command palette not opening:**
- Check Ctrl+K event listener
- Verify CommandPalette component is mounted
- Check for z-index conflicts

### Debug Tools

```typescript
// Debug navigation state
console.log('Navigation state:', {
  sidebarCollapsed: sidebarCollapsed.value,
  isMobile: isMobile.value,
  currentRoute: route.path,
  breadcrumbItems: breadcrumbItems.value
})
```

## Migration Guide

### From Old Navigation

1. **Update Layout Usage:**
   ```vue
   <!-- Old -->
   <MainLayout>
     <router-view />
   </MainLayout>

   <!-- New -->
   <ArtDecoBaseLayout :menu-items="MENU_ITEMS" page-title="Dashboard">
     <router-view />
   </ArtDecoBaseLayout>
   ```

2. **Update Route Meta:**
   ```typescript
   // Add breadcrumb support
   meta: {
     title: 'Orders',
     breadcrumb: 'Order Management' // Optional custom label
   }
   ```

3. **Update Menu Configuration:**
   ```typescript
   // Move to MenuConfig.ts
   export const TRADING_MENU_ITEMS = [
     { path: '/trading/orders', label: 'Orders', icon: '📋' }
   ]
   ```

## Future Enhancements

- **Advanced Command Palette**: AI-powered search suggestions
- **Navigation History**: Recently visited pages
- **Customizable Shortcuts**: User-defined keyboard shortcuts
- **Voice Navigation**: Voice-activated navigation commands
- **Gesture Support**: Touch gestures for mobile navigation