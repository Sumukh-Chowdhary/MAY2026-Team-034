<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import FacultyLayout from '@/layouts/FacultyLayout.vue'
import UserProfileModal from '@/components/common/UserProfileModal.vue'
import EventAttendanceView from '@/components/events/EventAttendanceView.vue'
import EventAttendanceModal from '@/components/events/EventAttendanceModal.vue'
import EventRoundsView from '@/components/events/EventRoundsView.vue'
import ParticipantProgressView from '@/components/events/ParticipantProgressView.vue'
import EventResultsView from '@/components/events/EventResultsView.vue'
import RequestVenueModal from '@/components/events/RequestVenueModal.vue'
import EventVolunteersSection from '@/components/events/EventVolunteersSection.vue'
import {
  getEvent,
  updateEventStatus,
  manageEventSchedule,
  manageEventAnnouncements,
  manageEventAttendance,
  assignVenue,
  updateVolunteerStatus
} from '@/api/events'
import { getVenues } from '@/api/venues'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const { showToast } = useToast()
const activeTab = ref('schedule')
const event = ref(null)
const loading = ref(false)
const statusDraft = ref('SCHEDULED')
const venues = ref([])
const selectedVenueId = ref('')
const scheduleInput = ref({ time: '', activity: '' })
const announcementInput = ref({ title: '', message: '' })

const showProfileModal = ref(false)
const showAttendanceModal = ref(false)
const showVenueRequestModal = ref(false)
const selectedProfileUserId = ref(null)

function openUserProfile(id) {
  if (!id) return
  selectedProfileUserId.value = id
  showProfileModal.value = true
}
const isSaving = ref(false)

// Attendance Sheet filter & search
const attendanceSearch = ref('')
const attendanceStatusFilter = ref('ALL') // 'ALL' | 'PRESENT' | 'ABSENT'

const normalizeEvent = (data) => ({
  ...data,
  emoji: data.emoji || '🎉',
  status: String(data.status || 'SCHEDULED'),
  club: data.clubName || data.club || 'Unknown Club',
  name: data.name || data.eventName || data.event_name || 'Untitled Event',
  description: data.description || data.eventDescription || data.event_description || 'No description available.',
  schedule: Array.isArray(data.schedule) ? data.schedule.map((item) => ({ time: item.time || item.scheduleTime || '', activity: item.activity || item.title || '' })) : [],
  announcements: Array.isArray(data.announcements) ? data.announcements : [],
  volunteers: Array.isArray(data.volunteers) ? data.volunteers : [],
  registrations: Array.isArray(data.registrations)
    ? data.registrations.map((entry) => ({
        id: entry.id,
        userId: entry.userId || entry.id,
        name: entry.userName || entry.name || 'Participant',
        registerNumber: entry.registerNumber || entry.userId || 'N/A',
        branch: entry.branch || 'N/A',
        status: entry.status || 'REGISTERED'
      }))
    : [],
  attendance: Array.isArray(data.attendance)
    ? data.attendance.map((entry) => ({
        id: entry.id,
        userId: entry.userId || entry.id,
        name: entry.userName || entry.name || 'Participant',
        registerNumber: entry.registerNumber || entry.userId || 'N/A',
        status: entry.status || 'PRESENT'
      }))
    : []
})

import { getMySupervisedClubs } from '@/api/faculty'
import { getCurrentUser } from '@/services/authService'

const isAuthorizedFaculty = ref(false)

async function checkFacultyAuthorization() {
  const user = getCurrentUser()
  if (!user || !event.value) return

  if (Number(event.value.createdBy) === Number(user.id)) {
    isAuthorizedFaculty.value = true
    return
  }

  if (!event.value.clubId) {
    if (Array.isArray(event.value.organizers) && event.value.organizers.some(o => Number(o.userId || o.id) === Number(user.id))) {
      isAuthorizedFaculty.value = true
    } else {
      isAuthorizedFaculty.value = false
    }
    return
  }

  try {
    const supervised = await getMySupervisedClubs()
    const list = Array.isArray(supervised) ? supervised : (supervised?.clubs || supervised?.data || [])
    const isCoord = list.some(c => Number(c.id || c.clubId) === Number(event.value.clubId))
    isAuthorizedFaculty.value = isCoord
  } catch (e) {
    isAuthorizedFaculty.value = false
  }
}

