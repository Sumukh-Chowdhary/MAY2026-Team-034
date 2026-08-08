<script setup>
import { ref, computed, onMounted } from 'vue'

import EventSearch from '@/components/faculty/events/EventSearch.vue'
import EventGrid from '@/components/faculty/events/EventGrid.vue'
import FacultyLayout from '@/layouts/FacultyLayout.vue'
import { getEvents } from '@/api/events'
import { getMySupervisedClubs, getFacultyGeneralEvents } from '@/api/faculty'
import { getEventStatus, sortEventsByStatusOrder } from '@/utils/eventUtils'

const search = ref('')
const statusFilter = ref('ALL')
const eventList = ref([])
const mySupervisedClubIds = ref([])
const myGeneralEvents = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const [events, myClubs, genEvents] = await Promise.all([
      getEvents().catch(() => []),
      getMySupervisedClubs().catch(() => []),
      getFacultyGeneralEvents().catch(() => [])
    ])

    eventList.value = (events || []).map((event) => ({
      ...event,
      club: event.clubName || event.club || 'Institutional'
    }))

    mySupervisedClubIds.value = (myClubs || []).map(c => Number(c.id || c.clubId))
    myGeneralEvents.value = genEvents || []
  } catch (error) {
    console.error('Failed to load faculty events', error)
  } finally {
    loading.value = false
  }
})

// Requirement 2: My Events displays active events (Scheduled, Live) where faculty is Club Coordinator or General Event Organizer. Completed events excluded.
const myActiveEventsList = computed(() => {
  const genIds = myGeneralEvents.value.map(g => g.id)
  return eventList.value.filter(ev => {
    const status = getEventStatus(ev)
    if (status === 'Completed') return false // Do not display completed events in My Events
    const isMyClub = ev.clubId && mySupervisedClubIds.value.includes(Number(ev.clubId))
    const isMyGen = genIds.includes(ev.id)
    return isMyClub || isMyGen
  })
})

// Requirement 2: All Club Events displays active club events
const allActiveClubEventsList = computed(() => {
  return eventList.value.filter(ev => ev.clubId && getEventStatus(ev) !== 'Completed')
})

const liveCount = computed(() => eventList.value.filter(e => getEventStatus(e) === 'Live').length)
const scheduledCount = computed(() => eventList.value.filter(e => getEventStatus(e) === 'Scheduled').length)
const completedCount = computed(() => eventList.value.filter(e => getEventStatus(e) === 'Completed').length)

const filteredMyEvents = computed(() => {
  const query = search.value.trim().toLowerCase()

  const list = myActiveEventsList.value.filter((event) => {
    const status = getEventStatus(event)
    const matchesQuery =
      !query ||
      (event.name && event.name.toLowerCase().includes(query)) ||
      (event.club && event.club.toLowerCase().includes(query))

    const matchesStatus =
      statusFilter.value === 'ALL' ||
      status.toUpperCase() === statusFilter.value.toUpperCase()

    return matchesQuery && matchesStatus
  })

  return sortEventsByStatusOrder(list)
})

const filteredAllClubEvents = computed(() => {
  const query = search.value.trim().toLowerCase()

  const list = allActiveClubEventsList.value.filter((event) => {
    const status = getEventStatus(event)
    const matchesQuery =
      !query ||
      (event.name && event.name.toLowerCase().includes(query)) ||
      (event.club && event.club.toLowerCase().includes(query))

    const matchesStatus =
      statusFilter.value === 'ALL' ||
      status.toUpperCase() === statusFilter.value.toUpperCase()

    return matchesQuery && matchesStatus
  })

  return sortEventsByStatusOrder(list)
})
</script>

