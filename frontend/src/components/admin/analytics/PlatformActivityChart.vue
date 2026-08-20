<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

import { platformActivity as defaultPlatformActivity } from '@/data/analytics.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps({
  activity: {
    type: Object,
    default: () => defaultPlatformActivity
  }
})

const chartData = computed(() => {
  const act = props.activity || defaultPlatformActivity
  return {
    labels: act.labels || [],
    datasets: [
      {
        label: 'Registrations & Participations',
        data: act.data || [],
        borderColor: '#2563EB',
        backgroundColor: 'rgba(37, 99, 235, 0.12)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: '#2563EB',
        pointHoverRadius: 6
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    intersect: false,
    mode: 'index'
  },
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        precision: 0
      },
      grid: {
        color: '#E2E8F0'
      }
    },
    x: {
      grid: {
        display: false
      }
    }
  }
}
</script>

<template>
  <div class="analytics-card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <div>
        <h4>Platform Engagement Trend</h4>
        <p>Monthly event registrations and active platform participation</p>
      </div>
      <span class="badge bg-primary-subtle text-primary border px-3 py-1 fw-semibold">2026 Academic Year</span>
    </div>

    <div class="chart-container">
      <Line
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
  height: 300px;
  margin-top: 20px;
}
</style>