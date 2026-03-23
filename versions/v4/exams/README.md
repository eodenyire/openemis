# exams — Examination System (v4)

Django app managing both traditional exams and online assessments.

## Files
- `models.py` — `Exam`, `ExamResult`, `OnlineExam`, `Question`, `StudentAnswer`, `OnlineExamResult`
- `views.py` — Exam management, mark entry, online exam taking, result views
- `urls.py` — Exam URL patterns
- `admin.py` — Admin registration

## Models
- `Exam` — Traditional exam definitions (name, class, subject, date, max marks)
- `ExamResult` — Student marks per exam
- `OnlineExam` — Online exam definitions with time limits
- `Question` — Multiple choice, true/false, and short answer questions
- `StudentAnswer` — Student responses to online exam questions
- `OnlineExamResult` — Auto-graded online exam results

## Key Features
- Traditional exam mark entry and grade assignment
- Online exam system with multiple question types
- Automatic grading for online exams
- Result calculation and GPA computation
- Result publishing and parent notifications
- Result slips (PDF)

## API
REST endpoints at `/api/exams/`.
