<template>
  <div class="breadcrumb-container">
    <el-breadcrumb :separator-icon="separatorIcon">
      <transition-group name="breadcrumb">
        <el-breadcrumb-item
          v-for="(item, index) in breadcrumbs"
          :key="item.path"
          :to="index < breadcrumbs.length - 1 ? { path: item.path } : null"
        >
          <el-icon v-if="item.icon && showIcon">
            <component :is="item.icon" />
          </el-icon>
          <span :class="{ 'breadcrumb-active': index === breadcrumbs.length - 1 }">
            {{ item.title }}
          </span>
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
 * 自动面包屑导航组件
 *
 * 功能:
 * - 根据当前路由自动生成面包屑路径
 * - 支持2级路由层级显示
 * - 自动识别路由的meta.title作为显示标题
 * - 支持路由图标显示
 * - 支持面包屑点击导航
 * - 支持自定义分隔符
 *
 * @example
 * <Breadcrumb
 *   :show-icon="true"
 *   :home-title="首页"
 * />
 */

// Props
const props = defineProps({
  // 首页标题
  homeTitle: {
    type: String,
    default: '首页'
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
      title: props.homeTitle,
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

    // 构建面包屑项
    const breadcrumbItem = {
      path: path,
      title: customConfig.title || meta.title || item.name || '未命名',
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
 *     title: '市场数据',
 *     icon: 'TrendCharts'
 *   },
 *   children: [
 *     {
 *       path: 'realtime',
 *       name: 'MarketRealtime',
 *       meta: {
 *         title: '实时行情',
 *         icon: 'DataLine'
 *       }
 *     }
 *   ]
 * }
 *
 * 面包屑将显示为: 首页 > 市场数据 > 实时行情
 */
export default {
  name: 'Breadcrumb'
}
</script>

<style scoped>
.breadcrumb-container {
  display: flex;
  align-items: center;
  height: 50px;
  padding: 0 20px;
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
}

/* 面包屑基础样式 */
.breadcrumb-container :deep(.el-breadcrumb) {
  font-size: 14px;
  line-height: 50px;
}

/* 面包屑项样式 */
.breadcrumb-container :deep(.el-breadcrumb__item) {
  display: inline-flex;
  align-items: center;
}

.breadcrumb-container :deep(.el-breadcrumb__inner) {
  display: inline-flex;
  align-items: center;
  color: #606266;
  font-weight: normal;
  transition: color 0.3s;
}

/* 面包屑链接悬停效果 */
.breadcrumb-container :deep(.el-breadcrumb__inner:hover) {
  color: #409eff;
  cursor: pointer;
}

/* 当前页面（最后一项）样式 */
.breadcrumb-active {
  color: #303133;
  font-weight: 500;
}

.breadcrumb-container :deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: #303133;
  font-weight: 500;
}

.breadcrumb-container :deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner:hover) {
  color: #303133;
  cursor: text;
}

/* 图标样式 */
.breadcrumb-container :deep(.el-icon) {
  margin-right: 5px;
  font-size: 16px;
}

/* 分隔符样式 */
.breadcrumb-container :deep(.el-breadcrumb__separator) {
  margin: 0 8px;
  color: #c0c4cc;
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
    padding: 0 10px;
  }

  .breadcrumb-container :deep(.el-breadcrumb) {
    font-size: 12px;
  }

  .breadcrumb-container :deep(.el-icon) {
    font-size: 14px;
    margin-right: 3px;
  }

  .breadcrumb-container :deep(.el-breadcrumb__separator) {
    margin: 0 5px;
  }
}

/* 暗黑模式支持 */
@media (prefers-color-scheme: dark) {
  .breadcrumb-container {
    background-color: #1f1f1f;
    border-bottom-color: #333;
  }

  .breadcrumb-container :deep(.el-breadcrumb__inner) {
    color: #b0b0b0;
  }

  .breadcrumb-active,
  .breadcrumb-container :deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
    color: #e0e0e0;
  }
}
</style>
