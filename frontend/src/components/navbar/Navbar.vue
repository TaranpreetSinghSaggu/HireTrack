<template>

    <nav class="navbar navbar-expand-lg bg-white shadow-sm">

        <div class="container-fluid">

            <!-- Logo -->

            <RouterLink
                to="/"
                class="navbar-brand fw-bold">

                HireTrack

            </RouterLink>


            <form class="d-flex w-50">

                <input
                    class="form-control"
                    type="search"
                    placeholder="Search...">

            </form>

            <div class="d-flex align-items-center">

                <!-- Notification -->

                <button class="btn me-2">

                    <i class="bi bi-bell fs-5"></i>

                </button>


                <button class="btn btn-light">

                    <i class="bi bi-person-circle me-2"></i>

                    Student

                </button>

            </div>

        </div>

    </nav>

</template>

<script setup>

import { RouterLink } from "vue-router"

</script>

<style scoped>

.navbar{

    height:70px;

}

.navbar-brand{

    color:var(--primary);

    font-size:24px;

}

.form-control{

    border-radius:20px;

}

</style>