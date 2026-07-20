<script setup>
import FacultyLayout from '@/layouts/FacultyLayout.vue'
import StatCard from '@/components/admin/analytics/StatCard.vue'

import {
  facultyStats,
  managedClubs,
  upcomingEvents,
  pendingRequests,
  recentActivity
} from '@/data/facultyDashboard.js'
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

  <!-- Managed Clubs -->
  <div class="col-12 col-lg-6">
    <div class="dashboard-card">
      <div class="card-header">
        <h5>Managed Clubs</h5>
        <p>Clubs you currently manage or advise.</p>
      </div>

      <div class="card-content">
        <div
          v-for="club in managedClubs"
          :key="club.id"
          class="club-item"
        >
          <div class="club-info">
            <div class="club-icon">
              {{ club.emoji }}
            </div>

            <div>
              <h6>{{ club.name }}</h6>
              <span>{{ club.role }} · {{ club.members }} members</span>
            </div>
          </div>

          <button class="view-btn">View</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Upcoming Events -->
  <div class="col-12 col-lg-6">
    <div class="dashboard-card">
      <div class="card-header">
        <h5>Upcoming Events</h5>
        <p>Upcoming events from your clubs.</p>
      </div>

      <div class="card-content">
        <div
          v-for="event in upcomingEvents"
          :key="event.id"
          class="event-item"
        >
          <div>
            <h6>{{ event.title }}</h6>
            <span>{{ event.club }}</span>
          </div>

          <div class="event-date">
            {{ event.date }}
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Pending Requests -->
  <div class="col-12 col-lg-6">
    <div class="dashboard-card">
      <div class="card-header">
        <h5>Pending Requests</h5>
        <p>Requests waiting for your review.</p>
      </div>

      <div class="card-content">
        <div
          v-for="request in pendingRequests"
          :key="request.id"
          class="request-item"
        >
          <div>
            <h6>{{ request.student }}</h6>
            <span>{{ request.club }} · {{ request.type }}</span>
          </div>

          <button class="review-btn">Review</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Recent Activity -->
  <div class="col-12 col-lg-6">
    <div class="dashboard-card">
      <div class="card-header">
        <h5>Recent Activity</h5>
        <p>Latest updates from your clubs and events.</p>
      </div>

      <div class="card-content">
        <div
          v-for="activity in recentActivity"
          :key="activity.id"
          class="activity-item"
        >
          <div class="activity-dot"></div>

          <div class="activity-info">
            <h6>{{ activity.text }}</h6>
            <span>{{ activity.time }}</span>
          </div>
        </div>
      </div>
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

.dashboard-card {
    height: 100%;
    background: #fff;
    border-radius: 20px;
    box-shadow: 0 8px 30px rgba(15, 23, 42, .05);
    overflow: hidden;
}

.card-header {
    padding: 22px 24px;
    border-bottom: 1px solid #E2E8F0;
}

.card-header h5 {
    margin: 0;
    color: #1E293B;
    font-size: 1.15rem;
    font-weight: 700;
}

.card-header p {
    margin: 5px 0 0;
    color: #64748B;
    font-size: .9rem;
}

.card-content {
    padding: 8px 24px;
}

.club-item,
.event-item,
.request-item,
.activity-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 18px 0;
    border-bottom: 1px solid #F1F5F9;
}

.club-item:last-child,
.event-item:last-child,
.request-item:last-child,
.activity-item:last-child {
    border-bottom: none;
}

.club-info {
    display: flex;
    align-items: center;
    gap: 14px;
}

.club-icon {
    width: 46px;
    height: 46px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #F1F5F9;
    border-radius: 12px;
    font-size: 1.4rem;
}

.club-item h6,
.event-item h6,
.request-item h6,
.activity-item h6 {
    margin: 0 0 4px;
    color: #1E293B;
    font-weight: 600;
}

.club-item span,
.event-item span,
.request-item span,
.activity-item span {
    color: #64748B;
    font-size: .85rem;
}

.view-btn,
.review-btn {
    flex-shrink: 0;
    padding: 7px 16px;
    border: none;
    border-radius: 9px;
    font-size: .85rem;
    font-weight: 600;
    transition: .2s;
}

.view-btn {
    background: #EFF6FF;
    color: #2563EB;
}

.view-btn:hover {
    background: #2563EB;
    color: #fff;
}

.review-btn {
    background: #F0FDF4;
    color: #16A34A;
}

.review-btn:hover {
    background: #16A34A;
    color: #fff;
}

.event-date {
    flex-shrink: 0;
    padding: 7px 12px;
    background: #F8FAFC;
    border-radius: 8px;
    color: #475569;
    font-size: .85rem;
    font-weight: 500;
}

.activity-item {
    justify-content: flex-start;
}

.activity-dot {
    width: 10px;
    height: 10px;
    flex-shrink: 0;
    background: #2563EB;
    border-radius: 50%;
}

.activity-info {
    flex: 1;
}

@media(max-width: 576px) {
    .card-header,
    .card-content {
        padding-left: 18px;
        padding-right: 18px;
    }

    .event-item,
    .request-item {
        align-items: flex-start;
        flex-direction: column;
    }
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