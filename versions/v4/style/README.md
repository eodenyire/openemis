# style — UI Stylesheets & Themes (v4 Legacy)

CSS/LESS stylesheets and UI theme files for the legacy frontend layer of the v4 system.

## Structure

```
style/
├── calendar/       # FullCalendar CSS overrides
├── cms/            # CMS/content page styles
├── flags/          # Country flag icon sprites
├── fonts/          # Embedded web fonts
├── fullcalendar/   # FullCalendar library styles
├── images/         # Background images and UI graphics
├── js/             # Theme-specific JavaScript
├── less/           # LESS source files (compiled to CSS)
├── login/          # Login page theme
├── olapp/          # Online application portal styles
├── tables/         # DataTables styling
├── tabs/           # Tab component styles
├── tinymce/        # TinyMCE rich text editor theme
├── style.css       # Main compiled stylesheet
└── picker.css      # Date/colour picker styles
```

## Note

These are legacy styles from the original PHP-based school management system. The Django REST API backend (v4 core) and the Next.js frontend (v2) use Tailwind CSS and shadcn/ui instead. These files are preserved for reference.
