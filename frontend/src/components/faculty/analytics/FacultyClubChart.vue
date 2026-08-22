<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

const props = defineProps({
  analytics: {
    type: Object,
    default: () => ({
      labels: ['AI Club', 'Robotics Club', 'Coding Club'],
      members: [48, 32, 40],
      events: [5, 3, 4]
    })
  }
})

const chartData = computed(() => {
  const data = props.analytics || {}
  return {
    labels: data.labels || [],
    datasets: [
      {
        label: 'Total Members',
        data: data.members || [],
        backgroundColor: '#2563EB',
        borderRadius: 8,
        barThickness: 24
      },
      {
        label: 'Events Conducted',
        data: data.events || [],
        backgroundColor: '#10B981',
        borderRadius: 8,
        barThickness: 24
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
      labels: {
        font: {
          family: 'Inter, sans-serif',
          weight: 600
        },
        padding: 12
      }
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
    <div class="card-header">
      <h4>Supervised Club Performance</h4>
      <p>Member strength & events conducted across your assigned clubs</p>
    </div>

    <div class="chart-container">
      <Bar
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
