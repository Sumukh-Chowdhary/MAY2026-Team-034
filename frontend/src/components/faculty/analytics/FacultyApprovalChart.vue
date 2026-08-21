<script setup>
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend
)

const props = defineProps({
  breakdown: {
    type: Object,
    default: () => ({
      labels: ['Pending', 'Approved', 'Changes Requested', 'Rejected'],
      data: [3, 12, 2, 1]
    })
  }
})

const chartData = computed(() => {
  const b = props.breakdown || {}
  return {
    labels: b.labels || ['Pending', 'Approved', 'Changes Requested', 'Rejected'],
    datasets: [
      {
        data: b.data || [0, 0, 0, 0],
        backgroundColor: [
          '#F59E0B',
          '#10B981',
          '#3B82F6',
          '#EF4444'
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
        padding: 14
      }
    }
  }
}
</script>

<template>
  <div class="analytics-card">
    <div class="card-header">
      <div>
        <h4>Approval Requests Breakdown</h4>
        <p>Distribution of incoming requests by workflow state</p>
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