async function fetchEventDetails() {
  try {
    const data = await getEvent(Number(route.params.id))
    event.value = normalizeEvent(data)
    statusDraft.value = event.value.status
    if (event.value.venueId) {
      selectedVenueId.value = String(event.value.venueId)
    }
    await checkFacultyAuthorization()
  } catch (error) {
    console.error('Failed to load event details', error)
  }
}

// Aliases for template compatibility
const loadEventData = fetchEventDetails
const loadEvent = fetchEventDetails

onMounted(async () => {
  loading.value = true
  try {
    venues.value = await getVenues()
    await fetchEventDetails()
  } finally {
    loading.value = false
  }
})

// Full Attendance Sheet Computations
const combinedAttendanceSheet = computed(() => {
  if (!event.value) return []
  const regs = event.value.registrations || []
  const attMap = new Map((event.value.attendance || []).map(a => [a.userId, a.status]))

  return regs.map(r => ({
    userId: r.userId,
    name: r.name,
    registerNumber: r.registerNumber,
    branch: r.branch,
    attendanceStatus: attMap.get(r.userId) || 'ABSENT'
  }))
})

const attendanceStats = computed(() => {
  const total = combinedAttendanceSheet.value.length
  const present = combinedAttendanceSheet.value.filter(s => s.attendanceStatus === 'PRESENT').length
  const absent = total - present
  const rate = total > 0 ? Math.round((present / total) * 100) : 0
  return { total, present, absent, rate }
})

const filteredAttendanceSheet = computed(() => {
  return combinedAttendanceSheet.value.filter(item => {
    const q = attendanceSearch.value.trim().toLowerCase()
    const matchesQuery = !q ||
      item.name.toLowerCase().includes(q) ||
      String(item.registerNumber).toLowerCase().includes(q)

    let matchesFilter = true
    if (attendanceStatusFilter.value === 'PRESENT') {
      matchesFilter = item.attendanceStatus === 'PRESENT'
    } else if (attendanceStatusFilter.value === 'ABSENT') {
      matchesFilter = item.attendanceStatus === 'ABSENT'
    }

    return matchesQuery && matchesFilter
  })
})

async function saveStatus() {
  if (!event.value) return
  isSaving.value = true
  try {
    const updated = await updateEventStatus(event.value.id, statusDraft.value)
    event.value = normalizeEvent(updated)
  } catch (error) {
    console.error('Failed to update status', error)
  } finally {
    isSaving.value = false
  }
}

async function saveSchedule() {
  if (!event.value || !scheduleInput.value.activity.trim()) return
  isSaving.value = true
  try {
    const updated = await manageEventSchedule(event.value.id, [{ time: scheduleInput.value.time || '10:00', activity: scheduleInput.value.activity }], true)
    event.value = normalizeEvent(updated)
    scheduleInput.value = { time: '', activity: '' }
  } catch (error) {
    console.error('Failed to update schedule', error)
  } finally {
    isSaving.value = false
  }
}

async function saveAnnouncement() {
  if (!event.value || !announcementInput.value.message.trim()) return
  isSaving.value = true
  try {
    const updated = await manageEventAnnouncements(event.value.id, [{ title: announcementInput.value.title || 'Announcement', message: announcementInput.value.message }], true)
    event.value = normalizeEvent(updated)
    announcementInput.value = { title: '', message: '' }
  } catch (error) {
    console.error('Failed to publish announcement', error)
  } finally {
    isSaving.value = false
  }
}

async function markAllAttendance(status) {
  if (!event.value) return
  isSaving.value = true
  try {
    const payload = (event.value.registrations || []).map((entry) => ({ userId: entry.userId || entry.id, status }))
    const updated = await manageEventAttendance(event.value.id, payload, true)
    event.value = normalizeEvent(updated)
  } catch (error) {
    console.error('Failed to update attendance', error)
  } finally {
    isSaving.value = false
  }
}

async function toggleStudentAttendance(userId, status) {
  if (!event.value) return
  isSaving.value = true
  try {
    const updated = await manageEventAttendance(event.value.id, { userId, status })
    event.value = normalizeEvent(updated)
  } catch (error) {
    console.error('Failed to update student attendance', error)
  } finally {
    isSaving.value = false
  }
}

