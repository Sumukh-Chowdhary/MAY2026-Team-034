<script setup>
</script>

<template>
  <nav class="navbar navbar-expand-lg bg-white shadow-sm sticky-top">
    <div class="container">

      <RouterLink class="navbar-brand" to="/">
        AllClub
      </RouterLink>

      <div class="nav-actions">

        <RouterLink
          class="nav-item"
          to="/clubs"
        >
          Clubs
        </RouterLink>

        <RouterLink
          class="btn btn-outline-primary"
          to="/login"
        >
          Login
        </RouterLink>

        <RouterLink
          class="btn btn-primary"
          to="/register"
        >
          Register
        </RouterLink>

      </div>

    </div>
  </nav>
</template>

<style scoped>

.navbar{
    padding:14px 0;
}

.navbar-brand{

    font-size:1.75rem;
    font-weight:800;
    color:#2563eb;
    text-decoration:none;
    letter-spacing:.5px;

}

.nav-actions{

    display:flex;
    align-items:center;
    gap:18px;

}

.nav-item{

    text-decoration:none;
    color:#374151;
    font-weight:600;
    padding-bottom:4px;
    transition:.25s;

}

.nav-item:hover{

    color:#2563eb;

}

.nav-item.router-link-active{

    color:#2563eb;
    border-bottom:2px solid #2563eb;

}

.btn{

    border-radius:10px;
    font-weight:600;
    padding:8px 18px;

}

</style>