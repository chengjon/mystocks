<template>
  <div class="nested-menu">
    <el-menu
      :default-active="activeMenu"
      :collapse="isCollapse"
      :unique-opened="uniqueOpened"
      :mode="mode"
      :background-color="backgroundColor"
      :text-color="textColor"
      :active-text-color="activeTextColor"
      router
      @select="handleMenuSelect"
    >
      <!-- 一级菜单和二级菜单 -->
      <template v-for="menu in menuList" :key="menu.id">
        <!-- 无子菜单的一级菜单 -->
        <el-menu-item
          v-if="!menu.children || menu.children.length === 0"
          :index="menu.path"
          :disabled="menu.disabled"
        >
          <el-icon v-if="menu.icon"><component :is="menu.icon" /></el-icon>
          <template #title>{{ menu.title }}</template>
        </el-menu-item>

        <!-- 有子菜单的一级菜单（二级嵌套） -->
        <el-sub-menu
          v-else
          :index="menu.id"
          :disabled="menu.disabled"
        >
          <template #title>
            <el-icon v-if="menu.icon"><component :is="menu.icon" /></el-icon>
            <span>{{ menu.title }}</span>
          </template>

          <!-- 二级菜单 -->
          <el-menu-item
            v-for="(subMenu, _idx) in menu.children"
            :key="subMenu.id"
            :index="subMenu.path"
            :disabled="subMenu.disabled"
          >
            <el-icon v-if="subMenu.icon"><component :is="subMenu.icon" /></el-icon>
            <template #title>{{ subMenu.title }}</template>
          </el-menu-item>
        </el-sub-menu>
      </template>
    </el-menu>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

/**
 * 2级嵌套菜单组件
 *
 * 功能:
 * - 支持一级菜单和二级子菜单
 * - 自动激活当前路由对应的菜单项
 * - 支持菜单折叠/展开
 * - 支持禁用菜单项
 * - 支持图标显示
 * - 支持水平和垂直模式
 *
 * @example
 * <NestedMenu
 *   :menu-list="menus"
 *   :is-collapse="false"
 *   @menu-select="handleSelect"
 * />
 */

// Props
const props = defineProps({
  // 菜单数据列表
  menuList: {
    type: Array,
    required: true,
    default: () => []
  },
  // 是否折叠菜单
  isCollapse: {
    type: Boolean,
    default: false
  },
  // 是否只保持一个子菜单展开
  uniqueOpened: {
    type: Boolean,
    default: true
  },
  // 菜单模式
  mode: {
    type: String,
    default: 'vertical', // 'vertical' | 'horizontal'
    validator: (value) => ['vertical', 'horizontal'].includes(value)
  },
  // 背景颜色
  backgroundColor: {
    type: String,
    default: 'var(--artdeco-bg-base)'
  },
  // 文字颜色
  textColor: {
    type: String,
    default: 'var(--artdeco-fg-muted)'
  },
  // 激活菜单的文字颜色
  activeTextColor: {
    type: String,
    default: 'var(--artdeco-gold-primary)'
  },
  // 默认激活的菜单路径
  defaultActive: {
    type: String,
    default: ''
  }
})

// Emits
const emit = defineEmits(['menu-select'])

// 当前路由
const route = useRoute()

// 当前激活的菜单
const activeMenu = ref(props.defaultActive || route.path)

// 监听路由变化，自动激活菜单
watch(
  () => route.path,
  (newPath) => {
    activeMenu.value = newPath
  },
  { immediate: true }
)

// 监听defaultActive变化
watch(
  () => props.defaultActive,
  (newValue) => {
    if (newValue) {
      activeMenu.value = newValue
    }
  }
)

/**
 * 菜单选择处理
 * @param {string} index - 选中菜单的索引
 * @param {Array} indexPath - 选中菜单的索引路径
 */
const handleMenuSelect = (index, indexPath) => {
  activeMenu.value = index
  emit('menu-select', { index, indexPath })
}
</script>

<script>
/**
 * 菜单数据结构示例:
 *
 * const menuList = [
 *   {
 *     id: 'dashboard',
 *     title: '交易室',
 *     path: '/dashboard',
 *     icon: 'Monitor',
 *     disabled: false
 *   },
 *   {
 *     id: 'market',
 *     title: '市场数据',
 *     icon: 'TrendCharts',
 *     disabled: false,
 *     children: [
 *       {
 *         id: 'market-realtime',
 *         title: '实时行情',
 *         path: '/market/realtime',
 *         icon: 'DataLine',
 *         disabled: false
 *       },
 *       {
 *         id: 'market-kline',
 *         title: 'K线图',
 *         path: '/market/kline',
 *         icon: 'DataAnalysis',
 *         disabled: false
 *       }
 *     ]
 *   }
 * ]
 */
export default {
  name: 'NestedMenu'
}
</script>

<style scoped>
.nested-menu {
  width: 100%;
  height: 100%;
}

/* 折叠状态下的样式 */
.nested-menu :deep(.el-menu--collapse) {
  width: var(--artdeco-sidebar-collapsed-width);
}

/* 菜单项悬停效果 */
.nested-menu :deep(.el-menu-item:hover),
.nested-menu :deep(.el-sub-menu__title:hover) {
  background-color: var(--artdeco-gold-opacity-10) !important;
}

/* 激活菜单项样式 */
.nested-menu :deep(.el-menu-item.is-active) {
  background-color: var(--artdeco-gold-opacity-20) !important;
}

/* 图标样式 */
.nested-menu :deep(.el-icon) {
  margin-right: var(--artdeco-spacing-2);
  font-size: calc(var(--artdeco-spacing-4) + var(--artdeco-spacing-px) * 2);
}

/* 折叠时隐藏图标右侧间距 */
.nested-menu :deep(.el-menu--collapse .el-icon) {
  margin-right: 0;
}

/* 子菜单标题样式 */
.nested-menu :deep(.el-sub-menu__title) {
  display: flex;
  align-items: center;
}

/* 禁用菜单项样式 */
.nested-menu :deep(.el-menu-item.is-disabled),
.nested-menu :deep(.el-sub-menu.is-disabled .el-sub-menu__title) {
  opacity: 50%;
  cursor: not-allowed;
}

/* 水平模式下的样式调整 */
.nested-menu :deep(.el-menu--horizontal) {
  border-bottom: none;
}

.nested-menu :deep(.el-menu--horizontal .el-menu-item),
.nested-menu :deep(.el-menu--horizontal .el-sub-menu__title) {
  height: calc(var(--artdeco-spacing-12) + var(--artdeco-spacing-3));
  line-height: calc(var(--artdeco-spacing-12) + var(--artdeco-spacing-3));
}

/* 响应式设计 */
@media (width <= var(--artdeco-breakpoint-md)) {
  .nested-menu :deep(.el-menu-item),
  .nested-menu :deep(.el-sub-menu__title) {
    font-size: var(--artdeco-text-sm);
  }
}
</style>
