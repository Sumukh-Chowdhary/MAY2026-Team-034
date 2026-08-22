<script setup>
import { ref, computed, onMounted } from 'vue'

import EventSearch from '@/components/student/events/EventSearch.vue'
import EventStatusTabs from '@/components/student/events/EventStatusTabs.vue'
import EventGrid from '@/components/student/events/EventGrid.vue'
import StudentLayout from '@/layouts/StudentLayout.vue'
import ScheduleConflictModal from '@/components/common/ScheduleConflictModal.vue'
import { getEvents, getMyEvents } from '@/api/events'
import { useScheduleConflictCheck } from '@/composables/useScheduleConflictCheck'

const search = ref('')
const statusFilter = ref('all')
const eventList = ref([])
const myRegisteredEventIds = ref([])
const myParticipatedEventIds = ref([])
const loading = ref(false)
const registeringIds = ref({})

const {
  showConflictModal,
  pendingConflicts,
  pendingEventName,
  registerWithConflictCheck,
  confirmRegistration,
  cancelRegistration
} = useScheduleConflictCheck()

const normalizeEvent = (event) => ({
  ...event,
  emoji: event.emoji || '🎉',
  club: event.clubName || event.club || 'Unknown Club',
  name: event.name || event.eventName || event.event_name || 'Untitled Event',
  description: event.description || event.eventDescription || event.event_description || 'No description available.',
  status: String(event.status || event.eventStatus || event.event_status || 'SCHEDULED'),
  startDate: event.startDate || event.start_date || 'TBD',
  endDate: event.endDate || event.end_date || 'TBD'
})

onMounted(async () => {
  loading.value = true
  try {
    const [events, registered, participated] = await Promise.all([
      getEvents(),
      getMyEvents('registered'),
      getMyEvents('participated')
    ])

    eventList.value = events.map(normalizeEvent)
    myRegisteredEventIds.value = registered.map((event) => event.id)
    myParticipatedEventIds.value = participated.map((event) => event.id)
  } catch (error) {
    console.error('Failed to load events', error)
  } finally {
    loading.value = false
  }
})

import { getEventStatus, sortEventsByStatusOrder } from '@/utils/eventUtils'

const counts = computed(() => ({
  all: eventList.value.length,
  live: eventList.value.filter((event) => getEventStatus(event) === 'Live').length,
  completed: eventList.value.filter((event) => getEventStatus(event) === 'Completed').length
}))

const filteredEvents = computed(() => {
  const query = search.value.trim().toLowerCase()

  const list = eventList.value.filter((event) => {
    const title = String(event.name || '').toLowerCase()
    const clubName = String(event.club || '').toLowerCase()
    const status = getEventStatus(event)

    const matchesQuery = !query || title.includes(query) || clubName.includes(query)
    const matchesStatus = statusFilter.value === 'all' || status.toLowerCase() === statusFilter.value.toLowerCase()

    return matchesQuery && matchesStatus
  })

  return sortEventsByStatusOrder(list)
})

async function handleRegister(event) {
  if (registeringIds.value[event.id]) return
  registeringIds.value[event.id] = true
  try {
    const result = await registerWithConflictCheck(event.id, event.name)
    if (result.cancelled) return
    myRegisteredEventIds.value = Array.from(new Set([...myRegisteredEventIds.value, event.id]))
  } catch (error) {
    console.error('Failed to register for event', error)
  } finally {
    registeringIds.value[event.id] = false
  }
}

function isRegisteredFor(eventId) {
  return myRegisteredEventIds.value.includes(eventId)
}

function isRegisteringFor(eventId) {
  return Boolean(registeringIds.value[eventId])
}
</script>

<template>
  <StudentLayout>
    <section class="hero">
      <h1>Explore Club Events</h1>
      <p>Browse events across every club, check schedules, and register for the ones that interest you.</p>
    </section>

    <div v-if="myRegisteredEventIds.length || myParticipatedEventIds.length" class="summary-card">
      <h3>Your event activity</h3>
      <p>{{ myRegisteredEventIds.length }} active registrations • {{ myParticipatedEventIds.length }} past participations</p>
    </div>

    <EventSearch v-model="search" />

    <div class="tabs-wrapper">
      <EventStatusTabs v-model="statusFilter" :counts="counts" />
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner-border text-primary" role="status"></div>
      <p>Loading events...</p>
    </div>

    <template v-else>
      <EventGrid
        :events="filteredEvents"
        :isRegisteredFor="isRegisteredFor"
        :isRegisteringFor="isRegisteringFor"
        :onRegister="handleRegister"
      />

      <div v-if="filteredEvents.length === 0" class="empty-state">
        <h3>No events matched your search.</h3>
        <p>Try searching with another keyword or switching tabs.</p>
      </div>
    </template>

    <ScheduleConflictModal
      :show="showConflictModal"
      :event-name="pendingEventName"
      :conflicts="pendingConflicts"
      @confirm="confirmRegistration"
      @cancel="cancelRegistration"
    />
  </StudentLayout>
</template>

<style scoped>
.hero {
  text-align: center;
  margin-bottom: 40px;
}

.hero h1 {
  color: #1f2937;
  font-size: 3rem;
  font-weight: 800;
}

.hero p {
  max-width: 720px;
  margin: 18px auto 0;
  color: #6b7280;
  font-size: 1.1rem;
  line-height: 1.8;
}

.summary-card {
  max-width: 960px;
  margin: 0 auto 24px;
  padding: 18px 22px;
  border-radius: 16px;
  background: #eff6ff;
  color: #1d4ed8;
}

.summary-card h3 {
  margin: 0 0 6px;
  font-size: 1.05rem;
}

.summary-card p {
  margin: 0;
}

.tabs-wrapper {
  display: flex;
  justify-content: center;
}

.empty-state {
  text-align: center;
  padding: 70px 20px;
  color: #6b7280;
}

.empty-state h3 {
  color: #1f2937;
  margin-bottom: 10px;
}

.loading-state {
  text-align: center;
  padding: 90px 20px;
  color: #6b7280;
}

.loading-state p {
  margin-top: 16px;
}
</style>