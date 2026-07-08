<template>

    <DashboardLayout role="admin">

        <div class="d-flex justify-content-between align-items-center mb-4">

            <div>
                <h2>Companies Management</h2>
                <p class="text-muted">
                    Approve and manage company profiles.
                </p>
            </div>

            <input
                type="text"
                class="form-control w-25"
                placeholder="Search Company..."
            >

        </div>

        <div class="card">

            <div class="card-body">

                <table class="table table-hover align-middle">

                    <thead>

                        <tr>
                            <th>Company</th>
                            <th>Industry</th>
                            <th>Location</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>

                    </thead>

                    <tbody>

                        <tr>

                            <td>Google</td>
                            <td>Technology</td>
                            <td>Bangalore</td>

                            <td>
                                <span class="badge bg-warning text-dark">
                                    Pending
                                </span>
                            </td>

                            <td>

                                <button class="btn btn-success btn-sm me-2">
                                    Approve
                                </button>

                                <button class="btn btn-danger btn-sm">
                                    Reject
                                </button>

                            </td>

                        </tr>

                        <tr>

                            <td>Microsoft</td>
                            <td>Technology</td>
                            <td>Hyderabad</td>

                            <td>
                                <span class="badge bg-success">
                                    Approved
                                </span>
                            </td>

                            <td>

                                <button class="btn btn-warning btn-sm me-2">
                                    View
                                </button>

                                <button class="btn btn-danger btn-sm">
                                    Blacklist
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