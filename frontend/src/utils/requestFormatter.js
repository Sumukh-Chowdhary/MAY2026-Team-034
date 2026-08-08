/**
 * Reusable Request Formatter / Preview Helper (getRequestPreview)
 * Parses stored JSON payloads or structured requests and formats clean human-readable preview objects.
 * Prevents raw JSON strings from being rendered anywhere in the application UI.
 */

export function parseRequestPayload(req) {
  if (!req) return null
  const desc = req.description || req.details || ''
  if (typeof desc === 'string' && desc.trim().startsWith('{') && desc.trim().endsWith('}')) {
    try {
      return JSON.parse(desc)
    } catch (e) {
      return null
    }
  }
  if (typeof desc === 'object' && desc !== null) {
    return desc
  }
  return null
}

export function formatEventCreationRequest(req) {
  if (!req) {
    return {
      name: '',
      club: 'Campus Club',
      venue: 'Campus Venue',
      startDate: '',
      endDate: '',
      startTime: null,
      endTime: null,
      eventType: 'General Event',
      capacity: null,
      description: '',
      rawStatus: 'PENDING',
      statusDisplay: 'Pending Approval'
    }
  }

  const payload = parseRequestPayload(req)

  const rawTitle = req.title || req.subject || 'Event Request'
  const name = (payload && payload.name) ? payload.name : rawTitle.replace(/^Create Event:\s*/i, '')
  let club = req.referenceName || req.club || (payload ? (payload.club || payload.clubName) : '') || 'Campus Club'
  if (club === 'General Event' || club === 'General') {
    club = 'General Institutional Event'
  }

  const venue = (payload ? (payload.venueName || payload.venue || payload.venue_name) : '') || req.venueName || 'Campus Venue'
  const startDate = (payload ? (payload.startDate || payload.date) : '') || req.startDate || req.date || ''
  const endDate = (payload ? (payload.endDate) : '') || req.endDate || startDate
  const startTime = payload ? payload.startTime : null
  const endTime = payload ? payload.endTime : null
  const eventType = (payload ? (payload.eventType || payload.organizerType) : '') || 'General Event'
  const capacity = payload && payload.capacity ? Number(payload.capacity) : null
  const description = payload ? (payload.description || '') : (typeof req.description === 'string' && !req.description.startsWith('{') ? req.description : '')

  const rawStatus = (req.workflowStatus || req.approvalStatus || req.status || 'PENDING').toUpperCase()
  let statusDisplay = 'Pending Approval'
  if (rawStatus === 'APPROVED') statusDisplay = 'Approved'
  else if (rawStatus === 'REJECTED') statusDisplay = 'Rejected'
  else if (rawStatus === 'CHANGES_REQUESTED') statusDisplay = 'Changes Requested'
  else if (rawStatus === 'CANCELLED') statusDisplay = 'Cancelled'

  return {
    name,
    club,
    venue,
    startDate,
    endDate,
    startTime,
    endTime,
    eventType,
    capacity,
    description,
    rawStatus,
    statusDisplay
  }
}

export function getRequestPreview(req) {
  if (!req) {
    return {
      title: '',
      subtitle: '',
      secondaryLine: '',
      date: '',
      capacity: null,
      status: 'Pending Approval',
      rawStatus: 'PENDING',
      isStructured: false,
      rawDescription: ''
    }
  }

  const payload = parseRequestPayload(req)
  const reqType = (req.requestType || req.ticketType || req.type || '').toUpperCase()

  const isEventCreation = reqType === 'CREATE_EVENT_AS_ORGANIZER' || !!(payload && (payload.name || payload.venueId || payload.organizerType))

  if (isEventCreation) {
    const formatted = formatEventCreationRequest(req)
    let dateFormatted = ''
    if (formatted.startDate) {
      try {
        const d = new Date(formatted.startDate)
        if (!isNaN(d.getTime())) {
          dateFormatted = d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
        } else {
          dateFormatted = formatted.startDate
        }
      } catch (e) {
        dateFormatted = formatted.startDate
      }
    }

    return {
      title: `Create Event: ${formatted.name}`,
      subtitle: formatted.club,
      secondaryLine: formatted.venue,
      date: dateFormatted,
      capacity: formatted.capacity,
      status: formatted.statusDisplay,
      rawStatus: formatted.rawStatus,
      isStructured: true,
      rawDescription: formatted.description
    }
  }

  // Handle other structured request types (Venue Request, Budget Request, Schedule Request, etc.)
  if (payload) {
    const rawStatus = (req.workflowStatus || req.approvalStatus || req.status || 'PENDING').toUpperCase()
    let statusDisplay = 'Pending Approval'
    if (rawStatus === 'APPROVED') statusDisplay = 'Approved'
    else if (rawStatus === 'REJECTED') statusDisplay = 'Rejected'
    else if (rawStatus === 'CHANGES_REQUESTED') statusDisplay = 'Changes Requested'

    return {
      title: payload.title || payload.subject || req.title || req.subject || 'Structured Request',
      subtitle: payload.club || req.referenceName || 'Campus Request',
      secondaryLine: payload.venue || payload.venueName || payload.reason || '',
      date: payload.date || payload.startDate || '',
      capacity: payload.capacity ? Number(payload.capacity) : null,
      status: statusDisplay,
      rawStatus,
      isStructured: true,
      rawDescription: payload.description || ''
    }
  }

  // Legacy / Plain text requests
  const rawStatus = (req.workflowStatus || req.approvalStatus || req.status || 'PENDING').toUpperCase()
  let statusDisplay = 'Pending Approval'
  if (rawStatus === 'APPROVED') statusDisplay = 'Approved'
  else if (rawStatus === 'REJECTED') statusDisplay = 'Rejected'
  else if (rawStatus === 'CHANGES_REQUESTED') statusDisplay = 'Changes Requested'

  let dateFormatted = ''
  if (req.createdAt || req.date) {
    try {
      const d = new Date(req.createdAt || req.date)
      if (!isNaN(d.getTime())) {
        dateFormatted = d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
      }
    } catch (e) {}
  }

  const desc = req.description || req.details || ''
  const isJsonStr = typeof desc === 'string' && desc.trim().startsWith('{')

  return {
    title: req.title || req.subject || 'Request',
    subtitle: req.referenceName || req.club || 'General',
    secondaryLine: '',
    date: dateFormatted,
    capacity: null,
    status: statusDisplay,
    rawStatus,
    isStructured: false,
    rawDescription: isJsonStr ? '' : desc
  }
}

export function formatRequestPreview(req) {
  return getRequestPreview(req)
}
