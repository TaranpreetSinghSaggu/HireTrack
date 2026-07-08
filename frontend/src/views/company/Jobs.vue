<template>

    <DashboardLayout role="company">

        <div class="d-flex justify-content-between align-items-center mb-4">

            <div>
                <h2>Manage Jobs</h2>
                <p class="text-muted">
                    Create and manage placement opportunities.
                </p>
            </div>

            <button class="btn btn-primary">
                <i class="bi bi-plus-circle me-2"></i>
                Post New Job
            </button>

        </div>

        <div class="card">

            <div class="card-body">

                <table class="table table-hover align-middle">

                    <thead>

                        <tr>

                            <th>Position</th>
                            <th>Location</th>
                            <th>Salary</th>
                            <th>Status</th>
                            <th>Actions</th>

                        </tr>

                    </thead>

                    <tbody>

                        <tr>

                            <td>Backend Developer</td>
                            <td>Delhi</td>
                            <td>12 LPA</td>

                            <td>
                                <span class="badge bg-success">
                                    Active
                                </span>
                            </td>

                            <td>

                                <button class="btn btn-sm btn-outline-primary me-2">
                                    Edit
                                </button>

                                <button class="btn btn-sm btn-outline-danger">
                                    Close
                                </button>

                            </td>

                        </tr>

                        <tr>

                            <td>Machine Learning Intern</td>
                            <td>Remote</td>
                            <td>18 LPA</td>

                            <td>
                                <span class="badge bg-secondary">
                                    Closed
                                </span>
                            </td>

                            <td>

                                <button class="btn btn-sm btn-outline-primary me-2">
                                    Edit
                                </button>

                                <button class="btn btn-sm btn-outline-danger">
                                    Delete
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