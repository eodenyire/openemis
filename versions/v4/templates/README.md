# templates — Django HTML Templates (v4)

Django HTML templates that render the server-side UI for the v4 school management system.

## Structure

```
templates/
├── base.html           # Master layout: navbar, sidebar, footer, JS/CSS includes
├── accounts/           # Login, register, profile, password change pages
└── includes/           # Reusable partials: nav, sidebar, alerts, pagination
```

## base.html

The master template that all other templates extend via `{% extends "base.html" %}`. It provides:
- Bootstrap-based responsive layout
- Navigation bar with user role-aware menu items
- Sidebar with module links
- Flash message display
- Common JS/CSS asset includes

## accounts/

Templates for user-facing auth flows:
- `login.html` — Login form
- `register.html` — Student/teacher registration
- `profile.html` — User profile view and edit

## includes/

Reusable template fragments included with `{% include %}`:
- `_navbar.html` — Top navigation bar
- `_sidebar.html` — Left sidebar with module links
- `_alerts.html` — Django messages display
- `_pagination.html` — Paginator controls

## Note

The v4 system also exposes a REST API (DRF) consumed by the Next.js frontend in v2. These templates serve the legacy server-rendered interface.
