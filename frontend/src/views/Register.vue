<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '../services/authService'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'

const auth = useAuthStore()
const router = useRouter()
const { showToast } = useToast()

const fullName = ref('')
const email = ref('')
const registerNumber = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)

async function handleRegister() {
  if (!fullName.value.trim() || !email.value.trim() || !password.value.trim()) {
    showToast('Full Name, Email, and Password are required.', 'warning')
    return
  }

  if (password.value !== confirmPassword.value) {
    showToast('Password and Confirm Password do not match.', 'warning')
    return
  }

  loading.value = true
  try {
    const user = await register({
      fullName: fullName.value.trim(),
      email: email.value.trim(),
      password: password.value,
      registerNumber: registerNumber.value.trim() || undefined
    })

    auth.setUser(user, localStorage.getItem('token'))

    showToast(`Welcome, ${user.name || 'User'}!`, 'success')

    if (auth.isAdmin) {
      router.push('/admin')
    } else if (auth.isFaculty) {
      router.push('/faculty')
    } else {
      router.push('/student')
    }
  } catch (err) {
    const errorMsg = err.response?.data?.error || 'Registration failed. Please try again.'
    showToast(errorMsg, 'error')
  } finally {
    loading.value = false
  }
}
</script>

<template>
    <section class="register-page">
        <div class="container d-flex justify-content-center align-items-center">
            <div class="card shadow border-0 register-card">
                <div class="card-body p-5">
                    <h2 class="text-center fw-bold mb-4">Create Account</h2>
                    <div class="mb-3">
                        <label class="form-label">Full Name</label>
                        <input
                          v-model="fullName"
                          type="text"
                          class="form-control"
                          placeholder="Enter full name"
                          @keyup.enter="handleRegister"
                        >
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Email</label>
                        <input
                          v-model="email"
                          type="email"
                          class="form-control"
                          placeholder="Enter email"
                          @keyup.enter="handleRegister"
                        >
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Register Number</label>
                        <input
                          v-model="registerNumber"
                          type="text"
                          class="form-control"
                          placeholder="Enter register number"
                          @keyup.enter="handleRegister"
                        >
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Password</label>
                        <input
                          v-model="password"
                          type="password"
                          class="form-control"
                          placeholder="Create password"
                          @keyup.enter="handleRegister"
                        >
                    </div>
                    <div class="mb-4">
                        <label class="form-label">Confirm Password</label>
                        <input
                          v-model="confirmPassword"
                          type="password"
                          class="form-control"
                          placeholder="Confirm password"
                          @keyup.enter="handleRegister"
                        >
                    </div>
                    <button
                      class="btn btn-primary w-100"
                      :disabled="loading"
                      @click="handleRegister"
                    >
                        <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
                        <span v-else>Register</span>
                    </button>
                    <p class="text-center mt-4 mb-0"> Already have an account?
                        <RouterLink to="/login">Login</RouterLink>
                    </p>
                </div>
            </div>
        </div>
    </section>
</template>

<style scoped>
.register-page{
    padding:50px 0;
    display:flex;
    align-items:center;
}

.register-card{
    width:100%;
    max-width:450px;
    border-radius:18px;
}
</style>
