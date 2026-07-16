<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

import { events } from '@/data/events'
import AdminLayout from '@/layouts/AdminLayout.vue'

const route = useRoute()
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
</script>

<template>
    <AdminLayout>
        <section class="event-details-page">
  <div class="container py-5" v-if="event">
    <div class="event-detail-card">
      <div class="detail-header">
        <div class="header-left">
          <div class="event-image">
            {{ event.emoji }}
          </div>

          <div>
            <span class="club-tag">{{ event.club }}</span>
            <h2>{{ event.name }}</h2>
          </div>

        </div>

        <span class="status-badge" :class="event.status.toLowerCase()">
          {{ event.status }}
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

      <div class="detail-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-option"
          :class="{active:activeTab===tab.key}"
          @click="activeTab=tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="tab-content">

        <div v-if="activeTab==='schedule'">
          <div
            v-for="(item,index) in event.schedule"
            :key="index"
            class="schedule-row"
          >
            <span class="time">{{ item.time }}</span>
            <span class="activity">{{ item.activity }}</span>
          </div>
          <p v-if="event.schedule.length===0" class="empty-tab">No schedule added yet.</p>
        </div>

        <div v-else-if="activeTab==='announcements'">
          <div
            v-for="(item,index) in event.announcements"
            :key="index"
            class="announcement-row"
          >
            <div class="d-flex justify-content-between align-items-start">
              <h5>{{ item.title }}</h5>
              <small class="text-secondary">{{ item.date }}</small>
            </div>
            <p>{{ item.message }}</p>
          </div>
          <p v-if="event.announcements.length===0" class="empty-tab">No announcements yet.</p>
        </div>

        <div v-else-if="activeTab==='registrations'">
          <table class="table" v-if="event.registrations.length">
            <thead>
              <tr>
                <th>Name</th>
                <th>Register Number</th>
                <th>Branch</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(student,index) in event.registrations"
                :key="index"
              >
                <td>{{ student.name }}</td>
                <td>{{ student.registerNumber }}</td>
                <td>{{ student.branch }}</td>
              </tr>
            </tbody>
          </table>
          <p v-else class="empty-tab">No registrations yet.</p>
        </div>

        <div v-else-if="activeTab==='attendance'">
          <table class="table" v-if="event.attendance.length">
            <thead>
              <tr>
                <th>Name</th>
                <th>Register Number</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(student,index) in event.attendance"
                :key="index"
              >
                <td>{{ student.name }}</td>
                <td>{{ student.registerNumber }}</td>
                <td>
                  <span
                    class="attendance-badge"
                    :class="student.status.toLowerCase()"
                  >
                    {{ student.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-else class="empty-tab">Attendance has not been recorded yet.</p>
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
  </AdminLayout>
</template>

<style scoped>
.event-details-page{
    width:100%;
    max-width:1500px;
    margin:0 auto;
}

.page-header{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:28px;
}

.page-header h2{
    margin:0;
    font-size:2rem;
    font-weight:700;
    color:#1f2937;
}

.page-header p{
    margin-top:6px;
    color:#64748b;
}

.header-left{
    display:flex;
    align-items:center;
    gap:18px;
}

.event-image{
    width:70px;
    height:70px;
    border-radius:50%;
    background:#EEF4FF;
    display:flex;
    justify-content:center;
    align-items:center;
    font-size:36px;
    flex-shrink:0;
}

.info-grid{
    display:grid;
    grid-template-columns:repeat(2,1fr);
    gap:20px;
    margin-bottom:24px;
}

.info-box{
    background:white;
    border:1px solid #E5E7EB;
    border-radius:16px;
    padding:22px;
}

.info-box label{
    display:block;
    color:#64748b;
    font-size:.85rem;
    font-weight:600;
    margin-bottom:8px;
}

.info-box p{
    margin:0;
    font-size:1rem;
}

.description-box{
    margin-bottom:28px;
}

.club-tag{
    display:inline-block;
    background:#EEF4FF;
    color:#2563EB;
    padding:5px 12px;
    border-radius:999px;
    font-size:12px;
    font-weight:600;
    margin-bottom:10px;
}

.detail-header{
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    margin-bottom:28px;
}

.detail-header h2{
    color:#1f2937;
    font-size:1.75rem;
    font-weight:700;
    margin:0;
}

.status-badge{
    padding:6px 14px;
    border-radius:999px;
    font-size:13px;
    font-weight:600;
    white-space:nowrap;
}

.status-badge.live{
    background:#dcfce7;
    color:#16a34a;
}

.status-badge.completed{
    background:#f1f5f9;
    color:#64748b;
}

.info-grid{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:20px;
    margin-bottom:20px;
}

.info-box{
    background:#f8fafc;
    border:1px solid #edf2f7;
    border-radius:14px;
    padding:16px 20px;
}

.info-box label{
    display:block;
    color:#64748b;
    font-size:13px;
    font-weight:600;
    margin-bottom:6px;
}

.info-box p{
    margin:0;
    color:#1f2937;
    font-weight:500;
}

.description-box{
    margin-bottom:28px;
}

.description-box p{
    line-height:1.7;
    font-weight:400;
    color:#374151;
}

.detail-tabs{
    display:flex;
    width:100%;
    gap:6px;
    background:#f8fafc;
    border:1px solid #D1D5DB;
    border-radius:16px;
    padding:6px;
    margin-bottom:28px;
}

.tab-option{
    flex:1;
    border:none;
    background:transparent;
    padding:12px;
    border-radius:10px;
    font-weight:600;
    text-align:center;
    transition:.25s;
}

.tab-option:hover{
    background:#EFF6FF;
}

.tab-option.active{
    background:#2563EB;
    color:white;
}

.tab-content{
    min-height:180px;
}

.schedule-row{
    display:flex;
    gap:20px;
    padding:14px 0;
    border-bottom:1px solid #f1f5f9;
}

.schedule-row .time{
    color:#2563eb;
    font-weight:600;
    min-width:90px;
}

.schedule-row .activity{
    color:#374151;
}

.announcement-row{
    padding:16px 0;
    border-bottom:1px solid #f1f5f9;
}

.announcement-row h5{
    color:#1f2937;
    font-weight:600;
    margin:0;
}

.announcement-row p{
    color:#6b7280;
    margin:8px 0 0;
}

.table{
    width:100%;
}

.table th{
    color:#64748b;
    font-size:13px;
    font-weight:600;
    border-bottom:2px solid #edf2f7;
    padding:10px 12px;
}

.table td{
    padding:12px;
    border-bottom:1px solid #f1f5f9;
    color:#374151;
}

.attendance-badge{
    padding:4px 12px;
    border-radius:999px;
    font-size:12px;
    font-weight:600;
}

.attendance-badge.present{
    background:#dcfce7;
    color:#16a34a;
}

.attendance-badge.absent{
    background:#fee2e2;
    color:#dc2626;
}

.empty-tab{
    color:#94a3b8;
    text-align:center;
    padding:40px 0;
}

.empty-state{
    text-align:center;
    padding:70px 20px;
    color:#6b7280;
}

.empty-state h3{
    color:#1f2937;
    margin-bottom:10px;
}

@media (max-width:576px){
.info-grid{
    grid-template-columns:1fr;
}

.detail-header{
    flex-direction:column;
    gap:16px;
}
}
</style>