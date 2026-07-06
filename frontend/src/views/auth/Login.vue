<template>
  <div class="container-fluid login-page">

    <div class="row justify-content-center align-items-center vh-100">

      <div class="col-md-5 col-lg-4">

        <div class="card shadow">

          <div class="card-body p-4">

            <div class="text-center mb-4">
              <h2 class="fw-bold text-primary">HireTrack</h2>
              <p class="text-muted">Placement Management System</p>
            </div>

            <h4 class="text-center mb-4">
              Welcome Back
            </h4>

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
                placeholder="Enter your password"
              >

            </div>

            <div class="d-grid">

              <button
                class="btn btn-primary"
                @click="loginUser"
              >
                Login
              </button>

            </div>

            <hr>


            <div class="text-center">

              <p class="mb-2">

                New Student?

                <RouterLink to="/register/student">
                  Register
                </RouterLink>

              </p>

              <p>

                Company?

                <RouterLink to="/register/company">
                  Register
                </RouterLink>

              </p>

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

const email = ref("");
const password = ref("");

function loginUser(){

    console.log("Email :", email.value);

    console.log("Password :", password.value);

}

</script>

<style scoped>

.login-page{

    background-color:#F5F7FA;

}

.card{

    border-radius:12px;

}

</style>