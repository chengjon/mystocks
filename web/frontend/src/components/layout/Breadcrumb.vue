<template>
  <div class="artdeco-breadcrumb-container">
    <div class="breadcrumb-decoration-line"></div>
    <el-breadcrumb :separator-icon="separatorIcon" class="artdeco-breadcrumb">
      <transition-group name="breadcrumb">
        <el-breadcrumb-item
          v-for="(item, index) in breadcrumbs"
          :key="item.path"
          :to="index < breadcrumbs.length - 1 ? { path: item.path } : null"
          class="breadcrumb-item"
        >
          <div class="breadcrumb-item-content">
            <el-icon v-if="item.icon && showIcon" class="breadcrumb-icon">
              <component :is="item.icon" />
            </el-icon>
            <span :class="{ 'breadcrumb-active': index === breadcrumbs.length - 1 }">
              {{ item.title }}
            </span>
          </div>
        </el-breadcrumb-item>
      </transition-group>
    </el-breadcrumb>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowRight } from '@element-plus/icons-vue'

/**
 * ArtDeco 风格面包屑导航组件
 *
 * 功能:
 * - 根据当前路由自动生成面包屑路径
 * - ArtDeco 装饰艺术风格（金色 + 黑色 + 锐利边角）
 * - 支持2级路由层级显示
 * - 自动识别路由的meta.title作为显示标题
 * - 支持路由图标显示
 * - 支持面包屑点击导航
 * - 支持自定义分隔符
 * - L形角落装饰 + 悬停发光效果
 *
 * @example
 * <Breadcrumb
 *   :show-icon="true"
 *   home-title="DASHBOARD"
 * />
 */

// Props
const props = defineProps({
  // 首页标题（大写）
  homeTitle: {
    type: String,
    default: 'DASHBOARD'
  },
  // 首页路径
  homePath: {
    type: String,
    default: '/dashboard'
  },
  // 是否显示图标
  showIcon: {
    type: Boolean,
    default: true
  },
  // 分隔符图标
  separatorIcon: {
    type: Object,
    default: () => ArrowRight
  },
  // 自定义面包屑映射（用于覆盖路由meta）
  customBreadcrumb: {
    type: Object,
    default: () => ({})
  }
})

// 当前路由
const route = useRoute()
const router = useRouter()

// 面包屑数据
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)

  // 创建面包屑数组
  const breadcrumbList = []

  // 添加首页（如果当前不在首页）
  if (route.path !== props.homePath) {
    breadcrumbList.push({
      path: props.homePath,
      title: props.homeTitle.toUpperCase(),
      icon: 'HomeFilled'
    })
  }

  // 添加路由匹配的面包屑
  matched.forEach((item, index) => {
    // 跳过重定向路由
    if (item.redirect) return

    // 获取路由配置
    const meta = item.meta || {}
    const path = item.path || ''

    // 检查是否有自定义配置
    const customConfig = props.customBreadcrumb[path] || {}

    // 构建面包屑项（确保大写）
    const breadcrumbItem = {
      path: path,
      title: (customConfig.title || meta.title || item.name || 'UNNAMED').toUpperCase(),
      icon: customConfig.icon || meta.icon || null
    }

    // 避免重复的首页
    if (breadcrumbItem.path !== props.homePath) {
      breadcrumbList.push(breadcrumbItem)
    }
  })

  return breadcrumbList
})

// 监听路由变化
watch(
  () => route.path,
  () => {
    // 路由变化时自动更新面包屑（computed会自动重新计算）
  },
  { immediate: true }
)
</script>

<script>
/**
 * 路由配置示例（需要在router中配置meta）:
 *
 * {
 *   path: '/market',
 *   name: 'Market',
 *   meta: {
 *     title: 'MARKET DATA',  // 将自动大写显示
 *     icon: 'TrendCharts'
 *   },
 *   children: [
 *     {
 *       path: 'realtime',
 *       name: 'MarketRealtime',
 *       meta: {
 *         title: 'REALTIME',
 *         icon: 'DataLine'
 *       }
 *     }
 *   ]
 * }
 *
 * 面包屑将显示为: DASHBOARD > MARKET DATA > REALTIME
 */
export default {
  name: 'Breadcrumb'
}
</script>

<style scoped lang="scss">

