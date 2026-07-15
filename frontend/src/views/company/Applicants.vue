<template>
  <PageHeader
    :title="isJobView ? (job.title || 'Job applicants') : 'Applicants'"
    :description="isJobView ? 'Move candidates through this job’s hiring pipeline.' : 'Review candidates across every job and open the right hiring pipeline.'"
  />
  <AlertMessage :message="message" :tone="tone" />

  <div v-if="isJobView && job.id" class="job-context card">
    <div>
      <div class="context-line"><StatusBadge :status="job.status" /><span class="muted">{{ job.location || 'Location not set' }}</span></div>
      <p class="muted">{{ job.salary || 'Package not set' }} · Deadline {{ formatDate(job.application_deadline, false) }}</p>
    </div>
    <RouterLink class="back-link" :to="`/company/jobs/${job.id}`"><i class="bi bi-arrow-left"></i> Job summary</RouterLink>
  </div>

  <div v-if="!isJobView" class="card filters">
    <input v-model="filters.search" class="input" placeholder="Search student" @keyup.enter="load" />
    <select v-model="filters.job_id" class="input" @change="load">
      <option value="">All jobs</option>
      <option v-for="item in jobs" :key="item.id" :value="item.id">{{ item.title }}</option>
    </select>
    <select v-model="filters.status" class="input" @change="load">
      <option value="">All statuses</option>
      <option v-for="status in statuses" :key="status">{{ status }}</option>
    </select>
    <AppButton label="Search" icon="search" @click="load" />
  </div>

  <div v-if="isJobView" class="pipeline-summary">
    <div v-for="stage in activeStages" :key="stage.key" class="summary-card card"><strong>{{ countFor(stage.key) }}</strong><span>{{ stage.label }}</span></div>
    <div class="summary-card card rejected-summary"><strong>{{ countFor('Rejected') }}</strong><span>Rejected</span></div>
  </div>

  <LoadingState v-if="loading" />
  <EmptyState v-else-if="!items.length" :title="isJobView ? 'No applicants for this job' : 'No applicants found'" :description="isJobView ? 'Applicants will appear here when students apply to this job.' : 'Applications matching these filters will appear here.'" />

  <section v-else-if="isJobView" class="pipeline-board">
    <div v-for="stage in activeStages" :key="stage.key" class="pipeline-column">
      <div class="column-heading"><div><h2>{{ stage.label }}</h2><span class="muted">{{ countFor(stage.key) }} candidates</span></div></div>
      <div v-if="itemsFor(stage.key).length" class="card-list">
        <article v-for="item in itemsFor(stage.key)" :key="item.application_id" class="candidate-card card">
          <button class="candidate-name" type="button" @click="openCandidate(item)">{{ item.student_name }}</button>
          <p class="candidate-meta">{{ item.student_degree || 'Degree not set' }} · Year {{ item.student_year || '-' }}</p>
          <p class="candidate-meta">Applied {{ formatDate(item.application_date, false) }}</p>
          <div class="match-label"><i class="bi bi-stars"></i> {{ matchLabel(item) }}</div>
          <div class="card-actions">
            <AppButton label="Review" variant="secondary" @click="openCandidate(item)" />
            <AppButton v-if="nextAction(item)" :label="nextAction(item).label" @click="openAction(item, nextAction(item).type)" />
          </div>
        </article>
      </div>
      <p v-else class="empty-column">No candidates</p>
    </div>
    <details v-if="countFor('Rejected')" class="rejected-list card">
      <summary>Rejected applicants ({{ countFor('Rejected') }})</summary>
      <div class="rejected-items">
        <button v-for="item in itemsFor('Rejected')" :key="item.application_id" type="button" class="rejected-item" @click="openCandidate(item)">{{ item.student_name }}<span>{{ formatDate(item.application_date, false) }}</span></button>
      </div>
    </details>
  </section>

  <div v-else-if="items.length" class="table-wrap">
    <table>
      <thead><tr><th>Candidate</th><th>Job</th><th>Profile</th><th>Status</th><th>Action</th></tr></thead>
      <tbody>
        <tr v-for="item in items" :key="item.application_id">
          <td><button class="candidate-link" type="button" @click="openCandidate(item)">{{ item.student_name }}</button><div class="muted">Applied {{ formatDate(item.application_date) }}</div></td>
          <td>{{ item.job_title }}</td>
          <td>{{ item.student_branch || '-' }} · CGPA {{ item.student_cgpa ?? '-' }}</td>
          <td><StatusBadge :status="item.status" /></td>
          <td><AppButton label="Open pipeline" variant="secondary" @click="openPipeline(item)" /></td>
        </tr>
      </tbody>
    </table>
  </div>

  <aside v-if="selected" class="drawer-backdrop" @click.self="closeCandidate">
    <section class="candidate-drawer">
      <div class="drawer-header"><div><h2>{{ selected.student_name }}</h2><p class="muted">{{ selected.job_title }}</p></div><button class="close-button" type="button" aria-label="Close candidate details" @click="closeCandidate">×</button></div>
      <StatusBadge :status="selected.status" />
      <div class="drawer-section"><strong>Application</strong><p>Applied {{ formatDate(selected.application_date) }}</p><p>{{ selected.feedback || 'No feedback yet.' }}</p></div>
      <div class="drawer-section"><strong>Academic profile</strong><p>{{ selected.student_degree || 'Degree not set' }} · {{ selected.student_institution || 'Institution not set' }}</p><p>Branch: {{ selected.student_branch || '-' }} · Year: {{ selected.student_year || '-' }} · CGPA: {{ selected.student_cgpa ?? '-' }}</p></div>
      <div class="drawer-section"><strong>Skills and experience</strong><p>{{ selected.student_skills || 'No skills listed.' }}</p><p>{{ selected.student_experience || 'No experience listed.' }}</p></div>
      <div class="drawer-section"><strong>Match explanation</strong><p>{{ selected.match?.score || 0 }}% · {{ selected.match?.decision_hint || 'No match detail' }}</p><p>Matched: {{ selected.match?.matched_skills?.join(', ') || 'None listed' }}</p><p>Missing: {{ selected.match?.missing_skills?.join(', ') || 'None listed' }}</p></div>
      <div v-if="selected.interview" class="drawer-section"><strong>Interview</strong><p>{{ formatDate(selected.interview.interview_date) }}</p><p>{{ selected.interview.interview_link || selected.interview.venue || 'Details not set' }}</p><p>{{ selected.interview.notes || '' }}</p></div>
      <div v-if="selected.offer" class="drawer-section"><strong>Offer</strong><p>Salary: {{ selected.offer.salary || 'Not set' }}</p><p>Joining: {{ formatDate(selected.offer.joining_date) }}</p><p>{{ selected.offer.remarks || 'No remarks.' }}</p></div>
      <div class="drawer-actions"><AppButton v-if="selected.has_resume" label="Download resume" icon="download" variant="secondary" @click="downloadResume(selected)" /><AppButton v-if="nextAction(selected)" :label="nextAction(selected).label" @click="openAction(selected, nextAction(selected).type)" /></div>
    </section>
  </aside>

  <div v-if="actionItem" class="modal-backdrop" @click.self="closeAction">
    <form class="card action-modal" @submit.prevent="submitAction">
      <h2>{{ actionTitle }}</h2><p class="muted">{{ actionItem.student_name }} · {{ actionItem.job_title }}</p>
      <template v-if="actionType === 'shortlist' || actionType === 'reject'"><label>Feedback *</label><textarea v-model="form.feedback" class="input" required rows="4" placeholder="Keep the feedback clear and respectful." /></template>
      <template v-if="actionType === 'interview'"><label>Interview date *</label><input v-model="form.interview_date" class="input" type="datetime-local" required /><label>Interview link</label><input v-model="form.interview_link" class="input" placeholder="https://..." /><label>Venue</label><input v-model="form.venue" class="input" placeholder="Seminar Hall" /><label>Notes</label><textarea v-model="form.notes" class="input" rows="3" /></template>
      <template v-if="actionType === 'offer'"><label>Offer salary</label><input v-model="form.salary" class="input" type="number" min="0" /><label>Joining date</label><input v-model="form.joining_date" class="input" type="datetime-local" /><label>Feedback *</label><textarea v-model="form.feedback" class="input" required rows="3" /><label>Remarks</label><textarea v-model="form.remarks" class="input" rows="3" /><label>Offer letter PDF *</label><input class="input" type="file" accept="application/pdf,.pdf" @change="form.offer_letter = $event.target.files[0]" required /></template>
      <template v-if="actionType === 'place'"><label>Joining date</label><input v-model="form.joining_date" class="input" type="datetime-local" /><label>Remarks</label><textarea v-model="form.remarks" class="input" rows="3" /></template>
      <div class="actions"><AppButton label="Cancel" variant="secondary" @click="closeAction" /><AppButton :label="actionButton" type="submit" :loading="saving" /></div>
    </form>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import PageHeader from "@/components/PageHeader.vue";
