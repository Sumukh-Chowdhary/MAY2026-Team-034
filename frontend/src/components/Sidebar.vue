<script setup>
</script>

<template>
    <aside class="sidebar">
        <div>
            <h3 class="logo">AllClub</h3>
            <ul class="nav-list">
                <li class="active"><i class="bi bi-house-door-fill"></i>Home</li>
                <li><i class="bi bi-people-fill"></i>Users</li>
                <li><i class="bi bi-collection-fill"></i>Clubs</li>
                <li><i class="bi bi-calendar-event-fill"></i>Events</li>
                <li><i class="bi bi-file-earmark-text-fill"></i>Requests</li>
            </ul>
        </div>
        <div class="profile">
            <div class="profile-icon">A</div>
            <div>
                <h6 class="mb-0">Admin</h6>
                <small>Administrator</small>
            </div>
        </div>
    </aside>
</template>

<style scoped>
.sidebar{
    width:250px;
    background:#ffffff;
    border-right:1px solid #E2E8F0;
    padding:30px 20px;
    display:flex;
    flex-direction:column;
    justify-content:space-between;
    height:100vh;
    position:fixed;
}

.logo{
    color:#2563EB;
    font-weight:700;
    margin-bottom:40px;
}

.nav-list{
    list-style:none;
    padding:0;
}

.nav-list li{
    display:flex;
    align-items:center;
    gap:12px;
    padding:12px 15px;
    border-radius:10px;
    cursor:pointer;
    margin-bottom:10px;
    transition:.3s;
}

.nav-list li:hover{
    background:#EFF6FF;
}

.active{
    background:#2563EB;
    color:white;
}

.profile{
    display:flex;
    align-items:center;
    gap:12px;
    border-top:1px solid #E2E8F0;
    padding-top:20px;
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
</style>