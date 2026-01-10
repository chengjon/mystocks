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
import { ref, computed, watch } from 'vue'
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

.breadcrumb-container {
  position: relative;
  display: flex;
  align-items: center;
  height: 60px;
  padding: 0 24px;
  background: #ffffff;
  border-bottom: 2px solid #409eff;
  overflow: hidden;

  // L形角落装饰
  &::before,
  &::after {
    content: '';
    position: absolute;
    background: #409eff;
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
    #409eff 50%,
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
    font-family: 'Inter', system-ui, sans-serif;
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #909399;

    .el-breadcrumb__inner {
      display: inline-flex;
      align-items: center;
      color: rgba(212, 175, 55, 0.7);
      transition: all 0.3s;

      &:hover {
        color: #409eff;
        text-shadow: 0 2px 4px rgba(64, 158, 255, 0.1);
      }
    }

    // 最后一个激活项
    &:last-child {
      .el-breadcrumb__inner {
        color: #409eff;
        font-weight: 700;
        text-shadow: 0 4px 8px rgba(64, 158, 255, 0.2);
        cursor: default;
      }
    }
  }

  // 分隔符样式
  :deep(.el-breadcrumb__separator) {
    color: #409eff;
    opacity: 0.4;
    margin: 0 12px;
    font-size: 12px;
  }
}

.breadcrumb-item-content {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.breadcrumb-icon {
  font-size: 16px;
  color: #409eff;
  opacity: 0.8;
  transition: all 0.3s;

  &:hover {
    opacity: 1;
    filter: drop-shadow(0 0 4px rgba(212, 175, 55, 0.5));
  }
}

.breadcrumb-active {
  color: #409eff;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(64, 158, 255, 0.1);
}

/* 面包屑过渡动画 */
.breadcrumb-enter-active,
.breadcrumb-leave-active {
  transition: all 0.3s;
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
  .breadcrumb-container {
    height: 50px;
    padding: 0 12px;

    &::before {
      width: 15px;
    }

    &::after {
      height: 15px;
    }
  }

  .breadcrumb {
    :deep(.el-breadcrumb__item) {
      font-size: 12px;
      letter-spacing: 0.5px;

      .el-breadcrumb__inner {
        padding: 4px 0;
      }
    }

    :deep(.el-breadcrumb__separator) {
      margin: 0 4px;
      font-size: 10px;
    }
  }

  .breadcrumb-icon {
    font-size: 14px;
  }
}

/* 大屏幕优化 */
@media (min-width: 1440px) {
  .breadcrumb-container {
    padding: 0 32px;

    &::before {
      width: 30px;
    }

    &::after {
      height: 30px;
    }
  }

  .breadcrumb {
    :deep(.el-breadcrumb__item) {
      font-size: 14px;
    }
  }
}

/* 打印样式 */
@media print {
  .breadcrumb-container {
    background: white;
    border-bottom: 1px solid #000;

    &::before,
    &::after {
      display: none;
    }
  }

  .breadcrumb :deep(.el-breadcrumb__item .el-breadcrumb__inner) {
    color: #000;
  }
}
</style>
