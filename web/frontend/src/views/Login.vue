<template>
  <div class="login-shell page-enter">
    <div class="login-backdrop" aria-hidden="true"></div>

    <section class="login-panel" aria-labelledby="login-title">
      <header class="login-header">
        <p class="eyebrow">MYSTOCKS</p>
        <h1 id="login-title" class="title">交易系统登录</h1>
        <p class="subtitle">量化交易管理中枢</p>
      </header>

      <ArtDecoAlert
        v-if="errorMessage"
        class="login-alert"
        type="error"
        title="登录提示"
        :message="errorMessage"
        :dismissible="false"
      />

      <form class="login-form" @submit.prevent="handleLogin">
        <label class="field" for="username-input">
          <span class="field-label">USERNAME</span>
          <input
            id="username-input"
            v-model="loginForm.username"
            type="text"
            class="field-input"
            placeholder="ENTER USERNAME"
            data-testid="username-input"
            autocomplete="username"
          >
        </label>

        <label class="field" for="password-input">
          <span class="field-label">PASSWORD</span>
          <input
            id="password-input"
            v-model="loginForm.password"
            type="password"
            class="field-input"
            placeholder="ENTER PASSWORD"
            data-testid="password-input"
            autocomplete="current-password"
            @keyup.enter="handleLogin"
          >
        </label>

        <button
          type="submit"
          class="login-submit"
          :disabled="loading"
          data-testid="login-button"
        >
          <span v-if="loading" class="spinner" aria-hidden="true"></span>
          <span>{{ loading ? 'SIGNING IN' : 'SIGN IN' }}</span>
        </button>
      </form>

      <footer class="test-accounts">
        <div class="accounts-header">TEST ACCOUNTS</div>
        <div class="account-row" data-testid="admin-account-hint">
          <span class="account-label">ADMIN</span>
          <span class="account-value">admin / admin123</span>
        </div>
        <div class="account-row" data-testid="user-account-hint">
          <span class="account-label">USER</span>
          <span class="account-value">user / user123</span>
        </div>
      </footer>
    </section>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArtDecoAlert } from '@/components/artdeco'
import { useAuthStore } from '@/stores/auth'
import { HOME_ROUTE_PATH, normalizeLegacyHomeRedirect } from '@/router/homeRoute'

interface LoginForm {
  username: string
  password: string
}

interface LoginResult {
  success: boolean
  message?: string
}

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loading = ref(false)
const errorMessage = ref('')
const loginForm = reactive<LoginForm>({
  username: '',
  password: ''
})

const handleLogin = async (): Promise<void> => {
  const username = loginForm.username.trim()
  const password = loginForm.password

  if (!username || !password) {
    errorMessage.value = '请输入用户名和密码'
    return
  }

  if (password.length < 6) {
    errorMessage.value = '密码长度不能少于 6 位'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    const result = await authStore.login(username, password) as LoginResult
    if (!result.success) {
      errorMessage.value = result.message || '登录失败，请检查账号或网络状态'
      return
    }

    ElMessage.success('LOGIN SUCCESSFUL')
    const redirect = normalizeLegacyHomeRedirect((route.query.redirect as string) || HOME_ROUTE_PATH)
    await router.push(redirect)
  } catch (_error) {
    errorMessage.value = '登录失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.login-shell {
  position: relative;
  display: grid;
  place-items: center;
  min-height: 100vh;
  padding: var(--artdeco-spacing-6);
  overflow: hidden;
  background:
    radial-gradient(circle at top, rgb(212 175 55 / 14%), transparent 32%),
    linear-gradient(135deg, rgb(255 255 255 / 3%), transparent 45%),
    var(--artdeco-bg-global);
}

.login-backdrop {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, transparent 0%, rgb(212 175 55 / 6%) 50%, transparent 100%),
    repeating-linear-gradient(
      135deg,
      transparent 0,
      transparent calc(var(--artdeco-spacing-6) * 1.5),
      rgb(212 175 55 / 6%) calc(var(--artdeco-spacing-6) * 1.5),
      rgb(212 175 55 / 6%) calc(var(--artdeco-spacing-6) * 1.625)
    );
  opacity: 0.6;
  pointer-events: none;
}