import LoadingState from "@/components/LoadingState.vue";
import EmptyState from "@/components/EmptyState.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import AppButton from "@/components/AppButton.vue";
import AlertMessage from "@/components/AlertMessage.vue";
import { companyApi } from "@/services/company";
import { getErrorMessage } from "@/services/http";

const route = useRoute();
const router = useRouter();
const activeStages = [{ key: "Applied", label: "Applied" }, { key: "Shortlisted", label: "Shortlisted" }, { key: "Interview", label: "Interview" }, { key: "Offer", label: "Offer" }, { key: "Placed", label: "Placed" }];
const statuses = [...activeStages.map((stage) => stage.key), "Rejected"];
const isJobView = computed(() => Boolean(route.params.id));
const items = ref([]); const jobs = ref([]); const job = ref({}); const selected = ref(null); const actionItem = ref(null); const actionType = ref("");
const loading = ref(true); const saving = ref(false); const message = ref(""); const tone = ref("info");
const filters = reactive({ search: "", job_id: route.params.id || "", status: "" });
const form = reactive({ feedback: "", interview_date: "", interview_link: "", venue: "", notes: "", salary: "", joining_date: "", remarks: "", offer_letter: null });
const actionTitle = computed(() => ({ shortlist: "Shortlist candidate", reject: "Reject candidate", interview: "Schedule interview", offer: "Create offer", place: "Confirm placement" }[actionType.value] || "Update application"));
const actionButton = computed(() => ({ shortlist: "Shortlist", reject: "Reject", interview: "Schedule", offer: "Create offer", place: "Mark placed" }[actionType.value] || "Save"));
const formatDate = (value, includeTime = true) => value ? new Date(value).toLocaleString([], includeTime ? {} : { dateStyle: "medium" }) : "Not set";
const itemsFor = (status) => items.value.filter((item) => item.status === status);
const countFor = (status) => itemsFor(status).length;
const matchLabel = (item) => `${item.match?.score || 0}% match`;
const nextAction = (item) => ({ Applied: { label: "Shortlist", type: "shortlist" }, Shortlisted: { label: "Schedule", type: "interview" }, Interview: { label: "Create offer", type: "offer" }, Offer: { label: "Confirm placement", type: "place" } }[item.status] || null);

