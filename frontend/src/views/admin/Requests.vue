<script setup>
import {ref,computed} from 'vue'
import {Modal} from 'bootstrap'
import AdminLayout from '../../layouts/AdminLayout.vue'
import clubRequests from '../../data/clubRequests.json'
import eventRequests from '../../data/eventRequests.json'
import RequestCard from '../../components/RequestCard.vue'
import RequestDetailsModal from '../../components/RequestDetailsModal.vue'
import RejectModal from '../../components/RejectModal.vue'

const activeTab=ref('clubs')
const search=ref('')
const selectedRequest=ref(null)

const requests=computed(()=>{
    const data=activeTab.value==='clubs'
        ? clubRequests
        : eventRequests

    return data.filter(request=>
        request.requestedBy.toLowerCase().includes(search.value.toLowerCase()) ||
        request.subject.toLowerCase().includes(search.value.toLowerCase()) ||
        request.club.toLowerCase().includes(search.value.toLowerCase())
    )
})

function openRequest(request){
    selectedRequest.value=request
    const modal=new Modal(document.getElementById('requestModal'))
    modal.show()
}
</script>

<template>
    <AdminLayout>
        <section class="requests-page">
            <div class="d-flex justify-content-between align-items-center flex-wrap gap-3 mb-4">
                <div>
                    <h2 class="fw-bold mb-1">Requests</h2>
                    <p class="text-secondary mb-0">Review and manage club and event requests.</p>
                </div>

                <input
                    v-model="search"
                    class="form-control search-box"
                    placeholder="Search requests...">
            </div>

            <div class="toggle-buttons mb-4">
                <button
                    class="btn"
                    :class="activeTab==='clubs' ? 'btn-primary' : 'btn-outline-primary'"
                    @click="activeTab='clubs'">Club Requests
                    <span class="badge bg-light text-dark ms-2">{{clubRequests.length}}</span>
                </button>

                <button
                    class="btn"
                    :class="activeTab==='events' ? 'btn-primary' : 'btn-outline-primary'"
                    @click="activeTab='events'">Event Requests
                    <span class="badge bg-light text-dark ms-2">{{eventRequests.length}}</span>
                </button>
            </div>
            <div class="row">
                <div
                    class="col-xl-4 col-lg-6 mb-4"
                    v-for="request in requests"
                    :key="request.id">

                    <RequestCard
                        :request="request"
                        @view="openRequest"/>
                </div>
            </div>
            <div v-if="requests.length===0" class="empty-state">
                <i class="bi bi-inbox display-2"></i>
                <h4 class="mt-3">No Requests Found</h4>
                <p class="text-secondary">There are no requests matching your search.</p>
            </div>
        </section>

        <RequestDetailsModal :request="selectedRequest"/>
        <RejectModal/>
    </AdminLayout>
</template>

<style scoped>
.requests-page{
    width:100%;
}

.search-box{
    width:320px;
}

.toggle-buttons{
    display:flex;
    gap:12px;
    flex-wrap:wrap;
}

.empty-state{
    padding:80px 0;
    text-align:center;
    color:#94A3B8;
}

@media(max-width:768px){
    .search-box{
        width:100%;
    }
}
</style>