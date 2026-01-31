<template>
  <nav class="artdeco-collapsible-sidebar">
    <!-- Decorative background pattern -->
    <div class="artdeco-sidebar-pattern"></div>

    <!-- Header Section -->
    <div class="artdeco-sidebar-header">
      <!-- Decorative corner ornaments -->
      <div class="artdeco-corner-tl"></div>
      <div class="artdeco-corner-tr"></div>

      <!-- Logo with ArtDeco style -->
      <router-link to="/dashboard" class="artdeco-logo">
        <div class="artdeco-logo-frame">
          <span class="artdeco-logo-text">MYSTOCKS</span>
          <span class="artdeco-logo-subtitle">ArtDeco Edition</span>
        </div>
      </router-link>

      <!-- Decorative divider line with ornament -->
      <div class="artdeco-header-divider">
        <div class="artdeco-divider-ornament"></div>
      </div>
    </div>

    <!-- Navigation Menu -->
    <div class="artdeco-nav">
      <div
        v-for="(menu, index) in menus"
        :key="menu.path"
        class="artdeco-nav-section animate-in"
        :style="{ animationDelay: `${index * 0.1}s` }"
      >
        <!-- Section Header with Icon -->
        <div class="artdeco-nav-section-header">
          <ArtDecoIcon
            :name="menu.icon"
            size="sm"
            class="artdeco-nav-section-icon"
          />
          <div class="artdeco-nav-section-title">{{ menu.label }}</div>
          <div class="artdeco-nav-section-line"></div>
        </div>

        <!-- Parent Menu Item -->
        <router-link
          v-if="!menu.children || menu.children.length === 0"
          :to="menu.path"
          class="artdeco-nav-item"
          active-class="active"
        >
          <ArtDecoIcon :name="menu.icon" size="md" />
          <div class="artdeco-nav-content">
            <div class="artdeco-nav-label">{{ menu.label }}</div>
            <div class="artdeco-nav-subtitle">{{ menu.description }}</div>
          </div>
          <!-- Live Update Indicator -->
          <ArtDecoStatusIndicator
            v-if="menu.liveUpdate"
            status="online"
            :animated="true"
            size="xs"
          />
        </router-link>

        <!-- Collapsible Sub-menu -->
        <template v-else>
          <div
            class="artdeco-nav-item artdeco-nav-item-parent"
            :class="{ expanded: expandedMenus[menu.path] }"
            @click="toggleMenu(menu.path)"
          >
            <ArtDecoIcon :name="menu.icon" size="md" />
            <div class="artdeco-nav-content">
              <div class="artdeco-nav-label">{{ menu.label }}</div>
              <div class="artdeco-nav-subtitle">{{ menu.description }}</div>
            </div>
            <!-- Collapse Icon -->
            <ArtDecoIcon
              :name="expandedMenus[menu.path] ? 'ChevronUp' : 'ChevronDown'"
              size="sm"
            />
          </div>

          <!-- Sub-menu Items -->
          <transition name="slide-fade">
            <div v-show="expandedMenus[menu.path]" class="artdeco-submenu">
              <router-link
                v-for="child in menu.children"
                :key="child.path"
                :to="child.path"
                class="artdeco-nav-item artdeco-nav-item-child"
                active-class="active"
              >
                <ArtDecoIcon :name="child.icon" size="sm" />
                <div class="artdeco-nav-content">
                  <div class="artdeco-nav-label">{{ child.label }}</div>
                  <div class="artdeco-nav-subtitle">{{ child.description }}</div>
                </div>

                <!-- Badge -->
                <ArtDecoBadge
                  v-if="child.badge"
                  :text="String(child.badge)"
                  type="info"
                  size="sm"
                />

                <!-- Live Update Indicator -->
                <ArtDecoStatusIndicator
                  v-if="child.liveUpdate"
                  status="online"
                  :animated="true"
                  size="xs"
                />
              </router-link>
            </div>
          </transition>
        </template>
      </div>
    </div>

    <!-- Footer with decorative element -->
    <div class="artdeco-sidebar-footer">
      <div class="artdeco-footer-ornament">❧</div>
      <div class="artdeco-footer-text">EST. 2025</div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import ArtDecoIcon from '../core/ArtDecoIcon.vue'
import ArtDecoBadge from '../base/ArtDecoBadge.vue'
import ArtDecoStatusIndicator from '../core/ArtDecoStatusIndicator.vue'
import type { MenuItem } from '@/layouts/MenuConfig.enhanced'
import { ARTDECO_MENU_ENHANCED } from '@/layouts/MenuConfig.enhanced'

// Props
interface Props {
  menus?: MenuItem[]
}

const props = withDefaults(defineProps<Props>(), {
  menus: () => ARTDECO_MENU_ENHANCED,
})

// Router
const router = useRouter()

// State
const expandedMenus = reactive<Record<string, boolean>>({})