.artdeco-breadcrumb-container {
  position: relative;
  display: flex;
  align-items: center;
  height: 60px;
  padding: 0 var(--artdeco-spacing-6);
  background: var(--artdeco-bg-primary);
  border-bottom: 2px solid var(--artdeco-accent-gold);
  overflow: hidden;

  // L形角落装饰
  &::before,
  &::after {
    content: '';
    position: absolute;
    background: var(--artdeco-accent-gold);
    opacity: 0.6;
  }

  // 左上角装饰
  &::before {
    top: 0;
    left: 0;
    width: 20px;
    height: 2px;
    box-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
  }

  // 右上角装饰
  &::after {
    top: 0;
    right: 0;
    width: 2px;
    height: 20px;
    box-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
  }
}

.breadcrumb-decoration-line {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    var(--artdeco-accent-gold) 50%,
    transparent 100%
  );
  opacity: 0.3;
}

/* ArtDeco 面包屑基础样式 */
.artdeco-breadcrumb {
  position: relative;
  z-index: 1;

  :deep(.el-breadcrumb__item) {
    display: inline-flex;
    align-items: center;
    font-family: var(--artdeco-font-display);
    font-size: var(--artdeco-font-size-small);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wider);
    color: var(--artdeco-fg-muted);

    .el-breadcrumb__inner {
      display: inline-flex;
      align-items: center;
      color: rgba(212, 175, 55, 0.7);
      transition: all var(--artdeco-transition-base);

      &:hover {
        color: var(--artdeco-accent-gold);
        text-shadow: var(--artdeco-glow-subtle);
      }
    }

    // 最后一个激活项
    &:last-child {
      .el-breadcrumb__inner {
        color: var(--artdeco-accent-gold);
        font-weight: 700;
        text-shadow: var(--artdeco-glow-medium);
        cursor: default;
      }
    }
  }

  // 分隔符样式
  :deep(.el-breadcrumb__separator) {
    color: var(--artdeco-accent-gold);
    opacity: 0.4;
    margin: 0 var(--artdeco-spacing-3);
    font-size: 12px;
  }
}

.breadcrumb-item-content {
  display: inline-flex;
  align-items: center;
  gap: var(--artdeco-spacing-1);
}

.breadcrumb-icon {
  font-size: 16px;
  color: var(--artdeco-accent-gold);
  opacity: 0.8;
  transition: all var(--artdeco-transition-base);

  &:hover {
    opacity: 1;
    filter: drop-shadow(0 0 4px rgba(212, 175, 55, 0.5));
  }
}

.breadcrumb-active {
  color: var(--artdeco-accent-gold);
  font-weight: 700;
  text-shadow: var(--artdeco-glow-subtle);
}

/* 面包屑过渡动画 */
.breadcrumb-enter-active,
.breadcrumb-leave-active {
  transition: all var(--artdeco-transition-base);
}

.breadcrumb-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.breadcrumb-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .artdeco-breadcrumb-container {
    height: 50px;
    padding: 0 var(--artdeco-spacing-3);

    &::before {
      width: 15px;
    }

    &::after {
      height: 15px;
    }
  }

  .artdeco-breadcrumb {
    :deep(.el-breadcrumb__item) {
      font-size: var(--artdeco-font-size-xs);
      letter-spacing: var(--artdeco-tracking-wide);

      .el-breadcrumb__inner {
        padding: var(--artdeco-spacing-1) 0;
      }
    }

    :deep(.el-breadcrumb__separator) {
      margin: 0 var(--artdeco-spacing-1);
      font-size: 10px;
    }
  }

  .breadcrumb-icon {
    font-size: 14px;
  }
}

/* 大屏幕优化 */
@media (min-width: 1440px) {
  .artdeco-breadcrumb-container {
    padding: 0 var(--artdeco-spacing-8);

    &::before {
      width: 30px;
    }

    &::after {
      height: 30px;
    }
  }

  .artdeco-breadcrumb {
    :deep(.el-breadcrumb__item) {
      font-size: var(--artdeco-font-size-body);
    }
  }
}

/* 打印样式 */
@media print {
  .artdeco-breadcrumb-container {
    background: white;
    border-bottom: 1px solid #000;

    &::before,
    &::after {
      display: none;
    }
  }

  .artdeco-breadcrumb :deep(.el-breadcrumb__item .el-breadcrumb__inner) {
    color: #000;
  }
}
</style>
