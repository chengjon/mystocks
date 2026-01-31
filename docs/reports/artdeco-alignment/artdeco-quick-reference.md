# ArtDeco Alignment Quick Reference

**Status**: 79% → 93% alignment achievable
**Effort**: 10 hours total
**Priority**: P0 (5h) > P1 (3h) > P2 (2h)

---

## 🔴 P0 Critical Fixes (5 hours)

### 1. Update Color Opacity (15 min)
**File**: `artdeco-tokens.scss`

```scss
// BEFORE
--artdeco-bg-base: #141414;
--artdeco-fg-muted: #888888;
--artdeco-border-default: rgba(212, 175, 55, 0.2);
--artdeco-border-hover: rgba(212, 175, 55, 0.5);

// AFTER
--artdeco-bg-base: #1E1E1E;
--artdeco-bg-elevated: #242424;
--artdeco-fg-muted: #A0A0A0;
--artdeco-border-default: rgba(212, 175, 55, 0.3);
--artdeco-border-hover: rgba(212, 175, 55, 1);
```

### 2. Strengthen Background Patterns (15 min)
**File**: `artdeco-global.scss`

```scss
// Crosshatch (line 68, 75)
rgba(212, 175, 55, 0.05)  // Was 0.02

// Sunburst (line 321-323)
rgba(212, 175, 55, 0.15) 0%,   // Was 0.1
rgba(212, 175, 55, 0.08) 25%,  // Was 0.05
rgba(212, 175, 55, 0.03) 50%,  // Was 0.02
```

### 3. Fix ArtDecoButton (2h)
**File**: `base/ArtDecoButton.vue`

```vue
<style scoped>
.artdeco-button {
  min-height: 48px;           /* ENFORCE */
  text-transform: uppercase;   /* ENFORCE */
  letter-spacing: 0.2em;       /* ENFORCE */
  border-width: 2px;           /* ENFORCE */
}
</style>
```

### 4. Fix ArtDecoInput (2h)
**File**: `base/ArtDecoInput.vue`

```vue
<style scoped>
.artdeco-input {
  background: transparent;
  border: none;
  border-bottom: 2px solid #D4AF37;  /* BOTTOM ONLY */
  min-height: 48px;
}

.artdeco-input:focus {
  border-bottom-color: #F2E8C4;  /* BRIGHTEN */
  box-shadow: 0 4px 10px rgba(212, 175, 55, 0.2);
}
</style>
```

### 5. Enhance ArtDecoCard (1h)
**File**: `base/ArtDecoCard.vue`

```vue
<template>
  <div class="artdeco-card artdeco-corner-brackets">
    <!-- Content -->
  </div>
</template>
```

---

## ⚠️ P1 High Priority (3 hours)

### 6. Add Missing Colors (15 min)
**File**: `artdeco-tokens.scss`

```scss
--artdeco-midnight-blue: #1E3D59;
--artdeco-pewter: #6B7280;
--artdeco-pewter-light: #9CA3AF;
--artdeco-gold-secondary: #C9A962;
```

### 7. Enforce Double Borders (1h)

Apply to: `ArtDecoCard`, `ArtDecoDialog`, `ArtDecoAlert`

```vue
<div class="artdeco-card artdeco-border-double">
  <!-- Content -->
</div>
```

### 8. Strengthen Glows (1h)

Verify glows on:
- Buttons (hover)
- Cards (hover)
- Inputs (focus)
- Active nav items

```scss
box-shadow: var(--artdeco-glow-intense);
```

### 9. Container Widths (30 min)
**File**: `artdeco-tokens.scss`

```scss
--artdeco-container-5xl: 64rem;   // Hero
--artdeco-container-6xl: 72rem;   // Primary
--artdeco-container-7xl: 80rem;   // Wide grids
```

---

## 💡 P2 Enhancements (2 hours)

### 10. Diamond Icon Containers (1h)

```vue
<template>
  <div class="artdeco-diamond-container">
    <div class="artdeco-diamond-content">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.artdeco-diamond-container {
  width: 64px;
  height: 64px;
  transform: rotate(45deg);
  border: 2px solid var(--artdeco-gold-primary);
}

.artdeco-diamond-content {
  transform: rotate(-45deg);
}
</style>
```

### 11. Section Divider (30 min)

New component: `ArtDecoSectionDivider.vue`

```vue
<template>
  <div class="artdeco-section-divider">
    <div class="artdeco-divider-line"></div>
    <h2><slot /></h2>
    <div class="artdeco-divider-line"></div>
  </div>
</template>
```

### 12. Stepped Corners (30 min)

Apply to cards:

```scss
.artdeco-stepped {
  clip-path: polygon(
    0 0, calc(100% - 8px) 0, 100% 8px,
    100% calc(100% - 8px), calc(100% - 8px) 100%,
    8px 100%, 0 calc(100% - 8px)
  );
}
```

---

## Verification Checklist

After P0 implementation:

- [ ] Crosshatch pattern visible (not invisible)
- [ ] Sunburst gradient dramatic (not weak)
- [ ] Buttons: 48px height, uppercase, 0.2em tracking
- [ ] Inputs: Bottom border only, 2px width
- [ ] Cards: 30% → 100% border on hover
- [ ] All glows activate on hover
- [ ] Double borders on dialogs/alerts
- [ ] Contrast ratios 6:1 minimum

---

## Testing Commands

```bash
# Visual regression
npm run test:visual

# Component library
npm run build:components

# Type checking
npm run type-check

# Linting
npm run lint
```

---

## Git Workflow

```bash
# Create branch
git checkout -b artdeco-alignment-p0

# Implement Phase 1 (tokens)
git commit -m "feat(artdeco): strengthen color opacities and patterns"

# Implement Phase 2 (components)
git commit -m "fix(artdeco): enforce P0 component requirements"

# Push for review
git push origin artdeco-alignment-p0
```

---

## Contact

**Questions**: Refer to full report at `/tmp/artdeco-alignment-analysis.md`

**Issues**: Create ticket with prefix `ARTDECO-`

**PR Template**: Include visual regression screenshots
