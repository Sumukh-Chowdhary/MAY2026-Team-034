import { createRouter, createWebHistory } from 'vue-router'

import Landing from '../views/Landing.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import ClubsPage from '../views/ClubsPage.vue'
import Events from '@/views/admin/Events.vue'
import EventDetails from '@/views/admin/EventDetails.vue'
import Dashboard from '@/views/admin/Dashboard.vue'
import Requests from '@/views/admin/Requests.vue'
import Clubs from '@/views/admin/Clubs.vue'

import FDashboard from '@/views/faculty/Dashboard.vue'

import SDashboard from '@/views/student/Dashboard.vue'

const routes = [
  { path: '/', name: 'Landing', component: Landing },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/clubs', name: 'Clubs', component: ClubsPage },
  { path: '/events/:id', name: 'EventDetail', component: EventDetails},
  { path: '/admin', name: 'AdminDashboard', component: Dashboard },
  { path: '/admin/requests', name:'AdminRequests', component: Requests },
  { path: '/admin/clubs', name:'AdminClubs', component: Clubs },
  { path: '/admin/events', name:'AdminEvents', component: Events },
  { path: '/admin/events/:id', name: 'EventDetail', component: EventDetails},
  { path: '/faculty', name:'FacultyDashboard', component: FDashboard},
  { path: '/student', name:'StudentDashboard', component: SDashboard},
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router