<script setup>
const props = defineProps({
  show: Boolean,
  ticket: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])
</script>

<template>

  <div
    v-if="show"
    class="modal-backdrop-custom"
  >
    <div class="ticket-modal">

      <div class="modal-header">
        <div>
          <h4>Ticket Details</h4>
          <p class="mb-0">View complete ticket information.</p>
        </div>

        <button
          class="btn-close"
          @click="emit('close')"
        />
      </div>

      <div
    v-if="ticket"
    class="modal-body"
>

    <div class="info-row">
        <span>Subject</span>
        <strong>{{ ticket.subject }}</strong>
    </div>

    <div class="info-row">
        <span>Related</span>
        <strong>{{ ticket.club }}</strong>
    </div>

    <div class="info-row">
        <span>Priority</span>
        <span class="badge bg-danger">
            {{ ticket.priority }}
        </span>
    </div>

    <div class="info-row">
        <span>Status</span>

        <span
            class="badge"
            :class="{
                'bg-warning text-dark': ticket.status==='Pending' || ticket.status==='In Progress',
                'bg-success': ticket.status==='Approved',
                'bg-danger': ticket.status==='Rejected'
            }"
        >
            {{ ticket.status }}
        </span>
    </div>

    <div class="info-row">
        <span>Submitted</span>
        <strong>{{ ticket.date }}</strong>
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
                :class="approval.status==='Approved'
                    ? 'text-success fw-bold'
                    : 'text-secondary fw-bold'"
            >
                {{ approval.status==='Approved' ? '✔ Approved' : '○ Pending' }}
            </span>

        </div>

    </div>

    <div class="description">

        <label>Description</label>

        <div class="description-box">
            {{ ticket.description }}
        </div>

    </div>

</div>

      <div class="modal-footer">

        <button
          class="btn btn-secondary"
          @click="emit('close')"
        >
          Close
        </button>

      </div>

    </div>
  </div>

</template>

<style scoped>
.modal-backdrop-custom{
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,.45);
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
    z-index: 9999;
}

.ticket-modal{
    width:650px;
    max-width:95%;
    max-height:calc(100vh - 40px);
    background:#fff;
    border-radius:18px;
    display:flex;
    flex-direction:column;
    overflow:hidden;
    box-shadow:0 20px 60px rgba(0,0,0,.2);
}

.modal-header{
    padding:24px;
    border-bottom:1px solid #eee;
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    flex-shrink:0;
}

.modal-header h4{
    margin-bottom:6px;
}

.modal-header p{
    color:#6b7280;
}

.modal-body{
    padding:24px;
    overflow-y:auto;
    flex:1;
}

.info-row{
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:14px 0;
    border-bottom:1px solid #f3f4f6;
}

.info-row span:first-child{
    color:#6b7280;
    font-weight:600;
}

.description{
    margin-top:24px;
}

.description label{
    font-weight:600;
    margin-bottom:10px;
}

.description-box{
    background:#f8fafc;
    border:1px solid #e5e7eb;
    border-radius:12px;
    padding:16px;
    min-height:120px;
}

.modal-footer{
    padding:20px 24px;
    border-top:1px solid #eee;
    display:flex;
    justify-content:flex-end;
    flex-shrink:0;
}

.approval-section{
    margin-top:24px;
    padding:18px;
    background:#f8fafc;
    border:1px solid #e5e7eb;
    border-radius:12px;
}

.approval-section h6{
    margin-bottom:16px;
    font-weight:600;
}

.approval-row{
    display:flex;
    justify-content:space-between;
    padding:10px 0;
    border-bottom:1px solid #eceff3;
}

.approval-row:last-child{
    border-bottom:none;
}
</style>