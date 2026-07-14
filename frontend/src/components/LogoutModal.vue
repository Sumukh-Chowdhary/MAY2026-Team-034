<script setup>
import {Modal} from 'bootstrap'
import {useRouter} from 'vue-router'

const router=useRouter()

function logout(){
    const modalElement=document.getElementById('logoutModal')
    const modal=Modal.getInstance(modalElement)
    modal.hide()
    setTimeout(()=>{
        router.push('/login')
    },200)
}
</script>

<template>
    <div class="modal fade" id="logoutModal" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Logout</h5>
                    <button class="btn-close"data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="logout-icon"><i class="bi bi-box-arrow-right"></i></div>
                    <h4 class="fw-bold mt-3">Logout Confirmation</h4>
                    <p class="text-secondary mt-2 mb-0">Are you sure you want to logout from AllClub?</p>
                </div>
                <div class="modal-footer justify-content-center">
                    <button class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button class="btn btn-danger" @click="logout">Logout</button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.modal-content{
    border:none;
    border-radius:18px;
}

.modal-header{
    border-bottom:none;
}

.modal-body{
    text-align:center;
    padding-bottom:10px;
}

.modal-footer{
    border-top:none;
    padding-bottom:25px;
}

.logout-icon{
    width:70px;
    height:70px;
    border-radius:50%;
    background:#FEF2F2;
    color:#DC2626;
    display:flex;
    justify-content:center;
    align-items:center;
    margin:auto;
    font-size:2rem;
}
</style>