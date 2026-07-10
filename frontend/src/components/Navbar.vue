<script setup>
</script>

<template>
    <nav class="navbar navbar-expand-lg bg-white shadow-sm">
        <div class="container">
            <RouterLink class="navbar-brand fw-bold text-primary" to="/">AllClub</RouterLink>
            <div class="ms-auto d-flex gap-2">
                <RouterLink class="btn btn-outline-primary" to="/login">Login</RouterLink>
                <RouterLink class="btn btn-primary" to="/register">Register</RouterLink>
            </div>
        </div>
    </nav>
</template>

<style scoped>
.navbar{
    padding:12px 0;
}

.navbar-brand{
    font-size:1.7rem !important;
    letter-spacing:.5px;
}
</style>