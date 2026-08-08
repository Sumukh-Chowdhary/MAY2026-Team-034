<script setup>
import { ref, computed, onMounted } from 'vue'

import EventSearch from '@/components/admin/events/EventSearch.vue'
import EventStatusTabs from '@/components/admin/events/EventStatusTabs.vue'
import EventGrid from '@/components/admin/events/EventGrid.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { getEvents, createEvent } from '@/api/events'

const search = ref('')
const statusFilter = ref('all')
const eventList = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const events = await getEvents()
    eventList.value = events.map((event) => ({
      ...event,
      club: event.clubName || event.club || 'Unknown Club'
    }))
  } catch (error) {
    console.error('Failed to load events', error)
  } finally {
    loading.value = false
  }
})

import CreateEventModal from '@/components/admin/events/CreateEventModal.vue'
import { getEventStatus, sortEventsByStatusOrder } from '@/utils/eventUtils'

const showCreateEventModal = ref(false)

function handleEventCreated(createdEvent) {
  eventList.value.unshift({
    ...createdEvent,
    club: createdEvent.clubName || createdEvent.club || 'Unknown Club'
  })
}

const counts = computed(() => ({
  all: eventList.value.length,
  live: eventList.value.filter((event) => getEventStatus(event) === 'Live').length,
  completed: eventList.value.filter((event) => getEventStatus(event) === 'Completed').length
}))

const filteredEvents = computed(() => {
  const query = search.value.trim().toLowerCase()

  const list = eventList.value.filter((event) => {
    const clubName = String(event.club || event.clubName || '')
    const eventName = String(event.name || event.eventName || '')
    const status = getEventStatus(event)

    const matchesQuery =
      !query ||
      eventName.toLowerCase().includes(query) ||
      clubName.toLowerCase().includes(query)

    const matchesStatus =
      statusFilter.value === 'all' ||
      status.toLowerCase() === statusFilter.value.toLowerCase()

    return matchesQuery && matchesStatus
  })

  return sortEventsByStatusOrder(list)
})
</script>

<template>
  <AdminLayout>
    <section class="page-header">
      <div class="header-left">
        <h1>Explore Club Events</h1>
        <p>Browse events across every club, check schedules, and manage events.</p>
      </div>
      <button class="create-event-btn" @click="showCreateEventModal = true">
        <span class="material-symbols-rounded">add</span>
        Create Event
      </button>
    </section>

    <!-- Create Event Modal -->
    <CreateEventModal
      v-if="showCreateEventModal"
      @close="showCreateEventModal = false"
      @created="handleEventCreated"
    />

    <div class="toolbar">
      <div class="search-wrap">
        <EventSearch v-model="search" />
      </div>
      <div class="status-tabs">
        <EventStatusTabs v-model="statusFilter" :counts="counts" />
      </div>
    </div>

    <EventGrid :events="filteredEvents" />
    <div v-if="filteredEvents.length === 0" class="empty-state">
      <h3>No events matched your search.</h3>
      <p>Try searching with another keyword or switching tabs.</p>
    </div>
  </AdminLayout>
</template>
<style scoped>

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
  padding: 24px 28px;
  border-radius: 20px;
  background: linear-gradient(135deg, #eff6ff, #ffffff);
  border: 1px solid #dbeafe;
  box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04);
}

.header-left h1 {
  color: #0f172a;
  font-size: 2rem;
  font-weight: 800;
  margin: 0 0 6px;
  letter-spacing: -0.02em;
}

.header-left p {
  margin: 0;
  color: #64748b;
  font-size: 0.95rem;
}

.create-event-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #10b981;
  color: #ffffff;
  border: none;
  border-radius: 12px;
  padding: 12px 20px;
  font-weight: 700;
  font-size: 0.95rem;
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.25);
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.create-event-btn:hover {
  background: #059669;
  transform: translateY(-1px);
}

.create-event-btn .material-symbols-rounded {
  font-size: 1.25rem;
}

.toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 24px;
  margin-bottom: 32px;
}

.search-wrap {
  width: 100%;
  max-width: 850px;
}

.status-tabs {
  justify-self: end;
}

.empty-state {
  text-align: center;
  padding: 50px 20px;
  color: #6b7280;
}

.empty-state h3 {
  color: #1f2937;
  margin-bottom: 8px;
}

@media (max-width: 900px) {
  .toolbar {
    grid-template-columns: 1fr;
  }

  .search-wrap {
    max-width: 100%;
  }

  .status-tabs {
    justify-self: start;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    padding: 20px;
  }

  .create-event-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>