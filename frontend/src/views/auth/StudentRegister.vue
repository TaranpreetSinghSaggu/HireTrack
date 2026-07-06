<template>
  <div class="container-fluid register-page">

    <div class="row justify-content-center align-items-center vh-100">

      <div class="col-md-6 col-lg-5">

        <div class="card shadow">

          <div class="card-body p-4">


            <div class="text-center mb-4">

              <h2 class="fw-bold text-primary">
                HireTrack
              </h2>

              <p class="text-muted">
                Student Registration
              </p>

            </div>


            <div class="mb-3">

              <label class="form-label">
                Full Name
              </label>

              <input
                v-model="name"
                type="text"
                class="form-control"
                placeholder="Enter your full name"
              >

            </div>


            <div class="mb-3">

              <label class="form-label">
                Email
              </label>

              <input
                v-model="email"
                type="email"
                class="form-control"
                placeholder="Enter your email"
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
                @click="registerStudent"
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

const name = ref("");

const email = ref("");

const password = ref("");

const confirmPassword = ref("");

function registerStudent(){

    console.log("Student Registration");

    console.log(name.value);

    console.log(email.value);

    console.log(password.value);

    console.log(confirmPassword.value);

}

</script>

<style scoped>

.register-page{

    background-color:#F5F7FA;

}

.card{

    border-radius:12px;

}

</style>