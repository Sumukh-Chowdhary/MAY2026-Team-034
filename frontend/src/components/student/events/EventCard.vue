<template>
  <article class="event-card">
    <div class="event-header">
      <div class="event-image">{{ event.emoji }}</div>
      <span class="status-badge" :class="(event.status || 'scheduled').toLowerCase()">
        {{ event.status }}
      </span>
    </div>

    <div class="event-content">
      <span class="club-tag">{{ event.club }}</span>
      <h3>{{ event.name }}</h3>
      <p class="description">{{ event.description }}</p>
    </div>

    <div class="event-footer">
      <span class="date">📅 {{ event.startDate }}</span>
      <div class="actions">
        <button class="register-btn" :disabled="isRegistered || isRegistering" @click="onRegister(event)">
          {{ isRegistering ? 'Registering…' : isRegistered ? 'Registered' : 'Register' }}
        </button>
        <RouterLink :to="{ name: 'StudentEventDetail', params: { id: event.id } }" class="view-btn">
          View
        </RouterLink>
      </div>
    </div>
  </article>
</template>

<script setup>
defineProps({
  event: {
    type: Object,
    required: true
  },
  isRegistered: {
    type: Boolean,
    default: false
  },
  isRegistering: {
    type: Boolean,
    default: false
  },
  onRegister: {
    type: Function,
    required: true
  }
})
</script>

<style scoped>
.event-card {
  background: #fff;
  border: 1px solid #edf2f7;
  border-radius: 18px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 18px;
  min-height: 330px;
  transition: all 0.28s ease;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.event-card:hover {
  transform: translateY(-6px);
  border-color: #2563eb;
  box-shadow: 0 18px 40px rgba(37, 99, 235, 0.12);
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.event-image {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #eef4ff;
  font-size: 38px;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
}

.status-badge.live,
.status-badge.scheduled {
  background: #dcfce7;
  color: #16a34a;
}

.status-badge.completed {
  background: #f1f5f9;
  color: #64748b;
}

.club-tag {
  display: inline-block;
  background: #eef4ff;
  color: #2563eb;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 10px;
}

.event-content h3 {
  margin: 0 0 12px;
  color: #1f2937;
  font-size: 1.35rem;
  font-weight: 700;
}

.description {
  margin: 0;
  color: #6b7280;
  line-height: 1.7;
  min-height: 72px;
}

.event-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.date {
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
}

.actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.register-btn,
.view-btn {
  border: none;
  border-radius: 10px;
  padding: 10px 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.register-btn {
  background: #16a34a;
  color: #fff;
}

.register-btn:disabled {
  opacity: 0.7;
  cursor: default;
}

.view-btn {
  background: #2563eb;
  color: #fff;
}

.view-btn:hover {
  background: #1d4ed8;
}

@media (max-width: 576px) {
  .event-footer {
    flex-direction: column;
    align-items: stretch;
  }

  .actions {
    flex-direction: column;
  }

  .register-btn,
  .view-btn {
    width: 100%;
    text-align: center;
  }
}
</style>