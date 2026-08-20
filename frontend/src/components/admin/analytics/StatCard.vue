<script setup>
defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    required: true
  },
  trend: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  }
})
</script>

<template>
  <div class="card stat-card">
    <div class="d-flex justify-content-between align-items-center mb-2">
      <h5>{{ label }}</h5>
      <i v-if="icon" class="bi" :class="icon" style="font-size: 1.4rem; color: #2563eb;"></i>
    </div>
    <div class="d-flex justify-content-between align-items-end">
      <h2>{{ value }}</h2>
      <span v-if="trend" class="stat-trend">{{ trend }}</span>
    </div>
  </div>
</template>

<style scoped>
.stat-card {
  height: 100%;
  border: none;
  border-radius: 18px;
  padding: 22px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
  background: #ffffff;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px rgba(37, 99, 235, 0.1);
}

.stat-card h5 {
  color: #64748B;
  margin-bottom: 0;
  font-size: 0.95rem;
  font-weight: 600;
}

.stat-card h2 {
  color: #1E293B;
  font-weight: 800;
  margin-bottom: 0;
  font-size: 1.85rem;
}

.stat-trend {
  font-size: 0.78rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 999px;
  background: #EFF6FF;
  color: #2563EB;
}
</style>