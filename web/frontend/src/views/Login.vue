<template>
  <main class="login-container" aria-labelledby="login-title">
    <div class="login-stage" aria-hidden="true"></div>

    <section class="login-card" :aria-busy="loading">
      <div class="login-header">
        <p class="eyebrow">MYSTOCKS ACCESS GATE</p>
        <h1 id="login-title" class="title">LOGIN</h1>
        <p class="subtitle">QUANTITATIVE TRADING MANAGEMENT SYSTEM</p>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="label" for="login-username">USERNAME</label>
          <input
            id="login-username"
            v-model="loginForm.username"
            type="text"
            class="input"
            placeholder="ENTER USERNAME"
            data-testid="username-input"
            autocomplete="username"
            spellcheck="false"
            @input="clearStatusMessage"
          >
        </div>

        <div class="form-group">
          <label class="label" for="login-password">PASSWORD</label>
          <input
            id="login-password"
            v-model="loginForm.password"
            type="password"
            class="input"
            placeholder="ENTER PASSWORD"
            data-testid="password-input"
            autocomplete="current-password"
            @keyup.enter="handleLogin"
            @input="clearStatusMessage"
          >
        </div>

        <p
          v-if="statusMessage"
          :class="['status-message', `status-message--${statusTone}`]"
          role="status"
          aria-live="polite"
        >
          {{ statusMessage }}
        </p>

        <button
          type="submit"
          class="submit-button"
          :disabled="loading"
          data-testid="login-button"
        >
          <span v-if="loading" class="spinner" aria-hidden="true"></span>
          <span>{{ loading ? 'SIGNING IN' : 'SIGN IN' }}</span>
        </button>
      </form>

      <section
        v-if="showTestAccounts"
        class="test-accounts"
        aria-labelledby="test-accounts-title"
      >
        <div class="divider">
          <span id="test-accounts-title" class="divider-text">TEST ACCOUNTS</span>
        </div>
        <p class="account-hint">Use the seeded demo credentials below for shell access checks.</p>
        <div class="account-row" data-testid="admin-account-hint">
          <span class="account-label">ADMIN</span>
          <span class="account-value">admin / admin123</span>
        </div>
        <div class="account-row" data-testid="user-account-hint">
          <span class="account-label">USER</span>
          <span class="account-value">user / user123</span>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { HOME_ROUTE_PATH, normalizeLegacyHomeRedirect } from '@/router/homeRoute'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loading = computed(() => authStore.isLoading)
const statusMessage = ref('')
const statusTone = ref<'neutral' | 'error' | 'success'>('neutral')
const showTestAccounts = computed(() => import.meta.env.DEV || import.meta.env.VITE_SHOW_TEST_ACCOUNTS === '1')

interface LoginForm {
  username: string
  password: string
}

const loginForm = reactive<LoginForm>({
  username: '',
  password: ''
})

interface LoginResult {
  success: boolean
  message?: string
}

const setStatusMessage = (message: string, tone: 'neutral' | 'error' | 'success' = 'neutral') => {
  statusMessage.value = message
  statusTone.value = tone
}

const clearStatusMessage = () => {
  if (statusMessage.value) {
    statusMessage.value = ''
    statusTone.value = 'neutral'
  }
}

