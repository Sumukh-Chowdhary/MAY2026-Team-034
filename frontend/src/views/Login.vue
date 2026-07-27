<script setup>
import {ref} from 'vue'
import {useRouter} from 'vue-router'
import {login} from '../services/authService'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const router=useRouter()

const username=ref('')
const password=ref('')

async function handleLogin() {
    try {
        const user = await login(
            username.value,
            password.value
        );
        // Save logged-in user to Pinia
        auth.setUser(
            user,
            localStorage.getItem("token")
        );

        if (auth.isAdmin) {
            router.push("/admin");
        }
        else if (auth.isFaculty) {
            router.push("/faculty");
        }
        else {
            router.push("/student");
        }
    } catch (err) {
        alert(err.response?.data?.error || "Login Failed");
    }
}
</script>

<template>
    <section class="login-page">
        <div class="container d-flex justify-content-center align-items-center">
            <div class="card shadow border-0 login-card">
                <div class="card-body p-5">
                    <h2 class="text-center fw-bold mb-4">Login</h2>
                    <div class="mb-3">
                        <label class="form-label">Register Number / Email</label>
                        <input v-model="username" type="text" class="form-control" placeholder="Enter register number or email">
                    </div>
                    <div class="mb-4">
                        <label class="form-label">Password</label>
                        <input v-model="password" type="password"class="form-control" placeholder="Enter password">
                    </div>
                    <button class="btn btn-primary w-100" @click="handleLogin">Login</button>
                    <p class="text-center mt-4 mb-0">Don't have an account?
                        <RouterLink to="/register">Register</RouterLink>
                    </p>
                </div>
            </div>
        </div>
    </section>
</template>

<style scoped>
.login-page{
    min-height:calc(100vh - 150px);
    display:flex;
    align-items:center;
}

.login-card{
    width:100%;
    max-width:430px;
    border-radius:18px;
}
</style>