<script setup>
import AdminLayout from '../../layouts/AdminLayout.vue'

import StatCard from '@/components/analytics/StatCard.vue'
import UserDistributionChart from '@/components/analytics/UserDistributionChart.vue'
import ClubMembershipChart from '@/components/analytics/ClubMembershipChart.vue'
import PlatformActivityChart from '@/components/analytics/PlatformActivityChart.vue'

import { dashboardStats } from '@/data/analytics.js'
</script>

<template>
  <AdminLayout>
    <section class="dashboard-page">

      <div class="dashboard-header">
        <div>
          <h2>Admin Dashboard</h2>
          <p>
            Monitor platform activity, users, clubs, and engagement.
          </p>
        </div>
      </div>

      <!-- Summary Statistics -->
      <div class="row g-4">
        <div
          v-for="stat in dashboardStats"
          :key="stat.label"
          class="col-12 col-sm-6 col-xl-3"
        >
          <StatCard
            :label="stat.label"
            :value="stat.value"
          />
        </div>
      </div>

      <!-- Main Analytics -->
      <div class="row g-4 mt-1">
        <div class="col-12 col-xl-8">
          <PlatformActivityChart />
        </div>

        <div class="col-12 col-xl-4">
          <UserDistributionChart />
        </div>
      </div>

      <!-- Club Analytics -->
      <div class="row g-4 mt-1">
        <div class="col-12">
          <ClubMembershipChart />
        </div>
      </div>

    </section>
  </AdminLayout>
</template>

<style scoped>
.dashboard-page {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.dashboard-header h2 {
  margin: 0;
  color: #1E293B;
  font-size: 1.75rem;
  font-weight: 700;
}

.dashboard-header p {
  margin: 7px 0 0;
  color: #64748B;
  font-size: 0.95rem;
}

@media (max-width: 768px) {
  .dashboard-header {
    align-items: flex-start;
  }

  .dashboard-header h2 {
    font-size: 1.5rem;
  }
}
</style>