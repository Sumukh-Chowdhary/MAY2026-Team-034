<script setup>
import { ref, computed, onMounted } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import VenueCalendarView from '@/components/admin/venues/VenueCalendarView.vue'
import { getVenues, createVenue, updateVenue, updateVenueStatus } from '@/api/venues'
import { getEvents } from '@/api/events'

const venueList = ref([])
const eventList = ref([])
const search = ref('')
const loading = ref(false)

// Modals state
const showVenueModal = ref(false)
const isEditing = ref(false)
const selectedVenue = ref(null)

const activeCalendarVenue = ref(null)

const venueForm = ref({
  id: null,
  name: '',
  location: '',
  type: 'Hall',
  capacity: 100
})

const venueTypes = ['Hall', 'Auditorium', 'Lab', 'Ground', 'Classroom', 'Conference Room']

const fetchVenues = async () => {
  try {
    loading.value = true
    venueList.value = await getVenues()
  } catch (error) {
    console.error('Failed to fetch venues', error)
  } finally {
    loading.value = false
  }
}

const fetchAllEvents = async () => {
  try {
    eventList.value = await getEvents()
  } catch (error) {
    console.error('Failed to fetch events', error)
  }
}

onMounted(() => {
  fetchVenues()
  fetchAllEvents()
})

const statusFilter = ref('all') // 'all' | 'available' | 'occupied' | 'archived'

const venueCounts = computed(() => {
  const counts = { all: venueList.value.length, available: 0, occupied: 0, archived: 0 }
  venueList.value.forEach((v) => {
    const st = (v.availabilityStatus || v.status || '').toUpperCase()
    if (st === 'AVAILABLE') counts.available++
    else if (st === 'OCCUPIED') counts.occupied++
    else if (st === 'ARCHIVED') counts.archived++
    else counts.available++
  })
  return counts
})

const filteredVenues = computed(() => {
  const query = search.value.trim().toLowerCase()
  const filter = statusFilter.value.toLowerCase()

  let list = venueList.value

  if (query) {
    list = list.filter((v) => {
      const name = String(v.name || '').toLowerCase()
      const loc = String(v.location || '').toLowerCase()
      const type = String(v.type || '').toLowerCase()
      return name.includes(query) || loc.includes(query) || type.includes(query)
    })
  }

  if (filter !== 'all') {
    list = list.filter((v) => {
      const st = (v.availabilityStatus || v.status || '').toUpperCase()
      if (filter === 'available') return st === 'AVAILABLE' || (!st || st === 'ACTIVE')
      if (filter === 'occupied') return st === 'OCCUPIED'
      if (filter === 'archived') return st === 'ARCHIVED'
      return true
    })
  }

  // Active/Available/Occupied venues first, Archived venues last
  return list.slice().sort((a, b) => {
    const isArchivedA = (a.availabilityStatus || a.status || '').toUpperCase() === 'ARCHIVED'
    const isArchivedB = (b.availabilityStatus || b.status || '').toUpperCase() === 'ARCHIVED'
    if (isArchivedA && !isArchivedB) return 1
    if (!isArchivedA && isArchivedB) return -1
    return 0
  })
})

function openAddModal() {
  isEditing.value = false
  selectedVenue.value = null
  venueForm.value = {
    id: null,
    name: '',
    location: '',
    type: 'Hall',
    capacity: 100
  }
  showVenueModal.value = true
}

function openEditModal(venue) {
  isEditing.value = true
  selectedVenue.value = venue
  venueForm.value = {
    id: venue.id,
    name: venue.name,
    location: venue.location,
    type: venue.type || 'Hall',
    capacity: venue.capacity || 0
  }
  showVenueModal.value = true
}

const toast = ref({
  show: false,
  message: '',
  type: 'success'
})

function showToast(message, type = 'success') {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3500)
}

const confirmModal = ref({
  show: false,
  title: '',
  message: '',
  onConfirm: null
})

function triggerConfirm(title, message, callback) {
  confirmModal.value = {
    show: true,
    title,
    message,
    onConfirm: callback
  }
}

function handleConfirmExecute() {
  if (confirmModal.value.onConfirm) {
    confirmModal.value.onConfirm()
  }
  confirmModal.value.show = false
}

