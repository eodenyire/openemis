# theme_web_openeducat — Web Theme (v1)

Custom Odoo web theme module providing the openEMIS visual identity for the v1 system's web interface.

## Purpose

This is an Odoo addon that overrides default Odoo web styling with the openEMIS brand — colours, fonts, logo, and layout adjustments tailored for an education management context.

## Structure

- `static/` — CSS, SCSS, images, and JavaScript assets for the theme
- `views/` — XML view overrides that inject theme assets into Odoo's web client
- `__manifest__.py` — Odoo module manifest declaring dependencies and asset bundles
- `__init__.py` — Python package marker

## What It Changes

- Primary colour palette to openEMIS brand colours
- Login page background and logo
- Navigation menu styling
- Dashboard card and list view aesthetics
- Print stylesheet for reports

## Note

This theme is specific to the Odoo-based v1 architecture. The v2 system uses a custom Next.js frontend (Tailwind CSS + shadcn/ui) and does not use this theme.
