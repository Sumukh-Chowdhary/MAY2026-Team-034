<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-dialog-custom shadow-2xl">
      <div class="modal-header-custom">
        <h4 class="fw-bold mb-0 text-dark">
          <span class="material-symbols-rounded text-primary me-2 align-middle">add_circle</span>
          Create New Event
        </h4>
        <button class="btn-close-custom" @click="$emit('close')">
          <span class="material-symbols-rounded">close</span>
        </button>
      </div>

      <div class="modal-body-custom">
        <!-- Event Name -->
        <div class="mb-3">
          <label class="form-label text-sm fw-bold">Event Name *</label>
          <input 
            v-model="form.name" 
            type="text" 
            class="form-control custom-input" 
            placeholder="e.g. AI & Machine Learning Workshop" 
          />
        </div>

        <!-- Event Scope (Only visible for Admin) -->
        <div class="mb-3" v-if="currentUser?.role === 'ADMIN'">
          <label class="form-label text-sm fw-bold">Event Classification *</label>
          <div class="scope-toggle-group">
            <button
              type="button"
              class="scope-toggle-btn"
              :class="{ 'scope-toggle-active': form.eventScope === 'CLUB_EVENT' }"
              @click="form.eventScope = 'CLUB_EVENT'"
            >
              👥 Club Event
            </button>
            <button
              type="button"
              class="scope-toggle-btn"
              :class="{ 'scope-toggle-active': form.eventScope === 'GENERAL_EVENT' }"
              @click="form.eventScope = 'GENERAL_EVENT'"
            >
              🎓 General Event
            </button>
          </div>
        </div>

        <!-- Event Type Category -->
        <div class="mb-3">
          <label class="form-label text-sm fw-bold">Event Category</label>
          <select v-model="form.eventType" class="form-select custom-input">
            <option value="Workshop">🏫 Workshop / Seminar</option>
            <option value="Hackathon">💻 Hackathon / Coding</option>
            <option value="Cultural">🎭 Cultural / Drama</option>
            <option value="Sports">⚽ Sports / Tournament</option>
            <option value="Music">🎵 Music / Performance</option>
            <option value="General">🎉 General Event</option>
          </select>
        </div>

        <!-- Searchable Club Autocomplete Dropdown (If Club Event) -->
        <div class="mb-3 position-relative" v-if="form.eventScope === 'CLUB_EVENT' && !fixedClubId">
          <label class="form-label text-sm fw-bold">Select Club *</label>
          
          <div class="input-group">
            <span class="input-group-text bg-light text-muted border-end-0">
              <span class="material-symbols-rounded icon-sm">search</span>
            </span>
            <input
              v-model="clubSearchQuery"
              type="text"
              class="form-control custom-input border-start-0"
              placeholder="Search and select club..."
              @focus="showClubDropdown = true"
              @input="onClubInput"
            />
          </div>

          <!-- Dropdown List -->
          <div v-if="showClubDropdown" class="club-autocomplete-dropdown">
            <div
              v-for="club in filteredClubs"
              :key="club.id"
              class="dropdown-item-custom"
              @click="selectClub(club)"
            >
              <div class="d-flex justify-content-between align-items-center">
                <span class="fw-semibold text-dark">{{ club.name || club.club_name }}</span>
                <span class="category-badge-sm">{{ club.category || club.club_category || 'General' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Searchable Faculty Organizer Dropdown (If Admin creating General Event) -->
        <div class="mb-3 position-relative" v-if="currentUser?.role === 'ADMIN' && form.eventScope === 'GENERAL_EVENT'">
          <label class="form-label text-sm fw-bold">Faculty Event Organizer *</label>
          
          <div class="input-group">
            <span class="input-group-text bg-light text-muted border-end-0">
              <span class="material-symbols-rounded icon-sm">person_search</span>
            </span>
            <input
              v-model="facultySearchQuery"
              type="text"
              class="form-control custom-input border-start-0"
              placeholder="Search and assign faculty organizer..."
              @focus="showFacultyDropdown = true"
            />
          </div>

          <div v-if="showFacultyDropdown && filteredFaculty.length" class="club-autocomplete-dropdown">
            <div
              v-for="fac in filteredFaculty"
              :key="fac.id"
              class="dropdown-item-custom"
              @click="selectFacultyOrganizer(fac)"
            >
              <div class="d-flex justify-content-between align-items-center">
                <span class="fw-semibold text-dark">👨‍🏫 {{ fac.name || fac.email }}</span>
                <span class="category-badge-sm">{{ fac.department || 'Faculty' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Searchable Venue Autocomplete Dropdown -->
        <div class="mb-3 position-relative">
          <label class="form-label text-sm fw-bold">Select Venue</label>

          <div class="input-group">
            <span class="input-group-text bg-light text-muted border-end-0">
              <span class="material-symbols-rounded icon-sm">location_on</span>
            </span>
            <input
              v-model="venueSearchQuery"
              type="text"
              class="form-control custom-input border-start-0"
              placeholder="Search or select a venue..."
              @focus="showVenueDropdown = true"
              @input="onVenueInput"
            />
          </div>

          <!-- Venue Dropdown List -->
          <div v-if="showVenueDropdown && filteredVenues.length" class="club-autocomplete-dropdown">
            <div
              v-for="v in filteredVenues"
              :key="v.id"
              class="dropdown-item-custom"
              @click="selectVenue(v)"
            >
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="fw-semibold text-dark">{{ v.name }}</span>
                <span class="category-badge-sm">{{ v.type || 'General' }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center text-muted text-xs">
                <span>📍 {{ v.location }}</span>
                <span>👥 {{ v.capacity }} Seats</span>
              </div>
            </div>
          </div>

          <div v-if="showVenueDropdown && !filteredVenues.length" class="club-autocomplete-dropdown p-3 text-muted text-center text-sm">
            No matching venues found
          </div>
        </div>

        <!-- Date Pickers (Goal 9) -->
        <div class="row g-3 mb-3">
          <div class="col-6">
            <label class="form-label text-sm fw-bold">Start Date *</label>
            <input 
              v-model="form.startDate" 
              type="date" 
              class="form-control custom-input" 
            />
          </div>
          <div class="col-6">
            <label class="form-label text-sm fw-bold">End Date *</label>
            <input 
              v-model="form.endDate" 
              type="date" 
              class="form-control custom-input" 
            />
          </div>
        </div>

        <!-- Venue Availability Status Indicator -->
        <div v-if="form.startDate && form.endDate" class="mb-3">
          <div v-if="form.endDate < form.startDate" class="p-3 rounded-3 border border-danger bg-danger-subtle text-danger font-semibold d-flex align-items-center gap-2">
            <span class="material-symbols-rounded text-danger">error</span>
            <span>⚠️ End date cannot be before start date</span>
          </div>

          <div v-else-if="form.venueId && checkingAvailability" class="p-3 bg-light rounded-3 border text-muted small d-flex align-items-center gap-2">
            <span class="spinner-border spinner-border-sm"></span>
            <span>Checking venue availability...</span>
          </div>

          <div v-else-if="form.venueId && venueAvailabilityStatus === 'AVAILABLE'" class="p-3 rounded-3 border border-success bg-success-subtle text-success font-semibold d-flex align-items-center gap-2">
            <span class="material-symbols-rounded">check_circle</span>
            <span>✓ Venue Available</span>
          </div>

          <div v-else-if="form.venueId && venueAvailabilityStatus === 'OCCUPIED'" class="p-3 rounded-3 border border-warning bg-warning-subtle text-dark">
            <div class="d-flex align-items-center gap-2 text-danger fw-bold mb-2">
              <span class="material-symbols-rounded text-danger">warning</span>
              <span>⚠ Venue already booked</span>
            </div>
            <div v-if="conflictingEventDetails" class="small bg-white p-2.5 rounded-3 border">
              <div class="mb-1"><strong>Existing Event:</strong> {{ conflictingEventDetails.name }}</div>
              <div class="mb-1"><strong>Club:</strong> {{ conflictingEventDetails.club || conflictingEventDetails.clubName || 'N/A' }}</div>
              <div><strong>Reserved Time:</strong> 📅 {{ conflictingEventDetails.startDate }} to {{ conflictingEventDetails.endDate }} (⏰ {{ conflictingEventDetails.startTime }} - {{ conflictingEventDetails.endTime }})</div>
            </div>
          </div>
        </div>

        <!-- Description -->
        <div class="mb-3">
          <label class="form-label text-sm fw-bold">Description</label>
          <textarea 
            v-model="form.description" 
            class="form-control custom-input" 
            rows="3" 
            placeholder="Provide event overview and details..."
          ></textarea>
        </div>

        <!-- Faculty Permission Warning Banner -->
        <div v-if="!isFacultyPermissionValid" class="alert alert-danger d-flex align-items-center gap-2 rounded-3 text-sm p-3 mb-0">
          <span class="material-symbols-rounded icon-sm">gpp_maybe</span>
          <div>
            <strong>Permission Denied:</strong> You are not assigned as Faculty Coordinator for this club. Only assigned Faculty Coordinators can submit event requests for this club.
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="modal-footer-custom">
        <button class="btn btn-light me-2 rounded-pill px-4" @click="$emit('close')">Cancel</button>
        <button
          class="btn btn-success font-semibold rounded-pill px-4"
          :disabled="loading || !isFacultyPermissionValid || checkingAvailability || venueAvailabilityStatus === 'OCCUPIED' || (form.startDate && form.endDate && form.endDate < form.startDate)"
          @click="handleSubmit"
        >
          <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
          {{ loading ? 'Creating...' : 'Create Event' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { createEvent } from '@/api/events'
import { getClubs } from '@/api/clubs'
import { getVenues, checkVenueAvailability } from '@/api/venues'
import { getCurrentUser } from '@/services/authService'
import { getMySupervisedClubs } from '@/api/faculty'
import { getUsers } from '@/api/users'
import { useToast } from '@/composables/useToast'

const { showToast } = useToast()
const currentUser = getCurrentUser()
const supervisedClubIds = ref([])

const props = defineProps({
  fixedClubId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['close', 'created', 'submit'])

const loading = ref(false)
const clubsList = ref([])
const clubSearchQuery = ref('')
const selectedClubObj = ref(null)
const showClubDropdown = ref(false)

const venuesList = ref([])
const venueSearchQuery = ref('')
const selectedVenueObj = ref(null)
const showVenueDropdown = ref(false)

const checkingAvailability = ref(false)
const venueAvailabilityStatus = ref(null) // null | 'AVAILABLE' | 'OCCUPIED'
const conflictingEventDetails = ref(null)

const facultyList = ref([])
const facultySearchQuery = ref('')
const selectedFacultyOrganizerObj = ref(null)
const showFacultyDropdown = ref(false)

const form = ref({
  name: '',
  eventScope: 'CLUB_EVENT',
  club: '',
  clubId: null,
  facultyOrganizerId: null,
  venueId: null,
  venueName: '',
  eventType: 'General',
  startDate: '',
  endDate: '',
  description: ''
})

async function runVenueCheck() {
  if (!form.value.venueId || !form.value.startDate || !form.value.endDate) {
    venueAvailabilityStatus.value = null
    conflictingEventDetails.value = null
    return
  }

  if (form.value.endDate < form.value.startDate) {
    venueAvailabilityStatus.value = 'INVALID_DATES'
    conflictingEventDetails.value = null
    return
  }

  checkingAvailability.value = true
  try {
    const res = await checkVenueAvailability(
      form.value.venueId,
      form.value.startDate,
      form.value.endDate
    )

    if (res.available) {
      venueAvailabilityStatus.value = 'AVAILABLE'
      conflictingEventDetails.value = null
    } else {
      venueAvailabilityStatus.value = 'OCCUPIED'
      conflictingEventDetails.value = res.conflictingEvent
    }
  } catch (err) {
    console.error('Error checking venue availability', err)
    venueAvailabilityStatus.value = null
    conflictingEventDetails.value = null
  } finally {
    checkingAvailability.value = false
  }
}

watch(
  [() => form.value.venueId, () => form.value.startDate, () => form.value.endDate],
  () => {
    runVenueCheck()
  }
)

onMounted(async () => {
  if (currentUser?.role === 'FACULTY') {
    try {
      const myClubs = await getMySupervisedClubs()
      supervisedClubIds.value = (myClubs || []).map(c => Number(c.id || c.clubId))
    } catch (e) {
      console.error('Failed to fetch supervised clubs', e)
    }
  }

  if (!props.fixedClubId) {
    try {
      const clubs = await getClubs()
      clubsList.value = clubs || []
    } catch (e) {
      console.error('Failed to fetch clubs list', e)
    }
  }

  try {
    const venues = await getVenues()
    venuesList.value = venues || []
  } catch (e) {
    console.error('Failed to fetch venues list', e)
  }

  if (currentUser?.role === 'ADMIN') {
    try {
      const usersRes = await getUsers()
      const users = Array.isArray(usersRes) ? usersRes : (usersRes.data || usersRes.users || [])
      facultyList.value = users.filter(u => (u.role || u.userRole || '').toUpperCase() === 'FACULTY')
    } catch (e) {
      console.error('Failed to fetch faculty list', e)
    }
  }
})

const isFacultyPermissionValid = computed(() => {
  if (currentUser?.role !== 'FACULTY') return true
  if (form.value.eventScope === 'GENERAL_EVENT') return true
  const targetId = Number(props.fixedClubId || form.value.clubId)
  if (!targetId) return true
  return supervisedClubIds.value.includes(targetId)
})

const filteredFaculty = computed(() => {
  if (!facultySearchQuery.value.trim()) return facultyList.value
  const q = facultySearchQuery.value.toLowerCase()
  return facultyList.value.filter(f => (f.name || f.email || '').toLowerCase().includes(q))
})

function selectFacultyOrganizer(fac) {
  selectedFacultyOrganizerObj.value = fac
  form.value.facultyOrganizerId = fac.id
  facultySearchQuery.value = fac.name || fac.email
  showFacultyDropdown.value = false
}

const filteredClubs = computed(() => {
  if (!clubSearchQuery.value.trim()) return clubsList.value
  const q = clubSearchQuery.value.toLowerCase()
  return clubsList.value.filter(c => {
    const name = (c.name || c.club_name || '').toLowerCase()
    const cat = (c.category || c.club_category || '').toLowerCase()
    return name.includes(q) || cat.includes(q)
  })
})

function onClubInput() {
  showClubDropdown.value = true
  form.value.club = clubSearchQuery.value
  form.value.clubId = null
}

function selectClub(club) {
  if (!club) {
    selectedClubObj.value = null
    form.value.club = 'General / Institutional'
    form.value.clubId = null
    clubSearchQuery.value = 'General / Institutional (No Club)'
  } else {
    selectedClubObj.value = club
    form.value.club = club.name || club.club_name
    form.value.clubId = club.id
    clubSearchQuery.value = club.name || club.club_name
  }
  showClubDropdown.value = false
}

const filteredVenues = computed(() => {
  const activeVenues = venuesList.value.filter(v => (v.availabilityStatus || v.status || '').toUpperCase() !== 'ARCHIVED')
  if (!venueSearchQuery.value.trim()) return activeVenues
  const q = venueSearchQuery.value.toLowerCase()
  return activeVenues.filter(v => {
    const name = (v.name || '').toLowerCase()
    const loc = (v.location || '').toLowerCase()
    const type = (v.type || '').toLowerCase()
    return name.includes(q) || loc.includes(q) || type.includes(q)
  })
})

function onVenueInput() {
  showVenueDropdown.value = true
  form.value.venueName = venueSearchQuery.value
  form.value.venueId = null
}

function selectVenue(v) {
  selectedVenueObj.value = v
  form.value.venueId = v.id
  form.value.venueName = v.name
  venueSearchQuery.value = v.name
  showVenueDropdown.value = false
}

async function handleSubmit() {
  if (!isFacultyPermissionValid.value) {
    showToast('You are not assigned as Faculty Coordinator for this club and cannot create event requests for it.', 'error')
    return
  }

  if (!form.value.name.trim()) {
    showToast('Please provide Event Name.', 'warning')
    return
  }

  if (form.value.eventScope === 'CLUB_EVENT' && !props.fixedClubId && !form.value.club.trim() && !form.value.clubId) {
    showToast('Please select a Club.', 'warning')
    return
  }

  if (!form.value.startDate || !form.value.endDate) {
    showToast('Please select valid Start and End dates.', 'warning')
    return
  }

  loading.value = true

  const isGeneral = form.value.eventScope === 'GENERAL_EVENT'
  const targetClubId = isGeneral ? null : (props.fixedClubId ?? form.value.clubId ?? form.value.club)

  const payload = {
    name: form.value.name.trim(),
    description: form.value.description,
    status: 'SCHEDULED',
    organizerType: isGeneral ? 'GENERAL' : 'CLUB',
    eventType: form.value.eventType,
    startDate: form.value.startDate,
    endDate: form.value.endDate,
    venueId: form.value.venueId,
    venueName: form.value.venueName || venueSearchQuery.value,
    club: isGeneral ? null : (form.value.club || 'Club Event'),
    clubId: targetClubId,
    facultyOrganizerId: isGeneral ? form.value.facultyOrganizerId : null,
    capacity: selectedVenueObj.value?.capacity || 0
  }

  try {
    const res = await createEvent(payload)

    if (res && res.isRequest) {
      showToast(`Event creation request for "${res.name || form.value.name}" submitted successfully for approval!`, 'success')
    } else {
      showToast(`Event "${res?.name || form.value.name}" created and venue reserved successfully!`, 'success')
    }

    emit('created', res)
    emit('submit', res)
    emit('close')
  } catch (error) {
    console.error('Failed to create event', error)
    const errMessage = error?.response?.data?.error || 'Failed to process event creation.'
    showToast(errMessage, 'error')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1.5rem;
}

.modal-dialog-custom {
  background: #ffffff;
  border-radius: 24px;
  width: 100%;
  max-width: 600px;
  overflow: hidden;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.modal-header-custom {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fafc;
}

.btn-close-custom {
  background: #e2e8f0;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-close-custom:hover {
  background: #cbd5e1;
  color: #0f172a;
}

.btn-close-custom .material-symbols-rounded {
  font-size: 1.2rem;
}

.modal-body-custom {
  padding: 1.5rem;
  max-height: 75vh;
  overflow-y: auto;
}

.custom-input {
  border-radius: 12px;
  border: 1px solid #cbd5e1;
  padding: 0.6rem 0.9rem;
  font-size: 0.95rem;
}

.custom-input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.club-autocomplete-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 1050;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 14px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.15);
  max-height: 200px;
  overflow-y: auto;
  margin-top: 4px;
}

.dropdown-item-custom {
  padding: 10px 14px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.dropdown-item-custom:hover {
  background: #eff6ff;
}

.category-badge-sm {
  background: #eef2ff;
  color: #2563eb;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.modal-footer-custom {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  background: #f8fafc;
}

/* Event Classification segmented toggle */
.scope-toggle-group {
  display: flex;
  width: 100%;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  overflow: hidden;
  background: #f8fafc;
}

.scope-toggle-btn {
  flex: 1;
  padding: 0.55rem 0.75rem;
  border: none;
  background: transparent;
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.18s ease, color 0.18s ease;
  white-space: nowrap;
}

.scope-toggle-btn:not(:last-child) {
  border-right: 1px solid #cbd5e1;
}

.scope-toggle-btn:hover:not(.scope-toggle-active) {
  background: #eff6ff;
  color: #2563eb;
}

.scope-toggle-active {
  background: #2563eb;
  color: #ffffff;
}
</style>
