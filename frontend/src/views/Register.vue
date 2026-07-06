<script setup>
</script>

<template>
    <section class="register-page">
        <div class="container d-flex justify-content-center align-items-center">
            <div class="card shadow border-0 register-card">
                <div class="card-body p-5">
                    <h2 class="text-center fw-bold mb-4">Create Account</h2>
                    <div class="mb-3">
                        <label class="form-label">Full Name</label>
                        <input type="text" class="form-control" placeholder="Enter full name">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Email</label>
                        <input type="email" class="form-control" placeholder="Enter email">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Register Number</label>
                        <input type="text" class="form-control" placeholder="Enter register number">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Password</label>
                        <input type="password" class="form-control" placeholder="Create password">
                    </div>
                    <div class="mb-4">
                        <label class="form-label">Confirm Password</label>
                        <input type="password" class="form-control" placeholder="Confirm password">
                    </div>
                    <button class="btn btn-primary w-100">Register</button>
                    <p class="text-center mt-4 mb-0"> Already have an account?
                        <RouterLink to="/login">Login</RouterLink>
                    </p>
                </div>
            </div>
        </div>
    </section>
</template>

<style scoped>
.register-page{
    padding:50px 0;
    display:flex;
    align-items:center;
}

.register-card{
    width:100%;
    max-width:450px;
    border-radius:18px;
}
</style>