function exportAttendanceCSV() {
  if (!event.value) return
  const rows = [
    ['Event Name', event.value.name],
    ['Club', event.value.club],
    ['Date', event.value.startDate],
    [],
    ['Student Name', 'Register Number / User ID', 'Branch', 'Attendance Status']
  ]

  combinedAttendanceSheet.value.forEach(item => {
    rows.push([item.name, item.registerNumber, item.branch, item.attendanceStatus])
  })

  const csvContent = 'data:text/csv;charset=utf-8,' + rows.map(e => e.map(x => `"${x}"`).join(',')).join('\n')
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement('a')
  link.setAttribute('href', encodedUri)
  link.setAttribute('download', `${event.value.name.replace(/\s+/g, '_')}_Attendance_Sheet.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

async function handleVolunteerStatus(volunteerId, status) {
  if (!event.value) return
  isSaving.value = true
  try {
    await updateVolunteerStatus(event.value.id, volunteerId, status)
    const data = await getEvent(event.value.id)
    event.value = normalizeEvent(data)
  } catch (err) {
    console.error('Failed to update volunteer status', err)
  } finally {
    isSaving.value = false
  }
}

async function saveVenue() {
  if (!event.value || !selectedVenueId.value) return
  isSaving.value = true
  try {
    const updated = await assignVenue(event.value.id, Number(selectedVenueId.value))
    event.value = normalizeEvent(updated)
  } catch (error) {
    console.error('Failed to assign venue', error)
  } finally {
    isSaving.value = false
  }
}

const tabs = [
  { key: 'schedule', label: 'Schedule' },
  { key: 'rounds', label: 'Rounds' },
  { key: 'progress', label: 'Participant Progress' },
  { key: 'results', label: 'Results & Podium' },
  { key: 'announcements', label: 'Announcements' },
  { key: 'registrations', label: 'Registrations' },
  { key: 'volunteers', label: 'Event Volunteers' }
]

const visibleTabs = computed(() => {
  const isComp = event.value ? (event.value.isCompetition !== false) : true
  return tabs.filter(t => {
    if (!isComp && (t.key === 'rounds' || t.key === 'progress' || t.key === 'results')) {
      return false
    }
    if (t.key === 'volunteers') {
      return isAuthorizedFaculty.value
    }
    return true
  })
})

const isAttendanceAvailable = computed(() => {
  if (!event.value) return false
  const rawDate = event.value.startDate || event.value.start_date
  if (!rawDate) return true
  try {
    const start = new Date(rawDate)
    start.setHours(0, 0, 0, 0)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    return today >= start
  } catch (e) {
    return true
  }
})

function handleAttendanceClick() {
  if (!isAttendanceAvailable.value) {
    showToast(`Attendance will be available when the event begins on ${event.value?.startDate || event.value?.start_date || 'the event date'}.`, 'info')
    return
  }
  showAttendanceModal.value = true
}
</script>

<template>
  <FacultyLayout>
    <section class="event-details-page">
      <div class="container py-5" v-if="event">
        <div class="event-detail-card">
          <div class="detail-header">
            <div class="header-left">
              <div class="event-image">{{ event.emoji }}</div>
              <div>
                <span class="club-tag">{{ event.club }}</span>
                <h2>{{ event.name }}</h2>
              </div>
            </div>

            <div class="header-actions">
              <span class="status-badge" :class="(event.status || 'scheduled').toLowerCase()">{{ event.status }}</span>
              <button 
                v-if="isAuthorizedFaculty" 
                class="btn btn-sm btn-outline-primary rounded-pill px-3 fw-semibold"
                :class="{ 'opacity-50': !isAttendanceAvailable }"
                :title="!isAttendanceAvailable ? `Attendance will be available when the event begins on ${event.startDate || event.start_date || ''}` : 'Manage Attendance'"
                @click="handleAttendanceClick"
              >
                <i class="bi bi-calendar-check me-1"></i> Attendance
              </button>
            </div>
          </div>

          <div class="info-grid">
            <div class="info-box">
              <label>Start Date</label>
              <p>{{ event.startDate }}</p>
            </div>
            <div class="info-box">
              <label>End Date</label>
              <p>{{ event.endDate }}</p>
            </div>
          </div>

          <!-- Read-only Venue Display with Request Venue Button -->
          <div class="info-box mb-3">
            <div class="d-flex align-items-center justify-content-between">
              <div>
                <label>Venue</label>
                <p class="mb-0 fw-semibold text-dark">{{ event.venueName || event.venue || 'No venue assigned yet' }}</p>
                <small v-if="event.venueLocation" class="text-muted text-xs d-block">{{ event.venueLocation }}</small>
              </div>
              <button 
                v-if="isAuthorizedFaculty" 
                class="btn btn-sm btn-outline-primary rounded-3 px-3 text-xs fw-semibold"
                @click="showVenueRequestModal = true"
              >
                <i class="bi bi-geo-alt me-1"></i> {{ event.venueId ? 'Request / Change Venue' : 'Request Venue' }}
              </button>
            </div>
          </div>

          <div class="info-box description-box">
            <label>Description</label>
            <p>{{ event.description }}</p>
          </div>

          <!-- Tabs -->
          <div class="detail-tabs">
            <button v-for="tab in visibleTabs" :key="tab.key" class="tab-option" :class="{ active: activeTab === tab.key }" @click="activeTab = tab.key">
              {{ tab.label }}
            </button>
          </div>

          <div class="tab-content">
            
            <!-- Schedule -->
            <div v-if="activeTab === 'schedule'">
              <div class="mb-3">
                <label class="form-label text-sm fw-bold">Add schedule item</label>
                <div class="d-flex gap-2">
                  <input v-model="scheduleInput.time" class="form-control" placeholder="Time" />
                  <input v-model="scheduleInput.activity" class="form-control" placeholder="Activity" />
                  <button class="btn btn-primary rounded-pill px-4" @click="saveSchedule" :disabled="isSaving">Save</button>
                </div>
              </div>
              <div v-for="(item, index) in event.schedule" :key="index" class="schedule-row">
                <span class="time">{{ item.time }}</span>
                <span class="activity">{{ item.activity }}</span>
              </div>
              <p v-if="event.schedule.length === 0" class="empty-tab">No schedule added yet.</p>
            </div>

            <!-- Rounds -->
            <div v-else-if="activeTab === 'rounds'">
              <EventRoundsView :eventId="event.id" :canManage="isAuthorizedFaculty" />
            </div>

            <!-- Participant Progress -->
            <div v-else-if="activeTab === 'progress'">
              <ParticipantProgressView :eventId="event.id" />
            </div>

            <!-- Results & Podium -->
            <div v-else-if="activeTab === 'results'">
              <EventResultsView :eventId="event.id" :prizes="event.prizes" :canManage="isAuthorizedFaculty" @refresh="fetchEventDetails" />
            </div>

            <!-- Announcements -->
            <div v-else-if="activeTab === 'announcements'">
              <div class="mb-3">
                <label class="form-label text-sm fw-bold">Publish announcement</label>
                <input v-model="announcementInput.title" class="form-control mb-2" placeholder="Title" />
                <textarea v-model="announcementInput.message" class="form-control" rows="3" placeholder="Message"></textarea>
                <button class="btn btn-success mt-2 rounded-pill px-4" @click="saveAnnouncement" :disabled="isSaving">Publish</button>
              </div>
              <div v-for="(item, index) in event.announcements" :key="index" class="announcement-row">
                <h5>{{ item.title }}</h5>
                <p>{{ item.message }}</p>
              </div>
              <p v-if="event.announcements.length === 0" class="empty-tab">No announcements yet.</p>
            </div>

            <!-- Registrations -->
            <div v-else-if="activeTab === 'registrations'">
              <table class="table" v-if="event.registrations.length">
                <thead>
                  <tr><th>Name</th><th>Register Number</th><th>Branch</th></tr>
                </thead>
                <tbody>
                  <tr v-for="(student, index) in event.registrations" :key="index">
                    <td>{{ student.name }}</td>
                    <td>{{ student.registerNumber }}</td>
                    <td>{{ student.branch }}</td>
                  </tr>
                </tbody>
              </table>
              <p v-else class="empty-tab">No registrations yet.</p>
            </div>

            <!-- TAB 4: ATTENDANCE SHEET -->
            <div v-else-if="activeTab === 'attendance'">
              <EventAttendanceView :eventId="event.id" :canManageSessions="isAuthorizedFaculty" @back="activeTab = 'schedule'" />
            </div>

            <!-- Module 22: Event Volunteers -->
            <div v-else-if="activeTab === 'volunteers'">
              <EventVolunteersSection 
                :eventId="event.id" 
                :event="event" 
                userRole="FACULTY"
                :isFacultyCoordinator="isFacultyCoordinator"
                @refresh="loadEventData" 
              />
            </div>

          </div>
        </div>
      </div>

      <div class="container py-5" v-else>
        <div class="empty-state">
          <h3>Event not found.</h3>
          <p>The event you are looking for does not exist.</p>
        </div>
      </div>

      <UserProfileModal 
        :show="showProfileModal"
        :userId="selectedProfileUserId"
        @close="showProfileModal = false"
      />

      <EventAttendanceModal 
        :show="showAttendanceModal"
        :eventId="event ? event.id : 0"
        :canManage="isAuthorizedFaculty"
        @close="showAttendanceModal = false"
        @saved="fetchEventDetails"
      />

      <RequestVenueModal
        v-if="event"
        :show="showVenueRequestModal"
        :event="event"
        @close="showVenueRequestModal = false"
        @submitted="fetchEventDetails"
      />
    </section>
  </FacultyLayout>
</template>

<style scoped>
.event-details-page { width: 100%; max-width: 1500px; margin: 0 auto; }
.event-detail-card { background: white; border: 1px solid #e5e7eb; border-radius: 24px; padding: 28px; box-shadow: 0 18px 45px rgba(15, 23, 42, 0.06); }
.header-left { display: flex; align-items: center; gap: 18px; }
.event-image { width: 70px; height: 70px; border-radius: 50%; background: #eef4ff; display: flex; justify-content: center; align-items: center; font-size: 36px; flex-shrink: 0; }
.club-tag { display: inline-block; background: #eef4ff; color: #2563eb; padding: 5px 12px; border-radius: 999px; font-size: 12px; font-weight: 600; margin-bottom: 10px; }
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 28px; }
.detail-header h2 { color: #1f2937; font-size: 1.75rem; font-weight: 700; margin: 0; }
.header-actions { display: flex; gap: 10px; align-items: center; }
.status-badge { padding: 6px 14px; border-radius: 999px; font-size: 13px; font-weight: 600; white-space: nowrap; }
.status-badge.live, .status-badge.scheduled { background: #dcfce7; color: #16a34a; }
.status-badge.completed { background: #f1f5f9; color: #64748b; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
.info-box { background: #f8fafc; border: 1px solid #edf2f7; border-radius: 14px; padding: 16px 20px; }
.info-box label { display: block; color: #64748b; font-size: 13px; font-weight: 600; margin-bottom: 6px; }
.info-box p { margin: 0; color: #1f2937; font-weight: 500; }
.description-box { margin-bottom: 24px; }
.description-box p { line-height: 1.7; color: #374151; }
.toolbar { display: flex; gap: 12px; align-items: end; margin-bottom: 24px; }
.venue-box { flex: 1; }
.detail-tabs { display: flex; width: 100%; gap: 6px; background: #f8fafc; border: 1px solid #d1d5db; border-radius: 16px; padding: 6px; margin-bottom: 28px; flex-wrap: wrap; }
.tab-option { flex: 1; border: none; background: transparent; padding: 12px; border-radius: 10px; font-weight: 600; text-align: center; transition: 0.25s; min-width: 120px; }
.tab-option.active { background: #2563eb; color: white; }
.schedule-row { display: flex; gap: 20px; padding: 14px 0; border-bottom: 1px solid #f1f5f9; }
.schedule-row .time { color: #2563eb; font-weight: 600; min-width: 90px; }
.announcement-row { padding: 16px 0; border-bottom: 1px solid #f1f5f9; }
.announcement-row h5 { color: #1f2937; font-weight: 600; margin: 0; }
.announcement-row p { color: #6b7280; margin: 8px 0 0; }
.table { width: 100%; }
.table th { color: #64748b; font-size: 13px; font-weight: 600; border-bottom: 2px solid #edf2f7; padding: 10px 12px; }
.table td { padding: 12px; border-bottom: 1px solid #f1f5f9; color: #374151; }
.attendance-badge { padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 600; }
.attendance-badge.present { background: #dcfce7; color: #16a34a; }
.attendance-badge.absent { background: #fee2e2; color: #dc2626; }
.empty-tab { color: #94a3b8; text-align: center; padding: 40px 0; }
.empty-state { text-align: center; padding: 70px 20px; color: #6b7280; }
.empty-state h3 { color: #1f2937; margin-bottom: 10px; }
@media (max-width: 576px) { .toolbar { flex-direction: column; align-items: stretch; } .info-grid { grid-template-columns: 1fr; } .detail-header { flex-direction: column; gap: 16px; } }
</style>