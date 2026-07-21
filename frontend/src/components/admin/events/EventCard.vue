<template>
  <article class="event-card">

    <div class="event-header">

      <div class="event-image">
        {{ event.emoji }}
      </div>

      <span class="status-badge" :class="event.status.toLowerCase()">
        {{ event.status }}
      </span>

    </div>

    <div class="event-content">

      <span class="club-tag">
        {{ event.club }}
      </span>

      <h3>{{ event.name }}</h3>

      <p class="description">
        {{ event.description }}
      </p>

    </div>

    <div class="event-footer">

      <span class="date">
        📅 {{ event.startDate }}
      </span>

      <RouterLink
        :to="eventTargetUrl"
        class="view-btn"
      >
        View
      </RouterLink>

    </div>

  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const props = defineProps({
  event: {
    type: Object,
    required: true
  }
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

.event-card{

    background:#fff;

    border:1px solid #edf2f7;

    border-radius:18px;

    padding:24px;

    display:flex;

    flex-direction:column;

    justify-content:space-between;

    gap:18px;

    min-height:330px;

    transition:all .28s ease;

    box-shadow:0 8px 24px rgba(15,23,42,.06);

}

.event-card:hover{

    transform:translateY(-6px);

    border-color:#2563eb;

    box-shadow:0 18px 40px rgba(37,99,235,.12);

}

.event-header{

    display:flex;

    justify-content:space-between;

    align-items:center;

}

.event-image{

    width:72px;

    height:72px;

    border-radius:50%;

    display:flex;

    justify-content:center;

    align-items:center;

    background:#eef4ff;

    font-size:38px;

}

.status-badge{

    padding:6px 12px;

    border-radius:999px;

    font-size:13px;

    font-weight:600;

}

.status-badge.live{

    background:#dcfce7;

    color:#16a34a;

}

.status-badge.completed{

    background:#f1f5f9;

    color:#64748b;

}

.club-tag{

    display:inline-block;

    background:#eef4ff;

    color:#2563eb;

    padding:4px 10px;

    border-radius:999px;

    font-size:12px;

    font-weight:600;

    margin-bottom:10px;

}

.event-content h3{

    margin:0 0 12px;

    color:#1f2937;

    font-size:1.35rem;

    font-weight:700;

}

.description{

    margin:0;

    color:#6b7280;

    line-height:1.7;

    min-height:72px;

}

.event-footer{

    display:flex;

    justify-content:space-between;

    align-items:center;

    gap:16px;

}

.date{

    color:#64748b;

    font-size:14px;

    font-weight:500;

}

.view-btn{

    border:none;

    border-radius:10px;

    background:#2563eb;

    color:#fff;

    padding:10px 18px;

    font-weight:600;

    cursor:pointer;

    transition:all .2s ease;

    text-decoration:none;

}

.view-btn:hover{

    background:#1d4ed8;

}

@media (max-width:576px){

.event-footer{

    flex-direction:column;

    align-items:stretch;

}

.view-btn{

    width:100%;

    text-align:center;

}

}

</style>