async function saveVenue() {
  if (!venueForm.value.name.trim() || !venueForm.value.location.trim()) {
    showToast('Please fill out Venue Name and Location.', 'warning')
    return
  }

  try {
    loading.value = true
    if (isEditing.value && venueForm.value.id) {
      await updateVenue(venueForm.value.id, {
        name: venueForm.value.name,
        location: venueForm.value.location,
        type: venueForm.value.type,
        capacity: Number(venueForm.value.capacity)
      })
      showToast('Venue updated successfully!', 'success')
    } else {
      await createVenue({
        name: venueForm.value.name,
        location: venueForm.value.location,
        type: venueForm.value.type,
        capacity: Number(venueForm.value.capacity)
      })
      showToast('Venue created successfully!', 'success')
    }
    showVenueModal.value = false
    await fetchVenues()
  } catch (error) {
    console.error(error)
    showToast(error?.response?.data?.error || 'Failed to save venue.', 'danger')
  } finally {
    loading.value = false
  }
}

function archiveVenue(venue) {
  const isArchived = (venue.availabilityStatus || venue.status || '').toUpperCase() === 'ARCHIVED'
  const newStatus = isArchived ? 'AVAILABLE' : 'ARCHIVED'
  const actionText = isArchived ? 'restore' : 'archive'

  triggerConfirm(
    `${isArchived ? 'Restore' : 'Archive'} Venue`,
    `Are you sure you want to ${actionText} "${venue.name}"?`,
    async () => {
      try {
        loading.value = true
        await updateVenueStatus(venue.id, newStatus)
        showToast(`Venue ${isArchived ? 'restored' : 'archived'} successfully!`, 'success')
        await fetchVenues()
      } catch (error) {
        console.error(error)
        showToast(`Failed to ${actionText} venue.`, 'danger')
      } finally {
        loading.value = false
      }
    }
  )
}

function openCalendarView(venue) {
  activeCalendarVenue.value = venue
}

const venueEvents = computed(() => {
  if (!activeCalendarVenue.value) return []
  return eventList.value.filter((e) => {
    return e.venueId === activeCalendarVenue.value.id || e.venueName === activeCalendarVenue.value.name
  })
})

function formatStatus(status) {
  const s = String(status || 'AVAILABLE').toUpperCase()
  if (s === 'AVAILABLE') return 'Available'
  if (s === 'OCCUPIED' || s === 'BOOKED') return 'Occupied'
  if (s === 'ARCHIVED' || s === 'INACTIVE') return 'Archived'
  return status
}

function getVenueUpcomingBooking(venue) {
  if (!venue || !eventList.value.length) return null
  const events = eventList.value.filter((e) => {
    const isMatchingVenue = e.venueId === venue.id || e.venueName === venue.name
    const isNotCancelled = (e.rawStatus || e.status || '').toUpperCase() !== 'CANCELLED' && (e.rawStatus || e.status || '').toUpperCase() !== 'CLOSED'
    return isMatchingVenue && isNotCancelled
  })
  return events.length ? events[0] : null
}
</script>

