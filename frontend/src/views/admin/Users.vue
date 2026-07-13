<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AdminLayout from '../../layouts/AdminLayout.vue'
import initialUsers from '../../data/users.json'

const router = useRouter()
const users = ref([])
const activeTab = ref('students') // 'students' or 'faculty'
const search = ref('')

onMounted(() => {
    const stored = localStorage.getItem('allclub_users')
    if (stored) {
        users.value = JSON.parse(stored)
    } else {
        // Initialize with default blocked: false
        users.value = initialUsers.map(user => ({
            ...user,
            blocked: user.blocked || false
        }))
        localStorage.setItem('allclub_users', JSON.stringify(users.value))
    }
})

const studentCount = computed(() => users.value.filter(u => u.role === 'STUDENT').length)
const facultyCount = computed(() => users.value.filter(u => u.role === 'FACULTY').length)

const filteredUsers = computed(() => {
    const roleToFilter = activeTab.value === 'students' ? 'STUDENT' : 'FACULTY'
    return users.value.filter(user => {
        if (user.role !== roleToFilter) return false
        
        const q = search.value.trim().toLowerCase()
        if (!q) return true
        
        return user.name.toLowerCase().includes(q) ||
               user.registerNumber.toLowerCase().includes(q) ||
               user.email.toLowerCase().includes(q)
    })
})

function viewUserDetails(userId) {
    router.push(`/admin/users/${userId}`)
}

function toggleUserBlock(user) {
    user.blocked = !user.blocked
    // Update local storage
    localStorage.setItem('allclub_users', JSON.stringify(users.value))
}
</script>

<template>
    <AdminLayout>
        <section class="users-page">
            <div class="d-flex justify-content-between align-items-center flex-wrap gap-3 mb-4">
                <div>
                    <h2 class="fw-bold mb-1">Users</h2>
                    <p class="text-secondary mb-0">Manage student and faculty accounts.</p>
                </div>

                <input
                    v-model="search"
                    class="form-control search-box"
                    placeholder="Search users by name, ID or email...">
            </div>

            <div class="toggle-buttons mb-4">
                <button
                    class="btn"
                    :class="activeTab==='students' ? 'btn-primary' : 'btn-outline-primary'"
                    @click="activeTab='students'">Students
                    <span class="badge bg-light text-dark ms-2">{{ studentCount }}</span>
                </button>

                <button
                    class="btn"
                    :class="activeTab==='faculty' ? 'btn-primary' : 'btn-outline-primary'"
                    @click="activeTab='faculty'">Faculty
                    <span class="badge bg-light text-dark ms-2">{{ facultyCount }}</span>
                </button>
            </div>

            <div class="card border-0 shadow-sm user-table-card">
                <div class="card-body p-0">
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>Name</th>
                                    <th>Register Number</th>
                                    <th>Email</th>
                                    <th>Status</th>
                                    <th class="text-end">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="user in filteredUsers" :key="user.id">
                                    <td>
                                        <div class="d-flex align-items-center gap-3">
                                            <div class="avatar-circle">{{ user.name.charAt(0) }}</div>
                                            <span class="fw-medium">{{ user.name }}</span>
                                        </div>
                                    </td>
                                    <td>{{ user.registerNumber }}</td>
                                    <td>{{ user.email }}</td>
                                    <td>
                                        <span class="badge" :class="user.blocked ? 'bg-danger-subtle text-danger' : 'bg-success-subtle text-success'">
                                            {{ user.blocked ? 'Blocked' : 'Active' }}
                                        </span>
                                    </td>
                                    <td class="text-end">
                                        <div class="d-flex justify-content-end gap-2">
                                            <button @click="viewUserDetails(user.id)" class="btn btn-outline-primary btn-sm px-3">
                                                View
                                            </button>
                                            <button @click="toggleUserBlock(user)" class="btn btn-sm px-3" :class="user.blocked ? 'btn-success' : 'btn-outline-danger'">
                                                {{ user.blocked ? 'Unblock' : 'Block' }}
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                                <tr v-if="filteredUsers.length === 0">
                                    <td colspan="5" class="text-center py-5 text-secondary">
                                        <i class="bi bi-people display-4 d-block mb-3 text-muted"></i>
                                        <h5 class="fw-bold text-dark">No Users Found</h5>
                                        <p class="mb-0 text-muted small">No users match your criteria.</p>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>
    </AdminLayout>
</template>

<style scoped>
@import "@/assets/css/Users.css";
</style>
