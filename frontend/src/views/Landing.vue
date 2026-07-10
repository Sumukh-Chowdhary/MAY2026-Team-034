<script setup>
import hero from '@/assets/hero.png'
</script>

<template>
  <section class="hero">
    <div class="container">
      <div class="row align-items-center gy-5">
        <div class="col-lg-6">
          <h1 class="display-3 fw-bold">Discover Clubs.<br>Build Connections.</h1>
            <p class="lead mt-4">Join exciting clubs, participate in events, collaborate with students and build an active campus community.</p>
              <RouterLink to="/register" class="btn btn-primary btn-lg mt-3 px-4">Get Started</RouterLink>
        </div>
        <div class="col-lg-6 text-center">
          <img :src="hero" class="img-fluid hero-image" alt="Hero">
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero{
    min-height:calc(100vh - 78px);
    display:flex;
    align-items:center;
}

.hero-image{
    max-width:650px;
}

h1{
    color:#1E293B;
}

p{
    color:#64748B;
}
</style>