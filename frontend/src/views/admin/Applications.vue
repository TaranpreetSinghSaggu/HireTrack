<template>

    <DashboardLayout role="admin">

        <h2 class="mb-4">
            Applications Management
        </h2>

        <div class="card">

            <div class="card-body">

                <table class="table table-hover align-middle">

                    <thead>

                        <tr>
                            <th>Student</th>
                            <th>Company</th>
                            <th>Position</th>
                            <th>Status</th>
                            <th>Date</th>
                        </tr>

                    </thead>

                    <tbody>

                        <tr>

                            <td>Taranpreet Singh</td>
                            <td>Google</td>
                            <td>SDE Intern</td>

                            <td>
                                <span class="badge bg-primary">
                                    Applied
                                </span>
                            </td>

                            <td>08 Jul 2026</td>

                        </tr>

                        <tr>

                            <td>Rahul Sharma</td>
                            <td>Microsoft</td>
                            <td>Backend Developer</td>

                            <td>
                                <span class="badge bg-warning text-dark">
                                    Interview
                                </span>
                            </td>

                            <td>06 Jul 2026</td>

                        </tr>

                        <tr>

                            <td>Priya Gupta</td>
                            <td>Adobe</td>
                            <td>ML Engineer</td>

                            <td>
                                <span class="badge bg-success">
                                    Selected
                                </span>
                            </td>

                            <td>04 Jul 2026</td>

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