<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import UserAvatar from '@/components/profile/UserAvatar.vue'
import { getEventAttendance, saveEventAttendance } from '@/api/events'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  show: Boolean,
  eventId: {
    type: Number,
    required: true
  },
  canManage: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'saved'])
const { showToast } = useToast()

// ── State ──────────────────────────────────────────────────────────────────
const loading    = ref(false)
const saving     = ref(false)
const activeStep = ref('OVERVIEW') // 'OVERVIEW' | 'SHEET'

const eventData             = ref(null)
const sessionsList          = ref([])
const summaryStats          = ref({ present: 0, absent: 0, pending: 0, eligible: 0, total: 0, percentage: 0 })
const hasParticipants       = ref(true)
const hasValidDates          = ref(true)
const isRoundBased          = ref(false)
const eventFormat           = ref('COMPETITION')

const selectedSessionId     = ref(null)
const activeSession         = ref(null)
const participants          = ref([])
const searchQuery           = ref('')
const isAttendanceAvailable = ref(true)
const isFutureSession       = ref(false)
const availableFromDate     = ref('')
const isEditMode            = ref(false)

// ── Date Helpers ───────────────────────────────────────────────────────────
function formatDate(raw) {
  if (!raw) return ''
  try {
    const d = new Date(raw)
    const adjusted = raw.includes('T') ? d : new Date(raw + 'T00:00:00')
    return adjusted.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
  } catch {
    return raw
  }
}

function isDateFuture(dateStr) {
  if (!dateStr) return false
  const d = new Date(dateStr + 'T00:00:00')
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return d > today
}

// ── Overview API ───────────────────────────────────────────────────────────
async function fetchAttendanceOverview() {
  if (!props.eventId) return
  loading.value = true
  try {
    const res = await getEventAttendance(props.eventId)
    if (res && res.success) {
      eventData.value       = res.event
      hasParticipants.value  = res.hasParticipants !== false
      hasValidDates.value   = res.hasValidDates !== false
      eventFormat.value     = res.eventFormat || 'COMPETITION'
      isRoundBased.value    = res.isRoundBased === true
      sessionsList.value    = (res.sessions || res.rounds || []).map(s => ({
        ...s,
        _isUpcoming: s.isFutureDate === true || isDateFuture(s.sessionDate)
      }))
      summaryStats.value    = res.summary || { present: 0, absent: 0, pending: 0, eligible: 0, total: 0, percentage: 0 }
      
      // Auto-select first active or available session/round
      if (sessionsList.value.length > 0) {
        if (!selectedSessionId.value) {
          const firstAvailable = sessionsList.value.find(s => !s._isUpcoming) || sessionsList.value[0]
          selectedSessionId.value = firstAvailable.id
        }
        await loadSessionData(selectedSessionId.value)
      }
    }
  } catch (err) {
    showToast(err.response?.data?.error || 'Failed to load attendance.', 'error')
  } finally {
    loading.value = false
  }
}

// ── Load session data for selected round/date ──────────────────────────────
async function loadSessionData(sessionId) {
  if (!sessionId || !props.eventId) return
  loading.value = true
  try {
    const res = await getEventAttendance(props.eventId, sessionId)
    if (res && res.success) {
      eventData.value             = res.event
      activeSession.value         = res.session
      summaryStats.value          = res.summary || { present: 0, absent: 0, pending: 0, eligible: 0, total: 0, percentage: 0 }
      isAttendanceAvailable.value = res.isAttendanceAvailable !== false
      isFutureSession.value       = res.isFutureDate === true
      availableFromDate.value     = res.availableFromDate || ''

      participants.value = (res.participants || []).map(p => ({
        ...p,
        currentStatus: p.status || 'PENDING'
      }))
    }
  } catch (err) {
    showToast(err.response?.data?.error || 'Failed to load round details.', 'error')
  } finally {
    loading.value = false
  }
}

async function onSessionSelectChange() {
  if (selectedSessionId.value) {
    await loadSessionData(selectedSessionId.value)
  }
}

function enterMarkingSheet() {
  if (!activeSession.value) return
  isEditMode.value = props.canManage && isAttendanceAvailable.value && !isFutureSession.value
  activeStep.value = 'SHEET'
}

