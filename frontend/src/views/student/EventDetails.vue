<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import StudentLayout from '@/layouts/StudentLayout.vue'
import { 
  getEvent, 
  registerForEvent, 
  manageEventSchedule, 
  manageEventAnnouncements, 
  manageEventAttendance, 
  manageEventPrizes 
} from '@/api/events'
import { getUserAssignments } from '@/api/assignmentTickets'
import { getCurrentUser } from '@/services/authService'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const { showToast } = useToast()

const activeTab = ref('schedule')
const event = ref(null)
const loading = ref(false)
const isRegistering = ref(false)
const isRegistered = ref(false)
const isOrganizer = ref(false)

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
  registrations: Array.isArray(data.registrations)
    ? data.registrations.map((entry) => ({
        id: entry.id,
        userId: entry.userId || entry.user_id,
        name: entry.userName || entry.name || 'Participant',
        registerNumber: entry.registerNumber || entry.userId || 'N/A',
        branch: entry.branch || 'N/A',
        status: entry.status || 'REGISTERED'
      }))
    : [],
  attendance: Array.isArray(data.attendance)
    ? data.attendance.map((entry) => ({
        id: entry.id,
        userId: entry.userId || entry.user_id,
        name: entry.userName || entry.name || 'Participant',
        registerNumber: entry.registerNumber || entry.userId || 'N/A',
        status: entry.status || 'PRESENT'
      }))
    : []
})

async function checkOrganizerPermission(clubId) {
  const user = getCurrentUser()
  if (!user) return

  let isOrg = false

  // 1. Check if user is listed in event's organizers or createdBy
  if (event.value) {
    if (Array.isArray(event.value.organizers) && event.value.organizers.some(o => Number(o.userId || o.id) === Number(user.id))) {
      isOrg = true
    }
    if (Number(event.value.createdBy) === Number(user.id)) {
      isOrg = true
    }
  }

  // 2. Check active Assignment Tickets
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
    const data = await getEvent(Number(route.params.id))
    event.value = normalizeEvent(data)
    if (event.value.clubId) {
      await checkOrganizerPermission(event.value.clubId)
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

async function handleRegister() {
  if (isRegistering.value || isRegistered.value) return
  isRegistering.value = true
  try {
    const response = await registerForEvent(Number(route.params.id))
    isRegistered.value = true
    event.value.registrations.unshift({
      id: response.id,
      name: 'You',
      registerNumber: 'You',
      branch: 'Your Branch',
      status: response.status || 'REGISTERED'
    })
    showToast('Registered for event successfully!', 'success')
  } catch (error) {
    console.error('Failed to register for event', error)
    showToast('Failed to register', 'error')
  } finally {
    isRegistering.value = false
  }
}

// ---------------- Organizers Actions ----------------
async function handleAddSchedule() {
  if (!newActivity.value.trim()) return
  try {
    await manageEventSchedule(Number(route.params.id), { time: newTime.value, activity: newActivity.value })
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
              <button class="register-btn" :disabled="isRegistered || isRegistering" @click="handleRegister">
                {{ isRegistering ? 'Registering…' : isRegistered ? 'Registered' : 'Register' }}
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

          <div class="info-box description-box">
            <label>Description</label>
            <p>{{ event.description }}</p>
          </div>

          <div class="detail-tabs">
            <button v-for="tab in tabs" :key="tab.key" class="tab-option" :class="{ active: activeTab === tab.key }" @click="activeTab = tab.key">
              {{ tab.label }}
            </button>
          </div>

          <div class="tab-content">
            
            <!-- TAB 1: SCHEDULE -->
            <div v-if="activeTab === 'schedule'">
              <!-- Organizer Form -->
              <div v-if="isOrganizer" class="organizer-form-box">
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

            <!-- TAB 2: ANNOUNCEMENTS -->
            <div v-else-if="activeTab === 'announcements'">
              <!-- Organizer Form -->
              <div v-if="isOrganizer" class="organizer-form-box">
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

            <!-- TAB 4: ATTENDANCE -->
            <div v-else-if="activeTab === 'attendance'">
              <table class="table" v-if="event.registrations.length">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Register Number</th>
                    <th>Attendance Status</th>
                    <th v-if="isOrganizer" class="text-end">Mark Attendance</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(student, index) in event.registrations" :key="index">
                    <td>{{ student.name }}</td>
                    <td>{{ student.registerNumber }}</td>
                    <td>
                      <span class="attendance-badge" :class="event.attendance.some(a => (a.userId === student.userId || a.name === student.name) && String(a.status).toUpperCase() === 'PRESENT') ? 'present' : 'absent'">
                        {{ event.attendance.some(a => (a.userId === student.userId || a.name === student.name) && String(a.status).toUpperCase() === 'PRESENT') ? 'PRESENT' : 'ABSENT / NOT MARKED' }}
                      </span>
                    </td>
                    <td v-if="isOrganizer" class="text-end">
                      <button class="btn-mark present-btn" @click="handleUpdateAttendance(student.userId, 'PRESENT')">Present</button>
                      <button class="btn-mark absent-btn" @click="handleUpdateAttendance(student.userId, 'ABSENT')">Absent</button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <p v-else class="empty-tab">No registered participants to mark attendance.</p>
            </div>

            <!-- TAB 5: PRIZES & WINNERS -->
            <div v-else-if="activeTab === 'prizes'">
              <!-- Organizer Form -->
              <div v-if="isOrganizer" class="organizer-form-box">
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
  </StudentLayout>
</template>

<style scoped>
.event-details-page { width: 100%; max-width: 1500px; margin: 0 auto; }
.header-actions { display: flex; gap: 10px; align-items: center; }
.register-btn { border: none; border-radius: 999px; background: #16a34a; color: white; padding: 10px 16px; font-weight: 600; }
.register-btn:disabled { opacity: 0.7; cursor: default; }
.event-detail-card { background: white; border: 1px solid #e5e7eb; border-radius: 24px; padding: 28px; box-shadow: 0 18px 45px rgba(15, 23, 42, 0.06); }
.header-left { display: flex; align-items: center; gap: 18px; }
.event-image { width: 70px; height: 70px; border-radius: 50%; background: #eef4ff; display: flex; justify-content: center; align-items: center; font-size: 36px; flex-shrink: 0; }
.club-tag { display: inline-block; background: #eef4ff; color: #2563eb; padding: 5px 12px; border-radius: 999px; font-size: 12px; font-weight: 600; margin-bottom: 6px; }
.organizer-badge { background: #fef3c7; color: #92400e; padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 28px; }
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
.detail-tabs { display: flex; width: 100%; gap: 6px; background: #f8fafc; border: 1px solid #d1d5db; border-radius: 16px; padding: 6px; margin-bottom: 28px; }
.tab-option { flex: 1; border: none; background: transparent; padding: 12px; border-radius: 10px; font-weight: 600; text-align: center; transition: 0.25s; cursor: pointer; }
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
@media (max-width: 576px) { .info-grid { grid-template-columns: 1fr; } .detail-header { flex-direction: column; gap: 16px; } }
</style>