# Change Tasks: Web Design System Comprehensive Update V2.0

## 1. Design System Foundation (Phase 0)

### 1.1 Color System V3.0 Implementation
- [ ] 1.1.1 Update SCSS tokens with ArtDeco gold palette
  - `--artdeco-gold: #D4AF37` (main brand color)
  - `--artdeco-gold-light: #F0E68C` (hover/highlight)
  - `--artdeco-bronze: #CD7F32` (secondary accent)
  - `--artdeco-champagne: #F7E7CE` (soft backgrounds)
- [ ] 1.1.2 Update financial data colors for A股 convention
  - `--color-rise: #00C853` (up - green)
  - `--color-fall: #FF1744` (down - red)
  - `--color-warning: #D4AF37` (warning - reuse brand gold)
- [ ] 1.1.3 Update background and text colors
  - `--color-bg-primary: #1A1A1D` (charcoal gray)
  - `--color-bg-card: #2A2A2E` (card background)
  - `--color-text-primary: #FFFFFF` (pure white)
- [ ] 1.1.4 Add ArtDeco geometric decoration colors
  - `--artdeco-border-gold: #D4AF37`
  - `--artdeco-accent-1: #4A90E2`
  - `--artdeco-accent-2: #E94B3C`

### 1.2 Typography System Implementation
- [ ] 1.2.1 Add font imports to global styles
  - Cinzel (display/headers)
  - Barlow (body text)
  - JetBrains Mono (numbers/code)
- [ ] 1.2.2 Define font variables
  - `--font-display: 'Cinzel', serif`
  - `--font-body: 'Barlow', sans-serif`
  - `--font-mono: 'JetBrains Mono', monospace`
- [ ] 1.2.3 Apply typography to components
  - Headers: Cinzel, 600 weight, uppercase
  - Body: Barlow, 400 weight
  - Prices/numbers: JetBrains Mono, tabular-nums

### 1.3 Animation System Implementation
- [ ] 1.3.1 Create page load animations
  - `@keyframes artdeco-page-load` (fade in + slide up)
  - Staggered card loading delays
- [ ] 1.3.2 Create button hover effects
  - Gold radial gradient expansion
  - Smooth transition states
- [ ] 1.3.3 Create card hover effects
  - Gold glow box-shadow
  - Subtle lift transform
- [ ] 1.3.4 Create data update flash animation
  - `@keyframes data-update-flash` (gold tint)
  - Apply to real-time data changes
- [ ] 1.3.5 Create tab switching animation
  - Gold slider transition
  - Smooth position animation
- [ ] 1.3.6 Create loading spinner
  - ArtDeco square loader (not round)
  - Golden border animation

### 1.4 ECharts ArtDeco Theme
- [ ] 1.4.1 Configure ECharts color palette
  - ArtDeco gold as primary
  - Coordinated accent colors
- [ ] 1.4.2 Configure chart typography
  - JetBrains Mono for axis labels
  - Barlow for legends
- [ ] 1.4.3 Configure grid and axis styles
  - Minimalist grid lines
  - Gold axis lines

## 2. Rapid Optimization (Phase 1)

### 2.1 Color System Upgrade
- [ ] 2.1.1 Update main navigation with gold accents
  - Gold logo/header text
  - Gold bottom border for active items
- [ ] 2.1.2 Update CTA buttons to gold variant
  - Primary buttons: gold background
  - Consistent with ArtDeco branding
- [ ] 2.1.3 Update card components
  - Gold border accents
  - Geometric corner decorations

### 2.2 Navigation Simplification
- [ ] 2.2.1 Restructure top navigation to 3 core workflows
  - Trading workflow (trade decisions)
  - Analysis workflow (backtesting/research)
  - Portfolio workflow (holdings/performance)
- [ ] 2.2.2 Add keyboard shortcuts documentation
- [ ] 2.2.3 Update CommandPalette integration

### 2.3 Compact Table Mode
- [ ] 2.3.1 Implement 32px row height option
  - Bloomberg Terminal standard density
  - Toggle between standard/compact modes
- [ ] 2.3.2 Optimize cell padding and spacing
- [ ] 2.3.3 Ensure readability at compact density

### 2.4 Dashboard Transformation
- [ ] 2.4.1 Transform to task-card layout
  - Clear action-oriented cards
  - Prioritized by user workflow
- [ ] 2.4.2 Add quick action buttons to cards
- [ ] 2.4.3 Implement drag-and-drop reordering

## 3. Core Function Integration (Phase 2)

