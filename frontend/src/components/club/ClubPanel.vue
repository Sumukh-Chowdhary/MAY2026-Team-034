<script setup>
defineProps({
  title: {
    type: String,
    required: true
  }
})
</script>

<template>
  <section class="club-panel">
    <header class="panel-header">
      <h2>{{ title }}</h2>
      <div v-if="$slots['header-actions']" class="header-actions">
        <slot name="header-actions" />
      </div>
    </header>

    <div class="panel-body">
      <slot />
    </div>
  </section>
</template>

<style scoped>
.club-panel {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.panel-header h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #1f2937;
}

.panel-body {
  min-height: 180px;
  height: 360px;
}
</style>