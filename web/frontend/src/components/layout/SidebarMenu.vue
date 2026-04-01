<template>
  <el-menu
    :default-active="activeMenu"
    :collapse="isCollapse"
    :router="false"
    background-color="transparent"
    text-color="var(--artdeco-fg-muted)"
    active-text-color="var(--artdeco-gold-primary)"
    class="artdeco-menu"
  >
    <SidebarMenuItem v-for="item in menuItems" :key="item.id" :item="item" />
  </el-menu>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRoute } from 'vue-router';
import SidebarMenuItem from './SidebarMenuItem.vue';
import menuConfig from '@/config/menu.config.js';
import { useAuthStore } from '@/stores/auth';
import { filterMenuByRoles } from '@/config/menu.config.js';

const route = useRoute();
const authStore = useAuthStore();

// This is a placeholder for the actual collapse state, which should be managed by the parent layout
const isCollapse = ref(false); 

const userRoles = computed(() => authStore.user?.roles || []);

const menuItems = computed(() => filterMenuByRoles(menuConfig, userRoles.value));

const activeMenu = computed(() => route.path);
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.artdeco-menu {
  border-right: none;
  background-color: var(--artdeco-bg-base);

  // Styling is inherited from the global styles and SidebarMenuItem.vue
}
</style>
