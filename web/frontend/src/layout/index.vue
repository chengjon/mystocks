<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar">
      <div class="logo" :class="{ collapse: isCollapse }">
        <span v-if="!isCollapse">MyStocks</span>
        <span v-else>MS</span>
      </div>
      <SidebarMenu :is-collapse="isCollapse" />
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
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { ElMessage, ElMessageBox } from 'element-plus';
import ApiVersionManager from '@/components/common/ApiVersionManager.vue';
import SidebarMenu from '@/components/layout/SidebarMenu.vue';

const router = useRouter();
const authStore = useAuthStore();

const isCollapse = ref(false);
const user = computed(() => authStore.user);

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value;
};


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
@import '@/styles/artdeco-tokens';

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
          background-color: rgb(212 175 55 / 10%);  // 金色半透明背景
          color: var(--artdeco-gold-primary);
        }

        &.is-active {
          background-color: rgb(212 175 55 / 15%);  // 金色半透明背景
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
       box-shadow: 0 0 2px rgb(212 175 55 / 30%);
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
       box-shadow: 0 0 2px rgb(212 175 55 / 30%);
     }
   }
}
</style>
