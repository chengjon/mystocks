<template>
  <nav 
    class="artdeco-sidebar-v3" 
    :class="{ 'is-collapsed': preferenceStore.sidebarCollapsed }"
  >
    <!-- Background Layer -->
    <div class="sidebar-bg-pattern"></div>

    <!-- Top Section: Brand -->
    <div class="sidebar-brand">
      <router-link to="/dashboard" class="brand-link">
        <div class="brand-icon-frame">
          <span class="brand-text">{{ preferenceStore.sidebarCollapsed ? 'MS' : 'MYSTOCKS' }}</span>
        </div>
      </router-link>
    </div>

    <!-- Navigation Body -->
    <div class="sidebar-nav-container">
      <div 
        v-for="domain in menus" 
        :key="domain.businessKey"
        class="nav-domain-group"
      >
        <!-- Domain Title (Visible only when expanded) -->
        <div v-if="!preferenceStore.sidebarCollapsed" class="domain-divider">
          <span class="domain-label">{{ domain.label }}</span>
          <div class="domain-line"></div>
        </div>

        <!-- Domain Root (Toggle for Children) -->
        <button
          class="nav-item domain-root"
          :class="{ 'is-active': isDomainActive(domain) }"
          @click="toggleDomain(domain.path)"
          :aria-expanded="expandedDomains[domain.path] ? 'true' : 'false'"
          :aria-controls="`domain-menu-${domain.path}`"
          type="button"
        >
          <ArtDecoIcon :name="domain.icon" size="sm" class="nav-icon" />
          <span v-if="!preferenceStore.sidebarCollapsed" class="nav-label">{{ domain.label }}</span>
          <ArtDecoIcon
            v-if="!preferenceStore.sidebarCollapsed && domain.children"
            :name="expandedDomains[domain.path] ? 'ChevronUp' : 'ChevronDown'"
            size="xs"
            class="arrow-icon"
          />
        </button>

        <!-- Sub Items -->
        <transition name="slide-fade">
          <div
            v-show="expandedDomains[domain.path] && !preferenceStore.sidebarCollapsed"
            class="nav-children"
            :id="`domain-menu-${domain.path}`"
          >
            <router-link
              v-for="child in domain.children"
              :key="child.path"
              :to="child.path"
              class="nav-item child-item"
              active-class="is-active"
            >
              <ArtDecoIcon :name="child.icon" size="xs" class="nav-icon" />
              <span class="nav-label">{{ child.label }}</span>
              <ArtDecoBadge v-if="child.badge" :text="String(child.badge)" size="sm" />
            </router-link>
          </div>
        </transition>
      </div>
    </div>

    <!-- Bottom Section: Actions & Signature -->
    <div class="sidebar-footer">
      <button class="collapse-toggle" @click="preferenceStore.toggleSidebar" aria-label="Toggle sidebar">
        <ArtDecoIcon :name="preferenceStore.sidebarCollapsed ? 'ChevronRight' : 'ChevronLeft'" size="xs" />
      </button>
      <div v-if="!preferenceStore.sidebarCollapsed" class="footer-signature">
        <span class="sig-text">AD v3.2 ELITE</span>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { reactive, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { usePreferenceStore } from '@/stores/preferenceStore'
import ArtDecoIcon from '../core/ArtDecoIcon.vue'
import ArtDecoBadge from '../base/ArtDecoBadge.vue'
import type { MenuItem } from '@/layouts/MenuConfig'
import { ARTDECO_MENU_ITEMS } from '@/layouts/MenuConfig'

interface Props {
  menus?: MenuItem[]
}

const props = withDefaults(defineProps<Props>(), {
  menus: () => ARTDECO_MENU_ITEMS
})

const route = useRoute()
const preferenceStore = usePreferenceStore()

// State for expanded groups
const expandedDomains = reactive<Record<string, boolean>>({})

// Helper to check if a domain should be active
const isDomainActive = (domain: MenuItem) => {
  return route.path.startsWith(domain.path)
}

// Toggle logic
const toggleDomain = (path: string) => {
  expandedDomains[path] = !expandedDomains[path]
}

// Auto-expand based on route
const syncExpansion = () => {
  props.menus.forEach(menu => {
    if (route.path.startsWith(menu.path)) {
      expandedDomains[menu.path] = true
    }
  })
}

watch(() => route.path, syncExpansion)
onMounted(syncExpansion)

</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.artdeco-sidebar-v3 {
  width: var(--artdeco-sidebar-width);
  height: 100vh;
  background: var(--artdeco-bg-global);
  border-right: 1px solid var(--artdeco-border-default);
  position: fixed;
  left: 0;
  top: 0;
  z-index: var(--artdeco-z-fixed);
  display: flex;
  flex-direction: column;
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;

  &.is-collapsed {
    width: var(--artdeco-sidebar-collapsed-width);
  }
}

.sidebar-bg-pattern {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle at 2px 2px, var(--artdeco-gold-opacity-05) 1px, transparent 0);
  background-size: 24px 24px;
  pointer-events: none;
}

