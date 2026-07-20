<script setup>
defineProps({
  ticket: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['view'])
</script>

<template>

<div class="ticket-card">

    <div class="card-header">

        <div>

            <h5>{{ ticket.subject }}</h5>

            <p>{{ ticket.club }}</p>

        </div>

        <span
            class="badge priority"
            :class="{
                high: ticket.priority === 'High',
                medium: ticket.priority === 'Medium',
                low: ticket.priority === 'Low'
            }"
        >
            {{ ticket.priority }}
        </span>

    </div>

    <div class="status-row">

        <span>Status</span>

        <span
            class="badge"
            :class="{
                'bg-warning text-dark':
                    ticket.status === 'Pending' ||
                    ticket.status === 'In Progress',

                'bg-success':
                    ticket.status === 'Approved',

                'bg-danger':
                    ticket.status === 'Rejected'
            }"
        >
            {{ ticket.status }}
        </span>

    </div>

    <div
        v-if="ticket.approvals"
        class="approval-section"
    >

        <h6>Approval Progress</h6>

        <div
            v-for="approval in ticket.approvals"
            :key="approval.name"
            class="approval-row"
        >

            <span>{{ approval.name }}</span>

            <span
                :class="
                    approval.status === 'Approved'
                        ? 'text-success fw-bold'
                        : 'text-secondary fw-bold'
                "
            >
                {{ approval.status === 'Approved'
                    ? '✔ Approved'
                    : '○ Pending' }}
            </span>

        </div>

    </div>

    <div class="footer">

        <small>
            Submitted {{ ticket.date }}
        </small>

        <button
            class="btn btn-outline-primary"
            @click="emit('view', ticket)"
        >
            View Ticket
        </button>

    </div>

</div>

</template>

<style scoped>

.ticket-card{
    background:#fff;
    border:1px solid #e5e7eb;
    border-radius:16px;
    padding:20px;
    display:flex;
    flex-direction:column;
    gap:18px;
    transition:.25s;
}

.ticket-card:hover{
    transform:translateY(-4px);
    box-shadow:0 10px 24px rgba(0,0,0,.08);
}

.card-header{
    display:flex;
    justify-content:space-between;
    gap:16px;
}

.card-header h5{
    margin:0;
    font-weight:700;
}

.card-header p{
    margin-top:6px;
    color:#6b7280;
    margin-bottom:0;
}

.priority{
    padding:8px 12px;
}

.high{
    background:#fee2e2;
    color:#dc2626;
}

.medium{
    background:#fef3c7;
    color:#b45309;
}

.low{
    background:#dcfce7;
    color:#15803d;
}

.status-row{
    display:flex;
    justify-content:space-between;
    align-items:center;
}

.approval-section{
    border-top:1px solid #eceff3;
    padding-top:16px;
}

.approval-section h6{
    margin-bottom:12px;
    font-weight:600;
}

.approval-row{
    display:flex;
    justify-content:space-between;
    padding:8px 0;
}

.footer{
    display:flex;
    justify-content:space-between;
    align-items:center;
    border-top:1px solid #eceff3;
    padding-top:16px;
}

.footer small{
    color:#6b7280;
}

</style>