const handleLogin = async (): Promise<void> => {
  if (!loginForm.username || !loginForm.password) {
    setStatusMessage('PLEASE ENTER USERNAME AND PASSWORD', 'error')
    ElMessage.error('PLEASE ENTER USERNAME AND PASSWORD')
    return
  }

  if (loginForm.password.length < 6) {
    setStatusMessage('PASSWORD MUST BE AT LEAST 6 CHARACTERS', 'error')
    ElMessage.error('PASSWORD MUST BE AT LEAST 6 CHARACTERS')
    return
  }

  setStatusMessage('AUTHENTICATING ACCESS REQUEST...', 'neutral')
  try {
    const result: LoginResult = await authStore.login(loginForm.username, loginForm.password)

    if (result.success) {
      setStatusMessage('LOGIN SUCCESSFUL. REDIRECTING...', 'success')
      ElMessage.success('LOGIN SUCCESSFUL')
      const redirect = normalizeLegacyHomeRedirect((route.query.redirect as string) || HOME_ROUTE_PATH)
      router.push(redirect)
    } else {
      setStatusMessage(result.message || 'LOGIN FAILED', 'error')
      ElMessage.error(result.message || 'LOGIN FAILED')
    }
  } catch (_error) {
    setStatusMessage('LOGIN FAILED', 'error')
    ElMessage.error('LOGIN FAILED')
  }
}
</script>

<style scoped lang="scss">
.login-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: var(--artdeco-spacing-8);
  overflow: hidden;
  background:
    radial-gradient(circle at top, rgb(212 175 55 / 14%), transparent 28%),
    linear-gradient(180deg, rgb(17 17 24 / 96%), rgb(10 10 10 / 98%)),
    var(--artdeco-bg-global);
}

.login-stage {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.36;
  background-image:
    linear-gradient(90deg, transparent 0, rgb(212 175 55 / 10%) 50%, transparent 100%),
    repeating-linear-gradient(
      45deg,
      transparent 0,
      transparent 12px,
      rgb(212 175 55 / 6%) 12px,
      rgb(212 175 55 / 6%) 13px
    );
}

.login-card {
  position: relative;
  z-index: 1;
  width: min(100%, 32rem);
  padding: var(--artdeco-spacing-8);
  border: 1px solid var(--artdeco-border-accent);
  background:
    linear-gradient(180deg, rgb(26 26 26 / 95%), rgb(10 10 10 / 92%)),
    var(--artdeco-bg-card);
  box-shadow:
    0 0 0 1px rgb(212 175 55 / 10%) inset,
    0 24px 64px rgb(0 0 0 / 45%),
    0 0 24px rgb(212 175 55 / 14%);
}

.login-header {
  margin-bottom: var(--artdeco-spacing-6);
  text-align: center;
}

.eyebrow {
  margin: 0 0 var(--artdeco-spacing-3);
  font-family: var(--font-mono);
  font-size: var(--artdeco-text-xs);
  letter-spacing: var(--artdeco-tracking-widest);
  text-transform: uppercase;
  color: var(--artdeco-gold-light);
}

.title {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(2.25rem, 5vw, 3rem);
  line-height: 1;
  letter-spacing: var(--artdeco-tracking-widest);
  color: var(--artdeco-gold-primary);
}

.subtitle {
  margin: var(--artdeco-spacing-3) 0 0;
  font-family: var(--font-body);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
  letter-spacing: var(--artdeco-tracking-wide);
  color: var(--artdeco-fg-muted);
}

.login-form {
  display: grid;
  gap: var(--artdeco-spacing-4);
}

.form-group {
  display: grid;
  gap: var(--artdeco-spacing-2);
}

.label {
  font-family: var(--font-display);
  font-size: var(--artdeco-text-xs);
  letter-spacing: var(--artdeco-tracking-wider);
  text-transform: uppercase;
  color: var(--artdeco-gold-light);
}

.input {
  width: 100%;
  min-height: 3rem;
  padding: 0 var(--artdeco-spacing-4);
  border: 1px solid var(--artdeco-border-default);
  background: rgb(255 255 255 / 2%);
  color: var(--artdeco-fg-primary);
  font-family: var(--font-body);
  font-size: var(--artdeco-text-base);
  transition:
    border-color var(--artdeco-transition-quick) ease,
    box-shadow var(--artdeco-transition-quick) ease,
    background-color var(--artdeco-transition-quick) ease;
}

.input::placeholder {
  color: var(--artdeco-fg-subtle);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}

.input:hover {
  border-color: var(--artdeco-border-accent);
}

