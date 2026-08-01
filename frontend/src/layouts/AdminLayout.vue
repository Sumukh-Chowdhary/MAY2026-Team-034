<script setup>
import {ref} from 'vue'
import Sidebar from '../components/Sidebar.vue'
import LogoutModal from '../components/LogoutModal.vue'
import NotificationBell from '../components/NotificationBell.vue'

const collapsed=ref(false)
</script>

<template>
    <div
        class="dashboard" :class="{collapsed:collapsed}">
        <Sidebar @toggle="collapsed=$event"/>
        <main class="page-content relative">
            <div class="absolute top-4 right-6 z-40" style="position: absolute; top: 1rem; right: 1.5rem; z-index: 40;">
                <NotificationBell />
            </div>
            <slot/>
        </main>
        <LogoutModal/>
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


@media (max-width: 992px) {
    .page-content,
    .dashboard.collapsed .page-content {
        margin-left: 80px;
        width: calc(100% - 80px);
        padding: 24px;
    }
}

@media (max-width: 576px) {
    .page-content,
    .dashboard.collapsed .page-content {
        margin-left: 70px;
        width: calc(100% - 70px);
        padding: 16px;
    }
}
</style>