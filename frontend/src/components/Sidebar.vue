<script setup>
import {ref} from 'vue'

const collapsed=ref(false)
const emit=defineEmits(['toggle'])

function toggleSidebar(){
    collapsed.value=!collapsed.value
    emit('toggle',collapsed.value)
}
</script>

<template>
    <aside
        class="sidebar"
        :class="{collapsed:collapsed}">
        <div>
            <div class="top-section">
                <div class="logo-section" v-if="!collapsed">
                    <h3>AllClub</h3>
                </div>
                <button class="toggle-btn" @click="toggleSidebar">
                    <i class="bi" :class="collapsed ? 'bi-layout-sidebar-inset' : 'bi-layout-sidebar'"></i>
                </button>
            </div>
            <p class="menu-title" v-if="!collapsed">MAIN MENU</p>
            <ul class="nav-list">
                <li>
                    <RouterLink
                        class="nav-item"
                        to="/admin">
                        <i class="bi bi-grid-fill"></i>
                        <span v-if="!collapsed">Dashboard</span>
                    </RouterLink>
                </li>
                <li>
                    <RouterLink
                        class="nav-item"
                        to="/admin/users">
                        <i class="bi bi-people-fill"></i>
                        <span v-if="!collapsed">Users</span>
                    </RouterLink>
                </li>
                <li>
                    <RouterLink
                        class="nav-item"
                        to="/admin/clubs">
                        <i class="bi bi-collection-fill"></i>
                        <span v-if="!collapsed">Clubs</span>
                    </RouterLink>
                </li>
                <li>
                    <RouterLink
                        class="nav-item"
                        to="/admin/events">
                        <i class="bi bi-calendar-event-fill"></i>
                        <span v-if="!collapsed">Events</span>
                    </RouterLink>
                </li>
                <li>
                    <RouterLink
                        class="nav-item"
                        to="/admin/requests">
                        <i class="bi bi-file-earmark-text-fill"></i>
                        <span v-if="!collapsed">Requests</span>
                    </RouterLink>
                </li>
            </ul>
        </div>
        <div class="profile">
            <div class="profile-icon">A</div>
            <div v-if="!collapsed">
                <h6>Admin</h6>
                <small>Administrator</small>
            </div>
        </div>
    </aside>
</template>

<style scoped>
.sidebar{
    width:260px;
    height:100vh;
    background:#fff;
    border-right:1px solid #E2E8F0;
    position:fixed;
    display:flex;
    flex-direction:column;
    justify-content:space-between;
    padding:20px 15px;
    transition:.3s;
}

.sidebar.collapsed{
    width:80px;
}

.top-section{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:35px;
}

.toggle-btn{
    width:42px;
    height:42px;
    border:none;
    border-radius:10px;
    background:#111827;
    color:white;
    display:flex;
    justify-content:center;
    align-items:center;
    transition:.25s;
}

.toggle-btn:hover{
    background:#1E293B;
}

.logo-section{
    display:flex;
    align-items:center;
}

.logo-section h3{
    margin:0;
    color:#2563EB;
    font-size:2rem;
    font-weight:700;
}

.menu-title{
    font-size:.75rem;
    color:#94A3B8;
    margin-bottom:15px;
}

.nav-list{
    list-style:none;
    padding:0;
}

.nav-list li{
    margin-bottom:10px;
}

.nav-item{
    display:flex;
    align-items:center;
    gap:15px;
    padding:12px;
    border-radius:12px;
    color:#475569;
    transition:.25s;
}

.nav-item:hover{
    background:#EFF6FF;
    color:#2563EB;
}

.router-link-active{
    background:#2563EB;
    color:white;
}

.profile{
    border-top:1px solid #E2E8F0;
    padding-top:20px;
    display:flex;
    align-items:center;
    gap:12px;
}

.profile-icon{
    width:45px;
    height:45px;
    border-radius:50%;
    background:#2563EB;
    color:white;
    display:flex;
    justify-content:center;
    align-items:center;
    font-weight:600;
}

.profile h6{
    margin:0;
}

.profile small{
    color:#64748B;
}

.sidebar.collapsed .nav-item{
    justify-content:center;
    padding:14px 0;
}

.sidebar.collapsed .profile{
    justify-content:center;
}

.sidebar.collapsed .toggle-btn{
    margin:auto;
}
</style>