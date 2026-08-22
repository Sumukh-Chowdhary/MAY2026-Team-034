<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Modal } from 'bootstrap'
import { getCurrentUser } from '@/services/authService'
import UserAvatar from '@/components/profile/UserAvatar.vue'

const router = useRouter()
const route = useRoute()
const collapsed = ref(false)
const showProfileMenu = ref(false)
const emit = defineEmits(['toggle'])

const user = computed(() => getCurrentUser() || {})
const userInitial = computed(() => (user.value.name || user.value.username || 'A').charAt(0).toUpperCase())
const userName = computed(() => user.value.name || user.value.username || 'Admin')
const userRole = computed(() => user.value.role || 'Administrator')
const userAvatarUrl = computed(() => {
  const style = user.value.avatarStyle || 'adventurer'
  const seed = user.value.avatarSeed || user.value.fullName || user.value.name || user.value.username || 'Admin'
  return `https://api.dicebear.com/7.x/${style}/svg?seed=${encodeURIComponent(seed)}`
})

function toggleSidebar() {
  collapsed.value = !collapsed.value
  emit('toggle', collapsed.value)
}

function toggleProfileMenu() {
  showProfileMenu.value = !showProfileMenu.value
}

function goToProfile() {
  showProfileMenu.value = false
  router.push('/admin/profile')
}

function goToSettings() {
  showProfileMenu.value = false
  router.push('/admin/profile')
}

function openLogoutModal() {
  showProfileMenu.value = false
  const modal = new Modal(document.getElementById('logoutModal'))
  modal.show()
}

function handleOutsideClick(event) {
  if (!event.target.closest('.profile-container')) {
    showProfileMenu.value = false
  }
}

function handleKeydown(event) {
  if (event.key === 'Escape') {
    showProfileMenu.value = false
  }
}

watch(() => route.path, () => {
  showProfileMenu.value = false
})

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
  document.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick)
  document.removeEventListener('keydown', handleKeydown)
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
                        to="/admin/venues">
                        <span class="material-symbols-rounded" style="font-size: 1.25rem;">meeting_room</span>
                        <span v-if="!collapsed">Venues</span>
                    </RouterLink>
                </li>
                <li>
                    <RouterLink
                        class="nav-item"
                        to="/admin/venue-calendar">
                        <i class="bi bi-calendar3"></i>
                        <span v-if="!collapsed">Venue Calendar</span>
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
        <div class="profile-container">
            <div class="profile d-flex align-items-center gap-2" @click.stop="toggleProfileMenu">
                <UserAvatar size="sidebar" :user="user" />
                <div class="profile-info" v-if="!collapsed">
                    <h6>{{ userName }}</h6>
                    <small>{{ userRole }}</small>
                </div>
            </div>
            <Transition name="dropdown">
                <div v-if="showProfileMenu" class="profile-menu">
                    <button class="menu-item" @click="goToProfile">
                        <i class="bi bi-person-circle"></i> My Profile
                    </button>
                    <button class="menu-item logout" @click="openLogoutModal">
                        <i class="bi bi-box-arrow-right"></i> Logout
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


/* Tablet */
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

    /* Sidebar is already collapsed on tablet,
       so the manual collapse/expand button is not needed */
    .sidebar .toggle-btn {
        display: none;
    }

    .sidebar .profile-menu {
        left: 70px;
        bottom: 0;
    }
}

/* Mobile */
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
