<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import StudentLayout from '@/layouts/StudentLayout.vue'
import UserProfileModal from '@/components/common/UserProfileModal.vue'
import EventAttendanceView from '@/components/events/EventAttendanceView.vue'
import EventAttendanceModal from '@/components/events/EventAttendanceModal.vue'
import EventRoundsView from '@/components/events/EventRoundsView.vue'
import ParticipantProgressView from '@/components/events/ParticipantProgressView.vue'
import EventResultsView from '@/components/events/EventResultsView.vue'
import RequestVenueModal from '@/components/events/RequestVenueModal.vue'
import EventVolunteersSection from '@/components/events/EventVolunteersSection.vue'
import ScheduleConflictModal from '@/components/common/ScheduleConflictModal.vue'
import { useScheduleConflictCheck } from '@/composables/useScheduleConflictCheck'

const showProfileModal = ref(false)
const selectedProfileUserId = ref(null)
const showVenueRequestModal = ref(false)

const {
  showConflictModal,
  pendingConflicts,
  pendingEventName,
  registerWithConflictCheck,
  confirmRegistration,
  cancelRegistration
} = useScheduleConflictCheck()

function openUserProfile(id) {
  if (!id) return
  selectedProfileUserId.value = id
  showProfileModal.value = true
}
import {
  getEvent,
  createEventTicket,
  manageEventSchedule,
  manageEventAnnouncements,
  manageEventAttendance,
  manageEventPrizes,
  manageEventVolunteers,
  cancelEventRegistration,
  downloadEventReport
} from '@/api/events'
import { createRequest } from '@/api/requests'
import { getUserAssignments } from '@/api/assignmentTickets'
import { getCurrentUser } from '@/services/authService'
import { useToast } from '@/composables/useToast'
import { eventSocketService } from '@/services/eventService'

const route = useRoute()
const router = useRouter()
const { showToast } = useToast()

const activeTab = ref('schedule')
const event = ref(null)
const loading = ref(false)
const isRegistering = ref(false)
const isRegistered = ref(false)
const isWaitlisted = ref(false)
const isCancelling = ref(false)
const isDownloadingReport = ref(false)
const isOrganizer = ref(false)
const currentUserId = ref(null)

// Ticket modal state
const showTicketModal = ref(false)
const showAttendanceModal = ref(false)
const ticketTargetRole = ref('ORGANIZER') // 'ORGANIZER' | 'COORDINATOR'
const ticketTitle = ref('')
const ticketDescription = ref('')
const ticketPriority = ref('MEDIUM')
const isSubmittingTicket = ref(false)
const ticketFeedback = ref('')

// Volunteer state (Module 22)
const isApplyingVolunteer = ref(false)
const volunteerFeedback = ref('')

// Organizer Forms State
const newTime = ref('')
const newActivity = ref('')
const newAnnTitle = ref('')
const newAnnMessage = ref('')
const newPrizeTitle = ref('')
const newPrizeWinner = ref('')
const newPrizeDesc = ref('')

const normalizeEvent = (data) => ({
  ...data,
  clubId: data.clubId || data.club_id,
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
        userId: entry.userId || entry.user_id || entry.id,
        name: entry.userName || entry.name || 'Participant',
        registerNumber: entry.registerNumber || entry.userId || 'N/A',
        branch: entry.branch || 'N/A',
        status: entry.status || 'REGISTERED'
      }))
    : [],
  attendance: Array.isArray(data.attendance)
    ? data.attendance.map((entry) => ({
        id: entry.id,
        userId: entry.userId || entry.user_id || entry.id,
        name: entry.userName || entry.name || 'Participant',
        registerNumber: entry.registerNumber || entry.userId || 'N/A',
        status: entry.status || 'PRESENT'
      }))
    : []
})

import { getMyClubs } from '@/api/clubs'

const myClubs = ref([])

const myVolunteerRecord = computed(() => {
  if (!event.value || !event.value.volunteers || !currentUserId.value) return null
  return event.value.volunteers.find(v => Number(v.userId) === Number(currentUserId.value))
})

const isApprovedVolunteer = computed(() => {
  return myVolunteerRecord.value && myVolunteerRecord.value.status === 'APPROVED'
})

const isClubMember = computed(() => {
  if (!event.value || !event.value.clubId) return false
  return myClubs.value.some(c => Number(c.id || c.clubId) === Number(event.value.clubId))
})