// Brand Section
.sidebar-brand {
  padding: var(--artdeco-spacing-8) 0;
  display: flex;
  justify-content: center;
  border-bottom: 1px solid var(--artdeco-gold-opacity-10);

  .brand-icon-frame {
    border: 2px solid var(--artdeco-gold-primary);
    padding: 8px 12px;
    background: var(--artdeco-gold-opacity-05);
    transition: all 0.3s ease;

    &:hover {
      background: var(--artdeco-gold-opacity-15);
      box-shadow: 0 0 15px var(--artdeco-gold-opacity-shadow);
    }
  }

  .brand-text {
    font-family: Cinzel, serif;
    font-weight: 700;
    color: var(--artdeco-gold-primary);
    letter-spacing: 4px;
    font-size: 1.2rem;
  }
}

// Nav Container
.sidebar-nav-container {
  flex: 1;
  padding: var(--artdeco-spacing-4) var(--artdeco-spacing-3);
  overflow-y: auto;
  scrollbar-width: none;
  &::-webkit-scrollbar { display: none; }
}

.domain-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 24px 0 12px 12px;
  opacity: 60%;

  .domain-label {
    font-family: Barlow, sans-serif;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--artdeco-gold-dim);
    white-space: nowrap;
  }

  .domain-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--artdeco-gold-opacity-30), transparent);
  }
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  margin-bottom: 4px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--artdeco-fg-muted);
  text-decoration: none;

  .nav-icon {
    margin-right: 16px;
    transition: color 0.3s;
  }

  .nav-label {
    font-size: 14px;
    font-weight: 500;
    flex: 1;
    transition: opacity 0.3s;
  }

  .arrow-icon {
    opacity: 50%;
  }

  &:hover {
    background: var(--artdeco-gold-opacity-08);
    color: var(--artdeco-gold-light);

    .nav-icon {
      color: var(--artdeco-gold-primary);
    }
  }

  &.is-active {
    background: linear-gradient(90deg, var(--artdeco-gold-opacity-15), transparent);
    color: var(--artdeco-gold-primary);
    border-left: 3px solid var(--artdeco-gold-primary);

    .nav-icon {
      color: var(--artdeco-gold-primary);
    }

    .nav-label {
      font-weight: 600;
    }
  }
}

.domain-root {
  width: 100%;
  border: none;
  background: transparent;
  font: inherit;
  text-align: left;
}

.child-item {
  padding-left: 44px;
  font-size: 13px;
  opacity: 80%;

  &:hover {
    opacity: 100%;
  }
}

// Footer
.sidebar-footer {
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid var(--artdeco-gold-opacity-10);

  .collapse-toggle {
    background: transparent;
    border: 1px solid var(--artdeco-border-default);
    color: var(--artdeco-gold-primary);
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      background: var(--artdeco-gold-primary);
      color: var(--artdeco-bg-global);
    }
  }

  .footer-signature {
    font-family: Cinzel, serif;
    font-size: 9px;
    color: var(--artdeco-gold-dim);
    letter-spacing: 1px;
  }
}

// Transitions
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0%;
}

// Reduced Motion Support
@media (prefers-reduced-motion: reduce) {
  .artdeco-sidebar-v3,
  .brand-icon-frame,
  .nav-item,
  .collapse-toggle {
    transition: none;
  }

  .slide-fade-enter-active,
  .slide-fade-leave-active {
    transition: none;
  }

  .slide-fade-enter-from,
  .slide-fade-leave-to {
    transform: none;
  }

  // Disable continuous pulse animations
  .sidebar-bg-pattern {
    background-image: none;
  }

  // Disable hover glow effects
  .brand-icon-frame:hover {
    box-shadow: none;
  }
}
</style>
