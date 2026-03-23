# finance — Finance & Payments (v4)

Django app handling school financial records — fee payments, expenses, and per-student payment tracking.

## Models

### PaymentCategory
Groups payments into categories (e.g., Tuition, Transport, Meals, Stationery).

### Payment
Core financial transaction record:
- `title`, `description`, `amount`
- `payment_type` — `income` (fees received) or `expense` (school expenditure)
- `category` → `PaymentCategory`
- `student` → `StudentProfile` (optional, for student-specific payments)
- `payment_date`, `academic_year` → `AcademicYear`
- `recorded_by` → `AccountantProfile`

## Views & URLs

- Record a new payment (income or expense)
- List payments by student, category, or academic year
- Financial summary dashboard (total income vs expenses)
- Per-student fee balance report

## Admin

Payment categories and transactions are managed via Django Admin.

## Dependencies

- `accounts` app — `StudentProfile`, `AccountantProfile`
- `academic` app — `AcademicYear`
