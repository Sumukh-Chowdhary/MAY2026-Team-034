export const LEGACY_READ_ONLY_MESSAGE = "Your student account is now read-only because your student lifecycle is marked Legacy."

export function isLegacyUser(user) {
  if (!user) {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        user = JSON.parse(userStr)
      } catch (e) {
        return false
      }
    }
  }
  if (!user) return false
  return user.status === 'LEGACY' || user.account_status === 'LEGACY' || user.isLegacy === true
}

export function canPerformStudentAction(user, action) {
  if (isLegacyUser(user)) {
    return false
  }
  return true
}
