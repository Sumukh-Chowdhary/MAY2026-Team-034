<script setup>
import { reactive } from 'vue'

const props = defineProps({
  show: Boolean
})

const emit = defineEmits(['close', 'submit'])

const form = reactive({
  title: '',
  category: '',
  club: '',
  priority: 'Medium',
  description: ''
})

function submitTicket() {
  emit('submit', {
    id: Date.now(),
    subject: form.title,
    category: form.category,
    club: form.club,
    priority: form.priority,
    description: form.description,
    status: 'Pending',
    date: new Date().toLocaleDateString()
  })

  form.title = ''
  form.category = ''
  form.club = ''
  form.priority = 'Medium'
  form.description = ''

  emit('close')
}
</script>

<template>

<div
    v-if="show"
    class="modal-backdrop-custom"
>

<div class="ticket-modal">

    <div class="modal-header">

        <div>
            <h4>New Ticket</h4>
            <p>Create a request for the administrator.</p>
        </div>

        <button
            class="btn-close"
            @click="emit('close')"
        />

    </div>

    <div class="modal-body">

        <div class="mb-3">
            <label class="form-label">Title</label>
            <input
                v-model="form.title"
                class="form-control"
                placeholder="Enter title"
            >
        </div>

        <div class="row">

            <div class="col-md-6 mb-3">
                <label class="form-label">Category</label>

                <select
                    v-model="form.category"
                    class="form-select"
                >
                    <option>Budget</option>
                    <option>Venue</option>
                    <option>Equipment</option>
                    <option>Event</option>
                    <option>General</option>
                </select>
            </div>

            <div class="col-md-6 mb-3">

                <label class="form-label">Priority</label>

                <select
                    v-model="form.priority"
                    class="form-select"
                >
                    <option>Low</option>
                    <option>Medium</option>
                    <option>High</option>
                </select>

            </div>

        </div>

        <div class="mb-3">

            <label class="form-label">Club</label>

            <input
                v-model="form.club"
                class="form-control"
                placeholder="Club name"
            >

        </div>

        <div>

            <label class="form-label">Description</label>

            <textarea
                v-model="form.description"
                rows="5"
                class="form-control"
                placeholder="Describe your request..."
            />

        </div>

    </div>

    <div class="modal-footer">

        <button
            class="btn btn-light"
            @click="emit('close')"
        >
            Cancel
        </button>

        <button
            class="btn btn-warning"
            @click="submitTicket"
        >
            Submit Ticket
        </button>

    </div>

</div>

</div>

</template>

<style scoped>

.modal-backdrop-custom{
    position:fixed;
    inset:0;
    background:rgba(0,0,0,.45);
    display:flex;
    justify-content:center;
    align-items:center;
    z-index:9999;
}

.ticket-modal{
    width:720px;
    max-width:95%;
    background:white;
    border-radius:18px;
    overflow:hidden;
}

.modal-header{
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    padding:24px;
    border-bottom:1px solid #eee;
}

.modal-body{
    padding:24px;
}

.modal-footer{
    padding:20px 24px;
    border-top:1px solid #eee;
    display:flex;
    justify-content:flex-end;
    gap:10px;
}

</style>