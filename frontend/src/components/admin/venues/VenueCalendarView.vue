<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  venue: {
    type: Object,
    required: true
  },
  events: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['back'])

// Base reference date (Current month = Aug 2026 by default or current date)
const baseDate = ref(new Date(2026, 7, 1)) // August 2026

// Generate 3 consecutive months starting from baseDate
const availableMonths = computed(() => {
  const months = []
  for (let i = 0; i < 3; i++) {
    const d = new Date(baseDate.value.getFullYear(), baseDate.value.getMonth() + i, 1)
    const label = d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    months.push({
      year: d.getFullYear(),
      month: d.getMonth(),
      label
    })
  }
  return months
})

// Active selected month index (0: Current Month, 1: Next Month, 2: 3rd Month)
const selectedMonthIdx = ref(0)
const viewMode = ref('month') // 'month' | 'week' | 'day'
const selectedDayDate = ref(new Date(2026, 7, 1))

// Selected month details
const activeMonthObj = computed(() => availableMonths.value[selectedMonthIdx.value] || availableMonths.value[0])

// Days of week header
const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

// Days matrix for Month View
const monthDaysGrid = computed(() => {
  const { year, month } = activeMonthObj.value
  const firstDayIndex = new Date(year, month, 1).getDay()
  const totalDaysInMonth = new Date(year, month + 1, 0).getDate()
  const prevMonthDays = new Date(year, month, 0).getDate()

  const grid = []

  // Fill padding days from previous month
  for (let i = firstDayIndex - 1; i >= 0; i--) {
    const dayNum = prevMonthDays - i
    const dateStr = formatDateStr(year, month - 1, dayNum)
    grid.push({
      dayNum,
      dateStr,
      isCurrentMonth: false
    })
  }

  // Current month days
  for (let d = 1; d <= totalDaysInMonth; d++) {
    const dateStr = formatDateStr(year, month, d)
    grid.push({
      dayNum: d,
      dateStr,
      isCurrentMonth: true
    })
  }

  // Fill trailing days to complete grid
  const remaining = 42 - grid.length
  for (let j = 1; j <= remaining; j++) {
    const dateStr = formatDateStr(year, month + 1, j)
    grid.push({
      dayNum: j,
      dateStr,
      isCurrentMonth: false
    })
  }

  return grid
})

function formatDateStr(year, month, day) {
  const d = new Date(year, month, day)
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

// Active non-completed events (exclude completed/closed events)
const activeEvents = computed(() => {
  return props.events.filter((ev) => {
    const status = String(ev.status || '').toUpperCase()
    return status !== 'COMPLETED' && status !== 'CLOSED'
  })
})

// Map active events to dates across their entire multi-day range
const eventsByDate = computed(() => {
  const map = {}
  activeEvents.value.forEach((ev) => {
    if (!ev.startDate) return
    const start = new Date(ev.startDate + 'T00:00:00')
    const end = ev.endDate ? new Date(ev.endDate + 'T00:00:00') : new Date(start)

    const curr = new Date(start)
    while (curr <= end) {
      const yyyy = curr.getFullYear()
      const mm = String(curr.getMonth() + 1).padStart(2, '0')
      const dd = String(curr.getDate()).padStart(2, '0')
      const dateKey = `${yyyy}-${mm}-${dd}`

      if (!map[dateKey]) map[dateKey] = []
      if (!map[dateKey].some(item => item.id === ev.id)) {
        map[dateKey].push(ev)
      }

      curr.setDate(curr.getDate() + 1)
    }
  })
  return map
})

function isGeneralEvent(ev) {
  if (!ev) return false
  const t = (ev.eventType || ev.organizerType || '').toUpperCase()
  return t === 'GENERAL_EVENT' || t === 'GENERAL'
}

// Events for selected month
const currentMonthEvents = computed(() => {
  const { year, month } = activeMonthObj.value
  const monthPrefix = `${year}-${String(month + 1).padStart(2, '0')}`
  const monthStart = `${monthPrefix}-01`
  const monthEnd = `${monthPrefix}-31`

  return activeEvents.value.filter((ev) => {
    const s = ev.startDate || ''
    const e = ev.endDate || s
    return s <= monthEnd && e >= monthStart
  })
})

// Week view days
const weekDays = computed(() => {
  const startOfWeek = new Date(selectedDayDate.value)
  startOfWeek.setDate(startOfWeek.getDate() - startOfWeek.getDay())
  const days = []
  for (let i = 0; i < 7; i++) {
    const d = new Date(startOfWeek)
    d.setDate(d.getDate() + i)
    const dateStr = formatDateStr(d.getFullYear(), d.getMonth(), d.getDate())
    days.push({
      dateStr,
      dayName: daysOfWeek[i],
      dayNum: d.getDate(),
      fullDate: d
    })
  }
  return days
})

// Day view events
const dayViewEvents = computed(() => {
  const dateStr = formatDateStr(
    selectedDayDate.value.getFullYear(),
    selectedDayDate.value.getMonth(),
    selectedDayDate.value.getDate()
  )
  return eventsByDate.value[dateStr] || []
})

function selectMonth(index) {
  selectedMonthIdx.value = index
  const m = availableMonths.value[index]
  selectedDayDate.value = new Date(m.year, m.month, 1)
}

function selectDayCell(cell) {
  const parts = cell.dateStr.split('-')
  selectedDayDate.value = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]))
  viewMode.value = 'day'
}

