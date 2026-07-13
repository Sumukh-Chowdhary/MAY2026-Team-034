<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AdminLayout from '../../layouts/AdminLayout.vue'
import initialUsers from '../../data/users.json'

const route = useRoute()
const router = useRouter()
const user = ref(null)
const usersList = ref([])

onMounted(() => {
    const stored = localStorage.getItem('allclub_users')
    if (stored) {
        usersList.value = JSON.parse(stored)
    } else {
        usersList.value = initialUsers.map(u => ({ ...u, blocked: u.blocked || false }))
        localStorage.setItem('allclub_users', JSON.stringify(usersList.value))
    }
    
    const id = parseInt(route.params.id)
    user.value = usersList.value.find(u => u.id === id)
})

function toggleBlock() {
    if (user.value) {
        user.value.blocked = !user.value.blocked
        // Sync back to usersList
        const index = usersList.value.findIndex(u => u.id === user.value.id)
        if (index !== -1) {
            usersList.value[index] = { ...user.value }
            localStorage.setItem('allclub_users', JSON.stringify(usersList.value))
        }
    }
}

function goBack() {
    router.push('/admin/users')
}
</script>

<template>
    <AdminLayout>
        <section class="user-details-page" v-if="user">
            <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-4">
                <div class="d-flex align-items-center gap-3">
                    <button @click="goBack" class="btn btn-icon-back" aria-label="Back">
                        <i class="bi bi-arrow-left" style="color: #000; font-size: 1.2rem;"></i>
                    </button>
                    <div>
                        <h2 class="fw-bold mb-1">User Profile</h2>
                        <p class="text-secondary mb-0">View and manage detailed profile information.</p>
                    </div>
                </div>
                <button @click="goBack" class="btn btn-outline-secondary px-3">
                    Back to Users
                </button>
            </div>

            <div class="row g-4">
                <div class="col-lg-4">
                    <div class="card border-0 shadow-sm text-center p-4 profile-side-card">
                        <div class="avatar-large mx-auto mb-3">{{ user.name.charAt(0) }}</div>
                        <h4 class="fw-bold mb-1">{{ user.name }}</h4>
                        <p class="text-secondary small mb-3">
                            {{ user.role === 'STUDENT' ? 'Student' : (user.role === 'FACULTY' ? 'Faculty Member' : 'Administrator') }}
                        </p>
                        
                        <div class="mb-3">
                            <span class="badge px-3 py-2" :class="user.blocked ? 'bg-danger-subtle text-danger' : 'bg-success-subtle text-success'">
                                {{ user.blocked ? 'Blocked' : 'Active' }}
                            </span>
                        </div>
                        
                        <hr class="w-100 my-4">
                        
                        <button @click="toggleBlock" class="btn w-100 d-flex align-items-center justify-content-center gap-2" :class="user.blocked ? 'btn-success' : 'btn-danger'">
                            <i class="bi" :class="user.blocked ? 'bi-unlock-fill' : 'bi-slash-circle-fill'"></i>
                            {{ user.blocked ? 'Unblock User' : 'Block User' }}
                        </button>
                    </div>
                </div>
                
                <div class="col-lg-8">
                    <div class="card border-0 shadow-sm p-4 profile-details-card">
                        <h5 class="fw-bold mb-4">Profile Information</h5>
                        
                        <div class="row g-4">
                          <div class="col-md-6">
                              <label class="form-label text-muted small text-uppercase">Full Name</label>
                              <p class="fw-semibold text-dark">{{ user.name }}</p>
                          </div>
                          
                          <div class="col-md-6">
                              <label class="form-label text-muted small text-uppercase">Register Number</label>
                              <p class="fw-semibold text-dark">{{ user.registerNumber }}</p>
                          </div>
                          
                          <div class="col-md-6">
                              <label class="form-label text-muted small text-uppercase">Email Address</label>
                              <p class="fw-semibold text-dark">{{ user.email }}</p>
                          </div>
                          
                          <div class="col-md-6">
                              <label class="form-label text-muted small text-uppercase">Role</label>
                              <p class="fw-semibold text-dark">{{ user.role.charAt(0) + user.role.slice(1).toLowerCase() }}</p>
                          </div>
                          
                          <div class="col-12">
                              <label class="form-label text-muted small text-uppercase">Biography / Description</label>
                              <p class="text-secondary leading-relaxed mb-0">
                                  {{ user.role === 'STUDENT' ? 'Active student participant at AllClub. Interested in collaborating in technology workshops, cultural events, photography, and community service projects.' : 'Experienced faculty coordinator guiding student organizations, evaluating proposed club activities, and organizing guest seminars.' }}
                              </p>
                          </div>

                          <div class="col-md-6">
                              <label class="form-label text-muted small text-uppercase">Joined Date</label>
                              <p class="text-secondary mb-0">January 2026</p>
                          </div>

                          <div class="col-md-6">
                              <label class="form-label text-muted small text-uppercase">Last Login Activity</label>
                              <p class="text-secondary mb-0">Recent (July 2026)</p>
                          </div>
                      </div>
                    </div>
                </div>
            </div>
        </section>
        <section v-else class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-3 text-secondary">Loading profile...</p>
        </section>
    </AdminLayout>
</template>

<style scoped>
@import "@/assets/css/UserDetails.css";
</style>
