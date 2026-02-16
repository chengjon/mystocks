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
                v-for="(child, _idx) in menu.children"
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
@import "./styles/ArtDecoCollapsibleSidebar.scss";
</style>
