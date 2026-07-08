<template>

    <DashboardLayout role="admin">

        <!-- Welcome -->

        <div class="mb-4">

            <h2>

                Welcome Company 👋

            </h2>

            <p class="text-muted">

                Manage your job postings and applicants.

            </p>

        </div>

        <!-- Dashboard Cards -->

        <div class="row g-4 mb-4">

            <div class="col-md-3">

                <DashboardCard
                    title="Jobs Posted"
                    :count="8"
                    icon="bi bi-briefcase"
                />

            </div>

            <div class="col-md-3">

                <DashboardCard
                    title="Applications"
                    :count="156"
                    icon="bi bi-file-earmark-text"
                />

            </div>

            <div class="col-md-3">

                <DashboardCard
                    title="Shortlisted"
                    :count="35"
                    icon="bi bi-check-circle"
                />

            </div>

            <div class="col-md-3">

                <DashboardCard
                    title="Interviews"
                    :count="12"
                    icon="bi bi-calendar-event"
                />

            </div>

        </div>

        <!-- Recent Job Posts -->

        <div class="card mb-4">

            <div class="card-body">

                <h5>

                    Recent Job Posts

                </h5>

                <hr>

                <p>

                    <strong>Backend Developer</strong>

                    • Delhi

                    • 25 Applications

                </p>

                <p>

                    <strong>Frontend Developer</strong>

                    • Bangalore

                    • 18 Applications

                </p>

                <p>

                    <strong>Machine Learning Intern</strong>

                    • Remote

                    • 40 Applications

                </p>

            </div>

        </div>

        <!-- Upcoming Interviews -->

        <div class="card">

            <div class="card-body">

                <h5>

                    Upcoming Interviews

                </h5>

                <hr>

                <ul>

                    <li>

                        Rahul Sharma • 10 July • 11:00 AM

                    </li>

                    <li>

                        Priya Gupta • 10 July • 2:00 PM

                    </li>

                    <li>

                        Aman Singh • 11 July • 10:30 AM

                    </li>

                </ul>

            </div>

        </div>

    </DashboardLayout>

</template>

<script setup>

import DashboardLayout from "../../layouts/DashboardLayout.vue";
import DashboardCard from "../../components/cards/DashboardCard.vue";

</script>

<style scoped>

h2{

    font-weight:600;

}

</style>