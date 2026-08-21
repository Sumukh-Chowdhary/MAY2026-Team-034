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
  growth: {
    type: Array,
    default: () => []
  }
})

const chartData = computed(() => ({
  labels: props.growth.map(g => g.month),
  datasets: [
    {
      label: 'Total Members',
      data: props.growth.map(g => g.totalMembers),
      borderColor: '#2563EB',
      backgroundColor: 'rgba(37, 99, 235, 0.1)',
      fill: true,
      tension: 0.4,
      pointRadius: 4,
      pointHoverRadius: 6
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { intersect: false, mode: 'index' },
  plugins: { legend: { display: false } },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { precision: 0 },
      grid: { color: '#E2E8F0' }
    },
    x: { grid: { display: false } }
  }
}
</script>

<template>
  <div class="analytics-card">
    <div class="card-header">
      <h4>Membership Growth</h4>
      <p>Cumulative club membership over time</p>
    </div>

    <div class="chart-container">
      <Line v-if="growth.length" :data="chartData" :options="chartOptions" />
      <p v-else class="empty-state">No membership data yet.</p>
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

.empty-state {
  color: #94A3B8;
  text-align: center;
  padding-top: 100px;
}
</style>
