<template>
  <nav class="breadcrumb-nav" aria-label="Breadcrumb">
    <ol class="breadcrumb-list">
      <li
        v-for="(item, index) in items"
        :key="index"
        class="breadcrumb-item"
      >
        <router-link
          v-if="item.path && index < items.length - 1"
          :to="item.path"
          class="breadcrumb-link"
        >
          {{ item.label }}
        </router-link>
        <span v-else class="breadcrumb-current">
          {{ item.label }}
        </span>
        
        <span
          v-if="index < items.length - 1"
          class="breadcrumb-separator"
          aria-hidden="true"
        >
          /
        </span>
      </li>
    </ol>
  </nav>
</template>

<script setup lang="ts">
/**
 * Bloomberg风格面包屑导航组件
 * 
 * 用于显示当前页面在导航层级中的位置
 * 
 * @example
 * <BreadcrumbNav :items="[
 *   { label: 'Home', path: '/' },
 *   { label: 'Dashboard', path: '/dashboard' },
 *   { label: 'Overview' }
 * ]" />
 */

export interface BreadcrumbItem {
  label: string
  path?: string
}

interface Props {
  items: BreadcrumbItem[]
}

defineProps<Props>()
</script>

<style scoped lang="scss">
@import '@/styles/theme-tokens.scss';

.breadcrumb-nav {
  display: flex;
  align-items: center;
}

.breadcrumb-list {
  display: flex;
  align-items: center;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: var(--spacing-xs);
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  font-size: var(--font-size-sm, 13px);
}

.breadcrumb-link {
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s;

  &:hover {
    color: var(--accent-color);
  }
}

.breadcrumb-current {
  color: var(--text-primary);
  font-weight: 600;
}

.breadcrumb-separator {
  color: var(--text-disabled);
  margin: 0 var(--spacing-xs);
}
</style>