function prevPeriod() {
  if (selectedMonthIdx.value > 0) {
    selectedMonthIdx.value--
    const m = availableMonths.value[selectedMonthIdx.value]
    selectedDayDate.value = new Date(m.year, m.month, 1)
  }
}

function nextPeriod() {
  if (selectedMonthIdx.value < 2) {
    selectedMonthIdx.value++
    const m = availableMonths.value[selectedMonthIdx.value]
    selectedDayDate.value = new Date(m.year, m.month, 1)
  }
}

function resetToday() {
  selectedMonthIdx.value = 0
  const m = availableMonths.value[0]
  selectedDayDate.value = new Date(m.year, m.month, 1)
}
</script>

<template>
  <div class="full-calendar-view">
    <!-- Top Action Header -->
    <div class="header-bar">
      <button class="back-btn" @click="emit('back')">
        <span class="material-symbols-rounded icon-sm">arrow_back</span>
        Back to Venues
      </button>

      <div class="venue-info-header">
        <h2>{{ venue.name }} — Schedule Calendar</h2>
        <p class="subtitle">
          📍 {{ venue.location }} • Capacity: {{ venue.capacity }} Seats • Type: {{ venue.type || 'General' }}
        </p>
      </div>
    </div>

    <!-- 3-Month Selector & View Mode Toolbar -->
    <div class="calendar-controls-card">
      <div class="month-tabs-bar">
        <span class="label-text">Available Months:</span>
        <button
          v-for="(m, idx) in availableMonths"
          :key="m.label"
          class="month-tab-btn"
          :class="{ active: selectedMonthIdx === idx }"
          @click="selectMonth(idx)"
        >
          <span class="material-symbols-rounded icon-xs">calendar_month</span>
          {{ m.label }}
        </button>
      </div>

      <div class="view-mode-bar">
        <div class="nav-btn-group">
          <button class="nav-icon-btn" :disabled="selectedMonthIdx === 0" @click="prevPeriod" title="Previous Month">
            <span class="material-symbols-rounded">chevron_left</span>
          </button>
          <button class="today-btn" @click="resetToday">Today</button>
          <button class="nav-icon-btn" :disabled="selectedMonthIdx === 2" @click="nextPeriod" title="Next Month">
            <span class="material-symbols-rounded">chevron_right</span>
          </button>
        </div>

        <div class="mode-btn-group">
          <button
            class="mode-btn"
            :class="{ active: viewMode === 'month' }"
            @click="viewMode = 'month'"
          >
            Month
          </button>
          <button
            class="mode-btn"
            :class="{ active: viewMode === 'week' }"
            @click="viewMode = 'week'"
          >
            Week
          </button>
          <button
            class="mode-btn"
            :class="{ active: viewMode === 'day' }"
            @click="viewMode = 'day'"
          >
            Day
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State Notification if no bookings exist for current venue -->
    <div v-if="events.length === 0" class="empty-state-banner mb-4">
      <span class="material-symbols-rounded icon-md">event_busy</span>
      <div>
        <h6 class="fw-bold m-0 text-dark">No Bookings Found</h6>
        <p class="text-secondary m-0">There are currently no events or bookings scheduled for this venue.</p>
      </div>
    </div>

    <!-- Event Type Legend (STEP 9) -->
    <div class="d-flex align-items-center gap-3 mb-3 px-3 py-2 bg-light rounded-3 border text-xs fw-bold">
      <span class="d-flex align-items-center gap-1 text-primary">
        <span class="legend-badge blue-pill"></span> 🟦 Club Events
      </span>
      <span class="d-flex align-items-center gap-1 text-purple">
        <span class="legend-badge purple-pill"></span> 🟪 General College Events
      </span>
    </div>

    <!-- MONTH VIEW -->
    <div v-if="viewMode === 'month'" class="calendar-board-card">
      <div class="calendar-header-grid">
        <div v-for="d in daysOfWeek" :key="d" class="day-name-cell">{{ d }}</div>
      </div>

      <div class="calendar-days-grid">
        <div
          v-for="(cell, idx) in monthDaysGrid"
          :key="idx"
          class="day-cell"
          :class="{
            'other-month': !cell.isCurrentMonth,
            'has-events': eventsByDate[cell.dateStr]?.length
          }"
          @click="selectDayCell(cell)"
        >
          <div class="day-number">{{ cell.dayNum }}</div>

          <div v-if="eventsByDate[cell.dateStr]?.length" class="events-stack">
            <div
              v-for="ev in eventsByDate[cell.dateStr]"
              :key="ev.id"
              class="event-chip"
              :class="isGeneralEvent(ev) ? 'general-event-chip' : 'club-event-chip'"
            >
              <div class="event-title">{{ ev.name || ev.eventName }}</div>
              <div class="event-club">{{ isGeneralEvent(ev) ? '🎓 General Event' : (ev.clubName || ev.club || 'Club Event') }}</div>
              <div class="event-time">⏰ {{ ev.startTime || '09:00' }} - {{ ev.endTime || '17:00' }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- WEEK VIEW -->
    <div v-else-if="viewMode === 'week'" class="calendar-board-card">
      <div class="week-grid">
        <div v-for="wDay in weekDays" :key="wDay.dateStr" class="week-column">
          <div class="week-col-header">
            <span class="w-name">{{ wDay.dayName }}</span>
            <span class="w-num">{{ wDay.dayNum }}</span>
          </div>

          <div class="week-col-body">
            <div
              v-for="ev in (eventsByDate[wDay.dateStr] || [])"
              :key="ev.id"
              class="event-chip-large"
            >
              <h6 class="fw-bold m-0 text-dark">{{ ev.name || ev.eventName }}</h6>
              <span class="badge bg-primary text-white my-1">{{ ev.clubName || ev.club }}</span>
              <div class="small text-muted">⏰ {{ ev.startTime || '09:00' }} - {{ ev.endTime || '17:00' }}</div>
            </div>

            <div v-if="!(eventsByDate[wDay.dateStr] || []).length" class="no-events-col">
              No events
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- DAY VIEW -->
    <div v-else-if="viewMode === 'day'" class="calendar-board-card">
      <div class="day-agenda-header">
        <h4 class="fw-bold m-0 text-dark">
          Schedule for {{ selectedDayDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }) }}
        </h4>
      </div>

      <div v-if="dayViewEvents.length" class="day-events-list">
        <div v-for="ev in dayViewEvents" :key="ev.id" class="agenda-item-card">
          <div class="agenda-time">
            <span class="material-symbols-rounded">schedule</span>
            {{ ev.startTime || '09:00' }} - {{ ev.endTime || '17:00' }}
          </div>
          <div class="agenda-details">
            <h5 class="fw-bold m-0 text-dark">{{ ev.name || ev.eventName }}</h5>
            <span class="badge bg-light text-primary border my-1">{{ ev.clubName || ev.club }}</span>
            <p v-if="ev.description" class="text-secondary small m-0">{{ ev.description }}</p>
          </div>
          <div class="agenda-status">
            <span class="status-badge available">Booked</span>
          </div>
        </div>
      </div>

      <div v-else class="empty-day-state">
        <span class="material-symbols-rounded empty-icon">event_available</span>
        <h5>No Bookings Scheduled</h5>
        <p class="text-secondary">This venue is completely free on this date.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.full-calendar-view {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
}

