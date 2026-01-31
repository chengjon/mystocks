<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar">
      <div class="logo" :class="{ collapse: isCollapse }">
        <span v-if="!isCollapse">MyStocks</span>
        <span v-else>MS</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :router="false"
        background-color="transparent"
        text-color="#B8B8B8"
        active-text-color="#D4AF37"
        @select="handleMenuSelect"
        class="artdeco-menu"
      >
        <!-- 3 Core Workflows - Phase 1 Optimization -->
        <!-- Workflow 1: Trading (交易决策) -->
        <el-sub-menu index="/trading">
          <template #title>
            <el-icon><Tickets /></el-icon>
            <span>交易决策</span>
          </template>
          <el-menu-item index="/trade">
            <template #title>交易执行</template>
          </el-menu-item>
          <el-menu-item index="/strategy">
            <template #title>策略管理</template>
          </el-menu-item>
          <el-menu-item index="/risk">
            <template #title>风险监控</template>
          </el-menu-item>
         </el-sub-menu>

         <!-- ArtDeco Gold Divider -->
         <div class="artdeco-gold-divider"></div>

         <!-- Workflow 2: Analysis (分析与回测) -->
        <el-sub-menu index="/analysis">
          <template #title>
            <el-icon><DataAnalysis /></el-icon>
            <span>分析研究</span>
          </template>
          <el-menu-item index="/backtest">
            <template #title>策略回测</template>
          </el-menu-item>
          <el-menu-item index="/technical">
            <template #title>技术分析</template>
          </el-menu-item>
          <el-menu-item index="/indicators">
            <template #title>指标库</template>
          </el-menu-item>
          <el-menu-item index="/analysis">
            <template #title>数据分析</template>
          </el-menu-item>
         </el-sub-menu>

         <!-- ArtDeco Gold Divider -->
         <div class="artdeco-gold-divider"></div>

         <!-- Workflow 3: Portfolio (持仓与表现) -->
        <el-sub-menu index="/portfolio">
          <template #title>
            <el-icon><Grid /></el-icon>
            <span>投资组合</span>
          </template>
          <el-menu-item index="/dashboard">
            <template #title>市场概览</template>
          </el-menu-item>
          <el-menu-item index="/stocks">
            <template #title>自选股</template>
          </el-menu-item>
          <el-menu-item index="/market-data">
            <template #title>市场数据</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- Market Data Quick Access -->
        <el-sub-menu index="/market">
          <template #title>
            <el-icon><TrendCharts /></el-icon>
            <span>市场行情</span>
          </template>
          <el-menu-item index="/market">
            <template #title>实时行情</template>
          </el-menu-item>
          <el-menu-item index="/tdx-market">
            <template #title>TDX行情</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- Demo (功能演示) -->
        <el-sub-menu index="/demo">
          <template #title>
            <el-icon><Operation /></el-icon>
            <span>功能演示</span>
          </template>
          <el-menu-item index="/demo/openstock">
            <template #title>OpenStock</template>
          </el-menu-item>
          <el-menu-item index="/demo/freqtrade">
            <template #title>Freqtrade</template>
          </el-menu-item>
          <el-menu-item index="/demo/stock-analysis">
            <template #title>Stock-Analysis</template>
          </el-menu-item>
          <el-menu-item index="/demo/tdxpy">
            <template #title>pytdx</template>
          </el-menu-item>
          <el-menu-item index="/demo/phase4-dashboard">
            <template #title>Phase 4 Dashboard</template>
          </el-menu-item>
          <el-menu-item index="/demo/wencai">
            <template #title>Wencai</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- Settings (系统设置) -->
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header class="navbar">
        <div class="left">
          <el-icon class="hamburger" @click="toggleSidebar">
            <component :is="isCollapse ? 'Expand' : 'Fold'" />
          </el-icon>
        </div>
         <div class="right">
           <!-- API版本管理组件 -->
           <ApiVersionManager />

           <el-dropdown @command="handleCommand">
             <span class="user-info">
               <el-icon><User /></el-icon>
               <span class="username">{{ user?.username }}</span>
               <el-icon><ArrowDown /></el-icon>
             </span>
             <template #dropdown>
               <el-dropdown-menu>
                 <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                 <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
               </el-dropdown-menu>
             </template>
           </el-dropdown>
         </div>
      </el-header>

      <!-- 内容区域 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import ApiVersionManager from '@/components/common/ApiVersionManager.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isCollapse = ref(false)