// ── Save Attendance ────────────────────────────────────────────────────────
async function handleSaveAttendance() {
  if (!isEditMode.value) {
    showToast('You do not have permission to save attendance.', 'warning')
    return
  }
  if (isFutureSession.value && !isAttendanceAvailable.value) {
    showToast(`Attendance available from ${availableFromDate.value || 'session date'}.`, 'warning')
    return
  }
  saving.value = true
  try {
    const payload = {
      sessionId: activeSession.value.id,
      records: participants.value.map(p => ({
        userId: p.userId,
        status: p.currentStatus
      }))
    }
    await saveEventAttendance(props.eventId, payload)
    showToast('Attendance saved successfully!', 'success')
    emit('saved')
    await fetchAttendanceOverview()
    activeStep.value = 'OVERVIEW'
  } catch (err) {
    showToast(err.response?.data?.error || 'Failed to save attendance.', 'error')
  } finally {
    saving.value = false
  }
}

// ── Computed ───────────────────────────────────────────────────────────────
const filteredParticipants = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return participants.value
  return participants.value.filter(p => {
    const name  = (p.userName || '').toLowerCase()
    const email = (p.userEmail || '').toLowerCase()
    const reg   = String(p.registerNumber || '').toLowerCase()
    return name.includes(q) || email.includes(q) || reg.includes(q)
  })
})

const liveSummary = computed(() => {
  const present = participants.value.filter(p => p.currentStatus === 'PRESENT').length
  const absent  = participants.value.filter(p => p.currentStatus === 'ABSENT').length
  const pending = participants.value.filter(p => p.currentStatus === 'PENDING').length
  const eligible = participants.value.length
  const percentage = eligible > 0 ? Math.round((present / eligible) * 100) : 0
  return { present, absent, pending, eligible, percentage }
})

const compactSummaryText = computed(() => {
  if (!hasParticipants.value || participants.value.length === 0) {
    return 'No eligible participants'
  }
  const { present, eligible, percentage } = liveSummary.value
  const recordedCount = present + liveSummary.value.absent
  if (recordedCount === 0) {
    return `0 / ${eligible} Present · Not recorded`
  }
  return `${present} / ${eligible} Present · ${percentage}%`
})

// ── Watchers ───────────────────────────────────────────────────────────────
watch(() => props.show, (val) => {
  if (val) {
    activeStep.value        = 'OVERVIEW'
    searchQuery.value       = ''
    participants.value      = []
    activeSession.value     = null
    selectedSessionId.value = null
    fetchAttendanceOverview()
  }
})

onMounted(() => {
  if (props.show) fetchAttendanceOverview()
})

// ── Sheet Actions ──────────────────────────────────────────────────────────
function markStatus(participant, status) {
  if (!isEditMode.value) return
  participant.currentStatus = participant.currentStatus === status ? 'PENDING' : status
}

function markAllPresent() {
  if (!isEditMode.value) return
  filteredParticipants.value.forEach(p => (p.currentStatus = 'PRESENT'))
}

function markAllAbsent() {
  if (!isEditMode.value) return
  filteredParticipants.value.forEach(p => (p.currentStatus = 'ABSENT'))
}

function backToOverview() {
  activeStep.value  = 'OVERVIEW'
  searchQuery.value = ''
  fetchAttendanceOverview()
}
</script>

