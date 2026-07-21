<script setup>
import { ref, computed } from 'vue'

import EventSearch from '@/components/faculty/events/EventSearch.vue'
import EventStatusTabs from '@/components/faculty/events/EventStatusTabs.vue'
import EventGrid from '@/components/faculty/events/EventGrid.vue'
import { events } from '@/data/events'
import FacultyLayout from '@/layouts/FacultyLayout.vue'

const search = ref('')
const statusFilter = ref('all')

const eventList = ref(events)

const counts = computed(() => ({
  all: eventList.value.length,
  live: eventList.value.filter((event) => event.status === 'Live').length,
  completed: eventList.value.filter((event) => event.status === 'Completed').length
}))

const filteredEvents = computed(() => {
  const query = search.value.trim().toLowerCase()

  return eventList.value.filter((event) => {
    const matchesQuery =
      !query ||
      event.name.toLowerCase().includes(query) ||
      event.club.toLowerCase().includes(query)

    const matchesStatus =
      statusFilter.value === 'all' ||
      event.status.toLowerCase() === statusFilter.value

    return matchesQuery && matchesStatus
  })
})
</script>

<template>
  <FacultyLayout>
    <section class="hero">
      <h1>Explore Club Events</h1>
      <p>
        Browse events across every club, check schedules, and register
        for the ones that interest you.
      </p>
    </section>

    <EventSearch v-model="search" />

    <div class="tabs-wrapper"><EventStatusTabs v-model="statusFilter" :counts="counts" /></div>
    <EventGrid :events="filteredEvents" />
    <div v-if="filteredEvents.length === 0" class="empty-state">
      <h3>No events matched your search.</h3>
      <p>Try searching with another keyword or switching tabs.</p>
    </div>
  </FacultyLayout>
</template>
<style scoped>

.hero{
    text-align:center;
    margin-bottom:40px;
}

.hero h1{
    color:#1f2937;
    font-size:3rem;
    font-weight:800;
}

.hero p{
    max-width:720px;
    margin:18px auto 0;
    color:#6b7280;
    font-size:1.1rem;
    line-height:1.8;
}

.tabs-wrapper{
    display:flex;
    justify-content:center;
}

.empty-state{
    text-align:center;
    padding:70px 20px;
    color:#6b7280;
}

.empty-state h3{
    color:#1f2937;
    margin-bottom:10px;
}
</style>