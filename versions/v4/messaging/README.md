# messaging — Communication System (v4)

Django app providing private messaging and group communication between users.

## Files
- `models.py` — `Message`, `GroupMessage`, `MessageAttachment`
- `views.py` — Inbox, compose, group messaging views
- `urls.py` — Messaging URL patterns
- `admin.py` — Admin registration

## Models
- `Message` — Private messages between two users (sender, recipient, content, timestamp, read status)
- `GroupMessage` — Messages sent to a group (class, all teachers, all parents)
- `MessageAttachment` — File attachments on messages

## Key Features
- Private messaging between any two users
- Group messaging (broadcast to class, role, or all users)
- File attachment support
- Read/unread status tracking
- Real-time notification triggers

## API
REST endpoints at `/api/messaging/`.