// 初始化：默认展开当前路由所在的菜单
const initializeExpandedMenus = () => {
  const currentPath = router.currentRoute.value.path

  props.menus.forEach(menu => {
    if (menu.children) {
      // 检查当前路径是否在这个菜单的子菜单中
      const hasActiveChild = menu.children.some(
        child => child.path === currentPath
      )
      if (hasActiveChild) {
        expandedMenus[menu.path] = true
      } else {
        expandedMenus[menu.path] = false
      }
    }
  })
}

// Toggle menu expand/collapse
const toggleMenu = (path: string) => {
  expandedMenus[path] = !expandedMenus[path]
}

// Initialize on mount
initializeExpandedMenus()
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

// ============================================
//   COLLAPSIBLE SIDEBAR CONTAINER
// ============================================
.artdeco-collapsible-sidebar {
  width: 320px;
  background: var(--artdeco-bg-header);
  border-right: 2px solid var(--artdeco-gold-dim);
  position: fixed;
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
  z-index: var(--artdeco-z-fixed);
  transition: transform var(--artdeco-transition-slow);

  // Custom scrollbar
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: var(--artdeco-bg-card);
  }

  &::-webkit-scrollbar-thumb {
    background: var(--artdeco-gold-primary);
    border-radius: 3px;

    &:hover {
      background: var(--artdeco-accent-gold);
    }
  }
}

// Decorative background pattern
.artdeco-sidebar-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 10px,
    rgba(212, 175, 55, 0.02) 10px,
    rgba(212, 175, 55, 0.02) 20px
  );
  pointer-events: none;
  z-index: 0;
}

// ============================================
//   HEADER SECTION
// ============================================
.artdeco-sidebar-header {
  padding: var(--artdeco-spacing-5) var(--artdeco-spacing-4);
  border-bottom: 2px solid rgba(212, 175, 55, 0.2);
  text-align: center;
  position: relative;
  background: var(--artdeco-bg-header);
  z-index: 1;
}

// Decorative corner ornaments
.artdeco-corner-tl,
.artdeco-corner-tr {
  position: absolute;
  width: 30px;
  height: 30px;
  border: 2px solid rgba(212, 175, 55, 0.2);
  pointer-events: none;
}

.artdeco-corner-tl {
  top: 10px;
  left: 10px;
  border-right: none;
  border-bottom: none;
}

.artdeco-corner-tr {
  top: 10px;
  right: 10px;
  border-left: none;
  border-bottom: none;
}

// Logo with frame
.artdeco-logo {
  display: inline-block;
  text-decoration: none;
  position: relative;
  z-index: 1;
  margin-top: var(--artdeco-spacing-2);

  .artdeco-logo-frame {
    border: 2px solid var(--artdeco-accent-gold);
    padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
    background: var(--artdeco-bg-card);
    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.1);
    transition: all var(--artdeco-transition-slow);
  }

  &:hover .artdeco-logo-frame {
    border-color: var(--artdeco-accent-gold);
    box-shadow: var(--artdeco-glow-subtle);
    transform: scale(1.02);
  }

  .artdeco-logo-text {
    font-family: var(--artdeco-font-display);
    font-size: var(--artdeco-text-base);
    font-weight: 700;
    color: var(--artdeco-accent-gold);
    letter-spacing: 0.25em;
    text-transform: uppercase;
    display: block;
    margin-bottom: 4px;
    transition: color var(--artdeco-transition-slow);
    line-height: 1.2;
  }

  &:hover .artdeco-logo-text {
    color: var(--artdeco-accent-gold);
  }

  .artdeco-logo-subtitle {
    font-family: var(--artdeco-font-body);
    font-size: var(--artdeco-text-xs);
    font-weight: 500;
    color: var(--artdeco-fg-muted);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    display: block;
  }
}

// Decorative divider with ornament
.artdeco-header-divider {
  height: 1px;
  background: linear-gradient(
    to right,
    transparent,
    var(--artdeco-accent-gold) 40%,
    var(--artdeco-accent-gold) 60%,
    transparent
  );
  margin: var(--artdeco-spacing-3) auto 0;
  position: relative;
  opacity: 0.6;
}

.artdeco-divider-ornament {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 8px;
  height: 8px;
  background: var(--artdeco-accent-gold);
  transform: translate(-50%, -50%) rotate(45deg);
  box-shadow: 0 0 8px var(--artdeco-accent-gold);
}

// ============================================
//   NAVIGATION MENU
// ============================================
.artdeco-nav {
  padding: var(--artdeco-spacing-4);
  position: relative;
  z-index: 1;
}

.artdeco-nav-section {
  margin-bottom: var(--artdeco-spacing-6);
}

// Section Header with Icon
.artdeco-nav-section-header {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  margin-bottom: var(--artdeco-spacing-3);
  padding-bottom: var(--artdeco-spacing-2);
  border-bottom: 1px solid rgba(212, 175, 55, 0.2);
}

