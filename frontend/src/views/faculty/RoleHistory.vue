<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import FacultyLayout from '@/layouts/FacultyLayout.vue'

const router = useRouter()

// Filter states
const searchQuery = ref('')
const categoryFilter = ref('ALL') // 'ALL' | 'CLUB' | 'GENERAL_EVENT'
const yearFilter = ref('ALL')     // 'ALL' | '2026' | '2025' | '2024'

// Historical Records Dataset
const roleHistory = ref([
  {
    id: 101,
    roleTitle: 'Faculty Coordinator',
    assignment: 'AI & Coding Club',
    category: 'Club',
    startDate: '2025-08',
    endDate: '2026-06',
    status: 'Completed',
    duration: '10 Months'
  },
  {
    id: 102,
    roleTitle: 'Faculty Event Coordinator',
    assignment: 'Orientation 2026',
    category: 'General Event',
    startDate: '2026-08',
    endDate: '2026-08',
    status: 'Completed',
    duration: '1 Week'
  },
  {
    id: 103,
    roleTitle: 'Faculty Coordinator',
    assignment: 'Robotics Society',
    category: 'Club',
    startDate: '2024-06',
    endDate: '2025-05',
    status: 'Completed',
    duration: '1 Year'
  },
  {
    id: 104,
    roleTitle: 'Faculty Event Coordinator',
    assignment: 'Annual Placement Drive 2025',
    category: 'General Event',
    startDate: '2025-03',
    endDate: '2025-03',
    status: 'Completed',
    duration: '2 Weeks'
  },
  {
    id: 105,
    roleTitle: 'Faculty Event Coordinator',
    assignment: 'Blood Donation Camp',
    category: 'General Event',
    startDate: '2024-10',
    endDate: '2024-10',
    status: 'Completed',
    duration: '2 Days'
  }
])

const filteredHistory = computed(() => {
  let list = roleHistory.value
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter(h => (h.roleTitle || h.assignment || '').toLowerCase().includes(q))
  }
  if (categoryFilter.value === 'CLUB') {
    list = list.filter(h => h.category === 'Club')
  } else if (categoryFilter.value === 'GENERAL_EVENT') {
    list = list.filter(h => h.category === 'General Event')
  }
  if (yearFilter.value !== 'ALL') {
    list = list.filter(h => h.startDate.startsWith(yearFilter.value))
  }
  return list
})

function goBackToResponsibilities() {
  router.push('/faculty/roles')
}
</script>

<template>
  <FacultyLayout>
    <section class="role-history-page">
      <!-- Back Link & Header -->
      <div class="mb-4">
        <button class="btn btn-sm btn-link text-decoration-none p-0 text-muted d-inline-flex align-items-center gap-1 mb-2 fw-semibold" @click="goBackToResponsibilities">
          <span class="material-symbols-rounded icon-sm">arrow_back</span>
          Back to Responsibilities
        </button>
        <h2 class="fw-bold text-dark m-0">Faculty Role History</h2>
        <p class="text-secondary text-sm m-0 mt-1">A complete historical record of every faculty coordination role and institutional event assignment held.</p>
      </div>

      <!-- Simple History Filter Toolbar -->
      <div class="card border-0 rounded-4 shadow-sm p-3 mb-4">
        <div class="row g-3 align-items-center">
          <div class="col-12 col-md-5">
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted">
                <span class="material-symbols-rounded icon-sm">search</span>
              </span>
              <input
                v-model="searchQuery"
                type="text"
                class="form-control border-start-0 ps-0"
                placeholder="Search history..."
              />
            </div>
          </div>

          <div class="col-6 col-md-3">
            <select v-model="categoryFilter" class="form-select text-sm font-semibold">
              <option value="ALL">All Categories</option>
              <option value="CLUB">Club Coordination</option>
              <option value="GENERAL_EVENT">General Event</option>
            </select>
          </div>

          <div class="col-6 col-md-4">
            <select v-model="yearFilter" class="form-select text-sm font-semibold">
              <option value="ALL">All Years</option>
              <option value="2026">2026</option>
              <option value="2025">2025</option>
              <option value="2024">2024</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Historical Table -->
      <div v-if="filteredHistory.length === 0" class="card p-5 text-center text-muted border-0 rounded-4 shadow-sm">
        No historical records match your filter criteria.
      </div>

      <div v-else class="table-responsive bg-white rounded-4 shadow-sm border p-3">
        <table class="table align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th>Role</th>
              <th>Assignment</th>
              <th>Category</th>
              <th>Start Date</th>
              <th>End Date</th>
              <th>Status</th>
              <th>Duration</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredHistory" :key="item.id">
              <td class="fw-bold text-dark">{{ item.roleTitle }}</td>
              <td class="fw-semibold text-primary">{{ item.assignment }}</td>
              <td>
                <span class="badge" :class="item.category === 'Club' ? 'bg-primary-subtle text-primary' : 'bg-purple-subtle text-purple'">
                  {{ item.category }}
                </span>
              </td>
              <td>{{ item.startDate }}</td>
              <td>{{ item.endDate }}</td>
              <td>
                <span class="badge bg-success-subtle text-success border">
                  {{ item.status }}
                </span>
              </td>
              <td class="fw-semibold text-secondary">{{ item.duration }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </FacultyLayout>
</template>

<style scoped>
.role-history-page {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
}

.bg-purple-subtle {
  background-color: #f3e8ff !important;
}

.text-purple {
  color: #7e22ce !important;
}
</style>
