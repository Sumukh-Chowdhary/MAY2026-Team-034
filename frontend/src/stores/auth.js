import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: JSON.parse(localStorage.getItem('user')) || null,
        token: localStorage.getItem('token')
    }),

    getters: {
        isLoggedIn: state => !!state.token,
        isAdmin: state => state.user?.role === 'ADMIN',
        isFaculty: state => state.user?.role === 'FACULTY',
        isStudent: state => state.user?.role === 'STUDENT'
    },

    actions: {
        setUser(user, token){
            this.user = user
            this.token = token
            localStorage.setItem("user", JSON.stringify(user))
            localStorage.setItem("token", token)
        },

        logout(){
            this.user = null
            this.token = null
            localStorage.removeItem("user")
            localStorage.removeItem("token")
        }
    }
})