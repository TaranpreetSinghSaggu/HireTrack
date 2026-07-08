<template>

    <DashboardLayout role="student">

        <div class="d-flex justify-content-between align-items-center mb-4">

            <div>
                <h2>Available Jobs</h2>
                <p class="text-muted">
                    Discover opportunities matching your skills.
                </p>
            </div>

            <button class="btn btn-primary">
                <i class="bi bi-funnel"></i>
                Filters
            </button>

        </div>

        <!-- Search -->

        <div class="card mb-4">

            <div class="card-body">

                <div class="row">

                    <div class="col-md-8">

                        <input
                            type="text"
                            class="form-control"
                            placeholder="Search by company, role or skill"
                        >

                    </div>

                    <div class="col-md-4">

                        <button class="btn btn-primary w-100">
                            Search
                        </button>

                    </div>

                </div>

            </div>

        </div>

        <!-- Jobs -->

        <div class="row g-4">

            <div class="col-md-6">

                <div class="card h-100 shadow-sm">

                    <div class="card-body">

                        <h5>Software Engineer Intern</h5>

                        <p class="text-muted mb-2">
                            Google • Bangalore
                        </p>

                        <span class="badge bg-primary me-2">
                            Python
                        </span>

                        <span class="badge bg-primary me-2">
                            SQL
                        </span>

                        <span class="badge bg-primary">
                            Machine Learning
                        </span>

                        <hr>

                        <p>
                            Package: ₹12 LPA
                        </p>

                        <button class="btn btn-success w-100">
                            Apply Now
                        </button>

                    </div>

                </div>

            </div>

            <div class="col-md-6">

                <div class="card h-100 shadow-sm">

                    <div class="card-body">

                        <h5>Backend Developer</h5>

                        <p class="text-muted mb-2">
                            Microsoft • Hyderabad
                        </p>

                        <span class="badge bg-primary me-2">
                            Flask
                        </span>

                        <span class="badge bg-primary me-2">
                            Redis
                        </span>

                        <span class="badge bg-primary">
                            Docker
                        </span>

                        <hr>

                        <p>
                            Package: ₹18 LPA
                        </p>

                        <button class="btn btn-success w-100">
                            Apply Now
                        </button>

                    </div>

                </div>

            </div>

        </div>

    </DashboardLayout>

</template>

<script setup>

import DashboardLayout from "../../layouts/DashboardLayout.vue"

</script>