const canApplyVolunteer = computed(() => {
  if (!event.value || !event.value.clubId) return false
  if (!isClubMember.value) return false
  if (event.value.status === 'COMPLETED') return false
  if (isOrganizer.value) return false
  if (myVolunteerRecord.value) return false
  return true
})

const canManage = computed(() => {
  return isOrganizer.value || isApprovedVolunteer.value
})

async function checkOrganizerPermission(clubId) {
  const user = getCurrentUser()
  if (!user) return

  let isOrg = false

  if (event.value) {
    if (Array.isArray(event.value.organizers) && event.value.organizers.some(o => Number(o.userId || o.id) === Number(user.id))) {
      isOrg = true
    }
    if (Number(event.value.createdBy) === Number(user.id)) {
      isOrg = true
    }
  }

  try {
    const res = await getUserAssignments(user.id)
    const activeGrants = res?.data?.active || res?.active || (Array.isArray(res?.data) ? res.data : [])
    if (Array.isArray(activeGrants)) {
      const hasGrant = activeGrants.some(
        a => (String(a.assignmentRole).toUpperCase() === 'ORGANIZER' || String(a.assignmentRole).toUpperCase() === 'PRESIDENT') &&
             String(a.referenceId) === String(clubId) &&
             String(a.status).toUpperCase() === 'ACTIVE'
      )
      if (hasGrant) isOrg = true
    }
  } catch (e) {
    console.error('Failed to check assignments', e)
  }

  isOrganizer.value = isOrg
}

async function loadEventData() {
  loading.value = true
  try {
    const user = getCurrentUser()
    if (user) {
      currentUserId.value = user.id
    }

    try {
      myClubs.value = await getMyClubs()
    } catch (e) {
      myClubs.value = []
    }

    const data = await getEvent(Number(route.params.id))
    event.value = normalizeEvent(data)

    if (event.value.clubId) {
      await checkOrganizerPermission(event.value.clubId)
    }

    if (currentUserId.value && event.value.registrations) {
      const myReg = event.value.registrations.find(r => Number(r.userId) === Number(currentUserId.value) || r.name === 'You')
      isRegistered.value = !!myReg && myReg.status !== 'WAITLISTED'
      isWaitlisted.value = !!myReg && myReg.status === 'WAITLISTED'
    }

    // Socket real-time updates for Module 22
    if (eventSocketService?.initSocket) {
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
    }
  } catch (error) {
    console.error('Failed to load event', error)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadEventData()
})

onUnmounted(() => {
  if (route.params.id && eventSocketService?.leaveEventRoom) {
    eventSocketService.leaveEventRoom(Number(route.params.id))
  }
})

async function handleRegister() {
  if (isRegistering.value || isRegistered.value || isWaitlisted.value) return
  isRegistering.value = true
  try {
    const result = await registerWithConflictCheck(
      Number(route.params.id),
      event.value?.name || event.value?.eventName || 'this event'
    )
    if (result.cancelled) {
      isRegistering.value = false
      return
    }
    const response = result.response
    const waitlisted = response.status === 'WAITLISTED'
    isRegistered.value = !waitlisted
    isWaitlisted.value = waitlisted
    event.value.registrations.unshift({
      id: response.id,
      userId: currentUserId.value,
      name: 'You',
      registerNumber: 'You',
      branch: 'Your Branch',
      status: response.status || 'REGISTERED'
    })
    showToast(
      waitlisted
        ? "Event is full — you've been added to the waitlist."
        : 'Registered for event successfully!',
      waitlisted ? 'info' : 'success'
    )
  } catch (error) {
    console.error('Failed to register for event', error)
    showToast('Failed to register', 'error')
  } finally {
    isRegistering.value = false
  }
}

async function handleCancelRegistration() {
  if (isCancelling.value || (!isRegistered.value && !isWaitlisted.value)) return
  isCancelling.value = true
  try {
    await cancelEventRegistration(Number(route.params.id))
    isRegistered.value = false
    isWaitlisted.value = false
    event.value.registrations = event.value.registrations.filter(
      r => !(Number(r.userId) === Number(currentUserId.value) || r.name === 'You')
    )
    showToast('Registration cancelled.', 'success')
  } catch (error) {
    console.error('Failed to cancel registration', error)
    showToast('Failed to cancel registration', 'error')
  } finally {
    isCancelling.value = false
  }
}

