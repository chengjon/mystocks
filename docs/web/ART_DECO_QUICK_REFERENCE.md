# Art Deco Quick Reference Guide
## MyStocks 装饰艺术快速参考手册

**Last Updated**: 2025-12-30

---

## TL;DR - Essential Commands

### Import Components

```typescript
import { ArtDecoButton, ArtDecoCard, ArtDecoInput } from '@/components/artdeco'
```

### Import Styles

```scss
@import '@/styles/artdeco-tokens.scss';
@import '@/styles/artdeco-patterns.scss';
```

### Quick Component Usage

```vue
<template>
  <!-- Button -->
  <ArtDecoButton variant="solid" @click="handleAction">
    Click Me
  </ArtDecoButton>

  <!-- Card -->
  <ArtDecoCard title="TITLE" subtitle="Description">
    <p>Content goes here</p>
  </ArtDecoCard>

  <!-- Input -->
  <ArtDecoInput v-model="text" label="LABEL" placeholder="Enter text" />
</template>
```

---

## Color Palette

### Primary Colors

```scss
var(--artdeco-bg-primary)      // #0A0A0A - Obsidian Black
var(--artdeco-bg-card)         // #141414 - Rich Charcoal
var(--artdeco-accent-gold)     // #D4AF37 - Metallic Gold ⭐
var(--artdeco-fg-primary)      // #F2F0E4 - Champagne Cream
var(--artdeco-fg-muted)        // #888888 - Pewter
```

### Market Colors (A-Share Convention)

```scss
var(--artdeco-color-up)        // #FF5252 - Red (涨)
var(--artdeco-color-down)      // #00E676 - Green (跌)
var(--artdeco-color-flat)      // #B0B3B8 - Gray (平)
```

---

## Typography

### Font Families

```scss
font-family: var(--artdeco-font-display);  // Marcellus (headings)
font-family: var(--artdeco-font-body);     // Josefin Sans (body)
```

### Heading Rules (MANDATORY)

```scss
// All headings MUST be:
text-transform: uppercase;                    // All caps
letter-spacing: var(--artdeco-tracking-widest); // 0.2em
color: var(--artdeco-accent-gold);            // Gold
```

### Font Sizes

```scss
--artdeco-text-6xl: 60px;   // H1
--artdeco-text-4xl: 36px;   // H2
--artdeco-text-2xl: 24px;   // H3
--artdeco-text-base: 16px;  // Body
```

---

## Common Patterns

### Background with Crosshatch

```scss
.hero-section {
  @include artdeco-crosshatch-bg();
}
```

### Card with Corner Brackets

```scss
.my-card {
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-gold-subtle);
  @include artdeco-corner-brackets(8px, 16px, 2px);
}
```

### Gold Glow on Hover

```scss
.button {
  transition: all var(--artdeco-duration-base);

  &:hover {
    @include artdeco-glow(var(--artdeco-glow-md));
  }
}
```

### Section Divider

```scss
.section-header {
  @include artdeco-section-divider(96px, 1px);
}
```

---

## Component API Reference

### ArtDecoButton

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | `'default' \| 'solid' \| 'outline'` | `'default'` | Button style |
| size | `'sm' \| 'md' \| 'lg'` | `'md'` | Button size |
| disabled | `boolean` | `false` | Disabled state |
| block | `boolean` | `false` | Full width |

```vue
<ArtDecoButton variant="solid" size="lg" block>
  Primary Action
</ArtDecoButton>
```

### ArtDecoCard

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| title | `string` | `''` | Card title (display font) |
| subtitle | `string` | `''` | Card subtitle (muted) |
| hoverable | `boolean` | `true` | Enable hover lift effect |
| clickable | `boolean` | `false` | Make card clickable |

```vue
<ArtDecoCard
  title="MARKET OVERVIEW"
  subtitle="Real-time data"
  hoverable
  @click="handleCardClick"
>
  <p>Card content here</p>
  <template #footer>
    <ArtDecoButton>View Details</ArtDecoButton>
  </template>
</ArtDecoCard>
```

