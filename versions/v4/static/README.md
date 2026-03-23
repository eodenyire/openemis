# static — Static Assets (v4)

Static files served by Django for the v4 school management system.

## Structure

```
static/
├── css/        # Custom stylesheets overriding Bootstrap defaults
└── images/     # School logo, default avatars, UI icons
```

## css/

Custom CSS that extends the Bootstrap base:
- Theme colours matching the openEMIS brand
- Dashboard card and table styles
- Print styles for reports and result slips

## images/

- Default student/teacher avatar placeholders
- School logo used in headers and PDF reports
- UI icons not covered by Font Awesome

## Collected Assets

Run `python manage.py collectstatic` to gather all static files (including from installed apps) into `staticfiles/` for production serving via Nginx or WhiteNoise.

## Note

User-uploaded files (profile photos, documents) are stored separately under `uploads/` and served via `MEDIA_URL`.
