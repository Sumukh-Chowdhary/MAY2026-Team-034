import { getCurrentUser } from '@/services/authService';

/**
 * Centralized Notification Action Resolver
 * Evaluates a notification object and returns a structured action object or null.
 * 
 * Returns:
 * {
 *   label: "View Ticket" | "View Request" | "View Club" | "View Event" | "View Application" | "View Role" | "View Budget",
 *   type: "route",
 *   route: "/student/events/12"
 * }
 * OR null if there is no valid actionable entity.
 * 
 * NEVER returns '/' or public landing page.
 */
export function resolveNotificationAction(notification, userRole = null) {
  if (!notification) return null;

  const role = String(userRole || getCurrentUser()?.role || 'STUDENT').toUpperCase();
  const rolePrefix = role === 'ADMIN' ? '/admin' : (role === 'FACULTY' ? '/faculty' : '/student');

  const rawType = String(notification.type || notification.notification_type || '').toUpperCase();
  const rawEntityType = String(notification.entityType || notification.entity_type || '').toUpperCase();
  const entityId = notification.entityId || notification.entity_id;
  const rawUrl = String(notification.referenceUrl || notification.reference_url || notification.target_url || '').trim();

  // Helper to construct clean route string
  const getEventRoute = (id) => id ? `${rolePrefix}/events/${id}` : `${rolePrefix}/events`;
  const getClubRoute = (id) => id ? `${rolePrefix}/clubs/${id}` : `${rolePrefix}/clubs`;
  const getRequestRoute = () => `${rolePrefix}/requests`;
  const getRoleRoute = () => `${rolePrefix}/roles`;

  // 1. TICKET Notifications
  if (
    rawType.includes('TICKET') ||
    rawEntityType === 'TICKET'
  ) {
    return {
      label: 'View Ticket',
      type: 'route',
      route: getRequestRoute()
    };
  }

  // 2. REQUEST & APPROVAL Notifications
  if (
    rawType.includes('REQUEST') ||
    rawType.includes('VENUE') ||
    rawEntityType === 'REQUEST'
  ) {
    return {
      label: 'View Request',
      type: 'route',
      route: getRequestRoute()
    };
  }

  // 3. BUDGET Notifications
  if (
    rawType.includes('BUDGET') ||
    rawEntityType === 'BUDGET' ||
    rawEntityType === 'BANK'
  ) {
    return {
      label: 'View Budget',
      type: 'route',
      route: getRequestRoute()
    };
  }

  // 4. VOLUNTEER Notifications
  if (
    rawType.includes('VOLUNTEER') ||
    rawEntityType === 'VOLUNTEER'
  ) {
    return {
      label: 'View Application',
      type: 'route',
      route: role === 'STUDENT' ? '/student/roles' : getRequestRoute()
    };
  }

  // 5. ROLE Notifications
  if (
    rawType.includes('ROLE') ||
    rawEntityType === 'ROLE'
  ) {
    return {
      label: 'View Role',
      type: 'route',
      route: getRoleRoute()
    };
  }

  // 6. EVENT & ANNOUNCEMENT Notifications
  if (
    rawType.includes('EVENT') ||
    rawType.includes('ANNOUNCEMENT') ||
    rawType.includes('COMPETITION') ||
    rawType.includes('REGISTRATION') ||
    rawType.includes('SHORTLISTED') ||
    rawType.includes('ELIMINATED') ||
    rawType.includes('WINNER') ||
    rawEntityType === 'EVENT'
  ) {
    return {
      label: 'View Event',
      type: 'route',
      route: getEventRoute(entityId)
    };
  }

  // 7. CLUB Notifications
  if (
    rawType.includes('CLUB') ||
    rawEntityType === 'CLUB'
  ) {
    return {
      label: 'View Club',
      type: 'route',
      route: getClubRoute(entityId)
    };
  }

  // 8. Sanitize & Inspect referenceUrl if provided
  if (rawUrl && rawUrl !== '/' && rawUrl !== '/login' && rawUrl !== '/register') {
    let sanitizedPath = rawUrl;
    if (sanitizedPath.startsWith('/student/') || sanitizedPath.startsWith('/faculty/') || sanitizedPath.startsWith('/admin/')) {
      sanitizedPath = sanitizedPath.replace(/^\/(student|faculty|admin)/, rolePrefix);
    } else if (!sanitizedPath.startsWith('/')) {
      sanitizedPath = `${rolePrefix}/${sanitizedPath}`;
    }

    if (sanitizedPath.includes('/events/')) {
      return { label: 'View Event', type: 'route', route: sanitizedPath };
    }
    if (sanitizedPath.includes('/clubs/')) {
      return { label: 'View Club', type: 'route', route: sanitizedPath };
    }
    if (sanitizedPath.includes('/requests') || sanitizedPath.includes('/tickets')) {
      return { label: 'View Request', type: 'route', route: getRequestRoute() };
    }
    if (sanitizedPath.includes('/roles')) {
      return { label: 'View Role', type: 'route', route: getRoleRoute() };
    }
  }

  // No actionable entity or valid route could be determined
  return null;
}

/**
 * Backward compatibility alias for resolveNotificationDestination
 */
export function resolveNotificationDestination(notification, userRole = 'STUDENT') {
  const action = resolveNotificationAction(notification, userRole);
  return action ? action.route : null;
}

/**
 * Main Centralized Notification Action Handler
 * Navigates to resolved entity route, or displays warning toast if details unavailable.
 * NEVER navigates to landing page '/' or invalid routes.
 */
export async function handleNotificationDetails(notification, router, notificationStore = null, showToast = null) {
  if (!notification) return;

  const user = getCurrentUser();
  const role = (user?.role || 'STUDENT').toUpperCase();
  const action = resolveNotificationAction(notification, role);

  const unavailableMsg = "Details are no longer available.";

  if (!action || !action.route) {
    if (showToast) showToast(unavailableMsg, "warning");
    return;
  }

  const targetPath = typeof action.route === 'string' ? action.route : (action.route.path || action.route);

  // Safety check: Never accept '/' or auth routes
  if (!targetPath || targetPath === '/' || targetPath === '/login' || targetPath === '/register') {
    if (showToast) showToast(unavailableMsg, "warning");
    return;
  }

  // Validate route in router
  try {
    const resolved = router.resolve(targetPath);
    if (!resolved || !resolved.matched || !resolved.matched.length || resolved.name === 'Landing') {
      if (showToast) showToast(unavailableMsg, "warning");
      return;
    }
  } catch (e) {
    if (showToast) showToast(unavailableMsg, "warning");
    return;
  }

  // Mark notification as read
  if (notificationStore && !notification.isRead) {
    try {
      await notificationStore.markAsRead(notification.id);
    } catch (err) {
      console.error("Failed to mark notification as read:", err);
    }
  }

  router.push(targetPath);
}
