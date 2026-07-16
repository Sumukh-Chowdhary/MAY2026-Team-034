<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from './components/Navbar.vue'
import Footer from './components/Footer.vue'

const route = useRoute()

const dashboardRoutes = ['/admin', '/faculty', '/student']

const isDashboard = computed(() =>
  dashboardRoutes.some(path => route.path.startsWith(path))
)
</script>

<template>
  <div v-if="!isDashboard" class="app-container">
    <Navbar />
    <main class="content">
      <RouterView />
    </main>
    <Footer />
  </div>

  <RouterView v-else />
</template>