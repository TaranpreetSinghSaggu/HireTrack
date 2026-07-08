<template>

    <DashboardLayout role="company">

        <div class="d-flex justify-content-between align-items-center mb-4">

            <div>

                <h2>Interview Schedule</h2>

                <p class="text-muted">
                    Manage upcoming interviews.
                </p>

            </div>

            <button class="btn btn-primary">

                <i class="bi bi-calendar-plus me-2"></i>

                Schedule Interview

            </button>

        </div>

        <div class="card">

            <div class="card-body">

                <table class="table table-hover align-middle">

                    <thead>

                        <tr>

                            <th>Student</th>
                            <th>Position</th>
                            <th>Date</th>
                            <th>Time</th>
                            <th>Status</th>

                        </tr>

                    </thead>

                    <tbody>

                        <tr>

                            <td>Taranpreet Singh</td>
                            <td>Backend Developer</td>
                            <td>10 July 2026</td>
                            <td>11:00 AM</td>

                            <td>

                                <span class="badge bg-warning text-dark">
                                    Scheduled
                                </span>

                            </td>

                        </tr>

                        <tr>

                            <td>Rahul Sharma</td>
                            <td>ML Intern</td>
                            <td>11 July 2026</td>
                            <td>2:00 PM</td>

                            <td>

                                <span class="badge bg-success">
                                    Completed
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