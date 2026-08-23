<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AdminLayout from '@/layouts/AdminLayout.vue'
import LoadingState from '@/components/common/LoadingState.vue'
import UserProfileModal from '@/components/common/UserProfileModal.vue'
import EventAttendanceView from '@/components/events/EventAttendanceView.vue'
import EventAttendanceModal from '@/components/events/EventAttendanceModal.vue'
import EventRoundsView from '@/components/events/EventRoundsView.vue'
import ParticipantProgressView from '@/components/events/ParticipantProgressView.vue'
import EventResultsView from '@/components/events/EventResultsView.vue'
import RequestVenueModal from '@/components/events/RequestVenueModal.vue'

const showProfileModal = ref(false)
const selectedProfileUserId = ref(null)
const showVenueRequestModal = ref(false)

function openUserProfile(id) {
  if (!id) return
  selectedProfileUserId.value = id
  showProfileModal.value = true
}
import {
  getEvent,
  updateEvent,
  updateEventStatus,
  manageEventSchedule,
  manageEventAnnouncements,
  manageEventAttendance,
  assignVenue,
  downloadEventReport
} from '@/api/events'
import { getEventStatus } from '@/utils/eventUtils'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const router = useRouter()
const { showToast } = useToast()
const activeTab = ref('schedule')
const showAttendanceModal = ref(false)
const event = ref(null)
const loading = ref(false)
const isDownloadingReport = ref(false)

const computedEventStatus = computed(() => {
  return getEventStatus(event.value)
})

const isCompletedOrClosed = computed(() => {
  if (!event.value) return false
  const s = String(event.value.rawStatus || event.value.status || '').toUpperCase()
  return s === 'COMPLETED' || s === 'CLOSED' || computedEventStatus.value === 'Completed'
})

async function toggleCloseEvent() {
  if (!event.value) return
  const isClosed = isCompletedOrClosed.value
  const targetStatus = isClosed ? 'SCHEDULED' : 'COMPLETED'
  const actionText = isClosed ? 'reopen' : 'close'

  if (!confirm(`Are you sure you want to ${actionText} "${event.value.name || 'this event'}"?`)) {
    return
  }

  try {
    loading.value = true
    const updatedEvent = await updateEventStatus(event.value.id, targetStatus)
    event.value = {
      ...updatedEvent,
      club: updatedEvent.clubName || updatedEvent.club || 'Unknown Club'
    }
    showEditEventModal.value = false
    alert(`Event ${isClosed ? 'reopened' : 'closed'} successfully!`)
  } catch (error) {
    console.error(error)
    alert(`Failed to ${actionText} event.`)
  } finally {
    loading.value = false
  }
}

async function fetchEventDetails() {
  try {
    loading.value = true
    const data = await getEvent(Number(route.params.id))
    event.value = {
      ...data,
      club: data.clubName || data.club || 'Unknown Club'
    }
  } catch (error) {
    console.error('Failed to load event', error)
  } finally {
    loading.value = false
  }
}

// Alias for template compatibility
const loadEvent = fetchEventDetails
const loadEventData = fetchEventDetails

onMounted(fetchEventDetails)

const tabs = [
  { key: 'schedule', label: 'Schedule' },
  { key: 'rounds', label: 'Rounds' },
  { key: 'progress', label: 'Participant Progress' },
  { key: 'results', label: 'Results & Podium' },
  { key: 'announcements', label: 'Announcements' },
  { key: 'registrations', label: 'Registrations' }
]

