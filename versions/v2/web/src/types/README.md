# src/types — TypeScript Type Definitions (v2)

Shared TypeScript interfaces and types used across the entire Next.js frontend.

## Files

| File | Types |
|---|---|
| `user.ts` | `User`, `Role`, `AuthToken`, `LoginCredentials` |
| `student.ts` | `Student`, `Guardian`, `Enrollment`, `ClassGroup` |
| `faculty.ts` | `Teacher`, `Department`, `Subject` |
| `admission.ts` | `Application`, `ApplicationStatus` |
| `attendance.ts` | `AttendanceRecord`, `AttendanceSummary` |
| `exam.ts` | `ExamResult`, `GradeReport`, `ResultSlip` |
| `fees.ts` | `Invoice`, `Payment`, `MpesaTransaction` |
| `cbc.ts` | `CBCStrand`, `LearningOutcome`, `Assessment`, `Portfolio` |
| `api.ts` | `ApiResponse<T>`, `PaginatedResponse<T>`, `ApiError` |

## Conventions

- All types mirror the Pydantic schemas from the v2 FastAPI backend
- Generic `ApiResponse<T>` wraps all API responses for consistent error handling
- Enums are defined as TypeScript `const` objects with `as const` for type safety
