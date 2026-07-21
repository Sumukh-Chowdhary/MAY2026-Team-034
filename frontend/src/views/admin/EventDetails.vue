<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { events } from '@/data/events'
import AdminLayout from '@/layouts/AdminLayout.vue'

const route = useRoute()
const router = useRouter()
const activeTab = ref('schedule')

const event = computed(() =>
  events.find((item) => item.id === Number(route.params.id))
)

const tabs = [
  { key: 'schedule', label: 'Schedule' },
  { key: 'announcements', label: 'Announcements' },
  { key: 'registrations', label: 'Registrations' },
  { key: 'attendance', label: 'Attendance' }
]

// Modal & Form States for Event Details page
const showAddScheduleModal = ref(false)
const newScheduleTime = ref('')
const newScheduleActivity = ref('')

const showAddAnnouncementModal = ref(false)
const newAnnouncementTitle = ref('')
const newAnnouncementMessage = ref('')

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/events')
  }
}

function submitNewSchedule() {
  if (!newScheduleActivity.value.trim()) return
  if (event.value) {
    if (!event.value.schedule) event.value.schedule = []
    event.value.schedule.push({
      time: newScheduleTime.value || '10:00 AM',
      activity: newScheduleActivity.value
    })
    showAddScheduleModal.value = false
    newScheduleTime.value = ''
    newScheduleActivity.value = ''
  }
}

function submitNewAnnouncement() {
  if (!newAnnouncementTitle.value.trim()) return
  if (event.value) {
    if (!event.value.announcements) event.value.announcements = []
    event.value.announcements.unshift({
      title: newAnnouncementTitle.value,
      message: newAnnouncementMessage.value,
      date: new Date().toLocaleDateString()
    })
    alert('Announcement broadcasted successfully!')
    showAddAnnouncementModal.value = false
    newAnnouncementTitle.value = ''
    newAnnouncementMessage.value = ''
  }
}

function postAttendance() {
  if (!event.value || !event.value.attendance) return
  const presentCount = event.value.attendance.filter(a => a.status === 'Present').length
  const totalCount = event.value.attendance.length
  alert(`Attendance updated! ${presentCount}/${totalCount} Present.`)
}
</script>

<template>
  <AdminLayout>
    <section class="event-details-page">
      <div class="container py-5" v-if="event">
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

            <span class="status-badge" :class="(event.status || 'Live').toLowerCase()">
              {{ event.status || 'Live' }}
            </span>
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

          <!-- Navigation Tabs -->
          <div class="detail-tabs">
            <button
              v-for="tab in tabs"
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
                    <td class="fw-semibold">{{ student.name }}</td>
                    <td>{{ student.registerNumber }}</td>
                    <td>{{ student.branch }}</td>
                  </tr>
                </tbody>
              </table>
              <div v-else class="empty-tab">No registrations yet.</div>
            </div>

            <!-- 4. Attendance Tab -->
            <div v-else-if="activeTab === 'attendance'">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="fw-bold m-0 text-dark">Participant Attendance</h5>
                <button class="btn btn-sm btn-primary" @click="postAttendance" v-if="event.attendance && event.attendance.length">
                  Post Attendance
                </button>
              </div>

              <table class="table align-middle" v-if="event.attendance && event.attendance.length">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Register Number</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(student, index) in event.attendance" :key="index">
                    <td class="fw-semibold">{{ student.name }}</td>
                    <td>{{ student.registerNumber }}</td>
                    <td>
                      <span class="attendance-badge" :class="(student.status || 'Present').toLowerCase()">
                        {{ student.status || 'Present' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-else class="empty-tab">Attendance has not been recorded yet.</div>
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