const visibleTabs = computed(() => {
  const isComp = event.value ? (event.value.isCompetition !== false) : true
  return tabs.filter(t => {
    if (!isComp && (t.key === 'rounds' || t.key === 'progress' || t.key === 'results')) {
      return false
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

async function handleDownloadReport() {
  if (!event.value || isDownloadingReport.value) return
  isDownloadingReport.value = true
  try {
    await downloadEventReport(event.value.id, event.value.name)
    showToast('Report downloaded.', 'success')
  } catch (error) {
    console.error('Failed to download report', error)
    showToast('Failed to download report.', 'error')
  } finally {
    isDownloadingReport.value = false
  }
}

// Modal & Form States for Event Details page
const showAddScheduleModal = ref(false)
const newScheduleTime = ref('')
const newScheduleActivity = ref('')

const showAddAnnouncementModal = ref(false)
const showEditEventModal = ref(false)

const editEventForm = ref({
  name: '',
  description: '',
  startDate: '',
  endDate: ''
})
const newAnnouncementTitle = ref('')
const newAnnouncementMessage = ref('')

async function saveEventChanges() {
  if (!event.value) return

  try {
    loading.value = true

    const updatedEvent = await updateEvent(event.value.id, {
      name: editEventForm.value.name,
      description: editEventForm.value.description,
      startDate: editEventForm.value.startDate,
      endDate: editEventForm.value.endDate
    })

    event.value = {
      ...updatedEvent,
      club: updatedEvent.clubName || updatedEvent.club || 'Unknown Club'
    }

    showEditEventModal.value = false

    alert('Event updated successfully!')
  } catch (error) {
    console.error(error)
    alert('Failed to update event.')
  } finally {
    loading.value = false
  }
}

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/events')
  }
}

async function submitNewSchedule() {
  if (!newScheduleActivity.value.trim() || !event.value) return

  try {
    loading.value = true

    const updatedEvent = await manageEventSchedule(event.value.id, {
      time: newScheduleTime.value,
      activity: newScheduleActivity.value
    })

    event.value = {
      ...updatedEvent,
      club: updatedEvent.clubName || updatedEvent.club || 'Unknown Club'
    }

    showAddScheduleModal.value = false
    newScheduleTime.value = ''
    newScheduleActivity.value = ''

    alert('Schedule added successfully!')
  } catch (error) {
    console.error(error)
    alert('Failed to add schedule.')
  } finally {
    loading.value = false
  }
}

async function submitNewAnnouncement() {
  if (!newAnnouncementTitle.value.trim() || !event.value) return

  try {
    loading.value = true

    const updatedEvent = await manageEventAnnouncements(event.value.id, {
      title: newAnnouncementTitle.value,
      message: newAnnouncementMessage.value
    })

    event.value = {
      ...updatedEvent,
      club: updatedEvent.clubName || updatedEvent.club || 'Unknown Club'
    }

    showAddAnnouncementModal.value = false
    newAnnouncementTitle.value = ''
    newAnnouncementMessage.value = ''

    alert('Announcement broadcasted successfully!')
  } catch (error) {
    console.error(error)
    alert('Failed to create announcement.')
  } finally {
    loading.value = false
  }
}

async function postAttendance() {
  if (!event.value || !event.value.attendance) return

  try {
    loading.value = true

    const updatedEvent = await manageEventAttendance(
      event.value.id,
      event.value.attendance,
      true
    )

    event.value = {
      ...updatedEvent,
      club: updatedEvent.clubName || updatedEvent.club || 'Unknown Club'
    }

    alert('Attendance updated successfully!')
  } catch (error) {
    console.error(error)
    alert('Failed to update attendance.')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AdminLayout>
    <section class="event-details-page">
      <div v-if="loading" class="container py-5">
        <LoadingState label="Loading event details..." />
      </div>
      <div class="container py-5" v-else-if="event">
        <!-- Back Navigation Button -->
        <button class="back-btn mb-4" @click="goBack">← Back</button>

        <div class="event-detail-card">
          <div class="detail-header">
            <div class="header-left">
              <div class="event-image">
                {{ event.emoji || '🎉' }}
              </div>

              <div>
                <span class="club-tag">{{ event.club }}</span>
                <h2>{{ event.name || event.title }}</h2>
              </div>
            </div>

            <div class="d-flex align-items-center gap-2">
              <button
                class="btn btn-outline-secondary btn-sm rounded-pill px-3 fw-semibold"
                :disabled="isDownloadingReport"
                @click="handleDownloadReport"
              >
                <i class="bi bi-file-earmark-arrow-down me-1"></i>
                {{ isDownloadingReport ? 'Preparing...' : 'Download Report' }}
              </button>
              <button 
                class="btn btn-outline-primary btn-sm rounded-pill px-3 fw-semibold" 
                :class="{ 'opacity-50': !isAttendanceAvailable }"
                :title="!isAttendanceAvailable ? `Attendance will be available when the event begins on ${event.startDate || event.start_date || ''}` : 'Manage Attendance'"
                @click="handleAttendanceClick"
              >
                <i class="bi bi-calendar-check me-1"></i> Attendance
              </button>

              <button
                class="btn btn-warning btn-sm"
                @click="
                editEventForm.name = event.name;
                editEventForm.description = event.description;
                editEventForm.startDate = event.startDate;
                editEventForm.endDate = event.endDate;
                showEditEventModal = true;
                "
              >
                ✏️ Edit
              </button>

              <span
                class="status-badge"
                :class="computedEventStatus.toLowerCase()"
              >
                {{ computedEventStatus }}
              </span>
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

          <!-- Navigation Tabs -->
          <div class="detail-tabs">
            <button
              v-for="tab in visibleTabs"
              :key="tab.key"
              class="tab-option"
              :class="{ active: activeTab === tab.key }"
              @click="activeTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>

          <!-- Tab Content Area -->
          <div class="tab-content">
            <!-- 1. Schedule Tab -->
            <div v-if="activeTab === 'schedule'">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="fw-bold m-0 text-dark">Event Agenda & Schedule</h5>
                <button class="btn btn-sm btn-outline-primary" @click="showAddScheduleModal = true">
                  + Add Agenda
                </button>
              </div>

              <div v-if="!event.schedule || event.schedule.length === 0" class="empty-tab">
                No schedule added yet.
              </div>
              <div v-else>
                <div v-for="(item, index) in event.schedule" :key="index" class="schedule-row">
                  <span class="time">{{ item.time }}</span>
                  <span class="activity">{{ item.activity }}</span>
                </div>
              </div>
            </div>

            <!-- 1B. Rounds Tab -->
            <div v-else-if="activeTab === 'rounds'">
              <EventRoundsView :eventId="event.id" :canManage="true" />
            </div>

            <!-- 1C. Participant Progress Tab -->
            <div v-else-if="activeTab === 'progress'">
              <ParticipantProgressView :eventId="event.id" />
            </div>

            <!-- 1D. Results Tab -->
            <div v-else-if="activeTab === 'results'">
              <EventResultsView :eventId="event.id" :prizes="event.prizes" :canManage="true" @refresh="fetchEventDetails" />
            </div>

            <!-- 2. Announcements Tab -->
            <div v-else-if="activeTab === 'announcements'">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="fw-bold m-0 text-dark">Broadcast Announcements</h5>
                <button class="btn btn-sm btn-success" @click="showAddAnnouncementModal = true">
                  + Trigger Announcement
                </button>
              </div>

              <div v-if="!event.announcements || event.announcements.length === 0" class="empty-tab">
                No announcements yet.
              </div>
              <div v-else>
                <div v-for="(item, index) in event.announcements" :key="index" class="announcement-row">
                  <div class="d-flex justify-content-between align-items-start">
                    <h5>{{ item.title }}</h5>
                    <small class="text-secondary">{{ item.date }}</small>
                  </div>
                  <p>{{ item.message }}</p>
                </div>
              </div>
            </div>

            <!-- 3. Registrations Tab -->
            <div v-else-if="activeTab === 'registrations'">
              <h5 class="fw-bold mb-3 text-dark">Registered Participants</h5>
              <table class="table align-middle" v-if="event.registrations && event.registrations.length">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Register Number</th>
                    <th>Branch</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(student, index) in event.registrations" :key="index">
                    <td class="fw-semibold">
                      {{ student.userName || student.name }}
                    </td>

                    <td>
                      {{ student.registerNumber || '-' }}
                    </td>

                    <td>
                      {{ student.branch || student.status }}
                    </td>  
                  </tr>
                </tbody>
              </table>
              <div v-else class="empty-tab">No registrations yet.</div>
            </div>

            <!-- 4. Attendance Tab -->
            <div v-else-if="activeTab === 'attendance'">
              <EventAttendanceView :eventId="event.id" :canManageSessions="true" @back="activeTab = 'schedule'" />
            </div>
          </div>
        </div>
      </div>

      <div class="container py-5" v-else>
        <div class="empty-state">
          <h3>Event not found.</h3>
          <p>The event you are looking for does not exist.</p>
          <button class="btn btn-primary mt-3" @click="goBack">Go Back</button>
        </div>
      </div>

      <!-- Add Agenda Modal -->
      <div v-if="showAddScheduleModal" class="modal-backdrop" @click.self="showAddScheduleModal = false">
        <div class="modal-dialog-custom">
          <h5 class="fw-bold mb-3">+ Create Schedule Item</h5>
          <div class="mb-3">
            <label class="form-label">Time</label>
            <input v-model="newScheduleTime" type="text" class="form-control" placeholder="e.g. 10:00 AM" />
          </div>
          <div class="mb-3">
            <label class="form-label">Activity</label>
            <input v-model="newScheduleActivity" type="text" class="form-control" placeholder="e.g. Opening Keynote" />
          </div>
          <div class="d-flex justify-content-end gap-2">
            <button class="btn btn-secondary" @click="showAddScheduleModal = false">Cancel</button>
            <button class="btn btn-primary" @click="submitNewSchedule">Add Agenda</button>
          </div>
        </div>
      </div>

      <!-- Add Announcement Modal -->
      <div v-if="showAddAnnouncementModal" class="modal-backdrop" @click.self="showAddAnnouncementModal = false">
        <div class="modal-dialog-custom">
          <h5 class="fw-bold mb-3">+ Trigger Announcement</h5>
          <div class="mb-3">
            <label class="form-label">Title</label>
            <input v-model="newAnnouncementTitle" type="text" class="form-control" />
          </div>
          <div class="mb-3">
            <label class="form-label">Message</label>
            <textarea v-model="newAnnouncementMessage" class="form-control" rows="3"></textarea>
          </div>
          <div class="d-flex justify-content-end gap-2">
            <button class="btn btn-secondary" @click="showAddAnnouncementModal = false">Cancel</button>
            <button class="btn btn-success" @click="submitNewAnnouncement">+ Broadcast</button>
          </div>
        </div>
      </div>
      <!-- Edit Event Modal -->
      <div
        v-if="showEditEventModal"
        class="modal-backdrop"
        @click.self="showEditEventModal = false"
      >
        <div class="modal-dialog-custom">
          <h5 class="fw-bold mb-3">Edit Event</h5>

          <div class="mb-3">
            <label class="form-label">Event Name</label>
            <input
              v-model="editEventForm.name"
              class="form-control"
              type="text"
            />
          </div>

          <div class="mb-3">
            <label class="form-label">Description</label>
            <textarea
              v-model="editEventForm.description"
              class="form-control"
              rows="3"
            ></textarea>
          </div>

          <div class="row">
            <div class="col">
              <label class="form-label">Start Date</label>
              <input
                v-model="editEventForm.startDate"
                class="form-control"
                type="text"
              />
            </div>

            <div class="col">
              <label class="form-label">End Date</label>
              <input
                v-model="editEventForm.endDate"
                class="form-control"
                type="text"
              />
            </div>
          </div>

          <div class="d-flex justify-content-between align-items-center mt-4">
            <div>
              <button
                v-if="isCompletedOrClosed"
                type="button"
                class="btn btn-outline-success font-semibold"
                @click="toggleCloseEvent"
              >
                🔓 Reopen Event
              </button>
              <button
                v-else
                type="button"
                class="btn btn-outline-danger font-semibold"
                @click="toggleCloseEvent"
              >
                🔒 Close Event
              </button>
            </div>

            <div class="d-flex gap-2">
              <button
                class="btn btn-secondary"
                @click="showEditEventModal = false"
              >
                Cancel
              </button>

              <button
                class="btn btn-primary"
                @click="saveEventChanges"
              >
                Save Changes
              </button>
            </div>
          </div>
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
        :canManage="true"
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
  </AdminLayout>
</template>

<style scoped>
.event-details-page {
  width: 100%;
  max-width: 1500px;
  margin: 0 auto;
}

.back-btn {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  padding: 8px 18px;
  border-radius: 10px;
  color: #334155;
  font-weight: 600;
  transition: 0.2s;
  cursor: pointer;
}

.back-btn:hover {
  background: #e2e8f0;
}

.event-detail-card {
  background: #fff;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.06);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 18px;
}

.event-image {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: #eef4ff;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 36px;
  flex-shrink: 0;
}

.club-tag {
  display: inline-block;
  background: #eef4ff;
  color: #2563eb;
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 10px;
}

.detail-header h2 {
  color: #1f2937;
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0;
}

.status-badge {
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
}

.status-badge.live,
.status-badge.active {
  background: #dcfce7;
  color: #16a34a;
}

.status-badge.completed {
  background: #f1f5f9;
  color: #64748b;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.info-box {
  background: #f8fafc;
  border: 1px solid #edf2f7;
  border-radius: 14px;
  padding: 16px 20px;
}

.info-box label {
  display: block;
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 6px;
}

.info-box p {
  margin: 0;
  color: #1f2937;
  font-weight: 500;
}

.description-box {
  margin-bottom: 28px;
}

.detail-tabs {
  display: flex;
  width: 100%;
  gap: 6px;
  background: #f8fafc;
  border: 1px solid #d1d5db;
  border-radius: 16px;
  padding: 6px;
  margin-bottom: 28px;
}

.tab-option {
  flex: 1;
  border: none;
  background: transparent;
  padding: 12px;
  border-radius: 10px;
  font-weight: 600;
  text-align: center;
  transition: 0.25s;
  cursor: pointer;
}

.tab-option:hover {
  background: #eef4ff;
}

.tab-option.active {
  background: #2563eb;
  color: white;
}

.tab-content {
  min-height: 180px;
}

.schedule-row {
  display: flex;
  gap: 20px;
  padding: 14px 0;
  border-bottom: 1px solid #f1f5f9;
}

.schedule-row .time {
  color: #2563eb;
  font-weight: 600;
  min-width: 90px;
}

.announcement-row {
  padding: 16px 0;
  border-bottom: 1px solid #f1f5f9;
}

.attendance-badge {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.attendance-badge.present {
  background: #dcfce7;
  color: #16a34a;
}

.attendance-badge.absent {
  background: #fee2e2;
  color: #dc2626;
}

.empty-tab {
  color: #94a3b8;
  text-align: center;
  padding: 40px 0;
}

.empty-state {
  text-align: center;
  padding: 70px 20px;
  color: #6b7280;
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
