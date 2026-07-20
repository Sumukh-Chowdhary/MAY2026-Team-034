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
import Users from '@/views/admin/Users.vue'
import UserDetails from '@/views/admin/UserDetails.vue'

import FDashboard from '@/views/faculty/Dashboard.vue'
import fRequests from '@/views/faculty/Requests.vue'
import FClubs from '@/views/faculty/Clubs.vue'

import SDashboard from '@/views/student/Dashboard.vue'
import SClubs from '@/views/student/Clubs.vue'
import SRequests from '@/views/student/Requests.vue'

const routes = [
  { path: '/', name: 'Landing', component: Landing },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/clubs', name: 'Clubs', component: ClubsPage },
  { path: '/events/:id', name: 'EventDetail', component: EventDetails},
  { path: '/admin', name: 'AdminDashboard', component: Dashboard },
  { path: '/admin/requests', name:'AdminRequests', component: Requests },
  { path: '/admin/clubs', name:'AdminClubs', component: Clubs },
  { path: '/admin/users', name:'AdminUsers', component: Users },
  { path: '/admin/users/:id', name:'AdminUserDetails', component: UserDetails },
  { path: '/admin/events', name:'AdminEvents', component: Events },
  { path: '/admin/events/:id', name: 'EventDetail', component: EventDetails},
  { path: '/faculty', name:'FacultyDashboard', component: FDashboard},
  { path: '/faculty/clubs', name:'FacultyClubs', component: FClubs},
  { path: '/faculty/requests', name:'FacultyRequests', component: fRequests},
  { path: '/student', name:'StudentDashboard', component: SDashboard},
  { path: '/student/clubs', name:'StudentClubs', component: SClubs},
  { path: '/student/requests', name:'StudentRequests', component: SRequests},
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router