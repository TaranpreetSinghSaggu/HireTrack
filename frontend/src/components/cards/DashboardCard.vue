<template>

    <div class="card shadow-sm h-100">

        <div class="card-body">

            <div class="d-flex justify-content-between align-items-center">

                <div>

                    <p class="text-muted mb-1">

                        {{ title }}

                    </p>

                    <h3>

                        {{ count }}

                    </h3>

                </div>

                <i
                    :class="icon"
                    class="fs-1 text-primary">

                </i>

            </div>

        </div>

    </div>

</template>

<script setup>

const props = defineProps({
    title: String,
    count: Number,
    icon: String
})

</script>

<style scoped>

.card{

    border-radius:12px;

}

</style>