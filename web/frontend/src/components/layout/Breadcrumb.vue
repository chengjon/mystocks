<template>
  <div class="breadcrumb-container">
    <div class="breadcrumb-decoration-line"></div>
    <el-breadcrumb :separator-icon="separatorIcon" class="breadcrumb">
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
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowRight } from '@element-plus/icons-vue'

/**
 *
 * 功能:
 * - 根据当前路由自动生成面包屑路径
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
 *   home-title="交易室"
 * />
 */

// Props
const props = defineProps({
  // 首页标题（大写）
  homeTitle: {
    type: String,
    default: '交易室'
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
const _router = useRouter()

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

.breadcrumb-container {
  position: relative;
  display: flex;
  align-items: center;
  height: calc(var(--artdeco-spacing-12) + var(--artdeco-spacing-3));
  padding: 0 var(--artdeco-spacing-6);
  background: var(--artdeco-bg-card);
  border-bottom: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-gold-primary);
  overflow: hidden;

  // L形角落装饰
  &::before,
  &::after {
    content: '';
    position: absolute;
    background: var(--artdeco-gold-primary);
    opacity: 0.6;
  }

  // 左上角装饰
  &::before {
    top: 0;
    left: 0;
    width: var(--artdeco-spacing-5);
    height: calc(var(--artdeco-spacing-px) * 2);
    box-shadow: var(--artdeco-glow-subtle);
  }

  // 右上角装饰
  &::after {
    top: 0;
    right: 0;
    width: calc(var(--artdeco-spacing-px) * 2);
    height: var(--artdeco-spacing-5);
    box-shadow: var(--artdeco-glow-subtle);
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
    var(--artdeco-gold-primary) 50%,
    transparent 100%
  );
  opacity: 0.3;
}

.breadcrumb {
  position: relative;
  z-index: 1;

  :deep(.el-breadcrumb__item) {
    display: inline-flex;
    align-items: center;
    font-family: var(--font-body);
    font-size: var(--artdeco-text-sm);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
    color: var(--artdeco-fg-muted);

    .el-breadcrumb__inner {
      display: inline-flex;
      align-items: center;
      color: color-mix(in srgb, var(--artdeco-gold-primary) 70%, transparent);
      transition:
        color var(--artdeco-transition-base) var(--artdeco-ease-out),
        text-shadow var(--artdeco-transition-base) var(--artdeco-ease-out);

      &:hover {
        color: var(--artdeco-gold-light);
        text-shadow: var(--artdeco-shadow-sm);
      }
    }

    // 最后一个激活项
    &:last-child {
      .el-breadcrumb__inner {
        color: var(--artdeco-gold-primary);
        font-weight: 700;
        text-shadow: var(--artdeco-shadow-md);
        cursor: default;
      }
    }
  }

  // 分隔符样式
  :deep(.el-breadcrumb__separator) {
    color: var(--artdeco-gold-primary);
    opacity: 0.4;
    margin: 0 var(--artdeco-spacing-3);
    font-size: var(--artdeco-text-xs);
  }
}

.breadcrumb-item-content {
  display: inline-flex;
  align-items: center;
  gap: var(--artdeco-spacing-1);
}

.breadcrumb-icon {
  font-size: var(--artdeco-text-base);
  color: var(--artdeco-gold-primary);
  opacity: 0.8;
  transition:
    opacity var(--artdeco-transition-base) var(--artdeco-ease-out),
    filter var(--artdeco-transition-base) var(--artdeco-ease-out);

  &:hover {
    opacity: 1;
    filter: drop-shadow(0 0 var(--artdeco-spacing-1) color-mix(in srgb, var(--artdeco-gold-primary) 50%, transparent));
  }
}

.breadcrumb-active {
  color: var(--artdeco-gold-primary);
  font-weight: 700;
  text-shadow: var(--artdeco-shadow-sm);
}

/* 面包屑过渡动画 */
.breadcrumb-enter-active,
.breadcrumb-leave-active {
  transition:
    opacity var(--artdeco-transition-base) var(--artdeco-ease-out),
    transform var(--artdeco-transition-base) var(--artdeco-ease-out);
}

.breadcrumb-enter-from {
  opacity: 0%;
  transform: translateX(var(--artdeco-spacing-5));
}

.breadcrumb-leave-to {
  opacity: 0%;
  transform: translateX(calc(var(--artdeco-spacing-5) * -1));
}

/* 响应式设计 */
@media (width <= var(--artdeco-breakpoint-md)) {
  .breadcrumb-container {
    height: calc(var(--artdeco-spacing-12) + var(--artdeco-spacing-px) * 2);
    padding: 0 var(--artdeco-spacing-3);

    &::before {
      width: var(--artdeco-spacing-4);
    }

    &::after {
      height: var(--artdeco-spacing-4);
    }
  }

  .breadcrumb {
    :deep(.el-breadcrumb__item) {
      font-size: var(--artdeco-text-xs);
      letter-spacing: calc(var(--artdeco-spacing-px) / 2);

      .el-breadcrumb__inner {
        padding: var(--artdeco-spacing-1) 0;
      }
    }

    :deep(.el-breadcrumb__separator) {
      margin: 0 var(--artdeco-spacing-1);
      font-size: calc(var(--artdeco-text-xs) - var(--artdeco-spacing-px) * 2);
    }
  }

  .breadcrumb-icon {
    font-size: var(--artdeco-text-sm);
  }
}

/* 大屏幕优化 */
@media (width >= 90rem) {
  .breadcrumb-container {
    padding: 0 var(--artdeco-spacing-8);

    &::before {
      width: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1));
    }

    &::after {
      height: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1));
    }
  }

  .breadcrumb {
    :deep(.el-breadcrumb__item) {
      font-size: var(--artdeco-text-sm);
    }
  }
}

/* 打印样式 */
@media print {
  .breadcrumb-container {
    background: var(--artdeco-bg-card);
    border-bottom: 1px solid var(--artdeco-gold-primary);

    &::before,
    &::after {
      display: none;
    }
  }

  .breadcrumb :deep(.el-breadcrumb__item .el-breadcrumb__inner) {
    color: var(--artdeco-fg-primary);
  }
}
</style>
