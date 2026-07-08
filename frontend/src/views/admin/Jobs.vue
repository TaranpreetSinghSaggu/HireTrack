<template>

    <DashboardLayout role="admin">

        <h2 class="mb-4">
            Job Management
        </h2>

        <div class="card">

            <div class="card-body">

                <table class="table table-hover align-middle">

                    <thead>

                        <tr>
                            <th>Company</th>
                            <th>Position</th>
                            <th>Salary</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>

                    </thead>

                    <tbody>

                        <tr>

                            <td>Google</td>
                            <td>SDE Intern</td>
                            <td>12 LPA</td>

                            <td>
                                <span class="badge bg-success">
                                    Active
                                </span>
                            </td>

                            <td>

                                <button class="btn btn-sm btn-warning me-2">
                                    View
                                </button>

                                <button class="btn btn-sm btn-danger">
                                    Remove
                                </button>

                            </td>

                        </tr>

                        <tr>

                            <td>Adobe</td>
                            <td>ML Engineer</td>
                            <td>18 LPA</td>

                            <td>
                                <span class="badge bg-secondary">
                                    Closed
                                </span>
                            </td>

                            <td>

                                <button class="btn btn-sm btn-warning me-2">
                                    View
                                </button>

                                <button class="btn btn-sm btn-danger">
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