### ArtDecoInput

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| modelValue | `string \| number` | `''` | Input value (v-model) |
| label | `string` | `''` | Uppercase label |
| placeholder | `string` | `''` | Placeholder text |
| type | `string` | `'text'` | Input type |
| disabled | `boolean` | `false` | Disabled state |
| required | `boolean` | `false` | Show asterisk |
| errorMessage | `string` | `''` | Error message (red) |
| helperText | `string` | `''` | Helper text (gray) |

```vue
<ArtDecoInput
  v-model="username"
  label="USERNAME"
  placeholder="Enter your username"
  required
  helperText="Must be at least 3 characters"
/>
```

---

## Utility Classes

### Text Colors

```html
<div class="text-artdeco-gold">Gold text</div>
<div class="text-artdeco-cream">Primary text</div>
<div class="text-artdeco-muted">Muted text</div>
```

### Background Colors

```html
<div class="bg-artdeco-primary">Black background</div>
<div class="bg-artdeco-card">Charcoal background</div>
```

### Typography

```html
<h1 class="font-artdeco-display">TITLE</h1>
<p class="font-artdeco-body">Body text</p>
```

### Borders & Glows

```html
<div class="border-artdeco-gold">Gold border</div>
<div class="artdeco-glow">Gold glow effect</div>
<div class="artdeco-glow-hover">Glow on hover</div>
```

---

## Design Rules (MANDATORY)

### 1. Headings

✅ **CORRECT:**
```scss
h1 {
  font-family: var(--artdeco-font-display);
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: var(--artdeco-accent-gold);
}
```

❌ **WRONG:**
```scss
h1 {
  font-family: 'Arial', sans-serif;
  text-transform: capitalize;
  letter-spacing: normal;
  color: #FFF;
}
```

### 2. Borders

✅ **CORRECT:**
```scss
.card {
  border: 1px solid var(--artdeco-border-gold-subtle);
  border-radius: 0; // Sharp corners
}
```

❌ **WRONG:**
```scss
.card {
  border: 1px solid #333;
  border-radius: 8px; // No rounded corners!
}
```

### 3. Backgrounds

✅ **CORRECT:**
```scss
body {
  @include artdeco-crosshatch-bg();
  background-color: var(--artdeco-bg-primary);
}
```

❌ **WRONG:**
```scss
body {
  background-color: #000;
  // Missing diagonal crosshatch pattern!
}
```

### 4. Buttons

✅ **CORRECT:**
```vue
<ArtDecoButton variant="solid">
  SUBMIT
</ArtDecoButton>
```

❌ **WRONG:**
```vue
<button class="el-button">Submit</button>
// Use ArtDecoButton instead!
```

---

## Common Tasks

### Add a New Page with Art Deco Styling

```vue
<template>
  <div class="page-container">
    <!-- Page header with section divider -->
    <div class="page-header">
      <h1>PAGE TITLE</h1>
      <p class="subtitle">Page description here</p>
    </div>

    <!-- Content with Art Deco cards -->
    <ArtDecoCard title="SECTION I" subtitle="First section">
      <p>Content goes here</p>
    </ArtDecoCard>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';
@import '@/styles/artdeco-patterns.scss';

.page-container {
  @include artdeco-crosshatch-bg();
  padding: var(--artdeco-spacing-6);
}

.page-header {
  @include artdeco-section-divider(120px, 1px);
  text-align: center;
  margin-bottom: var(--artdeco-spacing-8);
}

h1 {
  font-family: var(--artdeco-font-display);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-widest);
  color: var(--artdeco-accent-gold);
}

.subtitle {
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-body);
}
</style>
```

### Create an Art Deco Table

```vue
<template>
  <ArtDecoCard title="DATA TABLE">
    <table class="artdeco-table">
      <thead>
        <tr>
          <th>Column I</th>
          <th>Column II</th>
          <th>Column III</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.col1 }}</td>
          <td>{{ item.col2 }}</td>
          <td>{{ item.col3 }}</td>
        </tr>
      </tbody>
    </table>
  </ArtDecoCard>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.artdeco-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--artdeco-font-body);

  th {
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
    color: var(--artdeco-accent-gold);
    border-bottom: 2px solid var(--artdeco-border-gold);
    padding: var(--artdeco-spacing-3);
    text-align: left;
  }

  td {
    color: var(--artdeco-fg-primary);
    border-bottom: 1px solid var(--artdeco-border-gold-muted);
    padding: var(--artdeco-spacing-3);
  }

  tr:hover td {
    background: rgba(212, 175, 55, 0.05);
  }
}
</style>
```

