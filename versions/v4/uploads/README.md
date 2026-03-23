# uploads — User-Uploaded Media (v4)

Directory for user-uploaded files and media assets served via Django's `MEDIA_URL`.

## Structure

```
uploads/
├── icons/          # Custom school/module icons uploaded by admin
├── import/         # Bulk import files (CSV/Excel for student/teacher data)
├── parent_image/   # Parent profile photos
├── teacher_image/  # Teacher profile photos
├── templates/      # Downloadable document templates (admission forms, etc.)
└── *.png / *.svg   # Branding assets: logos, favicons, UI graphics
```

## Branding Assets

| File | Purpose |
|---|---|
| `logo.png` | Primary school logo |
| `logo-color.png` | Colour variant of the logo |
| `logo-white.png` | White variant for dark backgrounds |
| `logo-icon.png` | Icon-only logo for favicon/mobile |
| `favicon.png` | Browser tab favicon |

## Configuration

In `settings.py`:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

In production, serve media files via Nginx rather than Django's development server.

## Note

This directory is excluded from version control (`.gitignore`) for user-uploaded content. Only the branding assets and templates are committed.
