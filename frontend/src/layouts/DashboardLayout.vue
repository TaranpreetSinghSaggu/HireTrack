<template>

    <div class="dashboard">

        <!-- Navbar -->

        <Navbar />

        <div class="container-fluid">

            <div class="row">

                <!-- Sidebar -->

                <div class="col-md-2 p-0">

                    <Sidebar />

                </div>

                <!-- Page Content -->

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

</script>

<style scoped>

.dashboard{

    background: var(--background);
    min-height: 100vh;

}

</style>