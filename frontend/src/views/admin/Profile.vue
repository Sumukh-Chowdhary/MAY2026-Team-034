<script setup>
import AdminLayout from '@/layouts/AdminLayout.vue'
import UserProfileView from '@/components/common/UserProfileView.vue'
</script>

<template>
  <AdminLayout>
    <div class="mb-4">
      <h2 class="fw-bold text-dark m-0">Administrator Profile</h2>
      <p class="text-secondary m-0 mt-1">Manage system administrator credentials and profile configuration.</p>
    </div>

    <UserProfileView layoutRole="ADMIN" />
  </AdminLayout>
</template>
