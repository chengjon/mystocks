<template>
  <div class="account-settings-container">
    <!-- 账户设置主容器 -->
    <div class="account-settings-header">
      <h2 class="account-settings-title">账户设置</h2>
      <div class="account-settings-actions">
        <button class="btn-primary" @click="saveSettings">保存设置</button>
        <button class="btn-secondary" @click="resetSettings">重置</button>
      </div>
    </div>

    <!-- 账户信息 -->
    <div class="account-info-section">
      <div class="card info-card">
        <div class="card-header">
          <h3>账户信息</h3>
        </div>
        <div class="card-body">
          <div class="info-grid">
            <div class="info-item">
              <label class="info-label">用户名</label>
              <input type="text" v-model="accountInfo.username" placeholder="输入用户名" class="info-input" :disabled="!canEditUsername">
            </div>
            <div class="info-item">
              <label class="info-label">邮箱</label>
              <input type="email" v-model="accountInfo.email" placeholder="输入邮箱" class="info-input" :disabled="!canEditEmail">
            </div>
            <div class="info-item">
              <label class="info-label">手机号</label>
              <input type="tel" v-model="accountInfo.phone" placeholder="输入手机号" class="info-input">
            </div>
            <div class="info-item">
              <label class="info-label">昵称</label>
              <input type="text" v-model="accountInfo.nickname" placeholder="输入昵称" class="info-input">
            </div>
            <div class="info-item">
              <label class="info-label">性别</label>
              <select v-model="accountInfo.gender" class="info-select">
                <option value="">请选择</option>
                <option value="male">男</option>
                <option value="female">女</option>
              </select>
            </div>
            <div class="info-item">
              <label class="info-label">生日</label>
              <input type="date" v-model="accountInfo.birthday" class="info-input">
            </div>
            <div class="info-item">
              <label class="info-label">所在地</label>
              <select v-model="accountInfo.location" class="info-select">
                <option value="">请选择</option>
                <option value="beijing">北京</option>
                <option value="shanghai">上海</option>
                <option value="guangzhou">广州</option>
                <option value="shenzhen">深圳</option>
                <option value="hangzhou">杭州</option>
              </select>
            </div>
            <div class="info-item">
              <label class="info-label">职业</label>
              <input type="text" v-model="accountInfo.profession" placeholder="输入职业" class="info-input">
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 头像设置 -->
    <div class="avatar-settings-section">
      <div class="card avatar-card">
        <div class="card-header">
          <h3>头像设置</h3>
        </div>
        <div class="card-body">
          <div class="avatar-display">
            <img :src="accountInfo.avatar || '/default-avatar.png'" alt="用户头像" class="avatar-image">
          </div>
          <div class="avatar-actions">
            <button class="btn-upload" @click="uploadAvatar">上传头像</button>
            <button class="btn-remove" @click="removeAvatar" v-if="accountInfo.avatar">移除头像</button>
            <button class="btn-reset" @click="resetAvatar">重置为默认</button>
          </div>
          <input type="file" ref="avatarInput" accept="image/*" style="display: none;" @change="handleAvatarUpload">
        </div>
      </div>
    </div>

    <!-- 密码设置 -->
    <div class="password-settings-section">
      <div class="card password-card">
        <div class="card-header">
          <h3>密码设置</h3>
        </div>
        <div class="card-body">
          <div class="password-form">
            <div class="form-group">
              <label class="form-label">当前密码</label>
              <input type="password" v-model="passwordForm.currentPassword" placeholder="输入当前密码" class="form-input">
            </div>
            <div class="form-group">
              <label class="form-label">新密码</label>
              <input type="password" v-model="passwordForm.newPassword" placeholder="输入新密码" class="form-input">
            </div>
            <div class="form-group">
              <label class="form-label">确认新密码</label>
              <input type="password" v-model="passwordForm.confirmPassword" placeholder="再次输入新密码" class="form-input">
            </div>
          </div>
          <div class="password-strength" v-if="passwordForm.newPassword">
            <div class="strength-bar">
              <div class="strength-fill" :class="getStrengthClass(passwordStrength)"></div>
            </div>
            <div class="strength-text">
              密码强度: <span :class="getStrengthTextClass(passwordStrength)">{{ getStrengthText(passwordStrength) }}</span>
            </div>
          </div>
          <div class="password-actions">
            <button class="btn-primary" @click="changePassword">修改密码</button>
            <button class="btn-secondary" @click="resetPasswordForm">重置</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 隐私设置 -->
    <div class="privacy-settings-section">
      <div class="card privacy-card">
        <div class="card-header">
          <h3>隐私设置</h3>
        </div>
        <div class="card-body">
          <div class="privacy-settings-list">
            <div class="privacy-setting-item">
              <span class="setting-label">公开个人信息</span>
              <div class="setting-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="privacySettings.publicProfile">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
            <div class="privacy-setting-item">
              <span class="setting-label">公开交易记录</span>
              <div class="setting-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="privacySettings.publicTrades">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
            <div class="privacy-setting-item">
              <span class="setting-label">允许他人查看</span>
              <div class="setting-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="privacySettings.allowView">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
            <div class="privacy-setting-item">
              <span class="setting-label">显示在线状态</span>
              <div class="setting-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="privacySettings.showOnline">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 账户绑定 -->
    <div class="account-binding-section">
      <div class="card binding-card">
        <div class="card-header">
          <h3>账户绑定</h3>
        </div>
        <div class="card-body">
          <div class="binding-list">
            <div class="binding-item" v-for="binding in accountBindings" :key="binding.type">
              <span class="binding-icon" :class="binding.icon">{{ binding.icon }}</span>
              <span class="binding-type">{{ binding.type }}</span>
              <span class="binding-status" :class="getBindingStatusClass(binding.status)">
                {{ getBindingStatusText(binding.status) }}
              </span>
              <div class="binding-actions">
                <button class="btn-bind" v-if="!binding.isBound" @click="bindAccount(binding.type)">
                  {{ binding.bindText }}
                </button>
                <button class="btn-unbind" v-if="binding.isBound" @click="unbindAccount(binding.type)">
                  {{ binding.unbindText }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在保存设置...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { useRouter } from 'vue-router'
import type { AccountInfo, PasswordForm, PrivacySettings, AccountBinding } from '@/types/settings'
import { getAccountSettings, updateAccountSettings, changePassword, uploadAvatar, bindAccount, unbindAccount } from '@/api/settings'

const router = useRouter()
const settingsStore = useSettingsStore()

const canEditUsername = ref<boolean>(false)
const canEditEmail = ref<boolean>(false)

const accountInfo = reactive<AccountInfo>({
  username: '',
  email: '',
  phone: '',
  nickname: '',
  gender: '',
  birthday: '',
  location: '',
  profession: '',
  avatar: ''
})

const passwordForm = reactive<PasswordForm>({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const privacySettings = reactive<PrivacySettings>({
  publicProfile: false,
  publicTrades: false,
  allowView: false,
  showOnline: false
})

const accountBindings = ref<AccountBinding[]>([])

const passwordStrength = ref<number>(0)

const avatarInput = ref<HTMLInputElement>()

const isLoading = ref<boolean>(false)

const loadAccountSettings = async () => {
  try {
    const response = await getAccountSettings()
    
    if (response.code === 200 && response.data) {
      const settings = response.data.data
      
      Object.assign(accountInfo, settings.accountInfo)
      Object.assign(privacySettings, settings.privacySettings)
      accountBindings.value = settings.accountBindings || []
      
      canEditUsername.value = settings.canEditUsername
      canEditEmail.value = settings.canEditEmail
    } else {
      console.error('Failed to load account settings:', response.message)
    }
  } catch (error) {
    console.error('Error loading account settings:', error)
    throw error
  }
}

const saveSettings = async () => {
  try {
    isLoading.value = true
    
    const response = await updateAccountSettings({
      accountInfo: accountInfo,
      privacySettings: privacySettings
    })
    
    if (response.code === 200) {
      console.log('Account settings saved successfully')
      alert('账户设置保存成功！')
    } else {
      console.error('Failed to save account settings:', response.message)
      alert('保存失败：' + response.message)
    }
  } catch (error) {
    console.error('Error saving settings:', error)
  } finally {
    isLoading.value = false
  }
}

const resetSettings = () => {
  if (confirm('确定要重置所有设置吗？')) {
    loadAccountSettings()
  }
}

const uploadAvatar = () => {
  avatarInput.value?.click()
}

const handleAvatarUpload = async (event: Event) => {
  try {
    const input = event.target as HTMLInputElement
    const file = input.files?.[0]
    
    if (file) {
      const response = await uploadAvatar(file)
      
      if (response.code === 200) {
        accountInfo.avatar = response.data.data.avatarUrl
        console.log('Avatar uploaded successfully')
      } else {
        console.error('Failed to upload avatar:', response.message)
        alert('上传失败：' + response.message)
      }
    }
  } catch (error) {
    console.error('Error uploading avatar:', error)
    alert('上传失败：' + error.message)
  }
}

const removeAvatar = async () => {
  if (confirm('确定要移除头像吗？')) {
    try {
      const response = await updateAccountSettings({
        accountInfo: { ...accountInfo, avatar: '' }
      })
      
      if (response.code === 200) {
        accountInfo.avatar = ''
        console.log('Avatar removed successfully')
      } else {
        console.error('Failed to remove avatar:', response.message)
      }
    } catch (error) {
      console.error('Error removing avatar:', error)
    }
  }
}

const resetAvatar = async () => {
  if (confirm('确定要重置为默认头像吗？')) {
    try {
      const response = await updateAccountSettings({
        accountInfo: { ...accountInfo, avatar: '/default-avatar.png' }
      })
      
      if (response.code === 200) {
        accountInfo.avatar = '/default-avatar.png'
        console.log('Avatar reset successfully')
      } else {
        console.error('Failed to reset avatar:', response.message)
      }
    } catch (error) {
      console.error('Error resetting avatar:', error)
    }
  }
}

const changePassword = async () => {
  try {
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      alert('两次输入的新密码不一致！')
      return
    }
    
    if (passwordForm.newPassword.length < 8) {
      alert('新密码长度至少8位！')
      return
    }
    
    const response = await changePassword({
      currentPassword: passwordForm.currentPassword,
      newPassword: passwordForm.newPassword
    })
    
    if (response.code === 200) {
      console.log('Password changed successfully')
      alert('密码修改成功！')
      resetPasswordForm()
    } else {
      console.error('Failed to change password:', response.message)
      alert('修改失败：' + response.message)
    }
  } catch (error) {
    console.error('Error changing password:', error)
    alert('修改失败：' + error.message)
  }
}

const resetPasswordForm = () => {
  passwordForm.currentPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}

const bindAccount = async (type: string) => {
  try {
    const response = await bindAccount(type)
    
    if (response.code === 200) {
      console.log('Account bound successfully')
      alert('绑定成功！')
      loadAccountSettings()
    } else {
      console.error('Failed to bind account:', response.message)
      alert('绑定失败：' + response.message)
    }
  } catch (error) {
    console.error('Error binding account:', error)
    alert('绑定失败：' + error.message)
  }
}

const unbindAccount = async (type: string) => {
  try {
    if (confirm('确定要解除绑定吗？')) {
      const response = await unbindAccount(type)
      
      if (response.code === 200) {
        console.log('Account unbound successfully')
        alert('解除绑定成功！')
        loadAccountSettings()
      } else {
        console.error('Failed to unbind account:', response.message)
        alert('解除绑定失败：' + response.message)
      }
    }
  } catch (error) {
    console.error('Error unbinding account:', error)
    alert('解除绑定失败：' + error.message)
  }
}

const getStrengthClass = (strength: number) => {
  if (strength >= 4) return 'strength-strong'
  if (strength >= 3) return 'strength-medium'
  if (strength >= 2) return 'strength-fair'
  return 'strength-weak'
}

const getStrengthTextClass = (strength: number) => {
  return getStrengthClass(strength)
}

const getStrengthText = (strength: number) => {
  if (strength >= 4) return '强'
  if (strength >= 3) return '中'
  if (strength >= 2) return '弱'
  return '非常弱'
}

const getBindingStatusClass = (status: string) => {
  if (status === 'bound') return 'status-bound'
  if (status === 'unbound') return 'status-unbound'
  return 'status-unknown'
}

const getBindingStatusText = (status: string) => {
  const texts = {
    bound: '已绑定',
    unbound: '未绑定',
    unknown: '未知'
  }
  return texts[status] || '未知'
}

onMounted(async () => {
  await loadAccountSettings()
  console.log('AccountSettings component mounted')
})
</script>

<style scoped lang="scss">
.account-settings-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.account-settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.account-settings-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.account-settings-actions {
  display: flex;
  gap: 10px;
}

.btn-primary,
.btn-secondary,
.btn-upload,
.btn-remove,
.btn-reset {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background: #2196f3;
  color: white;
}

.btn-primary:hover {
  background: #1976d2;
}

.btn-secondary {
  background: transparent;
  color: #2196f3;
  border: 1px solid #2196f3;
}

.btn-secondary:hover {
  background: #f0f0f0;
  border-color: #2196f3;
}

.account-info-section {
  margin-bottom: 20px;
}

.info-card {
  background: white;
  border-radius: 8px;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.card-body {
  padding: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.info-input,
.info-select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.info-input:focus,
.info-select:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 3px rgba(33, 150, 243, 0.2);
}

.avatar-settings-section {
  margin-bottom: 20px;
}

.avatar-card {
  background: white;
  border-radius: 8px;
}

.avatar-display {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.avatar-image {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #ddd;
}

.avatar-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.btn-upload {
  background: #4caf50;
  color: white;
}

.btn-upload:hover {
  background: #45a049;
}

.btn-remove {
  background: #f44336;
  color: white;
}

.btn-remove:hover {
  background: #da190b;
}

.btn-reset {
  background: #2196f3;
  color: white;
}

.btn-reset:hover {
  background: #1976d2;
}

.password-settings-section {
  margin-bottom: 20px;
}

.password-card {
  background: white;
  border-radius: 8px;
}

.password-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.form-input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 3px rgba(33, 150, 243, 0.2);
}

.password-strength {
  margin-bottom: 20px;
}

.strength-bar {
  width: 100%;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.strength-fill {
  height: 100%;
  background: #f44336;
  transition: all 0.3s;
}

.strength-fill.strength-weak {
  background: #f44336;
  width: 25%;
}

.strength-fill.strength-fair {
  background: #ffc107;
  width: 50%;
}

.strength-fill.strength-medium {
  background: #4caf50;
  width: 75%;
}

.strength-fill.strength-strong {
  background: #2196f3;
  width: 100%;
}

.strength-text {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.strength-text.strength-weak {
  color: #f44336;
}

.strength-text.strength-fair {
  color: #ffc107;
}

.strength-text.strength-medium {
  color: #4caf50;
}

.strength-text.strength-strong {
  color: #2196f3;
}

.password-actions {
  display: flex;
  gap: 10px;
}

.privacy-settings-section {
  margin-bottom: 20px;
}

.privacy-card {
  background: white;
  border-radius: 8px;
}

.privacy-settings-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.privacy-setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}

.setting-label {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
  cursor: pointer;
}

.toggle-switch input {
  display: none;
}

.toggle-slider {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: #ccc;
  border-radius: 50%;
  transition: all 0.3s;
}

.toggle-switch input:checked + .toggle-slider {
  background: #2196f3;
  left: calc(100% - 20px);
}

.account-binding-section {
  margin-bottom: 20px;
}

.binding-card {
  background: white;
  border-radius: 8px;
}

.binding-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.binding-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}

.binding-icon {
  font-size: 24px;
  margin-right: 10px;
}

.binding-icon.wechat {
  color: #09bb07;
}

.binding-icon.qq {
  color: #1296db;
}

.binding-icon.weibo {
  color: #e6162d;
}

.binding-icon.alipay {
  color: #00a0e9;
}

.binding-type {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  flex: 1;
}

.binding-status {
  font-size: 14px;
  font-weight: 500;
  margin: 0 15px;
}

.binding-status.status-bound {
  color: #4caf50;
}

.binding-status.status-unbound {
  color: #999;
}

.binding-actions {
  display: flex;
  gap: 10px;
}

.btn-bind,
.btn-unbind {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-bind {
  background: #4caf50;
  color: white;
}

.btn-bind:hover {
  background: #45a049;
}

.btn-unbind {
  background: #f44336;
  color: white;
}

.btn-unbind:hover {
  background: #da190b;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #2196f3;
  border-top-color: transparent;
  border-right-color: #2196f3;
  border-bottom-color: #2196f3;
  border-left-color: #2196f3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: white;
  font-size: 16px;
  font-weight: 500;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .info-grid,
  .password-form {
    grid-template-columns: 1fr;
  }
}
</style>
