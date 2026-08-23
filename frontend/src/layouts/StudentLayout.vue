<script setup>
import { ref, computed } from 'vue'
import Sidebar from '@/components/student/Sidebar.vue'
import LogoutModal from '@/components/LogoutModal.vue'
import NotificationBell from '@/components/NotificationBell.vue'
import EventCalendarModal from '@/components/common/EventCalendarModal.vue'
import { isLegacyUser } from '@/utils/permissions'

const collapsed = ref(false)
const showCalendar = ref(false)

const userStr = localStorage.getItem('user')
const currentUser = userStr ? JSON.parse(userStr) : null
const isLegacy = computed(() => isLegacyUser(currentUser))
</script>

<template>
    <div class="dashboard" :class="{ collapsed }">
        <Sidebar @toggle="collapsed = $event" />
        <main class="page-content relative">
            <div class="header-actions-bar">
                <button class="btn btn-sm btn-white border shadow-sm rounded-pill px-3 fw-semibold text-slate-700" @click="showCalendar = true">
                    <i class="bi bi-calendar3 text-primary me-1"></i> Campus Calendar
                </button>
                <NotificationBell />
            </div>

            <!-- Centralized Legacy Read-Only Banner -->
            <div v-if="isLegacy" class="alert alert-warning border-warning border-opacity-50 rounded-4 shadow-sm mb-4 d-flex align-items-center justify-content-between p-3" style="background-color: #FFFBEB; margin-top: 1.5rem;">
                <div class="d-flex align-items-center gap-3">
                    <div class="bg-warning text-dark rounded-circle d-flex align-items-center justify-content-center flex-shrink-0" style="width: 38px; height: 38px;">
                        <i class="bi bi-clock-history fs-5"></i>
                    </div>
                    <div>
                        <div class="fw-bold text-dark text-sm">Legacy Account (Read-Only Mode)</div>
                        <div class="text-xs text-muted">Your student account is now read-only because your student lifecycle is marked Legacy.</div>
                    </div>
                </div>
                <span class="badge bg-warning text-dark px-3 py-2 text-uppercase text-xs font-semibold rounded-pill">Legacy Read-Only</span>
            </div>

            <slot />
        </main>
        <LogoutModal />
        <EventCalendarModal :show="showCalendar" @close="showCalendar = false" />
    </div>
</template>

<style scoped>
.header-actions-bar {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 12px;
    margin-bottom: 20px;
    position: relative;
    z-index: 10;
}

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