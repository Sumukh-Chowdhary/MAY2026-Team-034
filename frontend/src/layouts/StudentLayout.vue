<script setup>
import { ref } from 'vue'
import Sidebar from '@/components/student/Sidebar.vue'
import LogoutModal from '@/components/LogoutModal.vue'
import NotificationBell from '@/components/NotificationBell.vue'
import EventCalendarModal from '@/components/common/EventCalendarModal.vue'

const collapsed = ref(false)
const showCalendar = ref(false)
</script>

<template>
    <div class="dashboard" :class="{ collapsed }">
        <Sidebar @toggle="collapsed = $event" />
        <main class="page-content relative">
            <div class="header-actions-bar" style="position: absolute; top: 1rem; right: 1.5rem; z-index: 40; display: flex; align-items: center; gap: 12px;">
                <button class="btn btn-sm btn-white border shadow-sm rounded-pill px-3 fw-semibold text-slate-700" @click="showCalendar = true">
                    <i class="bi bi-calendar3 text-primary me-1"></i> Campus Calendar
                </button>
                <NotificationBell />
            </div>
            <slot />
        </main>
        <LogoutModal />
        <EventCalendarModal :show="showCalendar" @close="showCalendar = false" />
    </div>
</template>

<style scoped>
.dashboard{
    display:flex;
    min-height:100vh;
    background:#F8FAFC;
}

.page-content{
    margin-left:250px;
    width:calc(100% - 250px);
    padding:35px;
    transition:all .3s ease;
}

.dashboard.collapsed .page-content{
    margin-left:75px;
    width:calc(100% - 75px);
}

@media (max-width:992px){
    .page-content,
    .dashboard.collapsed .page-content{
        margin-left:80px;
        width:calc(100% - 80px);
        padding:24px;
    }
}

@media (max-width:576px){
    .page-content,
    .dashboard.collapsed .page-content{
        margin-left:70px;
        width:calc(100% - 70px);
        padding:16px;
    }
}
</style>