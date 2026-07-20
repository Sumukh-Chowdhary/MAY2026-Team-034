<script setup>
const emit = defineEmits(['view'])

defineProps({
  tickets: {
    type: Array,
    default: () => []
  }
})

const badgeClass = (status) => {
  switch (status) {
    case 'Approved':
      return 'bg-success'
    case 'Rejected':
      return 'bg-danger'
    default:
      return 'bg-warning text-dark'
  }
}
</script>

<template>
  <div class="ticket-table">
    <div class="table-header">
      <h5>Closed Tickets</h5>
      <span>{{ tickets.length }} Tickets</span>
    </div>

    <div class="table-responsive">
      <table class="table align-middle mb-0">
        <thead>
          <tr>
            <th>Subject</th>
            <th>Status</th>
            <th>Closed On</th>
            <th class="text-end">Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ticket in tickets" :key="ticket.id">
            <td>{{ ticket.subject }}</td>
            <td>
              <span class="badge" :class="badgeClass(ticket.status)">{{ ticket.status }}</span>
            </td>
            <td>{{ ticket.closed }}</td>
            <td class="text-end">
              <button class="btn btn-sm btn-outline-primary" @click="emit('view', ticket)">View</button>
            </td>
          </tr>

          <tr v-if="tickets.length === 0">
            <td colspan="4" class="text-center py-5 text-muted">
              No closed tickets found.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.ticket-table{
    background:#fff;
    border-radius:16px;
    border:1px solid #e5e7eb;
    overflow:hidden;
    box-shadow:0 2px 8px rgba(0,0,0,.05);
}

.table-header{
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:20px 24px;
    border-bottom:1px solid #eef2f7;
}

.table-header h5{
    margin:0;
    font-weight:700;
}

.table-header span{
    color:#6b7280;
    font-size:.9rem;
}

.table{
    margin:0;
}

.table th{
    font-weight:600;
    color:#6b7280;
    border-bottom:1px solid #eef2f7;
    padding:16px 24px;
}

.table td{
    padding:18px 24px;
    vertical-align:middle;
}

tbody tr:hover{
    background:#f8fafc;
}

.badge{
    padding:7px 12px;
    font-size:.8rem;
}

</style>