function resetForm() { Object.assign(form, { feedback: "", interview_date: "", interview_link: "", venue: "", notes: "", salary: "", joining_date: "", remarks: "", offer_letter: null }); }
function openAction(item, type) { actionItem.value = item; actionType.value = type; resetForm(); }
function closeAction() { actionItem.value = null; actionType.value = ""; }
function openCandidate(item) { selected.value = item; }
function closeCandidate() { selected.value = null; if (route.query.application_id) router.replace({ query: {} }); }
function openPipeline(item) { router.push({ path: `/company/jobs/${item.job_id}/applicants`, query: { application_id: item.application_id } }); }

async function load() {
  loading.value = true;
  try { items.value = (await companyApi.allApplicants({ ...filters, job_id: isJobView.value ? route.params.id : filters.job_id })).data; }
  catch (error) { tone.value = "danger"; message.value = getErrorMessage(error); }
  finally { loading.value = false; }
}

async function submitAction() {
  saving.value = true;
  try {
    if (actionType.value === "interview") await companyApi.scheduleInterview(actionItem.value.application_id, { interview_date: new Date(form.interview_date).toISOString(), interview_link: form.interview_link, venue: form.venue, notes: form.notes });
    else if (actionType.value === "offer") { const payload = new FormData(); payload.append("feedback", form.feedback); payload.append("salary", form.salary || ""); payload.append("joining_date", form.joining_date ? new Date(form.joining_date).toISOString() : ""); payload.append("remarks", form.remarks || ""); payload.append("offer_letter", form.offer_letter); await companyApi.createOffer(actionItem.value.application_id, payload); }
    else if (actionType.value === "place") await companyApi.placeCandidate(actionItem.value.application_id, { joining_date: form.joining_date ? new Date(form.joining_date).toISOString() : null, remarks: form.remarks });
    else await companyApi.updateApplication(actionItem.value.application_id, { status: actionType.value === "shortlist" ? "Shortlisted" : "Rejected", feedback: form.feedback });
    tone.value = "success"; message.value = "Application updated."; closeAction(); selected.value = null; await load();
  } catch (error) { tone.value = "danger"; message.value = getErrorMessage(error); }
  finally { saving.value = false; }
}

async function downloadResume(item) {
  try { const response = await companyApi.resume(item.application_id); const url = URL.createObjectURL(response.data); const link = document.createElement("a"); link.href = url; link.download = item.resume_filename || "resume.pdf"; link.click(); URL.revokeObjectURL(url); }
  catch (error) { tone.value = "danger"; message.value = getErrorMessage(error); }
}

