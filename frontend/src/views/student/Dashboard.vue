<template>

    <DashboardLayout role="student">

        <!-- Welcome -->

        <div class="mb-4">

            <h2>

                Welcome Back 👋

            </h2>

            <p class="text-muted">

                Find your dream placement opportunity.

            </p>

        </div>

        <!-- Dashboard Cards -->

        <div class="row g-4 mb-4">

            <div class="col-md-3">

                <DashboardCard
                    title="Applications"
                    :count="12"
                    icon="bi bi-file-earmark-text"
                />

            </div>

            <div class="col-md-3">

                <DashboardCard
                    title="Interviews"
                    :count="2"
                    icon="bi bi-calendar-event"
                />

            </div>

            <div class="col-md-3">

                <DashboardCard
                    title="Selected"
                    :count="1"
                    icon="bi bi-check-circle"
                />

            </div>

            <div class="col-md-3">

                <DashboardCard
                    title="Placed"
                    :count="0"
                    icon="bi bi-trophy"
                />

            </div>

        </div>

        <!-- Recent Jobs -->

        <div class="card mb-4">

            <div class="card-body">

                <h5>Recent Job Openings</h5>

                <hr>

                <p>
                    <strong>Google</strong> • SDE Intern • Bangalore
                </p>

                <p>
                    <strong>Microsoft</strong> • Software Engineer • Hyderabad
                </p>

                <p>
                    <strong>Adobe</strong> • Backend Developer • Noida
                </p>

            </div>

        </div>

        <!-- Notifications -->

        <div class="card">

            <div class="card-body">

                <h5>Latest Notifications</h5>

                <hr>

                <ul>

                    <li>Interview with Google tomorrow.</li>

                    <li>Resume viewed by Microsoft.</li>

                    <li>Amazon posted a new opportunity.</li>

                </ul>

            </div>

        </div>

    </DashboardLayout>

</template>

<script setup>

import DashboardLayout from "../../layouts/DashboardLayout.vue"
import DashboardCard from "../../components/cards/DashboardCard.vue"

</script>

<style scoped>

h2{

    font-weight:600;

}

</style>