.input:focus-visible {
  outline: none;
  border-color: var(--artdeco-gold-primary);
  background: rgb(255 255 255 / 4%);
  box-shadow: 0 0 0 3px rgb(212 175 55 / 14%);
}

.submit-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--artdeco-spacing-2);
  width: 100%;
  min-height: 3.25rem;
  margin-top: var(--artdeco-spacing-2);
  border: 1px solid var(--artdeco-gold-primary);
  background: linear-gradient(90deg, var(--artdeco-gold-primary), var(--artdeco-gold-light));
  color: var(--artdeco-bg-global);
  font-family: var(--font-display);
  font-size: var(--artdeco-text-sm);
  font-weight: var(--artdeco-font-semibold);
  letter-spacing: var(--artdeco-tracking-widest);
  text-transform: uppercase;
  cursor: pointer;
  transition:
    transform var(--artdeco-transition-quick) ease,
    box-shadow var(--artdeco-transition-quick) ease,
    filter var(--artdeco-transition-quick) ease;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 0 20px rgb(212 175 55 / 28%);
  filter: brightness(1.03);
}

.submit-button:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgb(212 175 55 / 18%);
}

.submit-button:disabled {
  cursor: wait;
  opacity: 0.75;
}

.status-message {
  margin: 0;
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  border: 1px solid var(--artdeco-border-default);
  background: rgb(255 255 255 / 3%);
  font-family: var(--font-mono);
  font-size: var(--artdeco-text-xs);
  letter-spacing: var(--artdeco-tracking-wide);
}

.status-message--neutral {
  color: var(--artdeco-gold-light);
}

.status-message--error {
  color: var(--artdeco-rise);
  border-color: rgb(255 82 82 / 45%);
  background: rgb(255 82 82 / 8%);
}

.status-message--success {
  color: var(--artdeco-gold-light);
  border-color: rgb(212 175 55 / 45%);
  background: rgb(212 175 55 / 8%);
}

.spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgb(0 0 0 / 18%);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: login-spin 0.7s linear infinite;
}

.test-accounts {
  margin-top: var(--artdeco-spacing-6);
  padding-top: var(--artdeco-spacing-5);
  border-top: 1px solid var(--artdeco-border-default);
}

.divider {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-3);
  margin-bottom: var(--artdeco-spacing-3);
}

.divider::before,
.divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgb(212 175 55 / 34%), transparent);
}

.divider-text {
  font-family: var(--font-display);
  font-size: var(--artdeco-text-xs);
  letter-spacing: var(--artdeco-tracking-widest);
  text-transform: uppercase;
  color: var(--artdeco-gold-primary);
}

.account-hint {
  margin: 0 0 var(--artdeco-spacing-3);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}

.account-row {
  display: flex;
  justify-content: space-between;
  gap: var(--artdeco-spacing-4);
  padding: var(--artdeco-spacing-2) 0;
  border-bottom: 1px solid rgb(212 175 55 / 10%);
}

.account-row:last-child {
  border-bottom: 0;
}

.account-label,
.account-value {
  font-size: var(--artdeco-text-sm);
}

.account-label {
  color: var(--artdeco-gold-light);
  font-family: var(--font-display);
  letter-spacing: var(--artdeco-tracking-wide);
}

.account-value {
  color: var(--artdeco-fg-primary);
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
}

@keyframes login-spin {
  to {
    transform: rotate(360deg);
  }
}

@media (width <= 768px) {
  .login-container {
    padding: var(--artdeco-spacing-5);
  }

  .login-card {
    padding: var(--artdeco-spacing-6);
  }

  .account-row {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--artdeco-spacing-1);
  }
}

@media (width <= 390px) {
  .login-container {
    padding: var(--artdeco-spacing-4);
  }

  .login-card {
    padding: var(--artdeco-spacing-5);
  }

  .submit-button,
  .input {
    min-height: 2.875rem;
  }
}
</style>
