import { createRouter, createWebHistory } from 'vue-router'

import Landing from '../views/Landing.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import ClubsPage from '../pages/Clubs/ClubsPage.vue'
import EventsPage from '../pages/Events/EventsPage.vue'
import EventDetailView from '../pages/Events/EventDetailView.vue'
import Dashboard from '@/views/admin/Dashboard.vue'
import Requests from '@/views/admin/Requests.vue'
import Clubs from '@/views/admin/Clubs.vue'

const routes = [
  { path: '/', name: 'Landing', component: Landing },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/clubs', name: 'Clubs', component: ClubsPage },
  { path: '/events', name: 'Events', component: EventsPage },
  { path: '/events/:id', name: 'EventDetail', component: EventDetailView },
  { path: '/admin', name: 'AdminDashboard', component: Dashboard },
  { path: '/admin/requests', name:'AdminRequests', component: Requests },
  { path: '/admin/clubs', name:'AdminClubs', component: Clubs }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router