<script setup>
import { ref, computed } from 'vue'

import StudentLayout from '@/layouts/StudentLayout.vue'

import TicketCard from '@/components/student/TicketCard.vue'
import TicketTable from '@/components/student/TicketTable.vue'
import TicketDetailsModal from '@/components/student/TicketDetailsModal.vue'
import NewTicketModal from '@/components/student/NewTicketModal.vue'

const search = ref('')
const filter = ref('open')

const selectedTicket = ref(null)
const showTicketModal = ref(false)
const showNewTicket = ref(false)

function openTicket(ticket) {
  selectedTicket.value = ticket
  showTicketModal.value = true
}

const openTickets = ref([
  {
    id:101,
    subject:'Budget Request',
    club:'@Photography Club',
    priority:'High',
    status:'In Progress',
    date:'20 Jul 2026',
    description:'Budget required for annual exhibition.',
    approvals:[
      {name:'Faculty',status:'Approved'},
      {name:'Club President',status:'Approved'},
      {name:'Admin',status:'Pending'}
    ]
  },
  {
    id:102,
    subject:'Equipment Request',
    club:'@Robotics Club',
    priority:'Medium',
    status:'Pending',
    date:'18 Jul 2026',
    description:'Need Arduino kits for workshop.',
    approvals:[
      {name:'Faculty',status:'Pending'},
      {name:'Club President',status:'Pending'},
      {name:'Admin',status:'Pending'}
    ]
  },
  {
    id:103,
    subject:'Event Permission',
    club:'@Coding Club',
    priority:'Low',
    status:'Pending',
    date:'15 Jul 2026',
    description:'Permission to organize coding contest.',
    approvals:[
      {name:'Faculty',status:'Approved'},
      {name:'Admin',status:'Pending'}
    ]
  }
])

const closedTickets = ref([
  {
    id:201,
    subject:'Venue Booking',
    status:'Approved',
    approvedBy:'Admin',
    closed:'15 Jul 2026'
  },
  {
    id:202,
    subject:'Poster Printing',
    status:'Rejected',
    approvedBy:'Faculty',
    closed:'10 Jul 2026'
  }
])

function addTicket(ticket){
  openTickets.value.unshift(ticket)
  showNewTicket.value = false
}

const filteredOpenTickets = computed(() =>
  openTickets.value.filter(ticket =>
    ticket.subject.toLowerCase().includes(search.value.toLowerCase())
  )
)

const filteredClosedTickets = computed(() =>
  closedTickets.value.filter(ticket =>
    ticket.subject.toLowerCase().includes(search.value.toLowerCase())
  )
)
</script>

<template>
  <StudentLayout>

    <section class="requests-page">

      <div class="page-header">
        <div>
          <h1>Requests</h1>
          <p>Track all requests submitted to clubs and administrators.</p>
        </div>
      </div>

      <div class="toolbar">

        <input
          v-model="search"
          type="text"
          class="form-control"
          placeholder="Search..."
        >

        <div class="actions">

          <button
            class="btn btn-warning"
            @click="showNewTicket = true"
          >
            + Raise Ticket
          </button>

          <select
            v-model="filter"
            class="form-select"
          >
            <option value="open">Open</option>
            <option value="closed">Closed</option>
            <option value="all">All</option>
          </select>

        </div>

      </div>

      <div
        v-if="filter === 'open' || filter === 'all'"
        class="cards-grid"
      >
        <TicketCard
          v-for="ticket in filteredOpenTickets"
          :key="ticket.id"
          :ticket="ticket"
          @view="openTicket"
        />
      </div>

      <TicketTable
        v-if="filter === 'closed' || filter === 'all'"
        :tickets="filteredClosedTickets"
        @view="openTicket"
      />

    </section>

    <TicketDetailsModal
      :show="showTicketModal"
      :ticket="selectedTicket"
      @close="showTicketModal = false"
    />

    <NewTicketModal
      :show="showNewTicket"
      @close="showNewTicket = false"
      @submit="addTicket"
    />

  </StudentLayout>
</template>

<style scoped>
.requests-page{
  display:flex;
  flex-direction:column;
  gap:24px;
}

.page-header h1{
  font-size:2.25rem;
  font-weight:700;
  margin-bottom:.35rem;
}

.page-header p{
  color:#6b7280;
  margin:0;
}

.toolbar{
  display:flex;
  justify-content:space-between;
  align-items:center;
  gap:20px;
  flex-wrap:wrap;
}

.toolbar .form-control{
  flex:1;
  min-width:260px;
  max-width:700px;
}

.actions{
  display:flex;
  align-items:center;
  gap:12px;
}

.actions .form-select{
  width:150px;
}

.cards-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(340px,1fr));
  gap:24px;
}

@media (max-width:768px){
  .toolbar{
    flex-direction:column;
    align-items:stretch;
  }

  .toolbar .form-control{
    max-width:100%;
  }

  .actions{
    justify-content:space-between;
  }
}
</style>
