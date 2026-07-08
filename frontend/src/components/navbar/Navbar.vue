<template>

<nav class="navbar navbar-expand-lg bg-white border-bottom px-4">

    <!-- Logo -->

    <RouterLink
        to="/"
        class="navbar-brand fw-bold text-primary"
    >

        <i class="bi bi-mortarboard-fill me-2"></i>

        HireTrack

    </RouterLink>

    <!-- Search -->

    <div class="mx-auto w-50">

        <div class="input-group">

            <span class="input-group-text bg-light border-end-0">

                <i class="bi bi-search"></i>

            </span>

            <input
                type="text"
                class="form-control border-start-0"
                placeholder="Search jobs, companies..."
            >

        </div>

    </div>

    <!-- Right Section -->

    <div class="d-flex align-items-center gap-4">

        <i class="bi bi-bell fs-5"></i>

        <div class="dropdown">

            <button
                class="btn btn-light dropdown-toggle"
                data-bs-toggle="dropdown"
            >

                <i class="bi bi-person-circle me-2"></i>

                Profile

            </button>

            <ul class="dropdown-menu dropdown-menu-end">

                <li>
                    <a class="dropdown-item">
                        Profile
                    </a>
                </li>

                <li>
                    <a class="dropdown-item">
                        Settings
                    </a>
                </li>

                <li>
                    <hr class="dropdown-divider">
                </li>

                <li>
                    <a class="dropdown-item text-danger">
                        Logout
                    </a>
                </li>

            </ul>

        </div>

    </div>

</nav>

</template>

<script setup>

import { RouterLink } from "vue-router"

</script>