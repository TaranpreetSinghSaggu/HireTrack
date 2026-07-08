<template>

    <div class="text-center py-5">

        <i
            class="bi bi-inbox fs-1 text-muted"
        ></i>

        <h4 class="mt-3">

            {{ title }}

        </h4>

        <p class="text-muted">

            {{ message }}

        </p>

    </div>

</template>

<script setup>

defineProps({

    title: String,
    message: String

})

</script>