.header-bar {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  padding: 20px 24px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04);
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  padding: 10px 18px;
  border-radius: 12px;
  color: #1e293b;
  font-weight: 700;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  cursor: pointer;
  white-space: nowrap;
}

.back-btn:hover {
  background: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.venue-info-header h2 {
  margin: 0;
  color: #0f172a;
  font-size: 1.4rem;
  font-weight: 800;
}

.subtitle {
  margin: 2px 0 0;
  color: #64748b;
  font-size: 0.9rem;
}

.calendar-controls-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 16px 24px;
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-shadow: 0 4px 18px rgba(15, 23, 42, 0.03);
}

.month-tabs-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.label-text {
  font-weight: 700;
  color: #475569;
  font-size: 0.9rem;
}

.month-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid #cbd5e1;
  background: #f8fafc;
  color: #334155;
  padding: 8px 16px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.88rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.month-tab-btn:hover {
  background: #eff6ff;
  border-color: #93c5fd;
  color: #2563eb;
}

.month-tab-btn.active {
  background: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

.view-mode-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.nav-btn-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-icon-btn {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #334155;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-icon-btn:hover {
  background: #2563eb;
  color: white;
  border-color: #2563eb;
}

.today-btn {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #2563eb;
  padding: 6px 14px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
}

.today-btn:hover {
  background: #2563eb;
  color: white;
}

.mode-btn-group {
  display: flex;
  background: #f1f5f9;
  padding: 4px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.mode-btn {
  border: none;
  background: transparent;
  padding: 6px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 700;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-btn.active {
  background: #ffffff;
  color: #2563eb;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.empty-state-banner {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 20px;
  background: #ffffff;
  border: 1px dashed #cbd5e1;
  border-radius: 16px;
}

.icon-md {
  font-size: 28px;
  color: #64748b;
}

.calendar-board-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.05);
}

.calendar-header-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  font-weight: 800;
  color: #475569;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 12px;
}

