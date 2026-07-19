<script setup>
import { computed } from 'vue'

const props = defineProps({
  ticket: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['view'])

const badgeClass = computed(() => {
  switch (props.ticket.status) {
    case 'Approved':
      return 'bg-success'
    case 'Rejected':
      return 'bg-danger'
    default:
      return 'bg-warning text-dark'
  }
})
</script>

<template>
  <div class="ticket-card">

    <div class="card-header">
      <h5>{{ ticket.subject }}</h5>

      <span
        class="badge"
        :class="badgeClass"
      >
        {{ ticket.status }}
      </span>
    </div>

    <div class="card-body">

      <div class="detail">
        <span class="label">Club</span>
        <span>{{ ticket.club }}</span>
      </div>

      <div class="detail">
        <span class="label">Sent</span>
        <span>{{ ticket.date }}</span>
      </div>

    </div>

    <div class="card-footer">

      <button
    class="btn btn-outline-primary w-100"
    @click="emit('view', ticket)"
    >
    View Ticket
    </button>

    </div>

  </div>
</template>

<style scoped>

.ticket-card{
    background:white;
    border-radius:16px;
    border:1px solid #e5e7eb;
    padding:20px;
    transition:.25s;
    box-shadow:0 2px 8px rgba(0,0,0,.05);
}

.ticket-card:hover{
    transform:translateY(-3px);
    box-shadow:0 10px 22px rgba(0,0,0,.08);
}

.card-header{
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    margin-bottom:18px;
}

.card-header h5{
    margin:0;
    font-size:1.05rem;
    font-weight:700;
}

.card-body{
    display:flex;
    flex-direction:column;
    gap:14px;
    margin-bottom:22px;
}

.detail{
    display:flex;
    justify-content:space-between;
    align-items:center;
}

.label{
    font-weight:600;
    color:#6b7280;
}

.card-footer{
    border-top:1px solid #eef2f7;
    padding-top:18px;
}

.badge{
    font-size:.82rem;
    padding:8px 12px;
}

</style>