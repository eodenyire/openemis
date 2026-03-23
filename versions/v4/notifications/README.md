# notifications — In-App Notifications (v4)

Django app that delivers in-app notifications to all user types — students, teachers, parents, and admins.

## Model

### Notification
- `recipient` → `User` (any user in the system)
- `title`, `message` — notification content
- `notification_type` — one of: `news`, `exam`, `message`, `attendance`, `payment`, `general`
- `is_read` — tracks read/unread state
- `url` — optional deep link to the relevant page
- `created_at` — ordered newest-first by default

## Views & URLs

- List notifications for the current user (unread first)
- Mark a notification as read
- Mark all notifications as read
- Notification count badge endpoint (for the UI header)

## Integration

Other apps trigger notifications by creating `Notification` objects:
- `exams` app creates exam result notifications
- `attendance` app creates absence alerts for parents
- `finance` app creates payment confirmation notifications
- `messaging` app creates message-received notifications

## Admin

Notifications are viewable in Django Admin for debugging and support.
