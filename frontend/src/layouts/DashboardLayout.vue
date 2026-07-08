<template>

    <div class="dashboard">

        <Navbar />

        <div class="container-fluid">

            <div class="row">

                <div class="col-md-2 p-0">

                    <Sidebar :role="role" />

                </div>

                <div class="col-md-10 p-4">

                    <slot></slot>

                </div>

            </div>

        </div>

    </div>

</template>

<script setup>

import Navbar from "../components/navbar/Navbar.vue"
import Sidebar from "../components/sidebar/Sidebar.vue"

defineProps({

    role: {
        type: String,
        default: "student"
    }

})

</script>

<style scoped>

.dashboard{
    background: var(--background);
    min-height: 100vh;
}

</style>