.artdeco-nav-section-icon {
  color: var(--artdeco-accent-gold);
  text-shadow: 0 0 8px rgba(212, 175, 55, 0.3);
}

.artdeco-nav-section-title {
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-xs);
  font-weight: 600;
  color: var(--artdeco-accent-gold);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
  flex: 1;
  opacity: 0.8;
}

.artdeco-nav-section-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(to right, rgba(212, 175, 55, 0.2), transparent);
}

// Navigation Item
.artdeco-nav-item {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-3);
  padding: 16px var(--artdeco-spacing-3);
  color: var(--artdeco-fg-primary);
  text-decoration: none;
  border-left: 3px solid transparent;
  background: transparent;
  transition: all var(--artdeco-transition-slow);
  margin-bottom: var(--artdeco-spacing-2);
  position: relative;
  overflow: hidden;
  min-height: 60px;
  cursor: pointer;

  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    width: 0;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.05));
    transition: width var(--artdeco-transition-slow);
  }
}

.artdeco-nav-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.artdeco-nav-label {
  font-family: var(--artdeco-font-body);
  font-weight: 600;
  font-size: var(--artdeco-text-base);
  color: var(--artdeco-fg-primary);
  letter-spacing: 0.05em;
  transition: all var(--artdeco-transition-slow);
  line-height: 1.3;
}

.artdeco-nav-subtitle {
  font-family: var(--artdeco-font-body);
  font-weight: 400;
  font-size: var(--artdeco-text-sm);
  color: var(--artdeco-fg-muted);
  letter-spacing: 1px;
  text-transform: uppercase;
  transition: all var(--artdeco-transition-slow);
  line-height: 1.2;
}

// Parent Menu Item (clickable to toggle)
.artdeco-nav-item-parent {
  user-select: none;

  &:hover {
    background: rgba(212, 175, 55, 0.08);
    border-left-color: var(--artdeco-accent-gold);
    padding-left: calc(var(--artdeco-spacing-3) + 4px);
  }

  &.expanded {
    background: rgba(212, 175, 55, 0.05);
    border-left-color: var(--artdeco-gold-primary);

    .artdeco-nav-label {
      color: var(--artdeco-accent-gold);
      font-weight: 700;
    }
  }
}

// Child Menu Item
.artdeco-nav-item-child {
  padding-left: calc(var(--artdeco-spacing-3) + 32px); // Indented
  font-size: var(--artdeco-text-sm);
  min-height: 50px;

  &:hover {
    background: rgba(212, 175, 55, 0.08);
    border-left-color: var(--artdeco-accent-gold);
    padding-left: calc(var(--artdeco-spacing-3) + 36px);
  }

  &.active {
    background: linear-gradient(
      90deg,
      rgba(212, 175, 55, 0.15),
      rgba(212, 175, 55, 0.05)
    );
    border-left-color: var(--artdeco-accent-gold);
    border-left-width: 4px;
  }
}

// Active State
.artdeco-nav-item.active {
  background: linear-gradient(90deg, rgba(212, 175, 55, 0.2), rgba(212, 175, 55, 0.08));
  border-left-color: var(--artdeco-accent-gold);
  border-left-width: 4px;
  box-shadow: inset 0 0 30px rgba(212, 175, 55, 0.15);

  .artdeco-nav-label {
    color: var(--artdeco-accent-gold);
    font-weight: 700;
    text-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
  }

  .artdeco-nav-subtitle {
    color: var(--artdeco-fg-secondary);
  }
}

// Sub-menu container
.artdeco-submenu {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-1);
  padding-left: var(--artdeco-spacing-4);
  border-left: 1px solid rgba(212, 175, 55, 0.1);
  margin-left: var(--artdeco-spacing-4);
}

// ============================================
//   ANIMATIONS
// ============================================
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-in {
  animation: fadeInUp 0.6s ease forwards;
}

// Slide-fade transition for sub-menus
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

// ============================================
//   FOOTER SECTION
// ============================================
.artdeco-sidebar-footer {
  padding: var(--artdeco-spacing-4);
  text-align: center;
  border-top: 1px solid rgba(212, 175, 55, 0.2);
  background: var(--artdeco-bg-header);
  position: relative;
  z-index: 1;
}

.artdeco-footer-ornament {
  font-size: var(--artdeco-text-lg);
  color: rgba(212, 175, 55, 0.2);
  margin-bottom: var(--artdeco-spacing-1);
  text-shadow: 0 0 8px rgba(212, 175, 55, 0.2);
}

.artdeco-footer-text {
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-xs);
  font-weight: 600;
  color: var(--artdeco-fg-muted);
  letter-spacing: 2px;
  text-transform: uppercase;
}

// ============================================
//   DESIGN NOTE - 设计说明
//   本项目仅支持桌面端，不包含移动端响应式代码
// ============================================
</style>
