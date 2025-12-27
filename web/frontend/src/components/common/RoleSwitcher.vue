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
import { ref, computed } from 'vue'
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
  gap: 10px;
  padding: 0 20px;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.9);
}

.role-label {
  font-size: 14px;
  color: #666;
}
</style>