async function handleDownloadReport() {
  if (isDownloadingReport.value || !event.value) return
  isDownloadingReport.value = true
  try {
    await downloadEventReport(Number(route.params.id), event.value.name)
    showToast('Report downloaded.', 'success')
  } catch (error) {
    console.error('Failed to download report', error)
    showToast('Failed to download report', 'error')
  } finally {
    isDownloadingReport.value = false
  }
}

async function applyVolunteer() {
  if (isApplyingVolunteer.value || myVolunteerRecord.value) {
    if (myVolunteerRecord.value?.status === 'PENDING') {
      showToast('You already have a pending volunteer application for this event.', 'warning')
    }
    return
  }
  isApplyingVolunteer.value = true
  volunteerFeedback.value = ''
  try {
    const payload = {
      title: `Apply as Volunteer - ${event.value.name}`,
      description: `Volunteer application for event ${event.value.name} under club ${event.value.club || 'Club'}.`,
      requestType: 'BECOME_VOLUNTEER',
      priority: 'MEDIUM',
      referenceType: 'EVENT',
      referenceId: event.value.id,
      referenceName: event.value.name
    }
    await createRequest(payload)
    volunteerFeedback.value = 'Volunteer application submitted! Awaiting faculty/admin approval.'
    showToast('Volunteer application submitted!', 'success')
    event.value.volunteers.push({
      userId: currentUserId.value,
      status: 'PENDING'
    })
  } catch (err) {
    const errorMsg = err.response?.data?.error || err.message || 'Failed to submit volunteer application.'
    if (errorMsg.toLowerCase().includes('already pending') || err.response?.status === 409) {
      showToast('You already have a pending volunteer application for this event.', 'warning')
      volunteerFeedback.value = 'You already have a pending volunteer application for this event.'
    } else {
      showToast(errorMsg, 'error')
      volunteerFeedback.value = errorMsg
    }
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
    ticketFeedback.value = 'Ticket successfully raised!'
    showToast('Ticket submitted successfully!', 'success')
    setTimeout(() => {
      showTicketModal.value = false
      ticketTitle.value = ''
      ticketDescription.value = ''
      ticketFeedback.value = ''
    }, 1200)
  } catch (err) {
    const msg = err.response?.data?.error || 'Failed to raise ticket.'
    ticketFeedback.value = msg
    showToast(msg, 'error')
  } finally {
    isSubmittingTicket.value = false
  }
}

// Management Handlers (Organizers + Approved Volunteers)
async function handleAddSchedule() {
  if (!newActivity.value.trim()) return
  try {
    await manageEventSchedule(Number(route.params.id), { time: newTime.value || '10:00 AM', activity: newActivity.value })
    showToast('Schedule item added!', 'success')
    newTime.value = ''
    newActivity.value = ''
    await loadEventData()
  } catch (e) {
    showToast('Failed to add schedule item', 'error')
  }
}

async function handlePostAnnouncement() {
  if (!newAnnMessage.value.trim()) return
  try {
    await manageEventAnnouncements(Number(route.params.id), { title: newAnnTitle.value || 'Announcement', message: newAnnMessage.value })
    showToast('Announcement posted!', 'success')
    newAnnTitle.value = ''
    newAnnMessage.value = ''
    await loadEventData()
  } catch (e) {
    showToast('Failed to post announcement', 'error')
  }
}

async function handleUpdateAttendance(userId, status) {
  try {
    await manageEventAttendance(Number(route.params.id), { userId, status })
    showToast(`Marked ${status}!`, 'success')
    await loadEventData()
  } catch (e) {
    showToast('Failed to update attendance', 'error')
  }
}

