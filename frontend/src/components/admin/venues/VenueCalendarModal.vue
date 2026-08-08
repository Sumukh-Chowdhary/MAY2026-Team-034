<script setup>
import { computed } from 'vue'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'

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

const emit = defineEmits(['close'])

const calendarEvents = computed(() => {
  return props.events.map((ev) => {
    const startStr = ev.startDate
      ? ev.startTime
        ? `${ev.startDate}T${ev.startTime}`
        : ev.startDate
      : ''
    const endStr = ev.endDate
      ? ev.endTime
        ? `${ev.endDate}T${ev.endTime}`
        : ev.endDate
      : startStr

    return {
      id: String(ev.id),
      title: `${ev.name || ev.eventName || 'Event'} (${ev.clubName || ev.club || 'Club'})`,
      start: startStr,
      end: endStr,
      extendedProps: {
        eventName: ev.name || ev.eventName || 'Event',
        clubName: ev.clubName || ev.club || 'Club',
        startDate: ev.startDate,
        endDate: ev.endDate,
        startTime: ev.startTime || '09:00',
        endTime: ev.endTime || '17:00',
        description: ev.description
      }
    }
  })
})

const calendarOptions = computed(() => {
  return {
    plugins: [dayGridPlugin, timeGridPlugin],
    initialView: 'dayGridMonth',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
    buttonText: {
      today: 'Today',
      month: 'Month',
      week: 'Week',
      day: 'Day'
    },
    events: calendarEvents.value,
    editable: false,
    selectable: false,
    height: 'auto',
    eventContent: (arg) => {
      const { eventName, clubName, startTime, endTime, startDate, endDate } = arg.event.extendedProps
      return {
        html: `
          <div class="fc-booking-item">
            <div class="fc-booking-title">${eventName}</div>
            <div class="fc-booking-club">${clubName}</div>
            <div class="fc-booking-time">📅 ${startDate || ''} | ⏰ ${startTime} - ${endTime}</div>
          </div>
        `
      }
    }
  }
})
</script>

<template>
  <div class="modal-backdrop" @click.self="emit('close')">
    <div class="modal-dialog-custom modal-lg">
      <div class="modal-header">
        <div>
          <h4 class="fw-bold m-0 text-dark">{{ venue.name }} — Venue Calendar</h4>
          <p class="subtitle text-secondary mb-0">
            📍 {{ venue.location }} • Capacity: {{ venue.capacity }} Seats • Type: {{ venue.type || 'General' }}
          </p>
        </div>
        <button class="close-btn" @click="emit('close')">&times;</button>
      </div>

      <div class="modal-body">
        <!-- Empty State Banner if no bookings -->
        <div v-if="events.length === 0" class="empty-state-banner mb-3">
          <span class="material-symbols-rounded icon-md">event_busy</span>
          <div>
            <h6 class="fw-bold m-0 text-secondary">No Bookings Found</h6>
            <small class="text-muted">There are currently no events or bookings scheduled for this venue.</small>
          </div>
        </div>

        <!-- FullCalendar Display -->
        <div class="calendar-wrapper">
          <FullCalendar :options="calendarOptions" />
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(15, 23, 42, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.modal-dialog-custom {
  background: #ffffff;
  border-radius: 20px;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 28px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.18);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.subtitle {
  font-size: 0.9rem;
  margin-top: 4px;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 28px;
  line-height: 1;
  color: #94a3b8;
  cursor: pointer;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #0f172a;
}

.empty-state-banner {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 20px;
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 14px;
}

.icon-md {
  font-size: 28px;
  color: #64748b;
}

.calendar-wrapper {
  background: #ffffff;
  padding: 12px;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

:deep(.fc) {
  font-family: inherit;
}

:deep(.fc-toolbar-title) {
  font-size: 1.15rem !important;
  font-weight: 700;
  color: #0f172a;
}

:deep(.fc-button-primary) {
  background-color: #2563eb !important;
  border-color: #2563eb !important;
  font-size: 0.85rem !important;
  font-weight: 600 !important;
  border-radius: 8px !important;
  padding: 6px 12px !important;
  box-shadow: none !important;
}

:deep(.fc-button-primary:hover) {
  background-color: #1d4ed8 !important;
  border-color: #1d4ed8 !important;
}

:deep(.fc-button-primary:disabled) {
  background-color: #94a3b8 !important;
  border-color: #94a3b8 !important;
}

:deep(.fc-booking-item) {
  background: #eff6ff;
  border-left: 3px solid #2563eb;
  padding: 4px 6px;
  border-radius: 6px;
  font-size: 0.75rem;
  overflow: hidden;
}

:deep(.fc-booking-title) {
  font-weight: 700;
  color: #1e293b;
}

:deep(.fc-booking-club) {
  font-weight: 600;
  color: #2563eb;
  font-size: 0.7rem;
}

:deep(.fc-booking-time) {
  color: #64748b;
  font-size: 0.68rem;
}
</style>
