/**
 * Helper to calculate event status consistently across the frontend:
 * - Scheduled -> current date is before start date.
 * - Live -> current date is between start and end date (inclusive).
 * - Completed -> current date is after end date OR manually closed/completed.
 */
export function getEventStatus(event) {
  if (!event) return 'Scheduled'

  const rawStatus = String(event.rawStatus || event.status || event.event_status || '').toUpperCase()
  if (['COMPLETED', 'CLOSED', 'CANCELLED'].includes(rawStatus)) {
    return 'Completed'
  }

  if (!event.startDate) {
    if (rawStatus === 'LIVE') return 'Live'
    return 'Scheduled'
  }

  const now = new Date()
  now.setHours(0, 0, 0, 0)

  const startDate = new Date(event.startDate)
  startDate.setHours(0, 0, 0, 0)

  const endDate = event.endDate ? new Date(event.endDate) : new Date(startDate)
  endDate.setHours(23, 59, 59, 999)

  if (now > endDate) {
    return 'Completed'
  } else if (now < startDate) {
    return 'Scheduled'
  } else {
    return 'Live'
  }
}

/**
 * Sorts events so that Live events come first, then Scheduled, then Completed.
 */
export function sortEventsByStatusOrder(events) {
  const statusPriority = {
    'Live': 1,
    'Scheduled': 2,
    'Completed': 3
  }

  return [...events].sort((a, b) => {
    const prioA = statusPriority[getEventStatus(a)] || 99
    const prioB = statusPriority[getEventStatus(b)] || 99
    return prioA - prioB
  })
}