<template>
  <AdminLayout>
    <!-- Full-screen Calendar Mode -->
    <VenueCalendarView
      v-if="activeCalendarVenue"
      :venue="activeCalendarVenue"
      :events="venueEvents"
      @back="activeCalendarVenue = null"
    />

    <!-- Main Venues Resource Management View -->
    <section v-else class="admin-venues-page">
      <!-- Page Header -->
      <div class="page-top">
        <div>
          <h1 class="page-title">Venues</h1>
          <p class="subtitle">
            Manage university venues and availability.
          </p>
        </div>
        <button type="button" class="add-btn" @click="openAddModal">
          <span class="material-symbols-rounded icon-sm">add</span>
          Add Venue
        </button>
      </div>

      <!-- Toolbar: Search Bar and Status Filter Toggle (All | Available | Occupied | Archived) -->
      <div class="venues-toolbar">
        <div class="search-wrapper">
          <span class="material-symbols-rounded search-icon">search</span>
          <input
            v-model="search"
            type="text"
            class="search-input"
            placeholder="Search venues by name, location, or type..."
          />
        </div>

        <div class="filter-toggle-container">
          <button
            class="filter-pill-btn"
            :class="{ active: statusFilter === 'all' }"
            @click="statusFilter = 'all'"
          >
            All <span class="badge-count">{{ venueCounts.all }}</span>
          </button>
          <button
            class="filter-pill-btn"
            :class="{ active: statusFilter === 'available' }"
            @click="statusFilter = 'available'"
          >
            Available <span class="badge-count">{{ venueCounts.available }}</span>
          </button>
          <button
            class="filter-pill-btn"
            :class="{ active: statusFilter === 'occupied' }"
            @click="statusFilter = 'occupied'"
          >
            Occupied <span class="badge-count">{{ venueCounts.occupied }}</span>
          </button>
          <button
            class="filter-pill-btn"
            :class="{ active: statusFilter === 'archived' }"
            @click="statusFilter = 'archived'"
          >
            Archived <span class="badge-count">{{ venueCounts.archived }}</span>
          </button>
        </div>
      </div>

      <!-- Venues Grid -->
      <div v-if="filteredVenues.length" class="venues-grid">
        <article
          v-for="venue in filteredVenues"
          :key="venue.id"
          class="venue-card"
        >
          <div class="venue-card-header">
            <div class="venue-icon-circle">
              <span class="material-symbols-rounded">meeting_room</span>
            </div>
            <span
              class="status-badge"
              :class="formatStatus(venue.availabilityStatus).toLowerCase()"
            >
              {{ formatStatus(venue.availabilityStatus) }}
            </span>
          </div>

          <div class="venue-card-body">
            <h3 class="venue-name">{{ venue.name }}</h3>
            <p class="venue-location">
              <span class="material-symbols-rounded icon-sub">location_on</span>
              {{ venue.location }}
            </p>
            <div class="venue-meta mb-2">
              <span class="meta-tag">
                <span class="material-symbols-rounded icon-sub">category</span>
                {{ venue.type || 'General' }}
              </span>
              <span class="meta-tag">
                <span class="material-symbols-rounded icon-sub">groups</span>
                {{ venue.capacity }} Seats
              </span>
            </div>

            <!-- Booking / Occupancy Info (STEP 8) -->
            <div class="p-2.5 rounded-3 bg-light border text-xs text-secondary mt-2">
              <div v-if="getVenueUpcomingBooking(venue)">
                <div class="fw-bold text-dark mb-0.5">📅 Upcoming Booking:</div>
                <div class="text-truncate"><strong>{{ getVenueUpcomingBooking(venue).name }}</strong> ({{ getVenueUpcomingBooking(venue).clubName }})</div>
                <div class="text-muted mt-0.5">🗓️ {{ getVenueUpcomingBooking(venue).startDate }}</div>
              </div>
              <div v-else class="text-muted fst-italic">
                No upcoming reservations.
              </div>
            </div>
          </div>

          <div class="venue-card-footer">
            <button
              class="action-btn calendar-btn"
              @click="openCalendarView(venue)"
              title="View Calendar & Scheduled Events"
            >
              <span class="material-symbols-rounded icon-sm">calendar_month</span>
              View Calendar
            </button>

            <div class="action-btn-group">
              <button
                class="action-btn edit-btn"
                @click="openEditModal(venue)"
                title="Edit Venue"
              >
                <span class="material-symbols-rounded icon-sm">edit</span>
                Edit
              </button>

              <button
                class="action-btn archive-btn"
                :class="{ isArchived: (venue.availabilityStatus || '').toUpperCase() === 'ARCHIVED' }"
                @click="archiveVenue(venue)"
                title="Archive Venue"
              >
                <span class="material-symbols-rounded icon-sm">
                  {{ (venue.availabilityStatus || '').toUpperCase() === 'ARCHIVED' ? 'unarchive' : 'archive' }}
                </span>
                {{ (venue.availabilityStatus || '').toUpperCase() === 'ARCHIVED' ? 'Restore' : 'Archive' }}
              </button>
            </div>
          </div>
        </article>
      </div>

      <div v-else-if="!loading" class="empty-state">
        <span class="material-symbols-rounded empty-icon">location_off</span>
        <h3>No venues found</h3>
        <p>Try searching with another keyword or add a new venue.</p>
      </div>

      <!-- Add / Edit Venue Modal -->
      <div v-if="showVenueModal" class="modal-backdrop" @click.self="showVenueModal = false">
        <div class="modal-dialog-custom">
          <div class="modal-header">
            <h5 class="fw-bold m-0">{{ isEditing ? 'Edit Venue' : 'Add Venue' }}</h5>
            <button class="close-btn" @click="showVenueModal = false">&times;</button>
          </div>

          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label font-semibold">Venue Name</label>
              <input
                v-model="venueForm.name"
                type="text"
                class="form-control"
                placeholder="e.g. Main Auditorium"
              />
            </div>

            <div class="mb-3">
              <label class="form-label font-semibold">Location</label>
              <input
                v-model="venueForm.location"
                type="text"
                class="form-control"
                placeholder="e.g. Block A, Floor 2"
              />
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label font-semibold">Venue Type</label>
                <select v-model="venueForm.type" class="form-select">
                  <option v-for="t in venueTypes" :key="t" :value="t">{{ t }}</option>
                </select>
              </div>

              <div class="col-md-6 mb-3">
                <label class="form-label font-semibold">Capacity (Seats)</label>
                <input
                  v-model.number="venueForm.capacity"
                  type="number"
                  min="1"
                  class="form-control"
                  placeholder="e.g. 250"
                />
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showVenueModal = false">Cancel</button>
            <button class="btn btn-primary" @click="saveVenue">
              {{ isEditing ? 'Save Changes' : 'Create Venue' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Toast Notification Popup -->
      <transition name="fade">
        <div
          v-if="toast.show"
          class="toast-notification-popup"
          :class="`toast-${toast.type}`"
        >
          <span class="material-symbols-rounded">
            {{ toast.type === 'success' ? 'check_circle' : toast.type === 'danger' ? 'error' : 'info' }}
          </span>
          <span>{{ toast.message }}</span>
          <button class="btn-close-toast" @click="toast.show = false">
            <span class="material-symbols-rounded">close</span>
          </button>
        </div>
      </transition>

      <!-- Custom Confirmation Modal -->
      <div v-if="confirmModal.show" class="modal-backdrop" @click.self="confirmModal.show = false">
        <div class="modal-dialog-custom" style="max-width: 440px;">
          <div class="d-flex align-items-center gap-3 mb-3">
            <div class="icon-circle bg-warning-subtle text-warning p-3 rounded-circle d-flex align-items-center justify-content-center">
              <span class="material-symbols-rounded fs-2">help_outline</span>
            </div>
            <div>
              <h5 class="fw-bold m-0 text-dark">{{ confirmModal.title }}</h5>
              <p class="text-muted text-sm m-0 mt-1">{{ confirmModal.message }}</p>
            </div>
          </div>
          <div class="d-flex justify-content-end gap-2 mt-4 pt-3 border-top">
            <button class="btn btn-light rounded-pill px-4" @click="confirmModal.show = false">Cancel</button>
            <button class="btn btn-primary rounded-pill px-4" @click="handleConfirmExecute">Confirm</button>
          </div>
        </div>
      </div>

      <!-- View Calendar Modal (FullCalendar Integration) -->
      <VenueCalendarModal
        v-if="showCalendarModal && calendarVenue"
        :venue="calendarVenue"
        :events="venueEvents"
        @close="showCalendarModal = false"
      />
    </section>
  </AdminLayout>
</template>

<style scoped>
.toast-notification-popup {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  border-radius: 12px;
  font-weight: 600;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  animation: slideInRight 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.toast-success {
  background-color: #ecfdf5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}
.toast-danger {
  background-color: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}
.toast-warning {
  background-color: #fffbeb;
  color: #92400e;
  border: 1px solid #fef3c7;
}
.btn-close-toast {
  background: transparent;
  border: none;
  color: inherit;
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 0;
  margin-left: 8px;
}

.admin-venues-page {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
}

.page-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 28px;
  padding: 24px 28px;
  border-radius: 24px;
  background: linear-gradient(135deg, #eff6ff, #ffffff);
  border: 1px solid #dbeafe;
  box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04);
}

.page-title {
  color: #0f172a;
  font-size: 2rem;
  font-weight: 800;
  margin: 0 0 6px;
  letter-spacing: -0.02em;
}

.subtitle {
  margin: 0;
  color: #64748b;
  font-size: 0.95rem;
}

.add-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: none;
  background: #2563eb;
  color: #ffffff;
  border-radius: 12px;
  padding: 12px 20px;
  font-weight: 700;
  font-size: 0.95rem;
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25);
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.add-btn:hover {
  background: #1d4ed8;
  transform: translateY(-1px);
}

.venues-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 28px;
  flex-wrap: wrap;
}

.search-wrapper {
  position: relative;
  flex: 1;
  min-width: 280px;
}

.filter-toggle-container {
  display: inline-flex;
  align-items: center;
  background: #ffffff;
  border: 1px solid #d1d5db;
  padding: 4px;
  border-radius: 14px;
  gap: 4px;
}

.filter-pill-btn {
  border: none;
  background: transparent;
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.25s ease;
}

.filter-pill-btn:hover {
  background: #eff6ff;
  color: #1e40af;
}

.filter-pill-btn.active {
  background: #2563eb;
  color: #ffffff;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
}

.badge-count {
  min-width: 22px;
  height: 22px;
  padding: 0 6px;
  border-radius: 999px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(37, 99, 235, 0.1);
  color: #2563eb;
  font-size: 0.75rem;
  font-weight: 700;
}

.filter-pill-btn.active .badge-count {
  background: #ffffff;
  color: #2563eb;
}

.search-icon {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 22px;
}

.search-input {
  width: 100%;
  height: 52px;
  padding: 0 20px 0 52px;
  border-radius: 14px;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
}

.venues-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.venue-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 16px;
  box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04);
  transition: all 0.28s ease;
}

