# Contributing to openEMIS

Thank you for your interest in contributing. This guide covers how to get set up, the branching strategy, code standards, and the review process.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Which Version to Work On](#which-version-to-work-on)
3. [Branching Strategy](#branching-strategy)
4. [Development Workflow](#development-workflow)
5. [Code Standards](#code-standards)
6. [Commit Messages](#commit-messages)
7. [Pull Request Process](#pull-request-process)
8. [Reporting Bugs](#reporting-bugs)
9. [Proposing Features](#proposing-features)

---

## Getting Started

1. Fork the repository on GitHub: https://github.com/eodenyire/openemis
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/openemis.git
   cd openemis
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/eodenyire/openemis.git
   ```
4. Pick the version you want to work on and follow its setup guide:
   - [v1 Developer Guide](versions/v1/DEVELOPER_GUIDE.md)
   - [v2 Developer Guide](versions/v2/DEVELOPER_GUIDE.md)
   - [v3 Developer Guide](versions/v3/DEVELOPER_GUIDE.md)
   - [v4 Developer Guide](versions/v4/DEVELOPER_GUIDE.md)

---

## Which Version to Work On

| If you want to... | Work on |
|-------------------|---------|
| Add a new REST API endpoint | v1 or v2 |
| Build a new frontend page/component | v2 (Next.js) |
| Add a new Odoo module or extend an existing one | v3 |
| Work on the Django web app | v4 |
| Fix a bug that exists across versions | Fix in the most relevant version first, then port |

---

## Branching Strategy

We use a simplified Git Flow:

```
main          → stable, production-ready code
develop       → integration branch — all PRs merge here first
feature/*     → new features (branch from develop)
fix/*         → bug fixes (branch from develop)
hotfix/*      → critical production fixes (branch from main)
```

### Branch naming

```bash
feature/v2-add-timetable-export
fix/v1-jwt-expiry-bug
hotfix/v3-odoo-module-install-error
```

Always prefix with the version if the change is version-specific.

---

## Development Workflow

```bash
# 1. Sync with upstream
git fetch upstream
git checkout develop
git merge upstream/develop

# 2. Create your branch
git checkout -b feature/v2-add-something

# 3. Make your changes
# ... write code ...

# 4. Run tests before committing
# v1/v2: pytest tests/ -v
# v3: bash scripts/run_module_tests.sh MODULE_NAME
# v4: python manage.py test

# 5. Commit
git add .
git commit -m "feat(v2): add timetable export to Excel"

# 6. Push and open PR
git push origin feature/v2-add-something
```

---

## Code Standards

### Python (v1, v2, v4)

- Follow PEP 8
- Use `black` for formatting: `black app/`
- Use `flake8` for linting: `flake8 app/`
- Use `pylint` for deeper analysis: `pylint app/`
- Type hints are required on all function signatures
- Docstrings on all public functions and classes

```python
# Good
def get_student(student_id: int, db: Session) -> StudentSchema:
    """Retrieve a student by ID. Raises 404 if not found."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
```

### TypeScript / React (v2 frontend)

- Use TypeScript strictly — no `any` types
- Components in `PascalCase`, files in `kebab-case`
- Use React Query for all server state — no raw `useEffect` for data fetching
- Use Zod schemas for all form validation
- Keep components small — extract logic into custom hooks

### Python / Odoo (v3)

- Follow Odoo coding guidelines: https://www.odoo.com/documentation/18.0/contributing/development/coding_guidelines.html
- All models must have `_name`, `_description`, and `_inherit` (if extending)
- Security: every new model needs an entry in `security/ir.model.access.csv`
- Views must be defined in XML under `views/`
- Use `_compute_` prefix for computed fields, `_onchange_` for onchange methods

### Django (v4)

- Follow Django best practices and the Django style guide
- Keep views thin — business logic belongs in model methods or service functions
- Use DRF serializers for all API responses
- Write migrations for every model change: `python manage.py makemigrations`

---

## Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

Types:
- `feat` — new feature
- `fix` — bug fix
- `docs` — documentation only
- `refactor` — code change that neither fixes a bug nor adds a feature
- `test` — adding or updating tests
- `chore` — build process, dependency updates, tooling

Examples:
```
feat(v1): add M-Pesa payment webhook endpoint
fix(v3): resolve openemis_fees module install dependency error
docs(v2): update API_REFERENCE with new digiguide endpoints
refactor(v4): extract attendance logic into service layer
```

---

## Pull Request Process

1. Ensure your branch is up to date with `develop`
2. All tests must pass
3. No linting errors
4. Update relevant documentation (README, API_REFERENCE, etc.)
5. Fill in the PR template — describe what changed and why
6. Request review from at least one maintainer
7. PRs are squash-merged into `develop`

### PR Checklist

- [ ] Tests pass locally
- [ ] No new linting errors
- [ ] Documentation updated
- [ ] CHANGELOG.md entry added (for features and fixes)
- [ ] No secrets or credentials committed

---

## Reporting Bugs

Open a GitHub Issue with:
- Which version (v1/v2/v3/v4)
- Steps to reproduce
- Expected vs actual behavior
- Environment (OS, Python version, browser if frontend)
- Relevant logs or error messages

---

## Proposing Features

Open a GitHub Issue with the `enhancement` label. Describe:
- The problem you're solving
- Your proposed solution
- Which version(s) it affects
- Any alternatives you considered

For large features, open a discussion first before writing code.

---

## License

By contributing, you agree that your contributions will be licensed under the LGPL-3.0 license (or MIT for v4).
