<template>

    <!-- Hero Section -->

    <div class="container-fluid bg-white py-5">

        <div class="container">

            <div class="row align-items-center min-vh-100">

                <!-- Left Side -->

                <div class="col-lg-6">

                    <h1 class="display-4 fw-bold mb-4">

                        Launch Your Career with

                        <span class="text-primary">

                            HireTrack

                        </span>

                    </h1>

                    <p class="lead text-muted mb-4">

                        Connecting students, companies and opportunities
                        through one modern placement management platform.

                    </p>

                    <div class="d-flex gap-3">

                        <RouterLink
                            to="/register/student"
                            class="btn btn-primary btn-lg"
                        >
                            Get Started
                        </RouterLink>

                        <RouterLink
                            to="/login"
                            class="btn btn-outline-primary btn-lg"
                        >
                            Login
                        </RouterLink>

                    </div>

                </div>

                <!-- Right Side -->

                <div class="col-lg-6 text-center">

                    <i
                        class="bi bi-mortarboard-fill text-primary"
                        style="font-size: 250px;"
                    ></i>

                </div>

            </div>

        </div>

    </div>

    <!-- Statistics -->

    <div class="container py-5">

        <div class="row text-center">

            <div class="col-md-3">

                <h2 class="text-primary fw-bold">

                    1000+

                </h2>

                <p class="text-muted">

                    Students

                </p>

            </div>

            <div class="col-md-3">

                <h2 class="text-primary fw-bold">

                    150+

                </h2>

                <p class="text-muted">

                    Companies

                </p>

            </div>

            <div class="col-md-3">

                <h2 class="text-primary fw-bold">

                    500+

                </h2>

                <p class="text-muted">

                    Placements

                </p>

            </div>

            <div class="col-md-3">

                <h2 class="text-primary fw-bold">

                    95%

                </h2>

                <p class="text-muted">

                    Placement Rate

                </p>

            </div>

        </div>

    </div>

    <!-- Features -->

    <div class="container py-5">

        <h2 class="text-center mb-5">

            Platform Features

        </h2>

        <div class="row g-4">

            <div class="col-md-4">

                <div class="card h-100 shadow-sm">

                    <div class="card-body text-center">

                        <i
                            class="bi bi-person-workspace text-primary fs-1"
                        ></i>

                        <h5 class="mt-3">

                            Student Portal

                        </h5>

                        <p class="text-muted">

                            Apply for jobs, track applications and manage
                            interviews.

                        </p>

                    </div>

                </div>

            </div>

            <div class="col-md-4">

                <div class="card h-100 shadow-sm">

                    <div class="card-body text-center">

                        <i
                            class="bi bi-building text-primary fs-1"
                        ></i>

                        <h5 class="mt-3">

                            Company Dashboard

                        </h5>

                        <p class="text-muted">

                            Post jobs, review applicants and schedule interviews.

                        </p>

                    </div>

                </div>

            </div>

            <div class="col-md-4">

                <div class="card h-100 shadow-sm">

                    <div class="card-body text-center">

                        <i
                            class="bi bi-shield-check text-primary fs-1"
                        ></i>

                        <h5 class="mt-3">

                            Admin Control

                        </h5>

                        <p class="text-muted">

                            Manage students, companies and placement activities.

                        </p>

                    </div>

                </div>

            </div>

        </div>

    </div>

    <!-- Recruiters -->

    <div class="container py-5">

        <h2 class="text-center mb-5">

            Trusted Recruiters

        </h2>

        <div class="row text-center">

            <div class="col-md-2">
                <h5>Google</h5>
            </div>

            <div class="col-md-2">
                <h5>Microsoft</h5>
            </div>

            <div class="col-md-2">
                <h5>Adobe</h5>
            </div>

            <div class="col-md-2">
                <h5>Amazon</h5>
            </div>

            <div class="col-md-2">
                <h5>TCS</h5>
            </div>

            <div class="col-md-2">
                <h5>Infosys</h5>
            </div>

        </div>

    </div>

    <!-- Footer -->

    <footer class="bg-dark text-white text-center py-4">

        <p class="mb-0">

            © 2026 HireTrack Placement Portal

        </p>

    </footer>

</template>

<script setup>

import { RouterLink } from "vue-router"

</script>