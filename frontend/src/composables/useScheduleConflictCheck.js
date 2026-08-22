import { ref } from 'vue'
import { getScheduleConflicts, registerForEvent } from '@/api/events'

/**
 * Wraps event registration with a schedule-conflict check.
 *
 * Before actually registering, this checks whether the student already
 * has an active registration for another event whose date/time overlaps
 * with the one they're about to register for. If so, it surfaces the
 * conflicting event(s) via reactive state so a <ScheduleConflictModal>
 * can show them and let the student decide whether to proceed.
 *
 * Usage:
 *   const {
 *     showConflictModal, pendingConflicts, pendingEventName,
 *     registerWithConflictCheck, confirmRegistration, cancelRegistration
 *   } = useScheduleConflictCheck()
 *
 *   const result = await registerWithConflictCheck(eventId, eventName)
 *   if (result.cancelled) return
 *   // result.response has the registration payload
 */
export function useScheduleConflictCheck() {
  const showConflictModal = ref(false)
  const pendingConflicts = ref([])
  const pendingEventName = ref('')
  const checkingConflicts = ref(false)

  let resolveDecision = null

  async function registerWithConflictCheck(eventId, eventName = '') {
    checkingConflicts.value = true
    let conflicts = []

    try {
      const data = await getScheduleConflicts(eventId)
      conflicts = data?.conflicts || []
    } catch (err) {
      // If the conflict check itself fails, don't block registration —
      // just skip straight to registering rather than leaving the user stuck.
      console.error('Could not check for schedule conflicts', err)
      conflicts = []
    } finally {
      checkingConflicts.value = false
    }

    if (conflicts.length > 0) {
      pendingConflicts.value = conflicts
      pendingEventName.value = eventName
      showConflictModal.value = true

      const proceed = await new Promise((resolve) => {
        resolveDecision = resolve
      })

      showConflictModal.value = false

      if (!proceed) {
        return { registered: false, cancelled: true }
      }
    }

    const response = await registerForEvent(eventId)
    return { registered: true, cancelled: false, response }
  }

  function confirmRegistration() {
    if (resolveDecision) resolveDecision(true)
  }

  function cancelRegistration() {
    if (resolveDecision) resolveDecision(false)
  }

  return {
    showConflictModal,
    pendingConflicts,
    pendingEventName,
    checkingConflicts,
    registerWithConflictCheck,
    confirmRegistration,
    cancelRegistration
  }
}