### Add Glow Effect to Elements

```scss
// Method 1: Using mixin
.highlight-box {
  @include artdeco-glow(var(--artdeco-glow-base));
}

// Method 2: Using utility class
<div class="artdeco-glow">Content</div>

// Method 3: Custom glow
.custom-glow {
  box-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
}
```

---

## Troubleshooting

### Fonts Not Loading

**Problem**: Marcellus or Josefin Sans not displaying

**Solution**:
1. Check browser console for network errors
2. Verify `artdeco-global.scss` is imported in `main.js`
3. Check internet connection (Google Fonts requires CDN)
4. Fallback to system fonts if blocked

### Colors Not Applied

**Problem**: Art Deco colors not showing

**Solution**:
1. Verify CSS custom properties are loaded: `getComputedStyle(document.documentElement).getPropertyValue('--artdeco-accent-gold')`
2. Check `artdeco-global.scss` import order (must be first)
3. Clear browser cache and rebuild: `npm run dev`

### Corner Brackets Not Visible

**Problem**: L-shaped corners not displaying

**Solution**:
1. Ensure parent has `position: relative`
2. Check `z-index` (brackets might be behind content)
3. Verify contrast against background
4. Increase border width if needed

---

## Best Practices

### DO's ✅

- Use ArtDecoButton, ArtDecoCard, ArtDecoInput components
- Apply `artdeco-crosshatch-bg()` to main containers
- Make headings uppercase with 0.2em tracking
- Use gold accent color sparingly but decisively
- Add corner brackets to cards and containers
- Include glow effects on interactive elements
- Maintain sharp corners (0px or 2px max radius)
- Test contrast ratios (minimum 7:1 for gold on black)

### DON'Ts ❌

- Don't use rounded corners (> 2px)
- Don't use drop shadows (use glow effects instead)
- Don't use lowercase for headings (must be uppercase)
- Don't use blue/purple/green for accents (gold only)
- Don't skip diagonal crosshatch background
- Don't use system fonts for headings (use Marcellus)
- Don't mix Art Deco with other design systems
- Don't override Art Deco tokens without good reason

---

## Resources

### Full Documentation
- [Art Deco Implementation Report](./ART_DECO_IMPLEMENTATION_REPORT.md)

### Design Specification
- `/opt/iflow/myhtml/prompts/ArtDeco.md`

### Component Files
- `/opt/claude/mystocks_spec/web/frontend/src/components/artdeco/`

### Style Files
- `/opt/claude/mystocks_spec/web/frontend/src/styles/artdeco-*.scss`

---

## Quick Copy-Paste Snippets

### Button Group

```vue
<ArtDecoButton variant="outline">Cancel</ArtDecoButton>
<ArtDecoButton variant="solid">Confirm</ArtDecoButton>
```

### Form Input

```vue
<ArtDecoInput
  v-model="formData.email"
  label="EMAIL ADDRESS"
  type="email"
  placeholder="user@example.com"
  required
  :error-messages="errors.email"
/>
```

### Stats Card

```vue
<ArtDecoCard :hoverable="false">
  <div class="stat-value">1,234</div>
  <div class="stat-label">TOTAL STOCKS</div>
</ArtDecoCard>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.stat-value {
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-4xl);
  color: var(--artdeco-accent-gold);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-widest);
}

.stat-label {
  color: var(--artdeco-fg-muted);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
  font-size: var(--artdeco-text-sm);
}
</style>
```

---

**End of Quick Reference**

For detailed implementation guide, see [ART_DECO_IMPLEMENTATION_REPORT.md](./ART_DECO_IMPLEMENTATION_REPORT.md)
