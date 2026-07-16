<script setup>
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js'

import { userDistribution } from '@/data/analytics.js'

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend
)

const chartData = computed(() => ({
  labels: userDistribution.labels,
  datasets: [
    {
      data: userDistribution.data,
      backgroundColor: [
        '#2563EB',
        '#60A5FA',
        '#CBD5E1'
      ],
      borderWidth: 0
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    }
  }
}
</script>

<template>
  <div class="analytics-card">
    <div class="card-header">
      <div>
        <h4>User Distribution</h4>
        <p>Overview of users by role</p>
      </div>
    </div>

    <div class="chart-container">
      <Doughnut
        :data="chartData"
        :options="chartOptions"
      />
    </div>
  </div>
</template>

<style scoped>
.analytics-card {
  height: 100%;
  background: #ffffff;
  border-radius: 18px;
  padding: 24px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
}

.card-header h4 {
  margin: 0;
  color: #1E293B;
  font-size: 1.15rem;
  font-weight: 700;
}

.card-header p {
  margin: 6px 0 0;
  color: #64748B;
  font-size: 0.9rem;
}

.chart-container {
  position: relative;
  height: 280px;
  margin-top: 20px;
}
</style>