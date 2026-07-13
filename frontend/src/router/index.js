import { createRouter, createWebHistory } from 'vue-router'

import Landing from '../views/Landing.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import ClubsPage from '../pages/Clubs/ClubsPage.vue'
import Dashboard from '@/views/admin/Dashboard.vue'
import Requests from '@/views/admin/Requests.vue'
import Users from '@/views/admin/Users.vue'
import UserDetails from '@/views/admin/UserDetails.vue'

const routes = [
  { path: '/', name: 'Landing', component: Landing },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/clubs', name: 'Clubs', component: ClubsPage },
  { path: '/admin', name: 'AdminDashboard', component: Dashboard },
  { path: '/admin/requests', name:'AdminRequests', component: Requests },
  { path: '/admin/users', name: 'AdminUsers', component: Users },
  { path: '/admin/users/:id', name: 'AdminUserDetails', component: UserDetails }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router