.login-panel {
  position: relative;
  z-index: 1;
  display: grid;
  gap: var(--artdeco-spacing-5);
  width: min(100%, 32rem);
  padding: var(--artdeco-spacing-8);
  border: thin solid var(--artdeco-border-accent);
  background:
    linear-gradient(145deg, rgb(212 175 55 / 10%), transparent 38%),
    var(--artdeco-bg-card);
  box-shadow:
    0 0 0 1px rgb(212 175 55 / 12%),
    0 1.5rem 4rem rgb(0 0 0 / 45%);
}

.login-header {
  display: grid;
  gap: var(--artdeco-spacing-2);
  text-align: center;
}

.eyebrow {
  margin: 0;
  color: var(--artdeco-gold-primary);
  font-family: var(--font-display);
  font-size: var(--artdeco-text-sm);
  letter-spacing: var(--artdeco-tracking-widest);
  text-transform: uppercase;
}

.title {
  margin: 0;
  color: var(--artdeco-fg-primary);
  font-family: var(--font-display);
  font-size: clamp(var(--artdeco-text-2xl), 4vw, var(--artdeco-text-4xl));
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

.subtitle {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  letter-spacing: var(--artdeco-tracking-wider);
  text-transform: uppercase;
}

.login-alert {
  width: 100%;
}

.login-form {
  display: grid;
  gap: var(--artdeco-spacing-4);
}

.field {
  display: grid;
  gap: var(--artdeco-spacing-2);
}

.field-label {
  color: var(--artdeco-gold-primary);
  font-family: var(--font-display);
  font-size: var(--artdeco-text-xs);
  letter-spacing: var(--artdeco-tracking-widest);
  text-transform: uppercase;
}

.field-input {
  width: 100%;
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  border: thin solid var(--artdeco-border-default);
  background: rgb(255 255 255 / 2%);
  color: var(--artdeco-fg-primary);
  font-family: var(--font-body);
  font-size: var(--artdeco-text-base);
  transition:
    border-color 180ms ease,
    box-shadow 180ms ease,
    background-color 180ms ease;

  &::placeholder {
    color: var(--artdeco-fg-muted);
    letter-spacing: var(--artdeco-tracking-wide);
  }

  &:focus {
    outline: none;
    border-color: var(--artdeco-border-hover);
    background: rgb(212 175 55 / 6%);
    box-shadow: 0 0 1.25rem rgb(212 175 55 / 12%);
  }
}

.login-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--artdeco-spacing-2);
  width: 100%;
  min-height: 3rem;
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-5);
  border: thin solid var(--artdeco-border-hover);
  background: linear-gradient(135deg, var(--artdeco-gold-primary), var(--artdeco-bronze));
  color: var(--artdeco-bg-global);
  font-family: var(--font-display);
  font-size: var(--artdeco-text-sm);
  font-weight: var(--artdeco-font-semibold);
  letter-spacing: var(--artdeco-tracking-widest);
  text-transform: uppercase;
  cursor: pointer;
  transition:
    transform 180ms ease,
    box-shadow 180ms ease,
    opacity 180ms ease;

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 0.75rem 1.5rem rgb(212 175 55 / 25%);
  }

  &:disabled {
    opacity: 0.65;
    cursor: not-allowed;
  }
}

.spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgb(0 0 0 / 15%);
  border-top-color: currentColor;
  border-radius: 999px;
  animation: spin 0.7s linear infinite;
}

.test-accounts {
  display: grid;
  gap: var(--artdeco-spacing-2);
  padding-top: var(--artdeco-spacing-4);
  border-top: thin solid var(--artdeco-gold-opacity-20);
}

.accounts-header {
  color: var(--artdeco-fg-muted);
  font-family: var(--font-display);
  font-size: var(--artdeco-text-xs);
  letter-spacing: var(--artdeco-tracking-widest);
  text-transform: uppercase;
  text-align: center;
}

.account-row {
  display: flex;
  justify-content: space-between;
  gap: var(--artdeco-spacing-3);
  color: var(--artdeco-fg-primary);
  font-size: var(--artdeco-text-sm);
}

.account-label {
  color: var(--artdeco-gold-primary);
  font-family: var(--font-display);
  letter-spacing: var(--artdeco-tracking-wide);
}

.account-value {
  font-family: var(--font-mono);
  color: var(--artdeco-fg-muted);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