const user = computed(() => authStore.user)
const activeMenu = computed(() => route.path)

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const handleMenuSelect = (index) => {
  console.log('Menu selected:', index)
  if (index && index.startsWith('/')) {
    router.push(index)
  }
}

const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(async () => {
      await authStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    }).catch(() => {})
  } else if (command === 'profile') {
    ElMessage.info('个人信息功能开发中...')
  }
}
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.layout-container {
  height: 100%;
  background-color: var(--artdeco-bg-global);

  .sidebar {
    background-color: var(--artdeco-bg-base);  // ArtDeco深炭灰
    transition: width var(--artdeco-transition-base);
    border-right: 1px solid var(--artdeco-border-gold);  // ArtDeco金色边框

    .logo {
      height: 50px;
      line-height: 50px;
      color: var(--artdeco-gold-primary);  // ArtDeco金色Logo
      font-family: var(--font-display);  // Cinzel字体
      font-size: 20px;
      font-weight: 600;
      text-align: center;
      background-color: var(--artdeco-bg-elevated);
      letter-spacing: 0.05em;  // ArtDeco宽字距
      transition: all var(--artdeco-transition-base);

      &.collapse {
        font-size: 18px;
      }
    }

    // Element Plus 菜单组件 ArtDeco 主题
    .el-menu {
      border-right: none;
      background-color: var(--artdeco-bg-base);

      // 菜单项悬停状态
      .el-menu-item {
        color: var(--artdeco-fg-muted);
        transition: all var(--artdeco-transition-base);

        &:hover {
          background-color: rgba(212, 175, 55, 0.1);  // 金色半透明背景
          color: var(--artdeco-gold-primary);
        }

        &.is-active {
          background-color: rgba(212, 175, 55, 0.15);  // 金色半透明背景
          color: var(--artdeco-gold-primary);  // 金色文本
          position: relative;

          // ArtDeco金色左边框指示器
          &::before {
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 3px;
            height: 60%;
            background-color: var(--artdeco-gold-primary);
          }
        }
      }

      // 菜单组标题
      .el-sub-menu__title {
        color: var(--artdeco-fg-muted);
        transition: all var(--artdeco-transition-base);

        &:hover {
          color: var(--artdeco-gold-primary);
         }
       }
     }
   }

   // ArtDeco 金色分隔线（用于分隔不同工作流区域）
   .artdeco-gold-divider {
     height: 2px;
     background: linear-gradient(90deg, 
       transparent 0%, 
       var(--artdeco-border-gold) 20%, 
       transparent 20%, 
       transparent 40%, 
       var(--artdeco-border-gold) 50%, 
       var(--artdeco-border-gold) 60%, 
       transparent 80%, 
       transparent 100%
     );
     margin: var(--artdeco-spacing-3) 0;
     border-radius: var(--artdeco-radius-sm);
     
     // ArtDeco 装饰元素（金色微边框 + 阴影）
     &::before {
       content: '';
       position: absolute;
       width: 6px;
       height: 6px;
       left: 50%;
       top: -2px;
       border-radius: 50%;
       background: var(--artdeco-gold-primary);
       box-shadow: 0 0 2px rgba(212, 175, 55, 0.3);
     }
     
     // 装饰点动画
     &::after {
       content: '';
       position: absolute;
       width: 6px;
       height: 6px;
       right: 50%;
       top: -2px;
       border-radius: 50%;
       background: var(--artdeco-gold-primary);
       box-shadow: 0 0 2px rgba(212, 175, 55, 0.3);
     }
   }
 </style>
