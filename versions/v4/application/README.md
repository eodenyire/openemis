# application — CodeIgniter Application (v4 Legacy)

The CodeIgniter MVC application directory from the original PHP-based school management system.

## Structure

```
application/
├── cache/          # CI framework cache storage
├── config/         # Database, routes, autoload, email config
├── controllers/    # PHP controllers (Students, Teachers, Exams, etc.)
├── core/           # Custom CI core extensions
├── helpers/        # Custom PHP helper functions
├── hooks/          # CI hooks for pre/post controller actions
├── language/       # Internationalisation language files
├── libraries/      # Custom PHP libraries
├── logs/           # Application error logs
├── models/         # PHP data models (CI Active Record)
├── third_party/    # Third-party PHP libraries
└── views/          # PHP view templates (HTML + PHP)
```

## Purpose

This is the original CodeIgniter 3 application that the v4 Django system was built to replace and modernise. It contains the full PHP MVC implementation of the school management features.

## Status

Legacy — not actively developed. The Django REST API (`school_management/` package) is the current backend. This directory is retained for:
- Reference when porting features to Django
- Understanding the original data model
- Backward compatibility during migration