.venue-card:hover {
  transform: translateY(-4px);
  border-color: #3b82f6;
  box-shadow: 0 16px 36px rgba(37, 99, 235, 0.1);
}

.venue-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.venue-icon-circle {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background: #eff6ff;
  color: #2563eb;
  display: flex;
  justify-content: center;
  align-items: center;
}

.venue-icon-circle .material-symbols-rounded {
  font-size: 28px;
}

.status-badge {
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.status-badge.available {
  background: #dcfce7;
  color: #15803d;
}

.status-badge.occupied {
  background: #fef3c7;
  color: #b45309;
}

.status-badge.archived {
  background: #f1f5f9;
  color: #64748b;
}

.venue-card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.venue-name {
  margin: 0;
  color: #0f172a;
  font-size: 1.25rem;
  font-weight: 700;
}

.venue-location {
  margin: 0;
  color: #64748b;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 4px;
}

.icon-sub {
  font-size: 1.1rem;
  color: #94a3b8;
}

.venue-meta {
  display: flex;
  gap: 10px;
  margin-top: 6px;
  flex-wrap: wrap;
}

.meta-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #475569;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
}

.venue-card-footer {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 14px;
  border-top: 1px solid #f1f5f9;
}

.action-btn-group {
  display: flex;
  gap: 10px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  border: none;
  border-radius: 10px;
  padding: 8px 14px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.calendar-btn {
  width: 100%;
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}

.calendar-btn:hover {
  background: #2563eb;
  color: #ffffff;
}

.edit-btn {
  flex: 1;
  background: #f8fafc;
  color: #334155;
  border: 1px solid #cbd5e1;
}

.edit-btn:hover {
  background: #e2e8f0;
}

.archive-btn {
  flex: 1;
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.archive-btn:hover {
  background: #dc2626;
  color: #ffffff;
}

.archive-btn.isArchived {
  background: #ecfdf5;
  color: #059669;
  border-color: #a7f3d0;
}

.archive-btn.isArchived:hover {
  background: #059669;
  color: #ffffff;
}

.icon-sm {
  font-size: 1rem;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #64748b;
  background: #ffffff;
  border-radius: 20px;
  border: 1px dashed #cbd5e1;
}

.empty-icon {
  font-size: 48px;
  color: #94a3b8;
  margin-bottom: 12px;
}

/* Modals */
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
  background: #ffffff;
  border-radius: 20px;
  width: 90%;
  max-width: 540px;
  padding: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.modal-dialog-custom.modal-lg {
  max-width: 700px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 18px;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 24px;
  line-height: 1;
  color: #94a3b8;
  cursor: pointer;
}

.close-btn:hover {
  color: #0f172a;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
}

.event-schedule-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 360px;
  overflow-y: auto;
}

.schedule-item-card {
  background: #f8fafc;
  border: 1px solid #edf2f7;
  border-radius: 12px;
  padding: 14px 18px;
}

.empty-calendar {
  text-align: center;
  padding: 36px 0;
  color: #94a3b8;
}

.empty-calendar .material-symbols-rounded {
  font-size: 42px;
  margin-bottom: 8px;
}
</style>
