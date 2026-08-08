<script setup>
import StudentLayout from '@/layouts/StudentLayout.vue'
import UserProfileView from '@/components/common/UserProfileView.vue'
</script>

<template>
  <StudentLayout>
    <div class="mb-4">
      <h2 class="fw-bold text-dark m-0">My Profile</h2>
      <p class="text-secondary m-0 mt-1">Manage your student account settings and personal details.</p>
    </div>

    <UserProfileView layoutRole="STUDENT" />
  </StudentLayout>
</template>