async function loadJobs() {
  try { jobs.value = (await companyApi.jobs()).data; if (isJobView.value) job.value = jobs.value.find((item) => String(item.id) === String(route.params.id)) || {}; }
  catch (error) { tone.value = "danger"; message.value = getErrorMessage(error); }
}

function openQueryCandidate() { if (route.query.application_id) { selected.value = items.value.find((item) => String(item.application_id) === String(route.query.application_id)) || null; } }
watch(() => route.query.application_id, openQueryCandidate);
onMounted(async () => { await loadJobs(); await load(); openQueryCandidate(); });
</script>

<style scoped>
.filters { display: grid; grid-template-columns: 1.3fr 1fr 1fr auto; gap: 12px; padding: 16px; margin-bottom: 20px; }
.job-context { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 16px 20px; margin-bottom: 20px; }
.context-line { display: flex; align-items: center; gap: 12px; }.context-line + p { margin-bottom: 0; }.back-link { color: var(--blue); font-weight: 600; }.muted, .candidate-meta { color: var(--muted); font-size: 13px; }.pipeline-summary { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 20px; }.summary-card { display: grid; gap: 4px; padding: 15px; }.summary-card strong { color: var(--navy); font-size: 24px; }.summary-card span { color: var(--muted); font-size: 13px; }.rejected-summary strong { color: var(--danger); }
.pipeline-board { display: grid; grid-template-columns: repeat(5, minmax(220px, 1fr)); gap: 14px; align-items: start; overflow-x: auto; padding-bottom: 8px; }.pipeline-column { min-width: 220px; }.column-heading { min-height: 58px; border-bottom: 2px solid var(--border); margin-bottom: 12px; }.column-heading h2 { color: var(--navy); font-size: 16px; margin: 0 0 4px; }.card-list { display: grid; gap: 12px; }.candidate-card { display: grid; gap: 8px; padding: 15px; }.candidate-name { width: fit-content; border: 0; padding: 0; background: transparent; color: var(--navy); font-size: 16px; font-weight: 700; text-align: left; cursor: pointer; }.candidate-name:hover, .candidate-link:hover { color: var(--blue); }.candidate-meta { margin: 0; }.match-label { color: var(--blue); font-size: 13px; font-weight: 600; }.card-actions, .drawer-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px; }.empty-column { color: var(--muted); font-size: 13px; padding: 14px 0; }.rejected-list { grid-column: 1 / -1; padding: 14px 16px; }.rejected-list summary { cursor: pointer; color: var(--danger); font-weight: 700; }.rejected-items { display: grid; gap: 6px; margin-top: 12px; }.rejected-item { display: flex; justify-content: space-between; border: 0; border-bottom: 1px solid var(--border); padding: 9px 0; background: transparent; color: var(--text); text-align: left; cursor: pointer; }.rejected-item span { color: var(--muted); font-size: 13px; }.candidate-link { border: 0; background: transparent; color: var(--blue); font-weight: 700; padding: 0; cursor: pointer; }.drawer-backdrop { position: fixed; inset: 0; z-index: 35; background: rgba(17, 24, 39, .28); }.candidate-drawer { position: absolute; top: 0; right: 0; width: min(470px, 100%); height: 100%; overflow-y: auto; background: #fff; padding: 24px; box-shadow: -8px 0 24px rgba(17, 24, 39, .12); }.drawer-header { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 16px; }.drawer-header h2 { margin: 0; color: var(--navy); }.close-button { width: 34px; height: 34px; border: 1px solid var(--border); border-radius: 6px; background: #fff; font-size: 24px; cursor: pointer; }.drawer-section { border-top: 1px solid var(--border); margin-top: 18px; padding-top: 14px; }.drawer-section p { line-height: 1.5; margin: 8px 0 0; }.drawer-actions { border-top: 1px solid var(--border); padding-top: 16px; margin-top: 20px; }.modal-backdrop { position: fixed; inset: 0; z-index: 40; display: grid; place-items: center; padding: 20px; background: rgba(17, 24, 39, .35); }.action-modal { width: min(520px, 100%); max-height: calc(100vh - 40px); overflow-y: auto; display: grid; gap: 8px; padding: 22px; }.action-modal h2 { margin: 0; color: var(--navy); }.action-modal label { font-weight: 600; margin-top: 6px; }.action-modal .actions { justify-content: flex-end; margin-top: 10px; }
@media (max-width: 1100px) { .pipeline-board { grid-template-columns: repeat(5, 240px); }.pipeline-summary { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 700px) { .filters, .job-context { grid-template-columns: 1fr; display: grid; }.pipeline-summary { grid-template-columns: repeat(2, 1fr); }.candidate-drawer { padding: 18px; } }
</style>
