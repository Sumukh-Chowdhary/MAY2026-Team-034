<script setup>
import { ref, computed, onMounted } from 'vue'
import StudentLayout from '@/layouts/StudentLayout.vue'
import { getVenueCalendar } from '@/api/venues'

const loading = ref(true)
const error = ref('')
const venues = ref([])
const windowStart = ref('')
const windowEnd = ref('')
const search = ref('')
const daysAhead = ref(30)

const filteredVenues = computed(() => {
  if (!search.value.trim()) return venues.value
  const q = search.value.trim().toLowerCase()
  return venues.value.filter(v =>
    v.name.toLowerCase().includes(q) || (v.location || '').toLowerCase().includes(q)
  )
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await getVenueCalendar(daysAhead.value)
    venues.value = data.venues || []
    windowStart.value = data.windowStart
    windowEnd.value = data.windowEnd
  } catch (err) {
    console.error(err)
    error.value = 'Could not load venue availability right now.'
  } finally {
    loading.value = false
  }
}

function formatBookingWhen(b) {
  const datePart = b.endDate && b.endDate !== b.startDate
    ? `${b.startDate} → ${b.endDate}`
    : b.startDate
  const timePart = b.startTime ? ` · ${b.startTime}${b.endTime ? ' - ' + b.endTime : ''}` : ''
  return datePart + timePart
}

onMounted(load)
</script>

<template>
  <StudentLayout>
    <section class="venue-calendar-page">
      <div class="page-header">
        <div>
          <h2>Venue Availability</h2>
          <p>See which venues are already booked before submitting a venue request.</p>
        </div>

        <div class="controls">
          <input
            v-model="search"
            type="text"
            class="form-control search-input"
            placeholder="Search venue or location..."
          />
          <select v-model.number="daysAhead" class="form-select days-select" @change="load">
            <option :value="14">Next 14 days</option>
            <option :value="30">Next 30 days</option>
            <option :value="60">Next 60 days</option>
            <option :value="90">Next 90 days</option>
          </select>
        </div>
      </div>

      <p v-if="!loading && windowStart" class="window-label">
        Showing bookings from <strong>{{ windowStart }}</strong> to <strong>{{ windowEnd }}</strong>
      </p>

      <div v-if="loading" class="loading-state">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <div v-else-if="error" class="empty-panel error">
        <i class="bi bi-exclamation-triangle"></i>
        <p>{{ error }}</p>
      </div>

      <div v-else-if="filteredVenues.length === 0" class="empty-panel">
        <i class="bi bi-search"></i>
        <p>No venues matched your search.</p>
      </div>

      <div v-else class="venue-list">
        <div v-for="venue in filteredVenues" :key="venue.id" class="venue-card">
          <div class="venue-card-header">
            <div>
              <h4>{{ venue.name }}</h4>
              <p class="venue-meta">{{ venue.location }} · Capacity {{ venue.capacity }}</p>
            </div>
            <span
              class="status-pill"
              :class="venue.bookings.length === 0 ? 'free' : 'busy'"
            >
              {{ venue.bookings.length === 0 ? 'Fully Free' : `${venue.bookings.length} booking${venue.bookings.length > 1 ? 's' : ''}` }}
            </span>
          </div>

          <div v-if="venue.bookings.length" class="bookings-list">
            <div v-for="b in venue.bookings" :key="b.eventId" class="booking-row">
              <div class="booking-name">{{ b.eventName }}</div>
              <div class="booking-details">
                <span class="club-badge">{{ b.clubName }}</span>
                <span class="when">{{ formatBookingWhen(b) }}</span>
              </div>
            </div>
          </div>
          <p v-else class="free-note">No events scheduled here in this window — good to go!</p>
        </div>
      </div>
    </section>
  </StudentLayout>
</template>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 8px;
}

.page-header h2 {
  margin: 0;
  font-weight: 700;
  color: #1E293B;
}

.page-header p {
  margin: 4px 0 0;
  color: #64748B;
}

.controls {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.search-input {
  min-width: 220px;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
}

.days-select {
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  font-weight: 600;
}

.window-label {
  color: #64748B;
  font-size: 0.85rem;
  margin: 12px 0 20px;
}

.loading-state, .empty-panel {
  background: #ffffff;
  border-radius: 18px;
  padding: 60px 24px;
  text-align: center;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
}

.empty-panel i {
  font-size: 1.8rem;
  color: #94A3B8;
  display: block;
  margin-bottom: 10px;
}

.empty-panel.error i { color: #DC2626; }

.venue-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.venue-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.05);
}

.venue-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  flex-wrap: wrap;
}

.venue-card-header h4 {
  margin: 0;
  color: #1E293B;
  font-weight: 700;
}

.venue-meta {
  margin: 4px 0 0;
  color: #64748B;
  font-size: 0.85rem;
}

.status-pill {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 5px 12px;
  border-radius: 999px;
  white-space: nowrap;
}

.status-pill.free {
  background: #ECFDF5;
  color: #059669;
}

.status-pill.busy {
  background: #FFFBEB;
  color: #D97706;
}

.bookings-list {
  margin-top: 14px;
  border-top: 1px solid #F1F5F9;
  padding-top: 12px;
}

.booking-row {
  padding: 8px 0;
  border-bottom: 1px solid #F8FAFC;
}

.booking-row:last-child {
  border-bottom: none;
}

.booking-name {
  font-weight: 600;
  color: #1E293B;
  font-size: 0.9rem;
}

.booking-details {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  flex-wrap: wrap;
}

.club-badge {
  background: #EFF6FF;
  color: #2563EB;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
}

.when {
  font-size: 0.8rem;
  color: #64748B;
}

.free-note {
  margin: 12px 0 0;
  color: #059669;
  font-size: 0.85rem;
  font-style: italic;
}
</style>
