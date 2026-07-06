<template>
  <div class="container-fluid register-page">

    <div class="row justify-content-center align-items-center vh-100">

      <div class="col-md-7 col-lg-6">

        <div class="card shadow">

          <div class="card-body p-4">

            <div class="text-center mb-4">

              <h2 class="fw-bold text-primary">
                HireTrack
              </h2>

              <p class="text-muted">
                Company Registration
              </p>

            </div>


            <div class="mb-3">

              <label class="form-label">
                Company Name
              </label>

              <input
                v-model="companyName"
                type="text"
                class="form-control"
                placeholder="Enter company name"
              >

            </div>


            <div class="mb-3">

              <label class="form-label">
                Company Email
              </label>

              <input
                v-model="email"
                type="email"
                class="form-control"
                placeholder="Enter company email"
              >

            </div>


            <div class="mb-3">

              <label class="form-label">
                HR Contact
              </label>

              <input
                v-model="contact"
                type="text"
                class="form-control"
                placeholder="Enter HR contact"
              >

            </div>


            <div class="mb-3">

              <label class="form-label">
                Website
              </label>

              <input
                v-model="website"
                type="text"
                class="form-control"
                placeholder="Enter company website"
              >

            </div>


            <div class="mb-3">

              <label class="form-label">
                Industry
              </label>

              <input
                v-model="industry"
                type="text"
                class="form-control"
                placeholder="Enter industry"
              >

            </div>


            <div class="mb-3">

              <label class="form-label">
                Location
              </label>

              <input
                v-model="location"
                type="text"
                class="form-control"
                placeholder="Enter company location"
              >

            </div>


            <div class="mb-3">

              <label class="form-label">
                Password
              </label>

              <input
                v-model="password"
                type="password"
                class="form-control"
                placeholder="Enter password"
              >

            </div>



            <div class="mb-4">

              <label class="form-label">
                Confirm Password
              </label>

              <input
                v-model="confirmPassword"
                type="password"
                class="form-control"
                placeholder="Confirm password"
              >

            </div>

            <div class="d-grid">

              <button
                class="btn btn-primary"
                @click="registerCompany"
              >
                Register
              </button>

            </div>

            <hr>

            <div class="text-center">

              Already have an account?

              <RouterLink to="/login">

                Login

              </RouterLink>

            </div>

          </div>

        </div>

      </div>

    </div>

  </div>
</template>

<script setup>

import { ref } from "vue";
import { RouterLink } from "vue-router";

const companyName = ref("");
const email = ref("");
const contact = ref("");
const website = ref("");
const industry = ref("");
const location = ref("");
const password = ref("");
const confirmPassword = ref("");

function registerCompany(){

    console.log(companyName.value);
    console.log(email.value);
    console.log(contact.value);
    console.log(website.value);
    console.log(industry.value);
    console.log(location.value);
    console.log(password.value);
    console.log(confirmPassword.value);

}

</script>

<style scoped>

.register-page{

    background:#F5F7FA;

}

.card{

    border-radius:12px;

}

</style>