<script setup>
import FacultyLayout from '@/layouts/FacultyLayout.vue'

import StatCard from '@/components/admin/analytics/StatCard.vue'

const facultyStats = [
  {
    label: 'My Roles',
    value: 2
  },
  {
    label: 'Clubs',
    value: 12
  },
  {
    label: 'Events',
    value: 8
  },
  {
    label: 'Pending Requests',
    value: 4
  }
]
</script>

<template>
  <FacultyLayout>
    <section class="dashboard-page">
      <div class="dashboard-header">
        <div>
          <h2>Faculty Dashboard</h2>
          <p>Manage clubs, events and requests from one place.</p>
        </div>

        <div class="dashboard-actions">
          <button class="request-btn">+ Request</button>
          <button class="notification-btn">Notifications</button>
        </div>
      </div>

      <div class="row g-4">
        <div
          v-for="stat in facultyStats"
          :key="stat.label"
          class="col-12 col-sm-6 col-xl-3"
        >
          <StatCard
            :label="stat.label"
            :value="stat.value"
          />
        </div>
      </div>
      <div class="row g-4 mt-1">
        <div class="col-12">
          <div class="placeholder-card">
            <div class="placeholder-header">
              <h5>Recent Activity</h5>
              <p>Latest updates from clubs and requests.</p>
            </div>
            <div class="placeholder-body">No recent activity available.</div>
          </div>
        </div>
      </div>
    </section>
  </FacultyLayout>
</template>

<style scoped>
.dashboard-page{
width:100%;
max-width:1600px;
margin:0 auto;
}

.dashboard-header{
display:flex;
justify-content:space-between;
align-items:flex-start;
margin-bottom:28px;
gap:20px;
}

.dashboard-header h2{
margin:0;
color:#1E293B;
font-size:1.75rem;
font-weight:700;
}

.dashboard-header p{
margin:7px 0 0;
color:#64748B;
font-size:.95rem;
}

.dashboard-actions{
display:flex;
gap:14px;
flex-wrap:wrap;
}

.request-btn{
padding:12px 22px;
background:#fff;
border:2px solid #22C55E;
color:#22C55E;
border-radius:14px;
font-weight:600;
transition:.25s;
}

.request-btn:hover{
background:#22C55E;
color:#fff;
}

.notification-btn{
padding:12px 22px;
background:#fff;
border:2px solid #2563EB;
color:#2563EB;
border-radius:14px;
font-weight:600;
transition:.25s;
}

.notification-btn:hover{
background:#2563EB;
color:#fff;
}

.placeholder-card{
background:#fff;
border-radius:24px;
box-shadow:0 8px 30px rgba(15,23,42,.05);
overflow:hidden;
min-height:420px;
}

.placeholder-header{
padding:28px 30px;
border-bottom:1px solid #E2E8F0;
}

.placeholder-header h5{
margin:0;
font-size:1.6rem;
font-weight:700;
color:#1E293B;
}

.placeholder-header p{
margin-top:6px;
font-size:.95rem;
color:#64748B;
}

.placeholder-body{
height:320px;
display:flex;
align-items:center;
justify-content:center;
color:#94A3B8;
font-size:1.05rem;
}

@media(max-width:768px){

.dashboard-header{
flex-direction:column;
align-items:flex-start;
}

.dashboard-actions{
width:100%;
}

}
</style>