import { reactive } from 'vue'

const state = reactive({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null
})

export function useAuthStore() {
    return {
        get user() { return state.user },
        get token() { return state.token },
        get isLoggedIn() { return !!state.token },
        get isAdmin() { return state.user?.role === 'ADMIN' },
        get isFaculty() { return state.user?.role === 'FACULTY' },
        get isStudent() { return state.user?.role === 'STUDENT' },
        setUser(user, token) {
            state.user = user
            state.token = token
            localStorage.setItem("user", JSON.stringify(user))
            localStorage.setItem("token", token)
        },
        logout() {
            state.user = null
            state.token = null
            localStorage.removeItem("user")
            localStorage.removeItem("token")
        }
    }
}