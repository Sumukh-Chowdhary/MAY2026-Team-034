<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { getCalendarEvents } from '@/api/events'
import ScheduleConflictModal from '@/components/common/ScheduleConflictModal.vue'
import { useScheduleConflictCheck } from '@/composables/useScheduleConflictCheck'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const events = ref([])
const loading = ref(false)
const search = ref('')
const selectedFilter = ref('ALL') // 'ALL' | 'REGISTERED' | 'UPCOMING' | 'COMPLETED'
const activeView = ref('agenda') // 'agenda' | 'month'
const registeringIds = ref({})

const {
  showConflictModal,
  pendingConflicts,
  pendingEventName,
  registerWithConflictCheck,
  confirmRegistration,
  cancelRegistration
} = useScheduleConflictCheck()

onMounted(() => {
  if (props.show) {
    loadCalendarData()
  }
})

watch(() => props.show, (newVal) => {
  if (newVal) {
    loadCalendarData()
  }
})

async function loadCalendarData() {
  loading.value = true
  try {
    const data = await getCalendarEvents()
    events.value = data || []
  } catch (err) {
    console.error('Failed to load calendar events', err)
  } finally {
    loading.value = false
  }
}

const filteredEvents = computed(() => {
  return events.value.filter(evt => {
    const q = search.value.trim().toLowerCase()
    const matchesSearch = !q ||
      (evt.name || '').toLowerCase().includes(q) ||
      (evt.clubName || '').toLowerCase().includes(q) ||
      (evt.venueName || '').toLowerCase().includes(q) ||
      (evt.contactName || '').toLowerCase().includes(q)

    let matchesFilter = true
    if (selectedFilter.value === 'REGISTERED') {
      matchesFilter = ['REGISTERED', 'CONFIRMED', 'ATTENDED', 'PRESENT'].includes(evt.registrationStatus)
    } else if (selectedFilter.value === 'UPCOMING') {
      matchesFilter = evt.status !== 'COMPLETED'
    } else if (selectedFilter.value === 'COMPLETED') {
      matchesFilter = evt.status === 'COMPLETED'
    }

    return matchesSearch && matchesFilter
  })
})

function formatGoogleCalendarUrl(evt) {
  const title = encodeURIComponent(evt.name || 'Campus Event')
  const details = encodeURIComponent(`${evt.description || ''}\n\nOrganizing Club: ${evt.clubName || 'General'}\nPoint of Contact: ${evt.contactName || 'N/A'} (${evt.contactRole || 'Coordinator'})`)
  const location = encodeURIComponent(`${evt.venueName || 'Campus Venue'} - ${evt.venueLocation || ''}`)

  let startStr = (evt.startDate || '').replace(/-/g, '')
  let endStr = (evt.endDate || evt.startDate || '').replace(/-/g, '')

  let startTimeStr = (evt.startTime || '09:00').replace(/:/g, '') + '00'
  let endTimeStr = (evt.endTime || '17:00').replace(/:/g, '') + '00'

  const datesStr = `${startStr}T${startTimeStr}/${endStr}T${endTimeStr}`
  return `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${datesStr}&details=${details}&location=${location}`
}

