<script setup>
</script>

<template>
    <section class="login-page">
        <div class="container d-flex justify-content-center align-items-center">
            <div class="card shadow border-0 login-card">
                <div class="card-body p-5">
                    <h2 class="text-center fw-bold mb-4">Login</h2>
                    <div class="mb-3">
                        <label class="form-label">Register Number / Email</label>
                        <input type="text" class="form-control" placeholder="Enter register number or email">
                    </div>
                    <div class="mb-4">
                        <label class="form-label">Password</label>
                        <input type="password"class="form-control" placeholder="Enter password">
                    </div>
                    <button class="btn btn-primary w-100">Login</button>
                    <p class="text-center mt-4 mb-0">Don't have an account?
                        <RouterLink to="/register">Register</RouterLink>
                    </p>
                </div>
            </div>
        </div>
    </section>
</template>

<style scoped>
.login-page{
    min-height:calc(100vh - 150px);
    display:flex;
    align-items:center;
}

.login-card{
    width:100%;
    max-width:430px;
    border-radius:18px;
}
</style>