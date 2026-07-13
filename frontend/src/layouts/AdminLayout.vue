<script setup>
import {ref} from 'vue'
import Sidebar from '../components/Sidebar.vue'

const collapsed=ref(false)
</script>

<template>
    <div
        class="dashboard" :class="{collapsed:collapsed}">
        <Sidebar @toggle="collapsed=$event"/>
        <main class="page-content">
            <slot/>
        </main>
    </div>
</template>

<style scoped>
.dashboard{
    display:flex;
    min-height:100vh;
    background:#F8FAFC;
}

.page-content{
    margin-left:250px;
    width:calc(100% - 250px);
    padding:35px;
    transition:all .3s ease;
}

.dashboard.collapsed .page-content{
    margin-left:75px;
    width:calc(100% - 75px);
}
</style>