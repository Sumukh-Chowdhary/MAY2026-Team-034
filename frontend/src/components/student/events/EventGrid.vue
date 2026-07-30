<template>
  <section class="event-grid">
    <EventCard
      v-for="event in events"
      :key="event.id"
      :event="event"
      :isRegistered="isRegisteredFor(event.id)"
      :isRegistering="isRegisteringFor(event.id)"
      :onRegister="onRegister"
    />
  </section>
</template>

<script setup>
import EventCard from './EventCard.vue'

const props = defineProps({
  events: {
    type: Array,
    required: true,
    default: () => []
  },
  isRegisteredFor: {
    type: Function,
    required: true
  },
  isRegisteringFor: {
    type: Function,
    required: true
  },
  onRegister: {
    type: Function,
    required: true
  }
})
</script>

<style scoped>
.event-grid {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 12px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 28px;
}

@media (max-width: 768px) {
  .event-grid {
    grid-template-columns: 1fr;
  }
}
</style>