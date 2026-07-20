<script setup>
import { computed } from 'vue'

const props = defineProps({
  request: {
    type: Object,
    required: true
  }
})

const badgeClass = computed(() => {
  switch (props.request.status) {
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
  <div class="request-card">

    <div class="card-header">
      <div>
        <h5>{{ request.name }}</h5>
        <small>{{ request.subject }}</small>
      </div>

      <span
        class="badge"
        :class="badgeClass"
      >
        {{ request.status }}
      </span>
    </div>

    <div class="card-body">

      <div class="detail">
        <span class="label">Club</span>
        <span>{{ request.club }}</span>
      </div>

      <div class="detail">
        <span class="label">Submitted</span>
        <span>{{ request.date }}</span>
      </div>

    </div>

    <div class="card-footer">
      <button class="btn btn-primary w-100">
        View Request
      </button>
    </div>

  </div>
</template>

<style scoped>

.request-card{
    background:#fff;
    border:1px solid #e5e7eb;
    border-radius:16px;
    padding:20px;
    transition:.25s;
    box-shadow:0 2px 8px rgba(0,0,0,.05);
}

.request-card:hover{
    transform:translateY(-3px);
    box-shadow:0 10px 22px rgba(0,0,0,.08);
}

.card-header{
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    margin-bottom:20px;
}

.card-header h5{
    margin:0;
    font-weight:700;
}

.card-header small{
    color:#6b7280;
}

.card-body{
    display:flex;
    flex-direction:column;
    gap:14px;
    margin-bottom:20px;
}

.detail{
    display:flex;
    justify-content:space-between;
    align-items:center;
}

.label{
    color:#6b7280;
    font-weight:600;
}

.card-footer{
    border-top:1px solid #eef2f7;
    padding-top:18px;
}

.badge{
    padding:8px 12px;
    font-size:.8rem;
}

</style>