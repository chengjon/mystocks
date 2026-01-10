<template>
  <div class="login-container">

    <div class="login-card">
      <div class="corner-tl"></div>
      <div class="corner-br"></div>

      <div class="login-header">
        <div class="divider">
          <span class="divider-text">MYSTOCKS</span>
        </div>
        <h1 class="title">LOGIN</h1>
        <p class="subtitle">QUANTITATIVE TRADING MANAGEMENT SYSTEM</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label class="label">USERNAME</label>
          <input
            v-model="loginForm.username"
            type="text"
            class="input"
            placeholder="ENTER USERNAME"
            data-testid="username-input"
          >
        </div>

        <div class="form-group">
          <label class="label">PASSWORD</label>
          <input
            v-model="loginForm.password"
            type="password"
            class="input"
            placeholder="ENTER PASSWORD"
            data-testid="password-input"
            @keyup.enter="handleLogin"
          >
        </div>

        <button
          type="submit"
          :disabled="loading"
          data-testid="login-button"
        >
          <span v-if="loading" class="spinner"></span>
          <span v-else>SIGN IN</span>
        </button>
      </form>

      <div class="test-accounts">
        <div class="divider">
          <span class="divider-text">TEST ACCOUNTS</span>
        </div>
        <div class="account-row" data-testid="admin-account-hint">
          <span class="account-label">ADMIN</span>
          <span class="account-value">admin / admin123</span>
        </div>
        <div class="account-row" data-testid="user-account-hint">
          <span class="account-label">USER</span>
          <span class="account-value">user / user123</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loading = ref<boolean>(false)

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

const handleLogin = async (): Promise<void> => {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.error('PLEASE ENTER USERNAME AND PASSWORD')
    return
  }

  if (loginForm.password.length < 6) {
    ElMessage.error('PASSWORD MUST BE AT LEAST 6 CHARACTERS')
    return
  }

  loading.value = true
  try {
    const result: LoginResult = await authStore.login(loginForm.username, loginForm.password)

    if (result.success) {
      ElMessage.success('LOGIN SUCCESSFUL')
      const redirect = (route.query.redirect as string) || '/'
      router.push(redirect)
    } else {
      ElMessage.error(result.message || 'LOGIN FAILED')
    }
  } catch (error) {
    ElMessage.error('LOGIN FAILED')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">

.login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background: var(--bg-primary);
  overflow: hidden;
}

