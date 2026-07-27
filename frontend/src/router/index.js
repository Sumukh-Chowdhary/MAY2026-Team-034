import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Landing', component: () => import('@/views/Landing.vue') },
  { path: '/login', name: 'Login', component: () => import('@/views/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('@/views/Register.vue') },
  { path: '/clubs', name: 'Clubs', component: () => import('@/views/ClubsPage.vue') },
  { path: '/admin', name: 'AdminDashboard', component: () => import('@/views/admin/Dashboard.vue') },
  { path: '/admin/requests', name: 'AdminRequests', component: () => import('@/views/admin/Requests.vue') },
  { path: '/admin/clubs', name: 'AdminClubs', component: () => import('@/views/admin/Clubs.vue') },
  { path: '/admin/users', name: 'AdminUsers', component: () => import('@/views/admin/Users.vue') },
  { path: '/admin/users/:id', name: 'AdminUserDetails', component: () => import('@/views/admin/UserDetails.vue') },
  { path: '/admin/events', name: 'AdminEvents', component: () => import('@/views/admin/Events.vue') },
  { path: '/admin/events/:id', name: 'AdminEventDetail', component: () => import('@/views/admin/EventDetails.vue') },
  { path: '/faculty', name: 'FacultyDashboard', component: () => import('@/views/faculty/Dashboard.vue') },
  { path: '/faculty/clubs', name: 'FacultyClubs', component: () => import('@/views/faculty/Clubs.vue') },
  { path: '/faculty/requests', name: 'FacultyRequests', component: () => import('@/views/faculty/Requests.vue') },
  { path: '/faculty/roles', name: 'FacultyRoles', component: () => import('@/views/faculty/Roles.vue') },
  { path: '/faculty/events', name: 'FacultyEvents', component: () => import('@/views/faculty/Events.vue') },
  { path: '/faculty/events/:id', name: 'FacultyEventDetail', component: () => import('@/views/faculty/EventDetails.vue') },
  { path: '/student', name: 'StudentDashboard', component: () => import('@/views/student/Dashboard.vue') },
  { path: '/student/clubs', name: 'StudentClubs', component: () => import('@/views/student/Clubs.vue') },
  { path: '/student/requests', name: 'StudentRequests', component: () => import('@/views/student/Requests.vue') },
  { path: '/student/roles', name: 'StudentRoles', component: () => import('@/views/student/Roles.vue') },
  { path: '/student/events', name: 'StudentEvents', component: () => import('@/views/student/Events.vue') },
  { path: '/student/events/:id', name: 'StudentEventDetail', component: () => import('@/views/student/EventDetails.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router