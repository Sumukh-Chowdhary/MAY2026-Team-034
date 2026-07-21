<script setup>
import {ref,onMounted,onBeforeUnmount} from 'vue'
import {Modal} from 'bootstrap'

const collapsed=ref(false)
const showProfileMenu=ref(false)
const emit=defineEmits(['toggle'])

function toggleSidebar(){
    collapsed.value=!collapsed.value
    emit('toggle',collapsed.value)
}

function toggleProfileMenu(){
    showProfileMenu.value=!showProfileMenu.value
}

function openLogoutModal(){
    showProfileMenu.value=false
    const modal=new Modal(document.getElementById('logoutModal'))
    modal.show()
}

function handleOutsideClick(event){
    if(!event.target.closest('.profile-container')){
        showProfileMenu.value=false
    }
}

onMounted(()=>{
    document.addEventListener('click',handleOutsideClick)
})

onBeforeUnmount(()=>{
    document.removeEventListener('click',handleOutsideClick)
})
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
                        to="/student">
                        <i class="bi bi-grid-fill"></i>
                        <span v-if="!collapsed">Dashboard</span>
                    </RouterLink>
                </li>
                <li>
                    <RouterLink
                        class="nav-item"
                        to="/student/roles">
                        <i class="bi bi-people-fill"></i>
                        <span v-if="!collapsed">My Roles</span>
                    </RouterLink>
                </li>
                <li>
                    <RouterLink
                        class="nav-item"
                        to="/student/clubs">
                        <i class="bi bi-collection-fill"></i>
                        <span v-if="!collapsed">Clubs</span>
                    </RouterLink>
                </li>
                <li>
                    <RouterLink
                        class="nav-item"
                        to="/student/events">
                        <i class="bi bi-calendar-event-fill"></i>
                        <span v-if="!collapsed">Events</span>
                    </RouterLink>
                </li>
                <li>
                    <RouterLink
                        class="nav-item"
                        to="/student/requests">
                        <i class="bi bi-file-earmark-text-fill"></i>
                        <span v-if="!collapsed">Requests</span>
                    </RouterLink>
                </li>
            </ul>
        </div>
        <div class="profile-container">
            <div class="profile" @click.stop="toggleProfileMenu">
                <div class="profile-icon">S</div>
                <div class="profile-info" v-if="!collapsed">
                    <h6>Student</h6>
                    <small>Participant</small>
                </div>
            </div>
            <Transition name="dropdown">
            <div v-if="showProfileMenu" class="profile-menu">
                <button class="menu-item"><i class="bi bi-person-circle"></i>Profile</button>
                <button
                class="menu-item logout"
                @click="openLogoutModal">
                <i class="bi bi-box-arrow-right"></i>Logout
            </button>
        </div>
            </Transition>
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

.profile-container{
    position:relative;
}

.profile{
    display:flex;
    align-items:center;
    gap:12px;
    border-top:1px solid #E2E8F0;
    padding-top:18px;
    cursor:pointer;
}

.profile-info h6{
    margin:0;
}

.profile-info small{
    color:#64748B;
}

.profile-menu{
    position:absolute;
    bottom:72px;
    left:0;
    width:180px;
    background:#fff;
    border:1px solid #E2E8F0;
    border-radius:14px;
    box-shadow:0 10px 30px rgba(0,0,0,.12);
    overflow:hidden;
    z-index:9999;
}

.menu-item{
    width:100%;
    border:none;
    background:white;
    padding:14px 18px;
    display:flex;
    align-items:center;
    gap:12px;
    transition:.2s;
}

.menu-item:hover{
    background:#F8FAFC;
}

.logout{
    color:#DC2626;
}

.logout:hover{
    background:#FEF2F2;
}

.sidebar.collapsed .profile{
    justify-content:center;
}

.sidebar.collapsed .profile-menu{
    left:70px;
    bottom:0;
}

.dropdown-enter-active,
.dropdown-leave-active{
    transition:all .2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to{
    opacity:0;
    transform:translateY(8px);
}

@media (max-width: 992px) {
    .sidebar {
        width: 80px;
    }

    .sidebar .logo-section,
    .sidebar .menu-title,
    .sidebar .nav-item span,
    .sidebar .profile-info {
        display: none;
    }

    .sidebar .nav-item {
        justify-content: center;
        padding: 14px 0;
    }

    .sidebar .profile {
        justify-content: center;
    }

    .sidebar .toggle-btn {
        display: none;
    }

    .sidebar .profile-menu {
        left: 70px;
        bottom: 0;
    }
}

@media (max-width: 576px) {
    .sidebar {
        width: 70px;
        padding: 15px 10px;
    }

    .profile-icon {
        width: 40px;
        height: 40px;
    }

    .sidebar .profile-menu {
        left: 60px;
    }
}
</style>