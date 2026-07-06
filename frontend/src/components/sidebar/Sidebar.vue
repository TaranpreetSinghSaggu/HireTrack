<template>

    <div class="sidebar">

        <ul class="nav flex-column">

            <li
                class="nav-item"
                v-for="item in menuItems"
                :key="item.name">

                <RouterLink
                    :to="item.path"
                    class="nav-link">

                    <i :class="item.icon"></i>

                    {{ item.name }}

                </RouterLink>

            </li>

        </ul>

    </div>

</template>

<script setup>

import { RouterLink } from "vue-router";

const menuItems = [

    {
        name:"Dashboard",
        path:"/student/dashboard",
        icon:"bi bi-speedometer2"
    },

    {
        name:"Jobs",
        path:"/student/jobs",
        icon:"bi bi-briefcase"
    },

    {
        name:"Applications",
        path:"/student/applications",
        icon:"bi bi-file-earmark-text"
    },

    {
        name:"Profile",
        path:"/student/profile",
        icon:"bi bi-person"
    }

]

</script>

<style scoped>

.sidebar{

    background:white;

    min-height:100vh;

    border-right:1px solid var(--border);

}

.nav-link{

    color:var(--text);

    padding:15px 20px;

}

.nav-link:hover{

    background:#EEF5FF;

    color:var(--primary);

}

.router-link-active{

    background:var(--primary);

    color:white !important;

}

i{

    margin-right:10px;

}

</style>