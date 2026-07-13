<script setup>
defineProps({
    request:Object
})

const emit=defineEmits(['view'])
</script>

<template>
    <div class="card shadow-sm border-0 request-card">
        <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h5 class="fw-semibold mb-1">{{request.requestedBy}}</h5>
                    <small class="text-secondary">{{request.registerNumber}}</small>
                </div>
                <span class="badge bg-warning text-dark">{{request.status}}</span>
            </div>
            <hr>
            <p><strong>Subject :</strong> {{request.subject}}</p>
            <p><strong>Club :</strong> {{request.club}}</p>
            <p class="text-secondary mb-4">{{request.date}}</p>
            <div class="text-end">
                <button
                    class="btn btn-primary"
                    @click="$emit('view',request)">
                    View
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.request-card{
    border-radius:18px;
    transition:.3s;
}

.request-card:hover{
    transform:translateY(-3px);
    box-shadow:0 10px 25px rgba(0,0,0,.08)!important;
}
</style>