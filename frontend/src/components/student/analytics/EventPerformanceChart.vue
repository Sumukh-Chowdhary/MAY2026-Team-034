<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const props = defineProps({
  events: {
    type: Array,
    default: () => []
  }
})

const chartData = computed(() => ({
  labels: props.events.map(e => e.name),
  datasets: [
    {
      label: 'Registrations',
      data: props.events.map(e => e.registrations),
      backgroundColor: '#CBD5E1',
      borderRadius: 6,
      maxBarThickness: 32
    },
    {
      label: 'Present',
      data: props.events.map(e => e.present),
      backgroundColor: '#2563EB',
      borderRadius: 6,
      maxBarThickness: 32
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom' } },
  scales: {
    y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: '#E2E8F0' } },
    x: { grid: { display: false } }
  }
}
</script>

<template>
  <div class="analytics-card">
    <div class="card-header">
      <h4>Event Registrations vs Attendance</h4>
      <p>How many registered members actually showed up, per event</p>
    </div>

    <div class="chart-container">
      <Bar v-if="events.length" :data="chartData" :options="chartOptions" />
      <p v-else class="empty-state">No events recorded for this club yet.</p>
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
  height: 320px;
  margin-top: 20px;
}

.empty-state {
  color: #94A3B8;
  text-align: center;
  padding-top: 120px;
}
</style>