async function handleAddPrize() {
  if (!newPrizeTitle.value.trim()) return
  try {
    await manageEventPrizes(Number(route.params.id), { title: newPrizeTitle.value, winnerName: newPrizeWinner.value, description: newPrizeDesc.value })
    showToast('Prize/Winner added successfully!', 'success')
    newPrizeTitle.value = ''
    newPrizeWinner.value = ''
    newPrizeDesc.value = ''
    await loadEventData()
  } catch (e) {
    showToast('Failed to add prize', 'error')
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
  return tabs.filter(tab => {
    if (!isComp && (tab.key === 'rounds' || tab.key === 'progress' || tab.key === 'results')) {
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
</script>

<template>
  <StudentLayout>
    <section class="event-details-page">
      <div v-if="loading" class="container py-5">
        <div class="loading-state">
          <div class="spinner-border text-primary" role="status"></div>
          <p>Loading event details...</p>
        </div>
      </div>

      <div class="container py-5" v-else-if="event">

        <!-- Module 22 Approved Volunteer Banner -->
        <div v-if="isApprovedVolunteer && !isOrganizer" class="volunteer-banner shadow-sm mb-4">
          <div class="d-flex align-items-center gap-3">
            <div class="banner-icon"><i class="bi bi-shield-check display-6 text-warning"></i></div>
            <div>
              <h5 class="fw-bold text-dark mb-1">⭐ Approved Event Volunteer Access</h5>
              <p class="text-secondary text-sm mb-0">You are an active volunteer for <strong>{{ event.name }}</strong>. You have permissions to manage Schedule, Announcements, Attendance, and Prizes.</p>
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
                <span v-if="isOrganizer" class="organizer-badge mt-2 d-inline-block">
                  ⭐ Organizer Management Mode Enabled
                </span>
              </div>
            </div>

            <div class="header-actions">
              <span class="status-badge" :class="(event.status || 'scheduled').toLowerCase()">{{ event.status }}</span>
              
              <button
                v-if="!isRegistered && !isWaitlisted"
                class="register-btn"
                :disabled="isRegistering"
                @click="handleRegister"
              >
                {{ isRegistering ? 'Registering…' : 'Register' }}
              </button>

              <button
                v-else
                class="register-btn"
                :class="{ 'waitlist-btn': isWaitlisted }"
                :disabled="isCancelling"
                @click="handleCancelRegistration"
              >
                {{ isCancelling ? 'Cancelling…' : isWaitlisted ? 'Waitlisted — Cancel' : 'Registered ✓ — Cancel' }}
              </button>

              <button class="btn btn-outline-primary rounded-pill px-3 fw-semibold text-xs" @click="showTicketModal = true">
                <i class="bi bi-ticket-perforated me-1"></i> Raise Ticket
              </button>

              <button
                v-if="canManage"
                class="btn btn-outline-secondary rounded-pill px-3 fw-semibold text-xs"
                :disabled="isDownloadingReport"
                @click="handleDownloadReport"
              >
                <i class="bi bi-file-earmark-arrow-down me-1"></i>
                {{ isDownloadingReport ? 'Preparing…' : 'Download Report' }}
              </button>

              <button 
                v-if="canManage" 
                class="btn btn-sm btn-outline-primary rounded-pill px-3 fw-semibold"
                :class="{ 'opacity-50': !isAttendanceAvailable }"
                :title="!isAttendanceAvailable ? `Attendance will be available when the event begins on ${event.startDate || event.start_date || ''}` : 'Manage Attendance'"
                @click="handleAttendanceClick"
              >
                <i class="bi bi-calendar-check me-1"></i> Attendance
              </button>

              <button 
                v-if="canApplyVolunteer" 
                class="btn btn-warning rounded-pill px-3 fw-semibold text-xs"
                :disabled="isApplyingVolunteer"
                @click="applyVolunteer"
              >
                <i class="bi bi-star me-1"></i> {{ isApplyingVolunteer ? 'Applying...' : 'Apply as Volunteer' }}
              </button>
              
              <span v-else-if="myVolunteerRecord && !isOrganizer" class="badge bg-info text-dark rounded-pill px-3">
                Volunteer: {{ myVolunteerRecord.status }}
              </span>
            </div>
          </div>

          <div v-if="volunteerFeedback" class="alert alert-info py-2 text-xs mb-3 d-flex justify-content-between align-items-center">
            <span>{{ volunteerFeedback }}</span>
            <button class="btn btn-sm btn-link text-primary p-0 ms-2 text-decoration-none fw-bold" @click="router.push('/student/requests')">
              View Requests <i class="bi bi-arrow-right"></i>
            </button>
          </div>

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

          <!-- Read-only Venue Display with Request Venue Button for Organizers -->
          <div class="info-box mb-3">
            <div class="d-flex align-items-center justify-content-between">
              <div>
                <label>Venue</label>
                <p class="mb-0 fw-semibold text-dark">{{ event.venueName || event.venue || 'No venue assigned yet' }}</p>
                <small v-if="event.venueLocation" class="text-muted text-xs d-block">{{ event.venueLocation }}</small>
              </div>
              <button 
                v-if="isOrganizer" 
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

          <div class="detail-tabs">
            <button v-for="tab in visibleTabs" :key="tab.key" class="tab-option" :class="{ active: activeTab === tab.key }" @click="activeTab = tab.key">
              {{ tab.label }}
            </button>
          </div>

          <div class="tab-content">
            
            <!-- TAB 1: SCHEDULE -->
            <div v-if="activeTab === 'schedule'">
              <div v-if="canManage" class="organizer-form-box">
                <label class="form-title">Add Schedule Item</label>
                <div class="form-row">
                  <input v-model="newTime" type="text" class="input-field time-input" placeholder="Time (e.g. 10:00 AM)" />
                  <input v-model="newActivity" type="text" class="input-field activity-input" placeholder="Activity (e.g. Keynote Talk)" />
                  <button class="action-btn" @click="handleAddSchedule">Add Item</button>
                </div>
              </div>

              <div v-for="(item, index) in event.schedule" :key="index" class="schedule-row">
                <span class="time">{{ item.time }}</span>
                <span class="activity">{{ item.activity }}</span>
              </div>
              <p v-if="event.schedule.length === 0" class="empty-tab">No schedule added yet.</p>
            </div>

            <!-- TAB 1B: ROUNDS -->
            <div v-else-if="activeTab === 'rounds'">
              <EventRoundsView :eventId="event.id" :canManage="canManage" />
            </div>

            <!-- TAB 1C: PARTICIPANT PROGRESS -->
            <div v-else-if="activeTab === 'progress'">
              <ParticipantProgressView :eventId="event.id" />
            </div>

            <!-- TAB 1D: RESULTS & PODIUM -->
            <div v-else-if="activeTab === 'results'">
              <EventResultsView :eventId="event.id" :prizes="event.prizes" :canManage="canManage" @refresh="loadEventData" />
            </div>

            <!-- TAB 2: ANNOUNCEMENTS -->
            <div v-else-if="activeTab === 'announcements'">
              <div v-if="canManage" class="organizer-form-box">
                <label class="form-title">Post New Announcement</label>
                <div class="form-col">
                  <input v-model="newAnnTitle" type="text" class="input-field" placeholder="Title (e.g. Room Changed)" />
                  <textarea v-model="newAnnMessage" class="textarea-field" rows="2" placeholder="Announcement Details..."></textarea>
                  <button class="action-btn" @click="handlePostAnnouncement">Post Announcement</button>
                </div>
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

            <!-- TAB 3: REGISTRATIONS -->
            <div v-else-if="activeTab === 'registrations'">
              <table class="table" v-if="event.registrations.length">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Register Number</th>
                    <th>Branch</th>
                  </tr>
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

            <!-- TAB 5: PRIZES & WINNERS -->
            <div v-else-if="activeTab === 'prizes'">
              <div v-if="canManage" class="organizer-form-box">
                <label class="form-title">Add Prize & Winner</label>
                <div class="form-row">
                  <input v-model="newPrizeTitle" type="text" class="input-field" placeholder="Prize Title (1st Place)" />
                  <input v-model="newPrizeWinner" type="text" class="input-field" placeholder="Winner Name" />
                  <input v-model="newPrizeDesc" type="text" class="input-field" placeholder="Reward Details" />
                  <button class="action-btn" @click="handleAddPrize">Save Winner</button>
                </div>
              </div>

              <div v-for="(prize, index) in event.prizes" :key="index" class="prize-card">
                <div class="prize-icon">🏆</div>
                <div>
                  <h5 class="prize-title">{{ prize.title }}</h5>
                  <p class="prize-winner">Winner: {{ prize.winnerName || prize.winner_name || 'TBA' }}</p>
                  <small class="prize-desc">{{ prize.description }}</small>
                </div>
              </div>
              <p v-if="event.prizes.length === 0" class="empty-tab">No prizes or winners announced yet.</p>
            </div>

            <!-- TAB 6: VOLUNTEERS -->
            <div v-else-if="activeTab === 'volunteers'" class="py-2">
              <EventVolunteersSection 
                :eventId="event.id" 
                :event="event" 
                userRole="STUDENT"
                :isClubMember="isClubMember"
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
    </section>

    <!-- Raise Ticket Modal -->
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
                  </label>
                </div>

                <div class="form-check flex-fill p-3 border rounded-3" :class="{ 'bg-primary-subtle border-primary': ticketTargetRole === 'COORDINATOR' }">
                  <input class="form-check-input" type="radio" id="targetCoord" value="COORDINATOR" v-model="ticketTargetRole" />
                  <label class="form-check-label fw-bold text-slate-800" for="targetCoord">
                    🎓 Faculty Coordinator
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

            <div v-if="ticketFeedback" class="alert alert-info text-xs py-2 d-flex justify-content-between align-items-center">
              <span>{{ ticketFeedback }}</span>
              <button class="btn btn-sm btn-link text-primary p-0 ms-2 text-decoration-none fw-bold" @click="showTicketModal = false; router.push('/student/requests')">
                View Requests <i class="bi bi-arrow-right"></i>
              </button>
            </div>
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

    <UserProfileModal 
      :show="showProfileModal"
      :userId="selectedProfileUserId"
      @close="showProfileModal = false"
    />

    <EventAttendanceModal 
      :show="showAttendanceModal"
      :eventId="event ? event.id : 0"
      :canManage="canManage"
      @close="showAttendanceModal = false"
      @saved="loadEventData"
    />

    <RequestVenueModal
      v-if="event"
      :show="showVenueRequestModal"
      :event="event"
      @close="showVenueRequestModal = false"
      @submitted="loadEventData"
    />

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
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 20px;
  color: #64748B;
}

.loading-state p {
  margin-top: 14px;
}

.event-details-page { width: 100%; max-width: 1500px; margin: 0 auto; }
.volunteer-banner { background: #fefce8; border: 1px solid #fef08a; border-radius: 20px; padding: 18px 24px; }
.header-actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.register-btn { border: none; border-radius: 999px; background: #16a34a; color: white; padding: 8px 18px; font-weight: 600; }
.register-btn:disabled { opacity: 0.7; cursor: default; }
.waitlist-btn { background: #d97706; }
.event-detail-card { background: white; border: 1px solid #e5e7eb; border-radius: 24px; padding: 28px; box-shadow: 0 18px 45px rgba(15, 23, 42, 0.06); }
.header-left { display: flex; align-items: center; gap: 18px; }
.event-image { width: 70px; height: 70px; border-radius: 50%; background: #eef4ff; display: flex; justify-content: center; align-items: center; font-size: 36px; flex-shrink: 0; }
.club-tag { display: inline-block; background: #eef4ff; color: #2563eb; padding: 5px 12px; border-radius: 999px; font-size: 12px; font-weight: 600; margin-bottom: 6px; }
.organizer-badge { background: #fef3c7; color: #92400e; padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; }
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
.tab-option { flex: 1; border: none; background: transparent; padding: 12px; border-radius: 10px; font-weight: 600; text-align: center; transition: 0.25s; min-width: 120px; cursor: pointer; }
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

/* Organizer Custom Controls CSS */
.organizer-form-box { background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 16px; padding: 16px; margin-bottom: 24px; }
.form-title { font-weight: 700; color: #2563eb; font-size: 14px; margin-bottom: 10px; display: block; }
.form-row { display: flex; gap: 10px; flex-wrap: wrap; }
.form-col { display: flex; flex-direction: column; gap: 10px; }
.input-field { flex: 1; min-width: 140px; padding: 8px 12px; border-radius: 8px; border: 1px solid #cbd5e1; font-size: 13px; }
.textarea-field { padding: 8px 12px; border-radius: 8px; border: 1px solid #cbd5e1; font-size: 13px; }
.action-btn { background: #2563eb; color: white; border: none; border-radius: 8px; padding: 8px 16px; font-size: 13px; font-weight: 600; cursor: pointer; }
.action-btn:hover { background: #1d4ed8; }
.btn-mark { border: none; border-radius: 6px; padding: 4px 10px; font-size: 12px; font-weight: 600; cursor: pointer; margin-left: 4px; }
.present-btn { background: #dcfce7; color: #15803d; }
.present-btn:hover { background: #bbf7d0; }
.absent-btn { background: #fee2e2; color: #b91c1c; }
.absent-btn:hover { background: #fca5a5; }
.prize-card { display: flex; align-items: center; gap: 16px; padding: 16px; background: #f8fafc; border: 1px solid #edf2f7; border-radius: 14px; margin-bottom: 12px; }
.prize-icon { font-size: 28px; }
.prize-title { margin: 0; font-weight: 700; color: #1f2937; font-size: 15px; }
.prize-winner { margin: 2px 0 0; color: #2563eb; font-weight: 600; font-size: 13px; }
.prize-desc { color: #64748b; font-size: 12px; }

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