<template>
  <FacultyLayout>
    <section class="faculty-events-page">
      <!-- Header -->
      <div class="page-top">
        <div>
          <p class="eyebrow">Faculty Dashboard</p>
          <h2 class="fw-bold mb-2">Faculty Events</h2>
          <p class="subtitle">
            Manage your assigned events, oversee supervised club activities, and track active campus events.
          </p>
        </div>
      </div>

      <!-- Toolbar with Search on Left and Segmented Toggle Control on Right in Same Row -->
      <div class="events-toolbar mb-4">
        <div class="toolbar-search">
          <EventSearch v-model="search" />
        </div>
        <div class="segmented-toggle-wrap">
          <div class="segmented-toggle-bar">
            <button
              type="button"
              class="segment-btn"
              :class="{ active: statusFilter === 'ALL' }"
              @click="statusFilter = 'ALL'"
            >
              <span>All</span>
              <span class="count-badge">{{ eventList.length }}</span>
            </button>
            <button
              type="button"
              class="segment-btn"
              :class="{ active: statusFilter === 'LIVE' }"
              @click="statusFilter = 'LIVE'"
            >
              <span>Live</span>
              <span class="count-badge">{{ liveCount }}</span>
            </button>
            <button
              type="button"
              class="segment-btn"
              :class="{ active: statusFilter === 'SCHEDULED' }"
              @click="statusFilter = 'SCHEDULED'"
            >
              <span>Scheduled</span>
              <span class="count-badge">{{ scheduledCount }}</span>
            </button>
            <button
              type="button"
              class="segment-btn"
              :class="{ active: statusFilter === 'COMPLETED' }"
              @click="statusFilter = 'COMPLETED'"
            >
              <span>Completed</span>
              <span class="count-badge">{{ completedCount }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- SECTION 1: My Events (Organized / Coordinated Active Events) -->
      <div class="events-section mb-5" v-if="filteredMyEvents.length > 0">
        <div class="d-flex align-items-center gap-2 mb-3">
          <span class="material-symbols-rounded text-primary fs-4">stars</span>
          <h4 class="fw-bold m-0 text-dark">My Events</h4>
          <span class="badge bg-primary-subtle text-primary border rounded-pill px-2.5 py-1 text-xs">
            {{ filteredMyEvents.length }} Managed
          </span>
        </div>
        <EventGrid :events="filteredMyEvents" />
      </div>

      <!-- SECTION 2: All Club Events -->
      <div class="events-section">
        <div class="d-flex align-items-center gap-2 mb-3">
          <span class="material-symbols-rounded text-secondary fs-4">groups</span>
          <h4 class="fw-bold m-0 text-dark">All Club Events</h4>
          <span class="badge bg-secondary-subtle text-secondary border rounded-pill px-2.5 py-1 text-xs">
            {{ filteredAllClubEvents.length }} Active
          </span>
        </div>

        <EventGrid :events="filteredAllClubEvents" />

        <div v-if="filteredAllClubEvents.length === 0" class="empty-state">
          <h3>No active events matched your search.</h3>
          <p>Try searching with another keyword or switching status filters.</p>
        </div>
      </div>
    </section>
  </FacultyLayout>
</template>

<style scoped>
.faculty-events-page {
  width: 100%;
}

.page-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 24px;
  padding: 24px 28px;
  border-radius: 24px;
  background: linear-gradient(135deg, #eff6ff, #ffffff);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
}

.eyebrow {
  margin: 0 0 8px;
  color: #2563eb;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.subtitle {
  margin: 0;
  color: #64748b;
  max-width: 720px;
  line-height: 1.7;
}

.events-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.toolbar-search {
  flex: 1 1 0%;
}

.toolbar-search :deep(.search-container) {
  max-width: 100% !important;
  margin: 0 !important;
}

.toolbar-search :deep(.search-input) {
  height: 52px !important;
  border-radius: 16px !important;
  border-color: #cbd5e1 !important;
}

.segmented-toggle-wrap {
  flex: 1 1 0%;
}

.segmented-toggle-bar {
  display: flex;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 16px;
  padding: 4px;
  width: 100%;
  height: 52px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
}

.segment-btn {
  flex: 1;
  border: none;
  background: transparent;
  color: #64748b;
  padding: 0 10px;
  font-size: 0.85rem;
  font-weight: 600;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
}

.segment-btn .count-badge {
  background: #f1f5f9;
  color: #475569;
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 0.75rem;
  font-weight: 700;
  transition: all 0.2s ease;
}

.segment-btn.active {
  background: #2563eb;
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

.segment-btn.active .count-badge {
  background: #ffffff;
  color: #2563eb;
}

@media (max-width: 992px) {
  .events-toolbar {
    flex-direction: column;
  }
  .toolbar-search,
  .segmented-toggle-wrap {
    width: 100%;
    flex: none;
  }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
}

.empty-state h3 {
  color: #1f2937;
  margin-bottom: 10px;
}
</style>