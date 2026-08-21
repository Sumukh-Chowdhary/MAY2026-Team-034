<script setup>
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js'

import { userDistribution as defaultUserDistribution } from '@/data/analytics.js'

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend
)

const props = defineProps({
  distribution: {
    type: Object,
    default: () => defaultUserDistribution
  }
})

const chartData = computed(() => {
  const dist = props.distribution || defaultUserDistribution
  return {
    labels: dist.labels || ['Students', 'Faculty', 'Admins'],
    datasets: [
      {
        data: dist.data || [100, 21, 2],
        backgroundColor: [
          '#2563EB',
          '#10B981',
          '#F59E0B'
        ],
        borderWidth: 0
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        font: {
          family: 'Inter, sans-serif',
          weight: 600
        },
        padding: 16
      }
    }
  }
}
</script>

<template>
  <div class="analytics-card">
    <div class="card-header">
      <div>
        <h4>User Distribution</h4>
        <p>Overview of campus community by role</p>
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