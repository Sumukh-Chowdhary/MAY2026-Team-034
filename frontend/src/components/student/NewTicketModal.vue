<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
    show: Boolean
})

const emit = defineEmits(['close', 'submit'])

const form = reactive({
    title: '',
    category: 'General',
    priority: 'Medium',
    reference: '',
    description: '',
    approvers: '@Faculty @Admin'
})

watch(
    () => props.show,
    (value) => {
        if (value) {
            form.title = ''
            form.category = 'General'
            form.priority = 'Medium'
            form.reference = ''
            form.description = ''
            form.approvers = '@Faculty @Admin'
        }
    }
)

function submit() {
    emit('submit', {
        id: Date.now(),
        subject: form.title,
        category: form.category,
        priority: form.priority,
        club: form.reference,
        approvers: form.approvers,
        description: form.description,
        status: 'Pending',
        date: new Date().toLocaleDateString(),

        approvals: [
            {
                name: 'Faculty',
                status: 'Pending'
            },
            {
                name: 'Club President',
                status: 'Pending'
            },
            {
                name: 'Admin',
                status: 'Pending'
            }
        ]
    })

    emit('close')
}
</script>

<template>

<Teleport to="body">

<div
    v-if="show"
    class="modal-backdrop-custom"
>

<div class="ticket-modal">

    <div class="modal-header">

        <h4>Raise New Ticket</h4>

        <button
            class="btn-close"
            @click="$emit('close')"
        />

    </div>

    <div class="modal-body">

        <div class="mb-3">

            <label class="form-label">
                Title
            </label>

            <input
                v-model="form.title"
                class="form-control"
                placeholder="Budget approval for Annual Hackathon"
            >

        </div>

        <div class="row">

            <div class="col">

                <label class="form-label">
                    Category
                </label>

                <select
                    v-model="form.category"
                    class="form-select"
                >
                    <option>General</option>
                    <option>Budget</option>
                    <option>Equipment</option>
                    <option>Venue</option>
                    <option>Event</option>
                    <option>Technical</option>
                    <option>Other</option>
                </select>

            </div>

            <div class="col">

                <label class="form-label">
                    Priority
                </label>

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

        <div class="mt-3">

            <label class="form-label">
                Related Club / Event
            </label>

            <input
                v-model="form.reference"
                class="form-control"
                placeholder="@Photography Club"
            >

        </div>

        <div class="mt-3">

            <label class="form-label">
                Description
            </label>

            <textarea
    v-model="form.description"
    rows="6"
    class="form-control"
    placeholder="Describe your request..."
></textarea>

        </div>

        <div class="mt-3">

            <label class="form-label">
                Approvers
            </label>

            <input
                v-model="form.approvers"
                class="form-control"
                placeholder="@Faculty @Admin"
            >

            <small class="text-muted">
                Future versions will support @mentions and autocomplete.
            </small>

        </div>

    </div>

    <div class="modal-footer">

        <button
            class="btn btn-secondary"
            @click="$emit('close')"
        >
            Cancel
        </button>

        <button
            class="btn btn-warning"
            @click="submit"
        >
            Raise Ticket
        </button>

    </div>

</div>

</div>

</Teleport>

</template>

<style scoped>
.modal-backdrop-custom{
    position:fixed;
    inset:0;
    background:rgba(0,0,0,.45);
    display:flex;
    justify-content:center;
    align-items:center;
    padding:20px;
    z-index:1055;
}

.ticket-modal{
    width:650px;
    max-width:95%;
    max-height:calc(100vh - 60px);
    margin:30px auto;
    background:#fff;
    border-radius:14px;
    display:flex;
    flex-direction:column;
    overflow:hidden;
    box-shadow:0 20px 50px rgba(0,0,0,.18);
}

.modal-header,
.modal-footer{
    padding:18px 24px;
    border-bottom:1px solid #eee;
}

.modal-footer{
    border-top:1px solid #eee;
    border-bottom:none;
    display:flex;
    justify-content:flex-end;
    gap:12px;
}

.modal-body{
    padding:24px;
    overflow-y:auto;
    flex:1;
}

</style>