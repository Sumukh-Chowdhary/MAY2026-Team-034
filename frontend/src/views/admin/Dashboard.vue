<script setup>
import Sidebar from '../../components/Sidebar.vue'
</script>

<template>
    <div class="dashboard">
        <Sidebar />

        <main class="content">
            <h2 class="fw-bold mb-4">Admin Dashboard</h2>
            <div class="row g-4">
                <div class="col-md-3">
                    <div class="card stat-card">
                        <h5>Total Users</h5>
                        <h2>5</h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stat-card">
                        <h5>Faculty</h5>
                        <h2>2</h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stat-card">
                        <h5>Students</h5>
                        <h2>2</h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stat-card">
                        <h5>Clubs</h5>
                        <h2>8</h2>
                    </div>
                </div>
            </div>
            <div class="card analytics-card mt-4">
                <h4 class="mb-3">Website Analytics</h4>
                <div class="placeholder">Analytics / Charts will be displayed here</div>
            </div>
        </main>
    </div>
</template>

<style scoped>
.dashboard{
    display:flex;
    background:#F8FAFC;
    min-height:100vh;
}

.content{
    margin-left:250px;
    padding:35px;
    width:100%;
}

.stat-card{
    border:none;
    border-radius:18px;
    padding:25px;
    box-shadow:0 8px 20px rgba(0,0,0,.05);
}

.stat-card h5{
    color:#64748B;
}

.stat-card h2{
    color:#2563EB;
    font-weight:700;
}

.analytics-card{
    border:none;
    border-radius:18px;
    padding:30px;
    box-shadow:0 8px 20px rgba(0,0,0,.05);
}

.placeholder{
    height:350px;
    border:2px dashed #CBD5E1;
    border-radius:12px;
    display:flex;
    justify-content:center;
    align-items:center;
    color:#64748B;
}
</style>