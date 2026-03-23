# library — Library Management (v4)

Django app managing the school library — book catalogue, borrowing requests, and return tracking.

## Models

### Book
Represents a physical book in the library:
- `title`, `author`, `isbn` (unique), `category`
- `total_copies` / `available_copies` — tracks stock
- `publication_year`, `added_by` (LibrarianProfile)

### BookRequest
Tracks a student's borrow lifecycle:
- Links `StudentProfile` → `Book`
- Status flow: `pending` → `approved` → `returned` (or `rejected`)
- Records `issue_date`, `return_date` (expected), `actual_return_date`
- `processed_by` — the librarian who approved/rejected

## Views & URLs

- List available books
- Student submits a borrow request
- Librarian approves/rejects requests
- Mark book as returned
- Overdue book tracking

## Admin

Books and requests are registered in Django Admin for librarian management.

## Dependencies

- `accounts` app — `StudentProfile`, `LibrarianProfile`
