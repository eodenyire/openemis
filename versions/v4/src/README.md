# src — Legacy PHP Source (v4)

PHP source files from the legacy CodeIgniter layer of the original open-source school management system.

## Structure

```
src/
├── auth/           # OAuth and authentication helpers
├── cache/          # Caching utilities
├── contrib/        # Third-party PHP contributions
├── external/       # External API integrations
├── io/             # File I/O helpers
├── service/        # Service layer classes
├── config.php      # PHP application configuration
└── Google_Client.php  # Google OAuth client integration
```

## Purpose

This directory contains the PHP/CodeIgniter source code from the original school management system that v4 was forked from. It provides:
- Google OAuth login integration
- Legacy API service classes
- File handling utilities

## Note

The active v4 backend is the Django application in the project root (`manage.py`, `school_management/`, `accounts/`, etc.). This `src/` directory is legacy code retained for reference and migration purposes. New features should be built in the Django layer.
