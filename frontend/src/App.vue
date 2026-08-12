<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from './components/Navbar.vue'
import Footer from './components/Footer.vue'
import ToastContainer from './components/common/ToastContainer.vue'
import { isLoggedIn } from "@/services/authService"

const route = useRoute()

const dashboardRoutes = ['/admin', '/faculty', '/student']

const isDashboard = computed(() => {
    // Normal dashboard routes
    if (dashboardRoutes.some(path => route.path.startsWith(path))) {
        return true
    }

    // Authenticated shared routes like /notifications or /profile
    if (route.path.startsWith('/notifications') || route.path.startsWith('/profile')) {
        return true
    }

    // Authenticated routes
    if (route.meta?.requiresAuth && isLoggedIn()) {
        return true
    }

    // Club page behaves differently depending on login status
    if (route.path.startsWith("/clubs/")) {
        return isLoggedIn()
    }

    return false
})
</script>

<template>
  <ToastContainer />

  <div v-if="!isDashboard" class="app-container">
    <Navbar />
    <main class="content">
      <RouterView v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </RouterView>
    </main>
    <Footer />
  </div>

  <RouterView v-else v-slot="{ Component }">
    <transition name="page-fade" mode="out-in">
      <component :is="Component" />
    </transition>
  </RouterView>
</template>

<style>
/* Page Transition Animations */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>