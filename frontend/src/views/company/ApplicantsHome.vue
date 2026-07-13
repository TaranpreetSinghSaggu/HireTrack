<template>
  <PageHeader
    title="Applicants"
    description="Open a job first, then review candidates in context."
  />
  <EmptyState
    title="Select a job to review applicants"
    description="Applicants are nested under each job so candidate actions always use the correct role."
  >
    <RouterLink to="/company/jobs"
      ><AppButton label="Go to jobs" icon="briefcase"
    /></RouterLink>
  </EmptyState>
</template>

<script setup>
import PageHeader from "@/components/PageHeader.vue";
import EmptyState from "@/components/EmptyState.vue";
import AppButton from "@/components/AppButton.vue";
</script>