.calendar-days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 10px;
}

.day-cell {
  min-height: 110px;
  background: #f8fafc;
  border: 1px solid #edf2f7;
  border-radius: 12px;
  padding: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
}

.day-cell:hover {
  border-color: #3b82f6;
  background: #ffffff;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08);
}

.day-cell.other-month {
  opacity: 0.45;
  background: #f1f5f9;
}

.day-number {
  font-weight: 800;
  font-size: 0.9rem;
  color: #334155;
  margin-bottom: 6px;
}

.events-stack {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.legend-badge {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.legend-badge.blue-pill {
  background: #2563eb;
}

.legend-badge.purple-pill {
  background: #8b5cf6;
}

.text-purple {
  color: #7c3aed;
}

.event-chip.club-event-chip {
  background: #eff6ff;
  border-left: 3px solid #2563eb;
  color: #1e3a8a;
}

.event-chip.general-event-chip {
  background: #f5f3ff;
  border-left: 3px solid #8b5cf6;
  color: #5b21b6;
}

.event-chip {
  padding: 4px 6px;
  border-radius: 6px;
  font-size: 0.72rem;
}

.event-title {
  font-weight: 700;
  color: #1e293b;
}

.event-club {
  font-weight: 600;
  color: #2563eb;
  font-size: 0.68rem;
}

.event-time {
  color: #64748b;
  font-size: 0.65rem;
}

/* Week View */
.week-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 12px;
}

.week-column {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 12px;
  min-height: 400px;
}

.week-col-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 10px;
  border-bottom: 1px solid #cbd5e1;
  margin-bottom: 12px;
}

.w-name {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
}

.w-num {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
}

.event-chip-large {
  background: #ffffff;
  border: 1px solid #bfdbfe;
  border-left: 4px solid #2563eb;
  padding: 10px;
  border-radius: 10px;
  margin-bottom: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.no-events-col {
  text-align: center;
  color: #94a3b8;
  font-size: 0.8rem;
  padding-top: 20px;
}

/* Day View */
.day-agenda-header {
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 20px;
}

.day-events-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.agenda-item-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-left: 5px solid #2563eb;
  padding: 16px 20px;
  border-radius: 14px;
}

.agenda-time {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 700;
  color: #2563eb;
  font-size: 0.95rem;
  min-width: 160px;
}

.agenda-details {
  flex: 1;
}

.empty-day-state {
  text-align: center;
  padding: 50px 20px;
  color: #94a3b8;
}

.empty-day-state .empty-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.icon-xs {
  font-size: 1rem;
}

.icon-sm {
  font-size: 1.1rem;
}

.status-badge.available {
  background: #dcfce7;
  color: #15803d;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
}
</style>
