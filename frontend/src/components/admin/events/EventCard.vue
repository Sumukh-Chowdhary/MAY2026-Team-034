<template>
  <article class="event-card">

    <div class="event-header">
      <div class="event-icon-circle" :class="iconBgClass">
        <span class="material-symbols-rounded">{{ eventIcon }}</span>
      </div>

      <div class="badge-group">
        <span v-if="event.eventType" class="type-badge">
          {{ event.eventType }}
        </span>
        <span class="status-badge" :class="statusClass">
          {{ eventStatusText }}
        </span>
      </div>
    </div>

    <div class="event-content">
      <span class="club-tag">
        <span class="material-symbols-rounded tag-icon">groups</span>
        {{ event.club }}
      </span>

      <h3>{{ event.name }}</h3>

      <p class="description">
        {{ event.description || 'No description provided.' }}
      </p>
    </div>

    <div class="event-footer">
      <div class="footer-info">
        <span class="date">
          <span class="material-symbols-rounded icon-sm">calendar_month</span>
          {{ event.startDate }}
        </span>
        <span class="venue" v-if="event.venueName || event.venue">
          <span class="material-symbols-rounded icon-sm">location_on</span>
          {{ event.venueName || event.venue }}
        </span>
      </div>

      <RouterLink
        :to="eventTargetUrl"
        class="view-btn"
      >
        View Details
      </RouterLink>
    </div>

  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { getEventStatus } from '@/utils/eventUtils'

const route = useRoute()

const props = defineProps({
  event: {
    type: Object,
    required: true
  }
})

const eventStatusText = computed(() => {
  return getEventStatus(props.event)
})

const statusClass = computed(() => {
  return eventStatusText.value.toLowerCase()
})

const eventIcon = computed(() => {
  if (props.event.icon && props.event.icon.length > 2) return props.event.icon
  const typeOrCat = (props.event.eventType || props.event.category || props.event.club || props.event.name || '').toLowerCase()
  if (typeOrCat.includes('hack') || typeOrCat.includes('code') || typeOrCat.includes('tech')) return 'terminal'
  if (typeOrCat.includes('music') || typeOrCat.includes('concert') || typeOrCat.includes('jam')) return 'music_note'
  if (typeOrCat.includes('sport') || typeOrCat.includes('game') || typeOrCat.includes('soccer')) return 'sports_soccer'
  if (typeOrCat.includes('drama') || typeOrCat.includes('theatre') || typeOrCat.includes('stage') || typeOrCat.includes('act')) return 'theater_comedy'
  if (typeOrCat.includes('photo') || typeOrCat.includes('camera') || typeOrCat.includes('film')) return 'photo_camera'
  if (typeOrCat.includes('ai') || typeOrCat.includes('robot') || typeOrCat.includes('mind')) return 'psychology'
  if (typeOrCat.includes('workshop') || typeOrCat.includes('seminar') || typeOrCat.includes('talk') || typeOrCat.includes('class')) return 'school'
  return 'event'
})

const iconBgClass = computed(() => {
  const icon = eventIcon.value
  if (icon === 'terminal' || icon === 'psychology') return 'bg-tech'
  if (icon === 'music_note') return 'bg-music'
  if (icon === 'sports_soccer') return 'bg-sports'
  if (icon === 'theater_comedy') return 'bg-arts'
  if (icon === 'photo_camera') return 'bg-creative'
  return 'bg-default'
})

const eventTargetUrl = computed(() => {
  const rolePrefix = route.path.startsWith('/admin')
    ? 'admin'
    : route.path.startsWith('/faculty')
    ? 'faculty'
    : 'student'
  return `/${rolePrefix}/events/${props.event.id}`
})
</script>

<style scoped>
.event-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 18px;
  min-height: 330px;
  transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04);
  position: relative;
  overflow: hidden;
}

.event-card:hover {
  transform: translateY(-4px);
  border-color: #3b82f6;
  box-shadow: 0 16px 36px rgba(37, 99, 235, 0.1);
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.event-icon-circle {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.event-icon-circle .material-symbols-rounded {
  font-size: 32px;
}

.bg-tech { background: #eff6ff; color: #2563eb; }
.bg-music { background: #fdf2f8; color: #db2777; }
.bg-sports { background: #ecfdf5; color: #059669; }
.bg-arts { background: #fff7ed; color: #ea580c; }
.bg-creative { background: #f5f3ff; color: #7c3aed; }
.bg-default { background: #eef2ff; color: #4338ca; }

.badge-group {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.type-badge {
  background: #f1f5f9;
  color: #475569;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.status-badge.live {
  background: #dcfce7;
  color: #15803d;
}

.status-badge.scheduled {
  background: #e0f2fe;
  color: #0369a1;
}

.status-badge.completed {
  background: #f1f5f9;
  color: #64748b;
}

.event-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.club-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #eff6ff;
  color: #2563eb;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  width: fit-content;
}

.tag-icon {
  font-size: 1rem;
}

.event-content h3 {
  margin: 4px 0 0;
  color: #0f172a;
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.35;
}

.description {
  margin: 0;
  color: #64748b;
  font-size: 0.9rem;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.event-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding-top: 14px;
  border-top: 1px solid #f1f5f9;
}

.footer-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.date, .venue {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #64748b;
  font-size: 0.85rem;
  font-weight: 500;
}

.icon-sm {
  font-size: 1rem;
  color: #94a3b8;
}

.view-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 12px;
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
  padding: 8px 16px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  white-space: nowrap;
}

.view-btn:hover {
  background: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

@media (max-width: 576px) {
  .event-footer {
    flex-direction: column;
    align-items: stretch;
  }

  .view-btn {
    width: 100%;
    text-align: center;
  }
}
</style>