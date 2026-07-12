import { createRouter, createWebHistory } from 'vue-router'

import Landing from '../views/Landing.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Dashboard from '@/views/admin/Dashboard.vue'

const routes = [
    { path: '/', name: 'Landing', component: Landing },
    { path: '/login', name: 'Login', component: Login },
    { path: '/register', name: 'Register', component: Register },
    { path: '/admin', name: 'AdminDashboard', component: Dashboard}
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router