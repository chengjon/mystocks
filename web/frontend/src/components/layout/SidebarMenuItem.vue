<template>
  <div v-if="!item.disabled">
    <el-menu-item v-if="!item.children || item.children.length === 0" :index="item.path" @click="navigateTo(item.path)">
      <el-icon v-if="item.icon">
        <component :is="item.icon" />
      </el-icon>
      <template #title>{{ item.title }}</template>
    </el-menu-item>
    <el-sub-menu v-else :index="item.id">
      <template #title>
        <el-icon v-if="item.icon">
          <component :is="item.icon" />
        </el-icon>
        <span>{{ item.title }}</span>
      </template>
      <SidebarMenuItem v-for="child in item.children" :key="child.id" :item="child" />
    </el-sub-menu>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

defineProps({
  item: {
    type: Object,
    required: true,
  },
});

const router = useRouter();

const navigateTo = (path: string) => {
  if (path && path !== router.currentRoute.value.path) {
    router.push(path);
  }
};
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

// Menu item styles are mostly handled by Element Plus and the parent theme
// However, we can add specific overrides here if needed.

.el-menu-item {
  color: var(--artdeco-fg-muted);
  transition: all var(--artdeco-transition-base);

  &:hover {
    background-color: var(--artdeco-gold-opacity-10);
    color: var(--artdeco-gold-primary);
  }

  &.is-active {
    background-color: var(--artdeco-gold-opacity-15);
    color: var(--artdeco-gold-primary);
    position: relative;

    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 50%;
      transform: translateY(-50%);
      width: calc(var(--artdeco-spacing-px) * 3);
      height: 60%;
      background-color: var(--artdeco-gold-primary);
    }
  }
}

.el-sub-menu__title {
  color: var(--artdeco-fg-muted);
  transition: all var(--artdeco-transition-base);

  &:hover {
    color: var(--artdeco-gold-primary);
  }
}
</style>
