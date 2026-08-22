<script setup>
defineProps({
  show: {
    type: Boolean,
    default: false
  },
  eventName: {
    type: String,
    default: ''
  },
  conflicts: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['confirm', 'cancel'])

function formatWhen(item) {
  if (!item.startDate) return ''
  const datePart = item.endDate && item.endDate !== item.startDate
    ? `${item.startDate} → ${item.endDate}`
    : item.startDate

  const timePart = item.startTime
    ? ` · ${item.startTime}${item.endTime ? ' - ' + item.endTime : ''}`
    : ''

  return datePart + timePart
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="conflict-backdrop" @click.self="emit('cancel')">
      <div class="conflict-box">
        <div class="conflict-icon">
          <i class="bi bi-exclamation-triangle-fill"></i>
        </div>

        <h4>Schedule Clash Detected</h4>
        <p class="subtitle">
          <strong>{{ eventName }}</strong> overlaps in time with {{ conflicts.length > 1 ? 'events' : 'an event' }}
          you're already registered for. You can still register for both, but you may not be able to attend everything.
        </p>

        <ul class="conflict-list">
          <li v-for="item in conflicts" :key="item.eventId">
            <div class="conflict-name">{{ item.name }}</div>
            <div class="conflict-meta">
              <span class="club-badge">{{ item.clubName }}</span>
              <span class="when">{{ formatWhen(item) }}</span>
            </div>
          </li>
        </ul>

        <div class="conflict-actions">
          <button class="btn btn-outline-secondary" @click="emit('cancel')">Cancel</button>
          <button class="btn btn-warning" @click="emit('confirm')">Register Anyway</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.conflict-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1080;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.conflict-box {
  width: 100%;
  max-width: 480px;
  background: #ffffff;
  border-radius: 20px;
  padding: 28px;
  text-align: center;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
}

.conflict-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #FFFBEB;
  color: #D97706;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  font-size: 1.6rem;
}

.conflict-box h4 {
  font-weight: 700;
  color: #1E293B;
  margin-bottom: 8px;
}

.subtitle {
  color: #64748B;
  font-size: 0.92rem;
  margin-bottom: 18px;
}

.conflict-list {
  list-style: none;
  padding: 0;
  margin: 0 0 20px;
  text-align: left;
  max-height: 220px;
  overflow-y: auto;
}

.conflict-list li {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 10px;
}

.conflict-name {
  font-weight: 600;
  color: #1E293B;
  font-size: 0.95rem;
}

.conflict-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
  flex-wrap: wrap;
}

.club-badge {
  background: #EFF6FF;
  color: #2563EB;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
}

.when {
  font-size: 0.8rem;
  color: #64748B;
}

.conflict-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.conflict-actions .btn {
  border-radius: 10px;
  padding: 8px 18px;
  font-weight: 600;
}
</style>
