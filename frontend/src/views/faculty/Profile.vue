<script setup>
import FacultyLayout from '@/layouts/FacultyLayout.vue'
import UserProfileView from '@/components/common/UserProfileView.vue'
</script>

<template>
  <FacultyLayout>
    <div class="mb-4">
      <h2 class="fw-bold text-dark m-0">Faculty Profile</h2>
      <p class="text-secondary m-0 mt-1">Manage faculty credentials, department information, and profile configuration.</p>
    </div>

    <UserProfileView layoutRole="FACULTY" />
  </FacultyLayout>
</template>
