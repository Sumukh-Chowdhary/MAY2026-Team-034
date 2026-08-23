<script setup>
defineProps({
  label: {
    type: String,
    default: 'Loading…'
  }
})
</script>

<template>
  <div class="shared-loading-state">
    <div class="spinner-border text-primary" role="status"></div>
    <p>{{ label }}</p>
  </div>
</template>

<style scoped>
.shared-loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 20px;
  color: #64748B;
}
.shared-loading-state p {
  margin-top: 14px;
}
</style>
