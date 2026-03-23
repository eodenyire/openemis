# accounts — User Management & Authentication (v4)

Django app handling all user accounts, authentication, and role-based access control.

## Files
- `models.py` — Custom `User` model extending `AbstractUser` with `user_type` field (admin, teacher, student, parent, librarian, accountant). Includes `AdminProfile`, `TeacherProfile`, `StudentProfile`, `ParentProfile`, `LibrarianProfile`, `AccountantProfile`.
- `views.py` — Login, logout, registration, profile management views
- `serializers.py` — DRF serializers for user data
- `urls.py` — Auth URL patterns
- `admin.py` — Django admin registration

## User Types
| Type | Access |
|------|--------|
| `admin` | Full system access |
| `teacher` | Classes, attendance, exams, marks |
| `student` | Results, online exams, materials |
| `parent` | Child's progress and attendance |
| `librarian` | Books and library operations |
| `accountant` | Payments and financial records |

## Auth
JWT-based authentication via `djangorestframework-simplejwt`. Access tokens expire in 60 minutes, refresh tokens in 7 days.