### 3.1 Trading Decision Center
- [ ] 3.1.1 Design single-page layout
  - All trading info on one page
  - Reduce 75% page jumps
- [ ] 3.1.2 Integrate market data panel
  - Real-time quotes
  - Technical indicators
- [ ] 3.1.3 Integrate order entry panel
  - Buy/sell forms
  - Position management
- [ ] 3.1.4 Integrate portfolio summary
  - Current positions
  - P&L overview

### 3.2 Backtesting Workflow
- [ ] 3.2.1 Implement wizard-style interface
  - Step-by-step configuration
  - Clear progress indicators
- [ ] 3.2.2 Add parameter comparison feature
  - Side-by-side results view
  - Performance metrics comparison
- [ ] 3.2.3 Create strategy templates
  - Pre-configured common strategies
  - Easy customization

### 3.3 Sidebar Enhancement
- [ ] 3.3.1 Implement collapsible sidebar
  - Save screen space
  - Smooth animation
- [ ] 3.3.2 Add ArtDeco gold dividers
  - Geometric separators
  - Consistent with design language
- [ ] 3.3.3 Optimize icon sizing and spacing

## 4. Experience Enhancement (Phase 3)

### 4.1 ECharts Theme Integration
- [ ] 4.1.1 Apply ArtDeco theme to 7 chart types
  - K-line charts
  - Fund flow charts
  - Technical indicator charts
  - Portfolio distribution charts
  - Performance trend charts
  - Heat maps
  - Radar charts
- [ ] 4.1.2 Add chart-specific customizations
  - Financial data formatting
  - Tooltip styling
  - Legend styling

### 4.2 Data Density Optimization
- [ ] 4.2.1 Implement Bloomberg-standard layout
  - Information-dense displays
  - Professional trading workspace
- [ ] 4.2.2 Add data density toggle
  - Standard/compact/dense modes
  - User preference persistence
- [ ] 4.2.3 Optimize mobile responsiveness
  - Breakpoint handling
  - Layout adjustments

### 4.3 Animation System Rollout
- [ ] 4.3.1 Apply page transitions
  - Route transitions
  - Modal animations
- [ ] 4.3.2 Apply data update animations
  - Price change highlighting
  - Order status updates
- [ ] 4.3.3 Apply interaction feedback
  - Form validation
  - Button states
  - Error/success states

## 5. Testing & Validation

### 5.1 Design Verification
- [ ] 5.1.1 Verify ArtDeco gold usage ratio (+200%)
- [ ] 5.1.2 Verify typography system implementation
- [ ] 5.1.3 Verify animation effects (6 types)
- [ ] 5.1.4 Verify data density (32px rows)

### 5.2 Performance Testing
- [ ] 5.2.1 Measure page load time (< 2s)
- [ ] 5.2.2 Measure animation frame rate (> 60fps)
- [ ] 5.2.3 Check for layout shifts
- [ ] 5.2.4 Verify no performance regressions

### 5.3 Compatibility Testing
- [ ] 5.3.1 Verify all existing components functional
- [ ] 5.3.2 Verify no breaking API changes
- [ ] 5.3.3 Test responsive design (1440px+)
- [ ] 5.3.4 Cross-browser testing

## 6. Documentation

### 6.1 Design System Documentation
- [ ] 6.1.1 Document color system with usage examples
- [ ] 6.1.2 Document typography with application rules
- [ ] 6.1.3 Document animation system with timing
- [ ] 6.1.4 Document component styling patterns

### 6.2 Migration Guide
- [ ] 6.2.1 Create migration guide from V1 to V2
- [ ] 6.2.2 Document deprecated patterns
- [ ] 6.2.3 Provide before/after code examples

## 7. Deployment Preparation

### 7.1 Code Review Checklist
- [ ] 7.1.1 Review all design token changes
- [ ] 7.1.2 Review typography application
- [ ] 7.1.3 Review animation implementations
- [ ] 7.1.4 Review performance impact

### 7.2 Staged Rollout Plan
- [ ] 7.2.1 Phase 0 rollout (design tokens)
- [ ] 7.2.2 Phase 1 rollout (colors, navigation)
- [ ] 7.2.3 Phase 2 rollout (core functions)
- [ ] 7.2.4 Phase 3 rollout (animations, polish)

### 7.3 Rollback Strategy
- [ ] 7.3.1 Document CSS variable fallbacks
- [ ] 7.3.2 Prepare feature flag for major changes
- [ ] 7.3.3 Define rollback triggers and procedure
