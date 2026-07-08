<template>

    <DashboardLayout role="student">

        <h2 class="mb-4">
            My Applications
        </h2>

        <div class="card">

            <div class="card-body">

                <table class="table table-hover">

                    <thead>

                        <tr>

                            <th>Company</th>
                            <th>Position</th>
                            <th>Date</th>
                            <th>Status</th>

                        </tr>

                    </thead>

                    <tbody>

                        <tr>

                            <td>Google</td>
                            <td>SDE Intern</td>
                            <td>07 Jul 2026</td>

                            <td>
                                <span class="badge bg-warning">
                                    Shortlisted
                                </span>
                            </td>

                        </tr>

                        <tr>

                            <td>Microsoft</td>
                            <td>Backend Developer</td>
                            <td>05 Jul 2026</td>

                            <td>
                                <span class="badge bg-primary">
                                    Applied
                                </span>
                            </td>

                        </tr>

                        <tr>

                            <td>Adobe</td>
                            <td>ML Engineer</td>
                            <td>03 Jul 2026</td>

                            <td>
                                <span class="badge bg-success">
                                    Selected
                                </span>
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