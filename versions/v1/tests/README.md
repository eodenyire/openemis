# tests — Test Suite (v1)

Pytest-based test suite for the openEMIS v1 FastAPI backend.

## Structure

```
tests/
├── __init__.py
└── test_api.py     # API endpoint integration tests
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run a specific test
pytest tests/test_api.py::test_health -v
```

## What's Tested

- Health check endpoint
- Authentication (login, token validation)
- Core CRUD operations (students, teachers, courses)
- API response schemas

## CI

Tests run automatically on every push and pull request via the GitHub Actions CI workflow (`.github/workflows/ci.yml`).
