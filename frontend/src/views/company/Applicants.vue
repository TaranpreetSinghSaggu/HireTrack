<template>

    <DashboardLayout role="company">

        <h2 class="mb-4">
            Applicants
        </h2>

        <div class="card">

            <div class="card-body">

                <table class="table table-hover align-middle">

                    <thead>

                        <tr>

                            <th>Name</th>
                            <th>CGPA</th>
                            <th>Skills</th>
                            <th>Resume</th>
                            <th>Actions</th>

                        </tr>

                    </thead>

                    <tbody>

                        <tr>

                            <td>Taranpreet Singh</td>

                            <td>8.7</td>

                            <td>
                                Python, Flask, Vue
                            </td>

                            <td>

                                <button class="btn btn-sm btn-outline-secondary">
                                    View Resume
                                </button>

                            </td>

                            <td>

                                <button class="btn btn-success btn-sm me-2">
                                    Shortlist
                                </button>

                                <button class="btn btn-danger btn-sm">
                                    Reject
                                </button>

                            </td>

                        </tr>

                        <tr>

                            <td>Rahul Sharma</td>

                            <td>8.3</td>

                            <td>
                                Java, Spring Boot
                            </td>

                            <td>

                                <button class="btn btn-sm btn-outline-secondary">
                                    View Resume
                                </button>

                            </td>

                            <td>

                                <button class="btn btn-success btn-sm me-2">
                                    Shortlist
                                </button>

                                <button class="btn btn-danger btn-sm">
                                    Reject
                                </button>

                            </td>

                        </tr>

                    </tbody>

                </table>

            </div>

        </div>

    </DashboardLayout>

</template>

<script setup>

import DashboardLayout from "../../layouts/DashboardLayout.vue"

</script>