<script setup>
import { ref, computed } from 'vue'

import FacultyLayout from '@/layouts/FacultyLayout.vue'

import RequestsToggle from '@/components/faculty/RequestsToggle.vue'
import TicketCard from '@/components/faculty/TicketCard.vue'
import TicketTable from '@/components/faculty/TicketTable.vue'
import IncomingRequestCard from '@/components/faculty/IncomingRequestCard.vue'
import TicketDetailsModal from '@/components/faculty/TicketDetailsModal.vue'
import NewTicketModal from '@/components/faculty/NewTicketModal.vue'

const activeTab = ref('tickets')
const search = ref('')
const filter = ref('open')

const selectedTicket = ref(null)
const showTicketModal = ref(false)
const showNewTicket = ref(false)

function openTicket(ticket) {
    selectedTicket.value = ticket
    showTicketModal.value = true
}

function addTicket(ticket) {
    openTickets.value.unshift(ticket)
}

const openTickets = ref([
    {
        id: 1,
        subject: 'Budget Approval',
        club: 'Photography Club',
        status: 'Pending',
        date: '20 Jul 2026',
        description: 'Requesting budget approval for the annual photography exhibition.'
    },
    {
        id: 2,
        subject: 'Venue Booking',
        club: 'Chess Club',
        status: 'Pending',
        date: '18 Jul 2026',
        description: 'Need the seminar hall for the inter-college chess tournament.'
    },
    {
        id: 3,
        subject: 'Workshop Equipment',
        club: 'Robotics Club',
        status: 'Pending',
        date: '16 Jul 2026',
        description: 'Require robotics kits and projectors for the workshop.'
    }
])

const closedTickets = ref([
    {
        id: 4,
        subject: 'Guest Speaker Approval',
        status: 'Approved',
        closed: '12 Jul 2026'
    },
    {
        id: 5,
        subject: 'Funding Request',
        status: 'Rejected',
        closed: '09 Jul 2026'
    }
])

const incomingRequests = ref([
    {
        id: 1,
        name: 'Rahul Sharma',
        subject: 'Join Photography Club',
        club: 'Photography Club',
        date: '20 Jul 2026',
        status: 'Pending'
    },
    {
        id: 2,
        name: 'Priya Nair',
        subject: 'Join Chess Club',
        club: 'Chess Club',
        date: '18 Jul 2026',
        status: 'Pending'
    }
])

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

const filteredIncoming = computed(() =>
    incomingRequests.value.filter(request =>
        request.subject.toLowerCase().includes(search.value.toLowerCase())
    )
)
</script>

<template>
    <FacultyLayout>

        <section class="requests-page">

            <div class="page-header">
                <div>
                    <h1>Requests</h1>
                    <p>Manage communication with administrators and students.</p>
                </div>
            </div>

            <div class="toggle-wrapper"><RequestsToggle v-model="activeTab" /></div>

            <div class="toolbar">

                <input
                    v-model="search"
                    type="text"
                    class="form-control"
                    placeholder="Search..."
                >

                <div class="actions">

                    <button
                        v-if="activeTab === 'tickets'"
                        class="btn btn-warning"
                        @click="showNewTicket = true"
                    >
                        + New Ticket
                    </button>

                    <select
                        v-if="activeTab === 'tickets'"
                        v-model="filter"
                        class="form-select"
                    >
                        <option value="open">Open</option>
                        <option value="closed">Closed</option>
                        <option value="all">All</option>
                    </select>

                </div>

            </div>

            <!-- MY TICKETS -->

            <template v-if="activeTab === 'tickets'">

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

            </template>

            <!-- INCOMING REQUESTS -->

            <div
                v-else
                class="cards-grid"
            >
                <IncomingRequestCard
                    v-for="request in filteredIncoming"
                    :key="request.id"
                    :request="request"
                />
            </div>

        </section>

        <!-- Ticket Details -->

        <TicketDetailsModal
            :show="showTicketModal"
            :ticket="selectedTicket"
            @close="showTicketModal = false"
        />

        <!-- New Ticket -->

        <NewTicketModal
            :show="showNewTicket"
            @close="showNewTicket = false"
            @submit="addTicket"
        />

    </FacultyLayout>
</template>

<style scoped>
.toggle-wrapper{
    display:flex;
    justify-content:flex-start;
}

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