.background-pattern {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.04;
  background-image:
    repeating-linear-gradient(
        45deg,
        var(--accent-gold) 0px,
        var(--accent-gold) 1px,
        transparent 1px,
        transparent 10px
      ),
      repeating-linear-gradient(
        -45deg,
        var(--accent-gold) 0px,
        var(--accent-gold) 1px,
        transparent 1px,
        transparent 10px
      );
  }

  .login-card {
    position: relative;
    width: 480px;
    background: var(--bg-card);
    border: 1px solid var(--accent-gold);
    border-radius: var(--radius-none);
    padding: var(--spacing-8);
    box-shadow: 0 0 40px rgba(212, 175, 55, 0.1);
    z-index: 1;
    transition: all var(--transition-base);
  }

  .corner-decoration {
    position: absolute;
    width: 24px;
    height: 24px;
    pointer-events: none;
    opacity: 0.6;
  }

  .corner-tl {
    top: 12px;
    left: 12px;
    border-top: 3px solid var(--accent-gold);
    border-left: 3px solid var(--accent-gold);
  }

  .corner-br {
    bottom: 12px;
    right: 12px;
    border-bottom: 3px solid var(--accent-gold);
    border-right: 3px solid var(--accent-gold);
  }

  .login-header {
    text-align: center;
    margin-bottom: var(--spacing-6);

    .logo-container {
      display: flex;
      align-items: center;
      gap: var(--spacing-4);
      margin-bottom: var(--spacing-4);
    }

    .logo-container {
      display: flex;
      align-items: center;
      gap: var(--spacing-4);
      margin-bottom: var(--spacing-4);

      &::before,
      &::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(
          to right,
          transparent,
          var(--accent-gold),
          transparent
        );
        opacity: 0.5;
      }
    }

    .logo-text {
      font-family: var(--font-display);
      font-size: var(--font-size-small);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: var(--tracking-widest);
      color: var(--accent-gold);
      padding: 0 var(--spacing-4);
    }

    .login-title {
      font-family: var(--font-display);
      font-size: var(--font-size-h2);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: var(--tracking-widest);
      color: var(--accent-gold);
      margin: var(--spacing-3) 0 var(--spacing-2) 0;
    }

    .login-subtitle {
      font-family: var(--font-body);
      font-size: var(--font-size-small);
      color: var(--fg-muted);
      text-transform: uppercase;
      letter-spacing: var(--tracking-wider);
      margin: 0;
    }
  }

  .login-form {
    margin-bottom: var(--spacing-6);

    .form-group {
      margin-bottom: var(--spacing-4);

      .form-label {
        display: block;

    .login-form {
      margin-bottom: var(--spacing-6);

      .form-group {
        margin-bottom: var(--spacing-4);

          display: block;
          font-family: var(--font-display);
          font-size: var(--font-size-xs);
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: var(--tracking-wider);
          color: var(--accent-gold);
          margin-bottom: var(--spacing-1);
        }

        .input {
          width: 100%;
          padding: var(--spacing-2) var(--spacing-3);
          font-family: var(--font-body);
          font-size: var(--font-size-body);
          color: var(--fg-primary);
          background: transparent;
          border: none;
          border-bottom: 2px solid var(--accent-gold);
          border-radius: var(--radius-none);
          transition: all var(--transition-base);

          &::placeholder {
            color: var(--fg-muted);
            text-transform: uppercase;
            letter-spacing: var(--tracking-normal);
          }

          &:focus {
            outline: none;
            border-bottom-color: var(--accent-gold-light);
            box-shadow: 0 4px 10px rgba(212, 175, 55, 0.2);
          }
        }
      }

      .btn-login {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: var(--spacing-3) var(--spacing-6);
        font-family: var(--font-display);
        font-size: var(--font-size-body);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: var(--tracking-widest);
        border: 2px solid var(--accent-gold);
        border-radius: var(--radius-none);
        cursor: pointer;
        transition: all var(--transition-base);
        margin-top: var(--spacing-4);

        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .spinner {
          display: inline-block;
          width: 20px;
          height: 20px;
          border: 2px solid rgba(0, 0, 0, 0.1);
          border-top-color: currentColor;
          border-radius: 50%;
          animation: spin 0.6s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      }

      .btn-login-primary {
        background: var(--accent-gold);
        color: var(--bg-primary);

        &:hover:not(:disabled) {
          background: var(--accent-gold-light);
          box-shadow: var(--glow-medium);
        }
      }
    }

    .test-accounts {
      text-align: center;
      padding-top: var(--spacing-4);
      border-top: 1px solid rgba(212, 175, 55, 0.2);

      .account-buttons {
        display: flex;
        align-items: center;
        gap: var(--spacing-4);
        margin-bottom: var(--spacing-3);

        &::before,
        &::after {
          content: '';
          flex: 1;
          height: 1px;
          background: linear-gradient(
            to right,
            transparent,
            var(--accent-gold),
            transparent
          );
          opacity: 0.3;
        }

          font-family: var(--font-display);
          font-size: var(--font-size-xs);
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: var(--tracking-widest);
          color: var(--fg-muted);
          padding: 0 var(--spacing-2);
        }
      }

      .account-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--spacing-2) 0;
        font-family: var(--font-body);

        .account-label {
          font-size: var(--font-size-small);
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: var(--tracking-wider);
          color: var(--fg-muted);
        }

        .account-value {
          font-size: var(--font-size-small);
          font-family: var(--font-body);
          color: var(--fg-secondary);
          letter-spacing: var(--tracking-normal);
        }
      }
    }
  }
</style>
