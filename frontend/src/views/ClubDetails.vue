<script setup>
import { computed } from "vue"
import { useRoute } from "vue-router"
import { getCurrentUser, isLoggedIn } from "@/services/authService"

import StudentLayout from "@/layouts/StudentLayout.vue"
import FacultyLayout from "@/layouts/FacultyLayout.vue"
import AdminLayout from "@/layouts/AdminLayout.vue"

import ClubContent from "@/components/club/ClubContent.vue"

const loggedIn = isLoggedIn()
const user = getCurrentUser()
const route = useRoute()

const clubId = Number(route.params.id)

const Layout = computed(() => {
    switch (user?.role) {
        case "ADMIN":
            return AdminLayout

        case "FACULTY":
            return FacultyLayout

        default:
            return StudentLayout
    }
})
</script>

<template>
    <component
        v-if="loggedIn"
        :is="Layout"
    >
        <ClubContent :club-id="clubId" />
    </component>

    <ClubContent
        v-else
        :club-id="clubId"
    />
</template>