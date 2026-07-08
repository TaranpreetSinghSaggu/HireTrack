<template>

    <DashboardLayout role="admin">

        <div class="d-flex justify-content-between align-items-center mb-4">

            <div>
                <h2>Students Management</h2>
                <p class="text-muted">
                    View and manage all registered students.
                </p>
            </div>

            <input
                type="text"
                class="form-control w-25"
                placeholder="Search Student..."
            >

        </div>

        <div class="card">

            <div class="card-body">

                <table class="table table-hover align-middle">

                    <thead>

                        <tr>
                            <th>Name</th>
                            <th>College</th>
                            <th>CGPA</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>

                    </thead>

                    <tbody>

                        <tr>

                            <td>Taranpreet Singh</td>
                            <td>GTBIT</td>
                            <td>8.7</td>

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
                                    Deactivate
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