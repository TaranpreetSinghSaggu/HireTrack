<template>

    <DashboardLayout role="student">

        <h2 class="mb-4">
            Student Profile
        </h2>

        <div class="card">

            <div class="card-body">

                <div class="row g-3">

                    <div class="col-md-6">

                        <label class="form-label">
                            Full Name
                        </label>

                        <input
                            type="text"
                            class="form-control"
                            value="Taranpreet Singh"
                        >

                    </div>

                    <div class="col-md-6">

                        <label class="form-label">
                            Email
                        </label>

                        <input
                            type="email"
                            class="form-control"
                            value="student@gmail.com"
                        >

                    </div>

                    <div class="col-md-6">

                        <label class="form-label">
                            College
                        </label>

                        <input
                            type="text"
                            class="form-control"
                            value="GTBIT"
                        >

                    </div>

                    <div class="col-md-6">

                        <label class="form-label">
                            CGPA
                        </label>

                        <input
                            type="text"
                            class="form-control"
                            value="8.7"
                        >

                    </div>

                    <div class="col-12">

                        <label class="form-label">
                            Skills
                        </label>

                        <textarea
                            rows="3"
                            class="form-control"
                        >Python, Flask, Vue, Machine Learning</textarea>

                    </div>

                    <div class="col-12">

                        <button class="btn btn-primary">
                            Update Profile
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