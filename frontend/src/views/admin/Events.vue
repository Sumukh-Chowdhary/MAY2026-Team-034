<script setup>
import { ref, computed } from 'vue'

import EventSearch from '@/components/admin/events/EventSearch.vue'
import EventStatusTabs from '@/components/admin/events/EventStatusTabs.vue'
import EventGrid from '@/components/admin/events/EventGrid.vue'
import { events } from '@/data/events'
import AdminLayout from '@/layouts/AdminLayout.vue'

const search = ref('')
const statusFilter = ref('all')
const eventList = ref(events)

const showCreateEventModal = ref(false)
const newEventForm = ref({
  name: '',
  club: '',
  emoji: '🎉',
  startDate: '',
  endDate: '',
  description: ''
})

function submitCreateEvent() {
  if (!newEventForm.value.name.trim() || !newEventForm.value.club.trim()) {
    alert('Please provide Event Name and Club Name.')
    return
  }

  const newId = eventList.value.length ? Math.max(...eventList.value.map(e => e.id)) + 1 : 1
  const createdEvent = {
    id: newId,
    emoji: newEventForm.value.emoji || '🎉',
    name: newEventForm.value.name,
    club: newEventForm.value.club,
    status: 'Live',
    startDate: newEventForm.value.startDate || '25 Jul 2026',
    endDate: newEventForm.value.endDate || '25 Jul 2026',
    description: newEventForm.value.description || 'New campus event.',
    schedule: [],
    announcements: [],
    registrations: [],
    attendance: []
  }

  eventList.value.unshift(createdEvent)
  events.unshift(createdEvent)
  alert(`Event "${createdEvent.name}" created successfully!`)

  showCreateEventModal.value = false
  newEventForm.value = { name: '', club: '', emoji: '🎉', startDate: '', endDate: '', description: '' }
}

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
  <AdminLayout>
    <section class="hero">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div></div>
        <button class="btn btn-success px-4 py-2 fw-bold rounded-3 shadow-sm" @click="showCreateEventModal = true">
          + Create Event
        </button>
      </div>
      <h1>Explore Club Events</h1>
      <p>
        Browse events across every club, check schedules, and manage events.
      </p>
    </section>

    <!-- Create Event Modal -->
    <div v-if="showCreateEventModal" class="modal-backdrop" @click.self="showCreateEventModal = false">
      <div class="modal-dialog-custom">
        <h4 class="fw-bold mb-3 text-dark">+ Create New Event</h4>
        <div class="mb-3">
          <label class="form-label font-semibold">Event Name</label>
          <input v-model="newEventForm.name" type="text" class="form-control" placeholder="e.g. AI & Machine Learning Workshop" />
        </div>
        <div class="mb-3">
          <label class="form-label font-semibold">Club Name</label>
          <input v-model="newEventForm.club" type="text" class="form-control" placeholder="e.g. AI Club" />
        </div>
        <div class="row g-2 mb-3">
          <div class="col-6">
            <label class="form-label font-semibold">Start Date</label>
            <input v-model="newEventForm.startDate" type="text" class="form-control" placeholder="e.g. 25 Jul 2026" />
          </div>
          <div class="col-6">
            <label class="form-label font-semibold">End Date</label>
            <input v-model="newEventForm.endDate" type="text" class="form-control" placeholder="e.g. 27 Jul 2026" />
          </div>
        </div>
        <div class="mb-3">
          <label class="form-label font-semibold">Description</label>
          <textarea v-model="newEventForm.description" class="form-control" rows="3" placeholder="Enter event details..."></textarea>
        </div>
        <div class="d-flex justify-content-end gap-2">
          <button class="btn btn-secondary" @click="showCreateEventModal = false">Cancel</button>
          <button class="btn btn-success" @click="submitCreateEvent">Create Event</button>
        </div>
      </div>
    </div>

    <EventSearch v-model="search" />

    <div class="tabs-wrapper"><EventStatusTabs v-model="statusFilter" :counts="counts" /></div>
    <EventGrid :events="filteredEvents" />
    <div v-if="filteredEvents.length === 0" class="empty-state">
      <h3>No events matched your search.</h3>
      <p>Try searching with another keyword or switching tabs.</p>
    </div>
  </AdminLayout>
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

/* Modal */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-dialog-custom {
  background: #fff;
  border-radius: 20px;
  width: 90%;
  max-width: 600px;
  padding: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

</style>