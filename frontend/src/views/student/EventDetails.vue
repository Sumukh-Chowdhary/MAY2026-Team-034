<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

import StudentLayout from '@/layouts/StudentLayout.vue'
import {
  getEvent,
  registerForEvent,
  createEventTicket,
  manageEventSchedule,
  manageEventAnnouncements,
  manageEventAttendance,
  manageEventPrizes,
  manageEventVolunteers
} from '@/api/events'
import { eventSocketService } from '@/services/eventService'

const route = useRoute()
const activeTab = ref('schedule')
const event = ref(null)
const loading = ref(false)
const isRegistering = ref(false)
const isRegistered = ref(false)
const currentUserId = ref(null)

// Ticket modal state
const showTicketModal = ref(false)
const ticketTargetRole = ref('ORGANIZER') // 'ORGANIZER' | 'COORDINATOR'
const ticketTitle = ref('')
const ticketDescription = ref('')
const ticketPriority = ref('MEDIUM')
const isSubmittingTicket = ref(false)
const ticketFeedback = ref('')

// Volunteer state (Module 22)
const isApplyingVolunteer = ref(false)
const volunteerFeedback = ref('')

// Volunteer management portal inputs
const isSaving = ref(false)
const scheduleInput = ref({ time: '10:00', activity: '' })
const announcementInput = ref({ title: '', message: '' })
const prizeInput = ref({ title: '', winnerName: '', description: '' })
const attendanceInputs = ref({})

