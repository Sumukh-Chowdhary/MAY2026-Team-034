<script setup>
defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    required: true
  }
})
</script>

<template>
  <div class="card stat-card">
    <h5>{{ label }}</h5>
    <h2>{{ value }}</h2>
  </div>
</template>

<style scoped>
.stat-card {
  height: 100%;
  border: none;
  border-radius: 18px;
  padding: 25px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
}

.stat-card h5 {
  color: #64748B;
  margin-bottom: 12px;
  font-weight: 500;
}

.stat-card h2 {
  color: #2563EB;
  font-weight: 700;
  margin-bottom: 0;
}
</style>