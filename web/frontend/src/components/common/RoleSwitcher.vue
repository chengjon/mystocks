<template>
  <div class="role-switcher">
    <el-select
      v-model="currentRole"
      placeholder="选择角色"
      @change="handleRoleChange"
      size="small"
    >
      <el-option label="用户 (User)" value="user" />
      <el-option label="管理员 (Admin)" value="admin" />
      <el-option label="无角色 (Guest)" value="" />
    </el-select>
    <span class="role-label">当前角色: {{ currentRole || 'Guest' }}</span>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const currentRole = ref('user')

// 从localStorage恢复角色设置
const savedRole = localStorage.getItem('user-role')
if (savedRole) {
  currentRole.value = savedRole
}

const handleRoleChange = (role) => {
  // 更新角色（这里只是演示，实际应该从后端获取）
  if (authStore.user) {
    authStore.user.roles = role ? [role] : []
  }

  // 保存到localStorage
  localStorage.setItem('user-role', role || '')

  // 刷新页面以更新菜单
  window.location.reload()
}
</script>

<style scoped>
.role-switcher {
  display: flex;
  align-items: center;
  gap: calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) * 2);
  padding: 0 var(--artdeco-spacing-5);
  height: 100%;
  background-color: color-mix(in srgb, var(--artdeco-bg-card) 90%, var(--artdeco-fg-primary));
}

.role-label {
  font-size: var(--artdeco-text-sm);
  color: var(--artdeco-fg-muted);
}
</style>