const normalizeEvent = (data) => ({
  ...data,
  emoji: data.emoji || '🎉',
  status: String(data.status || 'SCHEDULED'),
  club: data.clubName || data.club || 'Unknown Club',
  name: data.name || data.eventName || data.event_name || 'Untitled Event',
  description: data.description || data.eventDescription || data.event_description || 'No description available.',
  schedule: Array.isArray(data.schedule) ? data.schedule.map((item) => ({ time: item.time || item.scheduleTime || '', activity: item.activity || item.title || '' })) : [],
  announcements: Array.isArray(data.announcements) ? data.announcements : [],
  prizes: Array.isArray(data.prizes) ? data.prizes : [],
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

const myVolunteerRecord = computed(() => {
  if (!event.value || !event.value.volunteers || !currentUserId.value) return null
  return event.value.volunteers.find(v => v.userId === currentUserId.value)
})

const isApprovedVolunteer = computed(() => {
  return myVolunteerRecord.value && myVolunteerRecord.value.status === 'APPROVED'
})

onMounted(async () => {
  loading.value = true
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      currentUserId.value = user.id
    }

    const data = await getEvent(Number(route.params.id))
    event.value = normalizeEvent(data)

    if (currentUserId.value && event.value.registrations) {
      isRegistered.value = event.value.registrations.some(r => r.userId === currentUserId.value || r.name === 'You')
    }

    // Socket real-time updates
    eventSocketService.initSocket()
    eventSocketService.joinEventRoom(Number(route.params.id))

    eventSocketService.on('event_schedule_updated', (payload) => {
      if (payload.eventId === Number(route.params.id) && event.value) {
        event.value.schedule = payload.schedule
      }
    })

    eventSocketService.on('event_announcement_created', (payload) => {
      if (payload.eventId === Number(route.params.id) && event.value) {
        event.value.announcements = payload.announcements
      }
    })

    eventSocketService.on('event_attendance_updated', (payload) => {
      if (payload.eventId === Number(route.params.id) && event.value) {
        event.value.attendance = payload.attendance
      }
    })

    eventSocketService.on('event_prize_updated', (payload) => {
      if (payload.eventId === Number(route.params.id) && event.value) {
        event.value.prizes = payload.prizes
      }
    })

  } catch (error) {
    console.error('Failed to load event', error)
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (route.params.id) {
    eventSocketService.leaveEventRoom(Number(route.params.id))
  }
})

async function handleRegister() {
  if (isRegistering.value || isRegistered.value) return
  isRegistering.value = true
  try {
    const response = await registerForEvent(Number(route.params.id))
    isRegistered.value = true
    event.value.registrations.unshift({
      id: response.id,
      userId: currentUserId.value,
      name: 'You',
      registerNumber: 'You',
      branch: 'Your Branch',
      status: response.status || 'REGISTERED'
    })
  } catch (error) {
    console.error('Failed to register for event', error)
  } finally {
    isRegistering.value = false
  }
}

async function applyVolunteer() {
  if (isApplyingVolunteer.value || myVolunteerRecord.value) return
  isApplyingVolunteer.value = true
  volunteerFeedback.value = ''
  try {
    const res = await manageEventVolunteers(event.value.id, { userId: currentUserId.value })
    volunteerFeedback.value = 'Application submitted! Awaiting approval from organizer/faculty.'
    event.value.volunteers.push({
      userId: currentUserId.value,
      status: 'PENDING'
    })
  } catch (err) {
    volunteerFeedback.value = 'Failed to submit volunteer application.'
  } finally {
    isApplyingVolunteer.value = false
  }
}

async function submitTicketToTarget() {
  if (!ticketTitle.value.trim()) return
  isSubmittingTicket.value = true
  ticketFeedback.value = ''
  try {
    await createEventTicket(event.value.id, {
      title: ticketTitle.value,
      description: ticketDescription.value,
      targetRole: ticketTargetRole.value,
      priority: ticketPriority.value
    })
    ticketFeedback.value = `Ticket successfully raised to ${ticketTargetRole.value.title()}!`
    setTimeout(() => {
      showTicketModal.value = false
      ticketTitle.value = ''
      ticketDescription.value = ''
      ticketFeedback.value = ''
    }, 1500)
  } catch (err) {
    ticketFeedback.value = 'Failed to raise ticket.'
  } finally {
    isSubmittingTicket.value = false
  }
}

// Volunteer Action Handlers (Module 22)
async function addScheduleItem() {
  if (!scheduleInput.value.activity.trim() || !event.value) return
  isSaving.value = true
  try {
    const updated = await manageEventSchedule(event.value.id, { time: scheduleInput.value.time, activity: scheduleInput.value.activity })
    event.value = normalizeEvent(updated)
    scheduleInput.value = { time: '10:00', activity: '' }
  } catch (err) {
    console.error(err)
  } finally {
    isSaving.value = false
  }
}

async function publishAnnouncement() {
  if (!announcementInput.value.message.trim() || !event.value) return
  isSaving.value = true
  try {
    const updated = await manageEventAnnouncements(event.value.id, { title: announcementInput.value.title || 'Announcement', message: announcementInput.value.message })
    event.value = normalizeEvent(updated)
    announcementInput.value = { title: '', message: '' }
  } catch (err) {
    console.error(err)
  } finally {
    isSaving.value = false
  }
}

async function addPrize() {
  if (!prizeInput.value.title.trim() || !event.value) return
  isSaving.value = true
  try {
    const updated = await manageEventPrizes(event.value.id, { title: prizeInput.value.title, winnerName: prizeInput.value.winnerName, description: prizeInput.value.description })
    event.value = normalizeEvent(updated)
    prizeInput.value = { title: '', winnerName: '', description: '' }
  } catch (err) {
    console.error(err)
  } finally {
    isSaving.value = false
  }
}

async function toggleStudentAttendance(studentUserId, newStatus) {
  if (!event.value) return
  isSaving.value = true
  try {
    const updated = await manageEventAttendance(event.value.id, { userId: studentUserId, status: newStatus })
    event.value = normalizeEvent(updated)
  } catch (err) {
    console.error(err)
  } finally {
    isSaving.value = false
  }
}

const tabs = [
  { key: 'schedule', label: 'Schedule' },
  { key: 'announcements', label: 'Announcements' },
  { key: 'registrations', label: 'Registrations' },
  { key: 'attendance', label: 'Attendance' },
  { key: 'prizes', label: 'Prizes & Winners' }
]
</script>

<template>
  <StudentLayout>
    <section class="event-details-page">
      <div class="container py-5" v-if="event">
        
        <!-- Module 22 Volunteer Banner -->
        <div v-if="isApprovedVolunteer" class="volunteer-banner shadow-sm mb-4">
          <div class="d-flex align-items-center gap-3">
            <div class="banner-icon"><i class="bi bi-shield-check display-6 text-warning"></i></div>
            <div>
              <h5 class="fw-bold text-dark mb-1">⭐ Approved Event Volunteer Access</h5>
              <p class="text-secondary text-sm mb-0">You are an active volunteer for <strong>{{ event.name }}</strong>. You have permissions to manage Schedule, Announcements, Attendance, and Prizes for this event.</p>
            </div>
          </div>
        </div>

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
              
              <button class="register-btn" :disabled="isRegistered || isRegistering" @click="handleRegister">
                {{ isRegistering ? 'Registering…' : isRegistered ? 'Registered ✓' : 'Register' }}
              </button>

              <!-- Sprint 2: Raise Ticket to Organizer or Coordinator -->
              <button class="btn btn-outline-primary rounded-pill px-3 fw-semibold text-xs" @click="showTicketModal = true">
                <i class="bi bi-ticket-perforated me-1"></i> Raise Ticket
              </button>

              <!-- Module 22: Apply Volunteer -->
              <button 
                v-if="!myVolunteerRecord && event.status !== 'COMPLETED'" 
                class="btn btn-warning rounded-pill px-3 fw-semibold text-xs"
                :disabled="isApplyingVolunteer"
                @click="applyVolunteer"
              >
                <i class="bi bi-star me-1"></i> {{ isApplyingVolunteer ? 'Applying...' : 'Apply as Volunteer' }}
              </button>
              
              <span v-else-if="myVolunteerRecord" class="badge bg-info text-dark rounded-pill px-3">
                Volunteer: {{ myVolunteerRecord.status }}
              </span>
            </div>
          </div>

          <div v-if="volunteerFeedback" class="alert alert-info py-2 text-xs mb-3">{{ volunteerFeedback }}</div>

          <div class="info-grid">
            <div class="info-box">
              <label>Start Date</label>
              <p>{{ event.startDate }} <span v-if="event.startTime">({{ event.startTime }})</span></p>
            </div>
            <div class="info-box">
              <label>End Date</label>
              <p>{{ event.endDate }} <span v-if="event.endTime">({{ event.endTime }})</span></p>
            </div>
          </div>

          <div class="info-box description-box">
            <label>Description</label>
            <p>{{ event.description }}</p>
          </div>

          <!-- Tabs -->
          <div class="detail-tabs">
            <button v-for="tab in tabs" :key="tab.key" class="tab-option" :class="{ active: activeTab === tab.key }" @click="activeTab = tab.key">
              {{ tab.label }}
            </button>
          </div>

          <!-- Tab Content -->
          <div class="tab-content">
            
            <!-- Schedule Tab -->
            <div v-if="activeTab === 'schedule'">
              <!-- Volunteer Add Schedule Control -->
              <div v-if="isApprovedVolunteer" class="volunteer-input-card mb-4 p-3 bg-light rounded-3 border">
                <h6 class="fw-bold text-primary mb-2"><i class="bi bi-plus-circle me-1"></i> Volunteer Action: Add Schedule Activity</h6>
                <div class="row g-2">
                  <div class="col-md-3">
                    <input v-model="scheduleInput.time" class="form-control form-control-sm" placeholder="Time (e.g. 10:30 AM)" />
                  </div>
                  <div class="col-md-7">
                    <input v-model="scheduleInput.activity" class="form-control form-control-sm" placeholder="Activity details..." />
                  </div>
                  <div class="col-md-2">
                    <button class="btn btn-sm btn-primary w-100 fw-bold" :disabled="isSaving" @click="addScheduleItem">Add</button>
                  </div>
                </div>
              </div>

              <div v-for="(item, index) in event.schedule" :key="index" class="schedule-row">
                <span class="time">{{ item.time }}</span>
                <span class="activity">{{ item.activity }}</span>
              </div>
              <p v-if="event.schedule.length === 0" class="empty-tab">No schedule added yet.</p>
            </div>

            <!-- Announcements Tab -->
            <div v-else-if="activeTab === 'announcements'">
              <!-- Volunteer Add Announcement Control -->
              <div v-if="isApprovedVolunteer" class="volunteer-input-card mb-4 p-3 bg-light rounded-3 border">
                <h6 class="fw-bold text-success mb-2"><i class="bi bi-megaphone me-1"></i> Volunteer Action: Publish Announcement</h6>
                <input v-model="announcementInput.title" class="form-control form-control-sm mb-2" placeholder="Title (e.g. Venue Change Alert)" />
                <textarea v-model="announcementInput.message" class="form-control form-control-sm mb-2" rows="2" placeholder="Message content..."></textarea>
                <button class="btn btn-sm btn-success fw-bold px-4" :disabled="isSaving" @click="publishAnnouncement">Publish Announcement</button>
              </div>

              <div v-for="(item, index) in event.announcements" :key="index" class="announcement-row">
                <div class="d-flex justify-content-between align-items-start">
                  <h5>{{ item.title }}</h5>
                  <small class="text-secondary">{{ item.date }}</small>
                </div>
                <p>{{ item.message }}</p>
              </div>
              <p v-if="event.announcements.length === 0" class="empty-tab">No announcements yet.</p>
            </div>

            <!-- Registrations Tab -->
            <div v-else-if="activeTab === 'registrations'">
              <table class="table" v-if="event.registrations.length">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Register Number</th>
                    <th>Branch</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(student, index) in event.registrations" :key="index">
                    <td>{{ student.name }}</td>
                    <td>{{ student.registerNumber }}</td>
                    <td>{{ student.branch }}</td>
                    <td><span class="badge bg-success-subtle text-success">{{ student.status }}</span></td>
                  </tr>
                </tbody>
              </table>
              <p v-else class="empty-tab">No registrations yet.</p>
            </div>

            <!-- Attendance Tab -->
            <div v-else-if="activeTab === 'attendance'">
              <table class="table" v-if="event.registrations.length || event.attendance.length">
                <thead>
                  <tr>
                    <th>Student Name</th>
                    <th>Register Number</th>
                    <th>Attendance Status</th>
                    <th v-if="isApprovedVolunteer">Volunteer Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(student, index) in (event.attendance.length ? event.attendance : event.registrations)" :key="index">
                    <td>{{ student.name }}</td>
                    <td>{{ student.registerNumber }}</td>
                    <td>
                      <span class="attendance-badge" :class="(student.status || 'PRESENT').toLowerCase()">
                        {{ student.status || 'PRESENT' }}
                      </span>
                    </td>
                    <td v-if="isApprovedVolunteer">
                      <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-success btn-xs" @click="toggleStudentAttendance(student.userId || student.id, 'PRESENT')">Mark Present</button>
                        <button class="btn btn-outline-danger btn-xs" @click="toggleStudentAttendance(student.userId || student.id, 'ABSENT')">Mark Absent</button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
              <p v-else class="empty-tab">Attendance has not been recorded yet.</p>
            </div>

            <!-- Prizes Tab -->
            <div v-else-if="activeTab === 'prizes'">
              <!-- Volunteer Add Prize Control -->
              <div v-if="isApprovedVolunteer" class="volunteer-input-card mb-4 p-3 bg-light rounded-3 border">
                <h6 class="fw-bold text-warning mb-2"><i class="bi bi-trophy me-1"></i> Volunteer Action: Add Prize / Winner</h6>
                <div class="row g-2 mb-2">
                  <div class="col-md-5">
                    <input v-model="prizeInput.title" class="form-control form-control-sm" placeholder="Prize Title (e.g. First Prize)" />
                  </div>
                  <div class="col-md-7">
                    <input v-model="prizeInput.winnerName" class="form-control form-control-sm" placeholder="Winner Name (e.g. Alex Johnson)" />
                  </div>
                </div>
                <input v-model="prizeInput.description" class="form-control form-control-sm mb-2" placeholder="Prize details / Certificate description" />
                <button class="btn btn-sm btn-warning fw-bold px-4" :disabled="isSaving" @click="addPrize">Save Winner</button>
              </div>

              <div v-for="(prize, index) in event.prizes" :key="index" class="prize-card p-3 mb-2 bg-light rounded border">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="fw-bold text-dark mb-1">🏆 {{ prize.title }}</h6>
                    <p class="text-sm text-primary fw-semibold mb-0" v-if="prize.winnerName">Winner: {{ prize.winnerName }}</p>
                    <small class="text-muted" v-if="prize.description">{{ prize.description }}</small>
                  </div>
                </div>
              </div>

              <p v-if="!event.prizes || event.prizes.length === 0" class="empty-tab">No prizes or winners announced yet.</p>
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
    </section>

    <!-- Sprint 2: Raise Ticket Modal to Organizer or Coordinator -->
    <Teleport to="body">
      <div v-if="showTicketModal" class="modal-backdrop-glass" @click.self="showTicketModal = false">
        <div class="modal-box shadow-2xl">
          <div class="modal-header-custom">
            <h5 class="fw-bold mb-0">Raise Ticket for {{ event?.name }}</h5>
            <button class="btn-close-custom" @click="showTicketModal = false"><i class="bi bi-x-lg"></i></button>
          </div>

          <div class="modal-body-custom">
            <div class="mb-3">
              <label class="form-label text-sm fw-bold">Select Target Recipient</label>
              <div class="d-flex gap-3">
                <div class="form-check flex-fill p-3 border rounded-3" :class="{ 'bg-primary-subtle border-primary': ticketTargetRole === 'ORGANIZER' }">
                  <input class="form-check-input" type="radio" id="targetOrg" value="ORGANIZER" v-model="ticketTargetRole" />
                  <label class="form-check-label fw-bold text-slate-800" for="targetOrg">
                    👤 Student Organizer
                    <small class="text-muted d-block font-normal">Send query to Student Event Organizer</small>
                  </label>
                </div>

                <div class="form-check flex-fill p-3 border rounded-3" :class="{ 'bg-primary-subtle border-primary': ticketTargetRole === 'COORDINATOR' }">
                  <input class="form-check-input" type="radio" id="targetCoord" value="COORDINATOR" v-model="ticketTargetRole" />
                  <label class="form-check-label fw-bold text-slate-800" for="targetCoord">
                    🎓 Faculty Coordinator
                    <small class="text-muted d-block font-normal">Escalate to Club Faculty Coordinator</small>
                  </label>
                </div>
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label text-sm fw-bold">Subject / Title</label>
              <input v-model="ticketTitle" class="form-control custom-input" placeholder="e.g. Query regarding schedule or registration..." />
            </div>

            <div class="mb-3">
              <label class="form-label text-sm fw-bold">Priority</label>
              <select v-model="ticketPriority" class="form-select custom-input">
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
              </select>
            </div>

            <div class="mb-3">
              <label class="form-label text-sm fw-bold">Message Details</label>
              <textarea v-model="ticketDescription" class="form-control custom-input" rows="3" placeholder="Explain your request or issue in detail..."></textarea>
            </div>

            <div v-if="ticketFeedback" class="alert alert-info text-xs py-2">{{ ticketFeedback }}</div>
          </div>

          <div class="modal-footer-custom">
            <button class="btn btn-secondary me-2 rounded-pill px-3" @click="showTicketModal = false">Cancel</button>
            <button class="btn btn-primary rounded-pill px-4" :disabled="isSubmittingTicket" @click="submitTicketToTarget">
              {{ isSubmittingTicket ? 'Submitting...' : 'Submit Ticket' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </StudentLayout>
</template>

<style scoped>
.event-details-page { width: 100%; max-width: 1500px; margin: 0 auto; }
.volunteer-banner { background: #fefce8; border: 1px solid #fef08a; border-radius: 20px; padding: 18px 24px; }
.header-actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.register-btn { border: none; border-radius: 999px; background: #16a34a; color: white; padding: 8px 18px; font-weight: 600; }
.register-btn:disabled { opacity: 0.7; cursor: default; }
.event-detail-card { background: white; border: 1px solid #e5e7eb; border-radius: 24px; padding: 28px; box-shadow: 0 18px 45px rgba(15, 23, 42, 0.06); }
.header-left { display: flex; align-items: center; gap: 18px; }
.event-image { width: 70px; height: 70px; border-radius: 50%; background: #eef4ff; display: flex; justify-content: center; align-items: center; font-size: 36px; flex-shrink: 0; }
.club-tag { display: inline-block; background: #eef4ff; color: #2563eb; padding: 5px 12px; border-radius: 999px; font-size: 12px; font-weight: 600; margin-bottom: 10px; }
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 28px; flex-wrap: wrap; gap: 16px; }
.detail-header h2 { color: #1f2937; font-size: 1.75rem; font-weight: 700; margin: 0; }
.status-badge { padding: 6px 14px; border-radius: 999px; font-size: 13px; font-weight: 600; white-space: nowrap; }
.status-badge.live, .status-badge.scheduled { background: #dcfce7; color: #16a34a; }
.status-badge.completed { background: #f1f5f9; color: #64748b; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
.info-box { background: #f8fafc; border: 1px solid #edf2f7; border-radius: 14px; padding: 16px 20px; }
.info-box label { display: block; color: #64748b; font-size: 13px; font-weight: 600; margin-bottom: 6px; }
.info-box p { margin: 0; color: #1f2937; font-weight: 500; }
.description-box { margin-bottom: 28px; }
.description-box p { line-height: 1.7; color: #374151; }
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
.modal-backdrop-glass { position: fixed; inset: 0; z-index: 1060; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(8px); display: flex; align-items: center; justify-content: center; padding: 1.5rem; }
.modal-box { width: 100%; max-width: 600px; background: white; border-radius: 24px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.8); }
.modal-header-custom { padding: 1.25rem 1.5rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.btn-close-custom { background: #f1f5f9; border: none; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; color: #64748b; cursor: pointer; }
.modal-body-custom { padding: 1.5rem; max-height: 75vh; overflow-y: auto; }
.custom-input { border-radius: 12px; border: 1px solid #cbd5e1; }
.modal-footer-custom { padding: 1rem 1.5rem; border-top: 1px solid #e2e8f0; display: flex; justify-content: flex-end; }
@media (max-width: 576px) { .info-grid { grid-template-columns: 1fr; } .detail-header { flex-direction: column; gap: 16px; } }
</style>