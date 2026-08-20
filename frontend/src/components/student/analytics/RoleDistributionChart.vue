<script setup>
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  roles: {
    type: Array,
    default: () => []
  }
})

const palette = ['#2563EB', '#60A5FA', '#A78BFA', '#34D399', '#FBBF24', '#F87171']

const chartData = computed(() => ({
  labels: props.roles.map(r => r.role),
  datasets: [
    {
      data: props.roles.map(r => r.count),
      backgroundColor: props.roles.map((_, i) => palette[i % palette.length]),
      borderWidth: 0
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom' } }
}
</script>

<template>
  <div class="analytics-card">
    <div class="card-header">
      <h4>Role Distribution</h4>
      <p>Active members by role in the club</p>
    </div>

    <div class="chart-container">
      <Doughnut v-if="roles.length" :data="chartData" :options="chartOptions" />
      <p v-else class="empty-state">No active members yet.</p>
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

.empty-state {
  color: #94A3B8;
  text-align: center;
  padding-top: 100px;
}
</style>