function exportICal(evt) {
  const title = evt.name || 'Campus Event'
  const description = (evt.description || '').replace(/\n/g, ' ')
  const location = `${evt.venueName || 'Campus Venue'}, ${evt.venueLocation || ''}`

  const startStr = (evt.startDate || '').replace(/-/g, '')
  const endStr = (evt.endDate || evt.startDate || '').replace(/-/g, '')
  const startTimeStr = (evt.startTime || '09:00').replace(/:/g, '') + '00'
  const endTimeStr = (evt.endTime || '17:00').replace(/:/g, '') + '00'

  const icalData = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//Campus Club Event Management//EN',
    'BEGIN:VEVENT',
    `SUMMARY:${title}`,
    `DESCRIPTION:${description} | POC: ${evt.contactName || 'N/A'}`,
    `LOCATION:${location}`,
    `DTSTART:${startStr}T${startTimeStr}`,
    `DTEND:${endStr}T${endTimeStr}`,
    `STATUS:${evt.status === 'CANCELLED' ? 'CANCELLED' : 'CONFIRMED'}`,
    'END:VEVENT',
    'END:VCALENDAR'
  ].join('\r\n')

  const blob = new Blob([icalData], { type: 'text/calendar;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `${title.replace(/\s+/g, '_')}_event.ics`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

async function handleRegister(evt) {
  if (registeringIds.value[evt.id] || ['REGISTERED', 'CONFIRMED', 'ATTENDED'].includes(evt.registrationStatus)) return
  registeringIds.value[evt.id] = true
  try {
    const result = await registerWithConflictCheck(evt.id, evt.name || evt.title)
    if (result.cancelled) return
    evt.registrationStatus = 'REGISTERED'
    evt.color = '#10b981'
  } catch (err) {
    console.error('Registration failed', err)
  } finally {
    registeringIds.value[evt.id] = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="modal-backdrop-glass" @click.self="$emit('close')">
      <div class="modal-box shadow-2xl">
        
        <!-- Modal Header -->
        <div class="modal-header-custom">
          <div>
            <div class="d-flex align-items-center gap-2">
              <i class="bi bi-calendar-event-fill text-primary display-6"></i>
              <div>
                <h4 class="fw-bold mb-0 text-slate-800">Campus & Club Events Calendar</h4>
                <small class="text-secondary">Sync events to Google Calendar or export to local apps (.ics)</small>
              </div>
            </div>
          </div>
          <button class="btn-close-custom" @click="$emit('close')"><i class="bi bi-x-lg"></i></button>
        </div>

        <!-- Toolbar & Filters -->
        <div class="modal-subnav">
          <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
            
            <div class="search-box flex-grow-1">
              <div class="input-group input-group-sm">
                <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
                <input v-model="search" type="text" class="form-control border-start-0 ps-0" placeholder="Search event, club, venue or contact..." />
              </div>
            </div>

            <!-- View Switcher & Status Filter -->
            <div class="d-flex align-items-center gap-2">
              <div class="btn-group btn-group-sm">
                <button class="btn btn-outline-primary" :class="{ active: selectedFilter === 'ALL' }" @click="selectedFilter = 'ALL'">All</button>
                <button class="btn btn-outline-success" :class="{ active: selectedFilter === 'REGISTERED' }" @click="selectedFilter = 'REGISTERED'">Registered</button>
                <button class="btn btn-outline-info" :class="{ active: selectedFilter === 'UPCOMING' }" @click="selectedFilter = 'UPCOMING'">Upcoming</button>
                <button class="btn btn-outline-secondary" :class="{ active: selectedFilter === 'COMPLETED' }" @click="selectedFilter = 'COMPLETED'">Past</button>
              </div>
            </div>

          </div>

          <!-- Color Coding Legend -->
          <div class="legend-bar mt-2 d-flex align-items-center gap-3 flex-wrap text-xs">
            <span class="text-muted fw-bold">Legend:</span>
            <span class="legend-item"><span class="color-dot bg-registered"></span> Registered / Attended</span>
            <span class="legend-item"><span class="color-dot bg-available"></span> Available / Open</span>
            <span class="legend-item"><span class="color-dot bg-past"></span> Past / Completed</span>
          </div>
        </div>

        <!-- Body Content -->
        <div class="modal-body-custom">
          
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="text-muted mt-2">Loading calendar events...</p>
          </div>

          <div v-else-if="filteredEvents.length > 0" class="events-list d-flex flex-column gap-3">
            <div 
              v-for="evt in filteredEvents" 
              :key="evt.id"
              class="event-calendar-card"
              :style="{ borderLeftColor: evt.color }"
            >
              <div class="d-flex justify-content-between align-items-start flex-wrap gap-2">
                <div>
                  <div class="d-flex align-items-center gap-2 mb-1">
                    <span class="badge" :style="{ backgroundColor: evt.color, color: '#fff' }">
                      {{ evt.registrationStatus === 'REGISTERED' || evt.registrationStatus === 'ATTENDED' ? '✓ REGISTERED' : evt.registrationStatus }}
                    </span>
                    <span class="badge bg-light text-dark border">{{ evt.clubName }}</span>
                    <span class="badge bg-secondary-subtle text-dark" v-if="evt.status">{{ evt.status }}</span>
                  </div>

                  <h5 class="fw-bold text-slate-800 mb-1">{{ evt.name }}</h5>
                  <p class="text-sm text-secondary mb-2">{{ evt.description }}</p>

                  <div class="event-details-bar d-flex align-items-center gap-3 flex-wrap text-xs text-muted">
                    <span><i class="bi bi-calendar3 me-1 text-primary"></i> {{ evt.startDate }} <span v-if="evt.endDate && evt.endDate !== evt.startDate">to {{ evt.endDate }}</span></span>
                    <span><i class="bi bi-clock me-1 text-primary"></i> {{ evt.startTime }} - {{ evt.endTime }}</span>
                    <span><i class="bi bi-geo-alt-fill me-1 text-danger"></i> {{ evt.venueName }} ({{ evt.venueLocation }})</span>
                    <span v-if="evt.contactName"><i class="bi bi-person-circle me-1 text-info"></i> POC: <strong>{{ evt.contactName }}</strong> ({{ evt.contactRole }})</span>
                  </div>
                </div>

                <!-- Sync & Registration Actions -->
                <div class="d-flex flex-column align-items-end gap-2">
                  
                  <div class="d-flex gap-1">
                    <a :href="formatGoogleCalendarUrl(evt)" target="_blank" class="btn btn-sm btn-outline-danger rounded-pill px-3 text-xs" title="Sync to Google Calendar">
                      <i class="bi bi-google me-1"></i> Sync Google Cal
                    </a>

                    <button class="btn btn-sm btn-outline-secondary rounded-pill px-3 text-xs" @click="exportICal(evt)" title="Download .ics File">
                      <i class="bi bi-download me-1"></i> .ics Export
                    </button>
                  </div>

                  <button 
                    v-if="evt.registrationStatus !== 'REGISTERED' && evt.registrationStatus !== 'ATTENDED' && evt.status !== 'COMPLETED'"
                    class="btn btn-sm btn-success rounded-pill px-3 text-xs fw-bold"
                    :disabled="registeringIds[evt.id]"
                    @click="handleRegister(evt)"
                  >
                    {{ registeringIds[evt.id] ? 'Registering...' : 'Register for Event' }}
                  </button>
                </div>

              </div>
            </div>
          </div>

          <div v-else class="empty-state text-center py-5">
            <i class="bi bi-calendar-x display-4 text-muted"></i>
            <h5 class="mt-3 text-slate-700">No Events Found</h5>
            <p class="text-secondary text-sm">No events match your current filter or search criteria.</p>
          </div>

        </div>

        <!-- Modal Footer -->
        <div class="modal-footer-custom">
          <button class="btn btn-secondary rounded-pill px-4" @click="$emit('close')">Close Calendar</button>
        </div>

      </div>
    </div>
  </Teleport>

  <ScheduleConflictModal
    :show="showConflictModal"
    :event-name="pendingEventName"
    :conflicts="pendingConflicts"
    @confirm="confirmRegistration"
    @cancel="cancelRegistration"
  />
</template>

<style scoped>
.modal-backdrop-glass {
  position: fixed;
  inset: 0;
  z-index: 1070;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.modal-box {
  width: 100%;
  max-width: 900px;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(24px);
  border-radius: 24px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}

.modal-header-custom {
  padding: 1.25rem 1.75rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
}

.btn-close-custom {
  background: #f1f5f9;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  cursor: pointer;
}

.modal-subnav {
  padding: 1rem 1.75rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #475569;
}

.color-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.bg-registered { background: #10b981; }
.bg-available { background: #3b82f6; }
.bg-past { background: #6b7280; }

.modal-body-custom {
  padding: 1.5rem 1.75rem;
  overflow-y: auto;
  flex: 1;
}

.event-calendar-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-left-width: 6px;
  border-radius: 16px;
  padding: 1rem 1.25rem;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.event-calendar-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.06);
}

.modal-footer-custom {
  padding: 1rem 1.75rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  background: white;
}
</style>