<template>
  <div v-if="show" class="aw-backdrop" @mousedown.self="$emit('close')">
    <div class="aw-card">

      <!-- ═══ HEADER (Dynamic DB event data only, no hardcoded text) ═════ -->
      <div class="aw-header">
        <div class="aw-header-left">
          <button v-if="activeStep === 'SHEET'" class="aw-back-btn" @click="backToOverview" title="Back to Workspace">
            <i class="bi bi-arrow-left"></i>
          </button>
          <div>
            <div class="aw-title">Attendance Workspace</div>
            <div v-if="eventData" class="aw-subtitle">
              <span class="aw-event-name">{{ eventData.name }}</span>
              <span class="aw-club-tag">{{ eventData.clubName || eventData.club || 'General / Institutional' }}</span>
              <span v-if="eventData.eventType || eventData.eventFormat" class="aw-type-tag">
                {{ eventData.eventType || eventData.eventFormat }}
              </span>
            </div>
          </div>
        </div>
        <button class="aw-close-btn" @click="$emit('close')" title="Close">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>

      <!-- ═══ BODY ══════════════════════════════════════════════════════ -->
      <div class="aw-body">

        <!-- Loading spinner -->
        <div v-if="loading && !eventData" class="aw-loading">
          <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
          <span class="text-muted ms-2" style="font-size:0.8rem">Loading attendance records…</span>
        </div>

        <!-- ┌─────────────────────────────────────────────────────────┐ -->
        <!-- │  OVERVIEW VIEW                                          │ -->
        <!-- └─────────────────────────────────────────────────────────┘ -->
        <div v-else-if="activeStep === 'OVERVIEW'" class="aw-overview">

          <!-- Dynamic Selector & Compact Summary Bar -->
          <div class="aw-toolbar-row">
            <div class="aw-selector-wrap">
              <label class="aw-selector-label">
                {{ isRoundBased ? 'Select Round' : 'Attendance Date' }}
              </label>
              <select
                v-model="selectedSessionId"
                class="form-select form-select-sm aw-select-input"
                @change="onSessionSelectChange"
              >
                <option v-for="s in sessionsList" :key="s.id" :value="s.id">
                  {{ isRoundBased && s.roundNumber ? `Round ${s.roundNumber}: ${s.name}` : (formatDate(s.sessionDate) || s.name) }}
                  <template v-if="isRoundBased && s.sessionDate"> ({{ formatDate(s.sessionDate) }})</template>
                  <template v-if="s._isUpcoming"> — Upcoming</template>
                </option>
              </select>
            </div>

            <!-- Compact Summary Display (No giant card) -->
            <div class="aw-compact-summary">
              <span class="aw-cs-label">Summary:</span>
              <span class="aw-cs-value" :class="{ 'text-muted': !hasParticipants }">
                {{ compactSummaryText }}
              </span>
            </div>

            <!-- Single Primary Action -->
            <div class="aw-action-wrap">
              <button
                v-if="canManage"
                class="aw-btn aw-btn-primary"
                :disabled="!hasParticipants || isFutureSession || !isAttendanceAvailable"
                :title="isFutureSession ? `Attendance available on ${availableFromDate}` : (!hasParticipants ? 'No registered participants' : 'Mark Attendance')"
                @click="enterMarkingSheet"
              >
                <i class="bi bi-pencil-square me-1"></i> Mark Attendance
              </button>
              <button
                v-else
                class="aw-btn aw-btn-secondary"
                :disabled="!hasParticipants"
                @click="enterMarkingSheet"
              >
                <i class="bi bi-eye me-1"></i> View Attendance Sheet
              </button>
            </div>
          </div>

          <!-- Empty State: Unconfigured Dates -->
          <div v-if="!hasValidDates || sessionsList.length === 0" class="aw-empty-state">
            <i class="bi bi-calendar-x text-muted" style="font-size:2rem"></i>
            <h6 class="mt-2 text-dark fw-bold" style="font-size:0.85rem">Attendance dates are not configured for this event.</h6>
            <p class="text-secondary text-xs mb-0">No valid event schedule or attendance dates were found in the database.</p>
          </div>

          <!-- Empty State: No Registrations -->
          <div v-else-if="!hasParticipants" class="aw-empty-state">
            <i class="bi bi-people text-muted" style="font-size:2rem"></i>
            <h6 class="mt-2 text-dark fw-bold" style="font-size:0.85rem">No registered participants</h6>
            <p class="text-secondary text-xs mb-0">There are no participants registered for this event yet.</p>
          </div>

          <!-- Participant Summary Table -->
          <div v-else class="aw-table-card mt-3">
            <div class="aw-table-header-row">
              <span class="aw-table-title">Participant Summary</span>
              <span v-if="activeSession" class="aw-table-sub">
                Showing {{ activeSession.name }} <template v-if="activeSession.sessionDate">({{ formatDate(activeSession.sessionDate) }})</template>
              </span>
            </div>

            <div class="aw-table-wrap">
              <table class="aw-table">
                <thead>
                  <tr>
                    <th style="width:36%">Participant</th>
                    <th style="width:24%">Register / ID</th>
                    <th style="width:20%">Current Attendance</th>
                    <th style="width:20%" class="text-end">Total Attendance</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="participants.length === 0">
                    <td colspan="4" class="aw-table-empty">
                      {{ (activeSession?.roundNumber || 1) > 1
                          ? 'No eligible participants for this round.'
                          : 'No attendance recorded yet.' }}
                    </td>
                  </tr>
                  <tr v-for="p in participants" :key="p.userId" class="aw-p-row">
                    <td>
                      <div class="d-flex align-items-center gap-2">
                        <UserAvatar :name="p.userName" :size="26" />
                        <div>
                          <div class="aw-p-name">{{ p.userName }}</div>
                          <div v-if="p.userEmail" class="aw-p-email">{{ p.userEmail }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="aw-roll">{{ p.registerNumber || '—' }}</td>
                    <td>
                      <span class="aw-status-badge" :class="`aw-status-${(p.currentStatus || 'PENDING').toLowerCase()}`">
                        {{ p.currentStatus || 'PENDING' }}
                      </span>
                    </td>
                    <td class="text-end fw-semibold aw-tot-att">
                      {{ p.totalAttendance || `${p.totalPresent || 0} / ${p.totalSessions || 1} Present` }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

        </div>

        <!-- ┌─────────────────────────────────────────────────────────┐ -->
        <!-- │  ATTENDANCE SHEET VIEW (MARKING MODE)                   │ -->
        <!-- └─────────────────────────────────────────────────────────┘ -->
        <div v-else-if="activeStep === 'SHEET'" class="aw-sheet">

          <!-- Sheet sub-header -->
          <div class="aw-sheet-header">
            <div>
              <div class="aw-sheet-title">{{ activeSession?.name || 'Attendance Sheet' }}</div>
              <div class="aw-sheet-date">{{ formatDate(activeSession?.sessionDate) }}</div>
            </div>
            <span v-if="isFutureSession" class="aw-badge aw-badge-upcoming" style="align-self:center">Upcoming</span>
            <span v-else-if="activeSession?.status === 'COMPLETED'" class="aw-badge aw-badge-done" style="align-self:center">Completed</span>
          </div>

          <!-- Future/Date Lock Banner -->
          <div v-if="isFutureSession" class="aw-lock-banner">
            <i class="bi bi-lock-fill me-2"></i>
            Attendance will be available on <strong>{{ availableFromDate || 'the session date' }}</strong>
          </div>

          <!-- Compact Live Summary Bar -->
          <div class="aw-sheet-summary">
            <div class="aw-ss-item">
              <span class="aw-ss-dot aw-dot-present"></span>
              <span class="aw-ss-label">Present:</span>
              <span class="aw-ss-val aw-val-present">{{ liveSummary.present }} / {{ liveSummary.eligible }}</span>
            </div>
            <div class="aw-ss-sep"></div>
            <div class="aw-ss-item">
              <span class="aw-ss-dot aw-dot-absent"></span>
              <span class="aw-ss-label">Absent:</span>
              <span class="aw-ss-val aw-val-absent">{{ liveSummary.absent }}</span>
            </div>
            <div class="aw-ss-sep"></div>
            <div class="aw-ss-item">
              <span class="aw-ss-dot aw-dot-pending"></span>
              <span class="aw-ss-label">Pending:</span>
              <span class="aw-ss-val">{{ liveSummary.pending }}</span>
            </div>
          </div>

          <!-- Search + Bulk Actions -->
          <div class="aw-controls-row">
            <div class="aw-search-wrap">
              <i class="bi bi-search aw-search-icon"></i>
              <input
                v-model="searchQuery"
                type="text"
                class="aw-search-input"
                placeholder="Search participants…"
              />
            </div>
            <div v-if="isEditMode" class="aw-bulk-actions">
              <button class="aw-btn aw-btn-ghost" @click="markAllPresent">Mark All Present</button>
              <button class="aw-btn aw-btn-ghost aw-btn-danger" @click="markAllAbsent">Mark All Absent</button>
            </div>
          </div>

          <!-- Table -->
          <div class="aw-table-wrap" style="max-height: calc(85vh - 280px)">
            <table class="aw-table">
              <thead>
                <tr>
                  <th style="width:34%">Participant</th>
                  <th style="width:20%">Register / ID</th>
                  <th style="width:26%">Attendance</th>
                  <th style="width:20%" class="text-end">Total Attendance</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="filteredParticipants.length === 0">
                  <td colspan="4" class="aw-table-empty">
                    <span v-if="!searchQuery && participants.length === 0">
                      {{ (activeSession?.roundNumber || 1) > 1
                          ? 'No eligible participants for this round.'
                          : 'No registered participants.' }}
                    </span>
                    <span v-else>No participants match your search query.</span>
                  </td>
                </tr>
                <tr v-for="p in filteredParticipants" :key="p.userId" class="aw-p-row">
                  <td>
                    <div class="d-flex align-items-center gap-2">
                      <UserAvatar :name="p.userName" :size="26" />
                      <div>
                        <div class="aw-p-name">{{ p.userName }}</div>
                        <div v-if="p.userEmail" class="aw-p-email">{{ p.userEmail }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="aw-roll">{{ p.registerNumber || '—' }}</td>
                  <td>
                    <!-- Edit mode: toggle buttons -->
                    <div v-if="isEditMode" class="aw-att-toggle">
                      <button
                        class="aw-att-btn"
                        :class="{ 'aw-att-present': p.currentStatus === 'PRESENT' }"
                        @click="markStatus(p, 'PRESENT')"
                      >Present</button>
                      <button
                        class="aw-att-btn"
                        :class="{ 'aw-att-absent': p.currentStatus === 'ABSENT' }"
                        @click="markStatus(p, 'ABSENT')"
                      >Absent</button>
                    </div>
                    <!-- View mode static badge -->
                    <span v-else class="aw-status-badge" :class="`aw-status-${(p.currentStatus || 'PENDING').toLowerCase()}`">
                      {{ p.currentStatus || 'PENDING' }}
                    </span>
                  </td>
                  <td class="text-end fw-semibold aw-tot-att">
                    {{ p.totalAttendance || `${p.totalPresent || 0} / ${p.totalSessions || 1} Present` }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

        </div>

      </div>

      <!-- ═══ FOOTER ════════════════════════════════════════════════════ -->
      <div v-if="activeStep === 'SHEET'" class="aw-footer">
        <div v-if="isEditMode" class="aw-footer-counts">
          <span class="aw-fc-present">{{ liveSummary.present }} Present</span>
          <span class="aw-fc-sep">·</span>
          <span class="aw-fc-absent">{{ liveSummary.absent }} Absent</span>
          <span v-if="liveSummary.pending > 0" class="aw-fc-sep">·</span>
          <span v-if="liveSummary.pending > 0" class="aw-fc-pending">{{ liveSummary.pending }} Pending</span>
        </div>
        <div v-else style="flex:1"></div>

        <div class="aw-footer-actions">
          <button class="aw-btn aw-btn-ghost" @click="backToOverview">
            {{ isEditMode ? 'Cancel' : 'Back' }}
          </button>
          <button
            v-if="isEditMode"
            class="aw-btn aw-btn-primary"
            :disabled="saving"
            @click="handleSaveAttendance"
          >
            <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
            Save Attendance
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* ── Backdrop ─────────────────────────────────────────────────────────────── */
.aw-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(3px);
  z-index: 1060;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

/* ── Large Workspace Card (~88vw x 88vh as requested) ─────────────────────── */
.aw-card {
  width: 88vw;
  max-width: 1200px;
  height: 88vh;
  max-height: 850px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 24px 64px rgba(15, 23, 42, 0.22), 0 4px 16px rgba(15, 23, 42, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ── Header ───────────────────────────────────────────────────────────────── */
.aw-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f5;
  flex-shrink: 0;
  gap: 12px;
  background: #fafafa;
}
.aw-header-left { display: flex; align-items: center; gap: 12px; min-width: 0; }
.aw-back-btn {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: #4b5563; font-size: 0.88rem;
  flex-shrink: 0; transition: background 0.15s;
}
.aw-back-btn:hover { background: #f3f4f6; }
.aw-title { font-size: 0.95rem; font-weight: 700; color: #111827; line-height: 1.2; }
.aw-subtitle {
  font-size: 0.76rem; color: #6b7280; margin-top: 2px;
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.aw-event-name { font-weight: 600; color: #1f2937; }
.aw-club-tag {
  background: #eff6ff; color: #2563eb; border: 1px solid #dbeafe;
  border-radius: 4px; padding: 1px 7px; font-size: 0.69rem; font-weight: 600;
}
.aw-type-tag {
  background: #f3f4f6; color: #4b5563; border: 1px solid #e5e7eb;
  border-radius: 4px; padding: 1px 7px; font-size: 0.69rem; font-weight: 600;
}
.aw-close-btn {
  background: none; border: none;
  width: 32px; height: 32px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: #9ca3af; font-size: 0.95rem;
  flex-shrink: 0; transition: background 0.15s, color 0.15s;
}
.aw-close-btn:hover { background: #fef2f2; color: #dc2626; }

/* ── Body ─────────────────────────────────────────────────────────────────── */
.aw-body {
  flex: 1; overflow-y: auto; padding: 24px;
  display: flex; flex-direction: column;
}
.aw-loading {
  display: flex; align-items: center; justify-content: center; padding: 60px 0;
}

/* ── Overview ─────────────────────────────────────────────────────────────── */
.aw-overview { display: flex; flex-direction: column; flex: 1; }

.aw-toolbar-row {
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px; padding: 14px 18px; background: #f8fafc; border: 1px solid #e2e8f0;
  border-radius: 10px; flex-wrap: wrap;
}
.aw-selector-wrap { display: flex; align-items: center; gap: 10px; }
.aw-selector-label { font-size: 0.75rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.04em; white-space: nowrap; margin: 0; }
.aw-select-input { min-width: 240px; border-radius: 7px; font-size: 0.8rem; font-weight: 600; border-color: #cbd5e1; }

.aw-compact-summary {
  display: flex; align-items: center; gap: 8px;
  background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px 14px;
}
.aw-cs-label { font-size: 0.72rem; font-weight: 700; color: #64748b; text-transform: uppercase; }
.aw-cs-value { font-size: 0.82rem; font-weight: 700; color: #0f172a; }

.aw-action-wrap { display: flex; align-items: center; }

/* Empty state */
.aw-empty-state {
  text-align: center; padding: 60px 20px; background: #fafafa;
  border: 1px dashed #e2e8f0; border-radius: 12px; margin-top: 20px;
}

/* Table Card */
.aw-table-card {
  border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden;
  display: flex; flex-direction: column; flex: 1; background: #fff;
}
.aw-table-header-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 18px; background: #f8fafc; border-bottom: 1px solid #e2e8f0;
}
.aw-table-title { font-size: 0.82rem; font-weight: 700; color: #1e293b; }
.aw-table-sub { font-size: 0.75rem; color: #64748b; font-weight: 500; }

.aw-tot-att { font-size: 0.78rem; color: #2563eb; }

/* ── Badges ───────────────────────────────────────────────────────────────── */
.aw-badge {
  font-size: 0.63rem; font-weight: 700; padding: 1px 6px; border-radius: 4px;
  text-transform: uppercase; letter-spacing: 0.03em;
}
.aw-badge-upcoming { background: #fef9c3; color: #92400e; border: 1px solid #fde68a; }
.aw-badge-done     { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }

/* ── Buttons ──────────────────────────────────────────────────────────────── */
.aw-btn {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 6px 14px; border-radius: 7px;
  font-size: 0.78rem; font-weight: 600; cursor: pointer;
  border: 1px solid transparent;
  transition: background 0.13s, border-color 0.13s, opacity 0.13s;
  white-space: nowrap;
}
.aw-btn:disabled { opacity: 0.45; cursor: not-allowed; }

.aw-btn-primary { background: #2563eb; color: #fff; border-color: #2563eb; }
.aw-btn-primary:not(:disabled):hover { background: #1d4ed8; border-color: #1d4ed8; }

.aw-btn-secondary { background: #fff; color: #374151; border-color: #cbd5e1; }
.aw-btn-secondary:not(:disabled):hover { background: #f8fafc; }

.aw-btn-ghost { background: #f1f5f9; color: #334155; border-color: #e2e8f0; }
.aw-btn-ghost:not(:disabled):hover { background: #e2e8f0; }

.aw-btn-danger { background: #fff0f0; color: #dc2626; border-color: #fecaca; }
.aw-btn-danger:not(:disabled):hover { background: #fde8e8; }

/* ── Sheet ────────────────────────────────────────────────────────────────── */
.aw-sheet { display: flex; flex-direction: column; gap: 14px; flex: 1; }

.aw-sheet-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding-bottom: 10px; border-bottom: 1px solid #f1f5f9;
}
.aw-sheet-title { font-size: 0.9rem; font-weight: 700; color: #0f172a; }
.aw-sheet-date  { font-size: 0.76rem; color: #64748b; margin-top: 1px; }

.aw-lock-banner {
  background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px;
  padding: 9px 14px; font-size: 0.78rem; color: #92400e;
}

.aw-sheet-summary {
  display: flex; align-items: center; gap: 12px;
  background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;
  padding: 9px 16px;
}
.aw-ss-item  { display: flex; align-items: center; gap: 6px; }
.aw-ss-dot   { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.aw-dot-present { background: #16a34a; }
.aw-dot-absent  { background: #dc2626; }
.aw-dot-pending { background: #94a3b8; }
.aw-ss-label { font-size: 0.76rem; color: #64748b; }
.aw-ss-val   { font-size: 0.76rem; font-weight: 700; color: #0f172a; }
.aw-val-present { color: #16a34a; }
.aw-val-absent  { color: #dc2626; }
.aw-ss-sep   { width: 1px; height: 14px; background: #cbd5e1; margin: 0 2px; }

/* Controls row */
.aw-controls-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.aw-search-wrap { position: relative; flex: 1; min-width: 180px; }
.aw-search-icon {
  position: absolute; left: 10px; top: 50%; transform: translateY(-50%);
  color: #94a3b8; font-size: 0.78rem; pointer-events: none;
}
.aw-search-input {
  width: 100%; border: 1px solid #cbd5e1; border-radius: 7px;
  padding: 6px 10px 6px 30px; font-size: 0.78rem; color: #0f172a;
  outline: none; transition: border-color 0.13s; background: #fff;
}
.aw-search-input:focus { border-color: #2563eb; }
.aw-bulk-actions { display: flex; gap: 6px; flex-shrink: 0; }

/* Table */
.aw-table-wrap {
  border: 1px solid #e2e8f0; border-radius: 10px;
  overflow: hidden; overflow-y: auto; flex: 1;
}
.aw-table { width: 100%; border-collapse: collapse; }
.aw-table thead th {
  background: #f8fafc; font-size: 0.69rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.05em; color: #64748b;
  padding: 10px 14px; border-bottom: 1px solid #e2e8f0;
  position: sticky; top: 0; z-index: 1;
}
.aw-table tbody td {
  padding: 10px 14px; border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}
.aw-table tbody tr:last-child td { border-bottom: none; }
.aw-p-row:hover td { background: #f8fafc; }
.aw-table-empty { text-align: center; padding: 36px; color: #94a3b8; font-style: italic; font-size: 0.8rem; }

.aw-p-name  { font-size: 0.8rem; font-weight: 600; color: #0f172a; }
.aw-p-email { font-size: 0.7rem; color: #94a3b8; }
.aw-roll    { font-size: 0.78rem; color: #475569; font-weight: 500; }

/* Attendance toggle */
.aw-att-toggle {
  display: inline-flex; border: 1px solid #cbd5e1; border-radius: 7px; overflow: hidden;
}
.aw-att-btn {
  background: #f8fafc; border: none; padding: 4px 13px;
  font-size: 0.74rem; font-weight: 600; cursor: pointer; color: #64748b;
  transition: background 0.12s, color 0.12s; white-space: nowrap;
}
.aw-att-btn:not(:last-child) { border-right: 1px solid #cbd5e1; }
.aw-att-present { background: #16a34a !important; color: #fff !important; }
.aw-att-absent  { background: #dc2626 !important; color: #fff !important; }

/* Status badge */
.aw-status-badge {
  display: inline-block; font-size: 0.68rem; font-weight: 700;
  padding: 2px 8px; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.03em;
}
.aw-status-present { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
.aw-status-absent  { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
.aw-status-pending { background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; }

/* ── Footer ───────────────────────────────────────────────────────────────── */
.aw-footer {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 24px; border-top: 1px solid #f0f0f5;
  flex-shrink: 0; background: #fff; gap: 12px;
}
.aw-footer-counts { display: flex; align-items: center; gap: 6px; font-size: 0.76rem; flex: 1; }
.aw-fc-present { color: #16a34a; font-weight: 700; }
.aw-fc-absent  { color: #dc2626; font-weight: 700; }
.aw-fc-pending { color: #94a3b8; }
.aw-fc-sep     { color: #cbd5e1; }
.aw-footer-actions { display: flex; gap: 8px; flex-shrink: 0; }

/* Responsive */
@media (max-width: 768px) {
  .aw-card { width: 95vw; height: 92vh; border-radius: 12px; }
  .aw-toolbar-row { flex-direction: column; align-items: stretch; gap: 12px; }
  .aw-select-input { width: 100%; }
  .aw-action-wrap { justify-content: flex-end; }
}
</style>
