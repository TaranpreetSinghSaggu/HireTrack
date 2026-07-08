<template>

    <div class="sidebar">

        <ul class="nav flex-column">

            <li
                class="nav-item"
                v-for="item in menuItems"
                :key="item.name"
            >

                <RouterLink
                    :to="item.path"
                    class="nav-link"
                >

                    <i :class="item.icon"></i>

                    {{ item.name }}

                </RouterLink>

            </li>

        </ul>

    </div>

</template>

<script setup>

import { computed } from "vue"
import { RouterLink } from "vue-router"

const props = defineProps({

    role: {
        type: String,
        default: "student"
    }

})

const studentMenu = [

    {
        name: "Dashboard",
        path: "/student/dashboard",
        icon: "bi bi-speedometer2"
    },

    {
        name: "Jobs",
        path: "/student/jobs",
        icon: "bi bi-briefcase"
    },

    {
        name: "Applications",
        path: "/student/applications",
        icon: "bi bi-file-earmark-text"
    },

    {
        name: "Profile",
        path: "/student/profile",
        icon: "bi bi-person"
    }

]

const companyMenu = [

    {
        name: "Dashboard",
        path: "/company/dashboard",
        icon: "bi bi-speedometer2"
    },

    {
        name: "Jobs",
        path: "/company/jobs",
        icon: "bi bi-briefcase"
    },

    {
        name: "Applicants",
        path: "/company/applicants",
        icon: "bi bi-people"
    },

    {
        name: "Interviews",
        path: "/company/interviews",
        icon: "bi bi-calendar-event"
    }

]

const adminMenu = [

    {
        name: "Dashboard",
        path: "/admin/dashboard",
        icon: "bi bi-speedometer2"
    },

    {
        name: "Students",
        path: "/admin/students",
        icon: "bi bi-mortarboard"
    },

    {
        name: "Companies",
        path: "/admin/companies",
        icon: "bi bi-building"
    },

    {
        name: "Jobs",
        path: "/admin/jobs",
        icon: "bi bi-briefcase"
    },

    {
        name: "Applications",
        path: "/admin/applications",
        icon: "bi bi-file-earmark-text"
    }

]

const menuItems = computed(() => {

    if (props.role === "company") {
        return companyMenu
    }

    if (props.role === "admin") {
        return adminMenu
    }

    return studentMenu

})

</script>

<style scoped>

.sidebar{

    background: white;
    min-height: 100vh;
    border-right: 1px solid var(--border);

}

.nav-link{

    color: var(--text);
    padding: 15px 20px;

}

.nav-link:hover{

    background: #EEF5FF;
    color: var(--primary);

}

.router-link-active{

    background: var(--primary);
    color: white !important;

}

i{

    margin-right: 10px;

}

</style>