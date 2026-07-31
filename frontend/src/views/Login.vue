<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../services/authService'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'

const auth = useAuthStore()
const router = useRouter()
const { showToast } = useToast()

const username = ref('')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!username.value.trim() || !password.value.trim()) {
    showToast('Please enter both username/email and password.', 'warning')
    return
  }

  loading.value = true
  try {
    const user = await login(username.value, password.value)
    auth.setUser(user, localStorage.getItem('token'))

    showToast(`Welcome back, ${user.name || 'User'}!`, 'success')

    if (auth.isAdmin) {
      router.push('/admin')
    } else if (auth.isFaculty) {
      router.push('/faculty')
    } else {
      router.push('/student')
    }
  } catch (err) {
    const errorMsg = err.response?.data?.error || 'Incorrect username or password.'
    showToast(errorMsg, 'error')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="login-page">
    <div class="container d-flex justify-content-center align-items-center">
      <div class="card shadow border-0 login-card">
        <div class="card-body p-5">
          <h2 class="text-center fw-bold mb-4">Login to AllClub</h2>
          
          <div class="mb-3">
            <label class="form-label">Register Number / Email</label>
            <input 
              v-model="username" 
              type="text" 
              class="form-control" 
              placeholder="Enter register number or email"
              @keyup.enter="handleLogin"
            />
          </div>

          <div class="mb-4">
            <label class="form-label">Password</label>
            <input 
              v-model="password" 
              type="password" 
              class="form-control" 
              placeholder="Enter password"
              @keyup.enter="handleLogin"
            />
          </div>

          <button class="btn btn-primary w-100 font-semibold rounded-pill py-2" :disabled="loading" @click="handleLogin">
            <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
            <span v-else>Login</span>
          </button>

          <p class="text-center mt-4 mb-0 text-sm">
            Don't have an account?
            <RouterLink to="/register" class="fw-semibold text-primary">Register</RouterLink>
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.login-page {
  min-height: calc(100vh - 150px);
  display: flex;
  align-items: center;
}

.login-card {
  width: 100%;
  max-width: 430px;
  border-radius: 20px;
}
</style>