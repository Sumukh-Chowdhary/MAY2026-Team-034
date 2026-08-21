import { createRouter, createWebHistory } from 'vue-router';
import { isLoggedIn, getCurrentUser } from '@/services/authService';

const routes = [
  // --- Public Routes ---
  {
    path: '/',
    name: 'Landing',
    component: () => import('@/views/Landing.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue')
  },
  {
    path: '/clubs',
    name: 'Clubs',
    component: () => import('@/views/ClubsPage.vue')
  },
  {
    path: "/clubs/:id",
    name: "PublicClubDetails",
    component: () => import("@/views/ClubDetails.vue")
  },
  {
      path: "/student/clubs/:id",
      name: "StudentClubDetails",
      component: () => import("@/views/ClubDetails.vue")
  },
  {
      path: "/faculty/clubs/:id",
      name: "FacultyClubDetails",
      component: () => import("@/views/ClubDetails.vue")
  },
  {
      path: "/admin/clubs/:id",
      name: "AdminClubDetails",
      component: () => import("@/views/ClubDetails.vue")
  },

  // --- Admin Routes ---
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('@/views/admin/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'ADMIN' }
  },
  {
    path: '/admin/requests',
    name: 'AdminRequests',
    component: () => import('@/views/admin/Requests.vue'),
    meta: { requiresAuth: true, role: 'ADMIN' }
  },
  {
    path: '/admin/clubs',
    name: 'AdminClubs',
    component: () => import('@/views/admin/Clubs.vue'),
    meta: { requiresAuth: true, role: 'ADMIN' }
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: () => import('@/views/admin/Users.vue'),
    meta: { requiresAuth: true, role: 'ADMIN' }
  },
  {
    path: '/admin/users/:id',
    name: 'AdminUserDetails',
    component: () => import('@/views/admin/UserDetails.vue'),
    meta: { requiresAuth: true, role: 'ADMIN' }
  },
  {
    path: '/admin/events',
    name: 'AdminEvents',
    component: () => import('@/views/admin/Events.vue'),
    meta: { requiresAuth: true, role: 'ADMIN' }
  },
  {
    path: '/admin/events/:id',
    name: 'AdminEventDetail',
    component: () => import('@/views/admin/EventDetails.vue'),
    meta: { requiresAuth: true, role: 'ADMIN' }
  },
  {
    path: '/admin/venues',
    name: 'AdminVenues',
    component: () => import('@/views/admin/Venues.vue'),
    meta: { requiresAuth: true, role: 'ADMIN' }
  },
  {
    path: '/admin/profile',
    name: 'AdminProfile',
    component: () => import('@/views/admin/Profile.vue'),
    meta: { requiresAuth: true, role: 'ADMIN' }
  },
  {
    path: '/admin/profile/:id',
    name: 'AdminUserProfileView',
    component: () => import('@/views/PublicUserProfile.vue'),
    meta: { requiresAuth: true, role: 'ADMIN' }
  },
  {
    path: '/admin/notifications',
    name: 'AdminNotifications',
    component: () => import('@/views/Notifications.vue'),
    meta: { requiresAuth: true, role: 'ADMIN' }
  },

  // --- Faculty Routes ---
  {
    path: '/faculty',
    name: 'FacultyDashboard',
    component: () => import('@/views/faculty/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'FACULTY' }
  },
  {
    path: '/faculty/clubs',
    name: 'FacultyClubs',
    component: () => import('@/views/faculty/Clubs.vue'),
    meta: { requiresAuth: true, role: 'FACULTY' }
  },
  {
    path: '/faculty/requests',
    name: 'FacultyRequests',
    component: () => import('@/views/faculty/Requests.vue'),
    meta: { requiresAuth: true, role: 'FACULTY' }
  },
  {
    path: '/faculty/roles',
    name: 'FacultyRoles',
    component: () => import('@/views/faculty/Roles.vue'),
    meta: { requiresAuth: true, role: 'FACULTY' }
  },
  {
    path: '/faculty/roles/history',
    name: 'FacultyRoleHistory',
    component: () => import('@/views/faculty/RoleHistory.vue'),
    meta: { requiresAuth: true, role: 'FACULTY' }
  },
  {
    path: '/faculty/events',
    name: 'FacultyEvents',
    component: () => import('@/views/faculty/Events.vue'),
    meta: { requiresAuth: true, role: 'FACULTY' }
  },
  {
    path: '/faculty/events/:id',
    name: 'FacultyEventDetail',
    component: () => import('@/views/faculty/EventDetails.vue'),
    meta: { requiresAuth: true, role: 'FACULTY' }
  },
  {
    path: '/faculty/profile',
    name: 'FacultyProfile',
    component: () => import('@/views/faculty/Profile.vue'),
    meta: { requiresAuth: true, role: 'FACULTY' }
  },
  {
    path: '/faculty/profile/:id',
    name: 'FacultyUserProfileView',
    component: () => import('@/views/PublicUserProfile.vue'),
    meta: { requiresAuth: true, role: 'FACULTY' }
  },
  {
    path: '/faculty/notifications',
    name: 'FacultyNotifications',
    component: () => import('@/views/Notifications.vue'),
    meta: { requiresAuth: true, role: 'FACULTY' }
  },

  {
    path: '/faculty/profile',
    name: 'FacultyProfile',
    component: () => import('@/views/faculty/Profile.vue'),
    meta: { requiresAuth: true, role: 'FACULTY' }
  },

  // --- Student Routes ---
  {
    path: '/student',
    name: 'StudentDashboard',
    component: () => import('@/views/student/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'STUDENT' }
  },
  {
    path: '/student/clubs',
    name: 'StudentClubs',
    component: () => import('@/views/student/Clubs.vue'),
    meta: { requiresAuth: true, role: 'STUDENT' }
  },
  {
    path: '/student/requests',
    name: 'StudentRequests',
    component: () => import('@/views/student/Requests.vue'),
    meta: { requiresAuth: true, role: 'STUDENT' }
  },
  {
    path: '/student/roles',
    name: 'StudentRoles',
    component: () => import('@/views/student/Roles.vue'),
    meta: { requiresAuth: true, role: 'STUDENT' }
  },
  {
    path: '/student/events',
    name: 'StudentEvents',
    component: () => import('@/views/student/Events.vue'),
    meta: { requiresAuth: true, role: 'STUDENT' }
  },
  {
    path: '/student/events/:id',
    name: 'StudentEventDetail',
    component: () => import('@/views/student/EventDetails.vue'),
    meta: { requiresAuth: true, role: 'STUDENT' }
  },
  {
    path: '/student/analytics',
    name: 'StudentClubAnalytics',
    component: () => import('@/views/student/Analytics.vue'),
    meta: { requiresAuth: true, role: 'STUDENT' }
  },
  {
    path: '/student/profile',
    name: 'StudentProfile',
    component: () => import('@/views/student/Profile.vue'),
    meta: { requiresAuth: true, role: 'STUDENT' }
  },
  {
    path: '/student/profile/:id',
    name: 'StudentUserProfileView',
    component: () => import('@/views/PublicUserProfile.vue'),
    meta: { requiresAuth: true, role: 'STUDENT' }
  },
  {
    path: '/student/notifications',
    name: 'StudentNotifications',
    component: () => import('@/views/Notifications.vue'),
    meta: { requiresAuth: true, role: 'STUDENT' }
  },

  {
    path: '/profile/:id',
    name: 'SharedUserProfileView',
    component: () => import('@/views/PublicUserProfile.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/notifications',
    name: 'Notifications',
    component: () => import('@/views/Notifications.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});


router.beforeEach((to) => {
  if (!to.meta.requiresAuth) {
    return true;
  }

  if (!isLoggedIn()) {
    return '/login';
  }

  const user = getCurrentUser();

  if (to.meta.role && user?.role !== to.meta.role) {
    const rolePrefix = user?.role === 'ADMIN' ? '/admin' : (user?.role === 'FACULTY' ? '/faculty' : '/student');
    return rolePrefix;
  }

  return true;
});

export default router;