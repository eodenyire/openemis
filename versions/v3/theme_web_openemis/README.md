# theme_web_openemis — Custom UI Theme

Custom Odoo web theme for openEMIS providing branded styling for the Odoo web client and portal.

## Structure

```
theme_web_openemis/
├── static/
│   └── src/
│       ├── scss/       # Custom SCSS overrides
│       └── img/        # Brand assets (logo, favicon)
└── views/
    └── templates.xml   # QWeb template overrides
```

## What It Does
- Applies openEMIS branding (colors, logo, fonts) to the Odoo web interface
- Overrides default Odoo portal templates for student/parent-facing pages
- Custom login page styling

## Depends On
`website`
