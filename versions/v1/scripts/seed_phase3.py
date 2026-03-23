"""Phase 3 seed — Timetable, Lesson Plans, LMS (Virtual Classrooms, Quizzes)."""
import sys, random, string, json
from datetime import date, datetime, timedelta

import app.db.registry  # noqa — must be first

from app.db.session import SessionLocal
from app.db.base import Base
from app.db.session import engine
from app.models.core import Course, Subject, AcademicYear, AcademicTerm, Batch
from app.models.people import Teacher, Student
from app.models.timetable import Timing, Classroom as TimetableClassroom
from app.models.lms import (
    SchemeOfWork, LessonPlan, LessonPlanStatus, TeachingResource, ResourceType,
    VirtualClassroom, VirtualClassEnrollment, ClassPost, ClassAssignment,
    ClassAssignmentSubmission, AssignmentSubmissionStatus,
    Quiz, QuizQuestion, QuizQuestionType, QuizAttempt,
    TimetableSlot, AcademicCalendarEvent, CalendarEventType,
)
from app.models.cbc import SubStrand

Base.metadata.create_all(bind=engine)
db = SessionLocal()

def gen_code():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    while db.query(VirtualClassroom).filter_by(join_code=code).first():
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return code

print("=== Phase 3 Seed ===")

# ── Fetch base data ───────────────────────────────────────────────────────────
year = db.query(AcademicYear).first()
term = db.query(AcademicTerm).first()
if not year or not term:
    print("[SKIP] No academic year/term found — run seed_kenya.py first")
    sys.exit(0)

# Grade 7 course
grade7 = db.query(Course).filter(Course.name.ilike("%grade 7%")).first()
if not grade7:
    grade7 = db.query(Course).first()
print(f"[INFO] Using course: {grade7.name} (id={grade7.id})")

batch = db.query(Batch).filter_by(course_id=grade7.id).first()
if not batch:
    batch = db.query(Batch).first()

subjects = db.query(Subject).join(
    Subject.courses).filter(Course.id == grade7.id).limit(5).all()
if not subjects:
    subjects = db.query(Subject).limit(5).all()
print(f"[INFO] Found {len(subjects)} subjects")

teachers = db.query(Teacher).limit(10).all()
students_all = db.query(Student).limit(30).all()
print(f"[INFO] {len(teachers)} teachers, {len(students_all)} students available")

# ── Timings (periods) ─────────────────────────────────────────────────────────
PERIODS = [
    ("Period 1", "08:00", "08:40"),
    ("Period 2", "08:45", "09:25"),
    ("Period 3", "09:30", "10:10"),
    ("Break",    "10:10", "10:30"),
    ("Period 4", "10:30", "11:10"),
    ("Period 5", "11:15", "11:55"),
    ("Period 6", "12:00", "12:40"),
    ("Lunch",    "12:40", "13:20"),
    ("Period 7", "13:20", "14:00"),
    ("Period 8", "14:05", "14:45"),
]
timings = []
for name, start, end in PERIODS:
    existing = db.query(Timing).filter_by(name=name).first()
    if not existing:
        from datetime import time
        sh, sm = map(int, start.split(":"))
        eh, em = map(int, end.split(":"))
        t = Timing(name=name, start_time=time(sh, sm), end_time=time(eh, em))
        db.add(t); db.flush()
        timings.append(t)
    else:
        timings.append(existing)
db.commit()
print(f"[OK] {len(timings)} timings ready")

# ── Timetable Slots (Grade 7, Mon-Fri, 8 teaching periods) ───────────────────
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday"]
teaching_timings = [t for t in timings if "Period" in t.name]

# Clear existing slots for this term/course
db.query(TimetableSlot).filter_by(
    academic_term_id=term.id, course_id=grade7.id).delete()
db.commit()

slot_count = 0
subj_cycle = subjects * 10
idx = 0
for day in DAYS:
    for timing in teaching_timings:
        subj = subj_cycle[idx % len(subj_cycle)]
        teacher = teachers[idx % len(teachers)]
        idx += 1
        slot = TimetableSlot(
            academic_year_id=year.id,
            academic_term_id=term.id,
            course_id=grade7.id,
            batch_id=batch.id if batch else 1,
            subject_id=subj.id,
            teacher_id=teacher.id,
            timing_id=timing.id,
            day_of_week=day,
        )
        db.add(slot)
        slot_count += 1
db.commit()
print(f"[OK] {slot_count} timetable slots created")

# ── Academic Calendar Events ──────────────────────────────────────────────────
EVENTS = [
    ("Term 1 Begins", "other", date(2026, 1, 6), date(2026, 1, 6)),
    ("Mid-Term Break", "holiday", date(2026, 2, 20), date(2026, 2, 22)),
    ("Term 1 Exams", "exam", date(2026, 3, 20), date(2026, 3, 27)),
    ("Term 1 Ends", "other", date(2026, 3, 28), date(2026, 3, 28)),
    ("April Holiday", "holiday", date(2026, 3, 29), date(2026, 4, 26)),
    ("Term 2 Begins", "other", date(2026, 4, 27), date(2026, 4, 27)),
    ("Sports Day", "sports", date(2026, 5, 15), date(2026, 5, 15)),
    ("Parent-Teacher Meeting", "meeting", date(2026, 6, 5), date(2026, 6, 5)),
    ("Term 2 Exams", "exam", date(2026, 7, 3), date(2026, 7, 10)),
    ("Term 2 Ends", "other", date(2026, 7, 11), date(2026, 7, 11)),
    ("August Holiday", "holiday", date(2026, 7, 12), date(2026, 8, 9)),
    ("Term 3 Begins", "other", date(2026, 8, 10), date(2026, 8, 10)),
    ("School Trip", "trip", date(2026, 9, 18), date(2026, 9, 19)),
    ("End-Year Exams", "exam", date(2026, 10, 23), date(2026, 10, 30)),
    ("Graduation Day", "other", date(2026, 11, 6), date(2026, 11, 6)),
]

for title, etype, start, end in EVENTS:
    if not db.query(AcademicCalendarEvent).filter_by(title=title).first():
        db.add(AcademicCalendarEvent(
            title=title, event_type=CalendarEventType(etype),
            start_date=start, end_date=end,
            academic_year_id=year.id,
        ))
db.commit()
print(f"[OK] {len(EVENTS)} calendar events seeded")

# ── Schemes of Work + Lesson Plans ───────────────────────────────────────────
schemes_created = 0
lessons_created = 0
for i, subj in enumerate(subjects[:2]):
    teacher = teachers[i % len(teachers)]
    existing = db.query(SchemeOfWork).filter_by(
        subject_id=subj.id, academic_term_id=term.id).first()
    if existing:
        scheme = existing
    else:
        scheme = SchemeOfWork(
            title=f"Scheme of Work — {subj.name} Term 1",
            course_id=grade7.id,
            subject_id=subj.id,
            teacher_id=teacher.id,
            academic_year_id=year.id,
            academic_term_id=term.id,
            status=LessonPlanStatus.APPROVED,
        )
        db.add(scheme); db.flush()
        schemes_created += 1

    # 3 lesson plans per scheme
    for week in range(1, 4):
        if not db.query(LessonPlan).filter_by(scheme_id=scheme.id, week_number=week).first():
            db.add(LessonPlan(
                scheme_id=scheme.id,
                title=f"Week {week} — {subj.name}",
                week_number=week,
                lesson_number=1,
                objectives=f"By end of week {week}, learners will be able to demonstrate understanding of {subj.name} concepts.",
                activities="Group discussion, practical exercises, peer review",
                resources_needed="Textbook, charts, markers",
                assessment_method="Observation, oral questions, written exercise",
                duration_minutes=40,
                status=LessonPlanStatus.APPROVED,
            ))
            lessons_created += 1
db.commit()
print(f"[OK] {schemes_created} schemes, {lessons_created} lesson plans created")

# ── Teaching Resources ────────────────────────────────────────────────────────
resources_data = [
    ("CBC Mathematics Grade 7 Notes", ResourceType.PDF, "https://example.com/math-notes.pdf"),
    ("Science Experiments Video", ResourceType.VIDEO, "https://youtube.com/watch?v=example"),
    ("English Grammar Guide", ResourceType.DOCUMENT, "https://example.com/english-guide.pdf"),
    ("Kiswahili Vocabulary List", ResourceType.PDF, "https://example.com/kiswahili.pdf"),
    ("Social Studies Map Resources", ResourceType.LINK, "https://maps.example.com"),
]
res_count = 0
for title, rtype, url in resources_data:
    if not db.query(TeachingResource).filter_by(title=title).first():
        db.add(TeachingResource(
            title=title, resource_type=rtype, url=url,
            uploaded_by_id=teachers[0].id, is_public=True,
        ))
        res_count += 1
db.commit()
print(f"[OK] {res_count} teaching resources seeded")

# ── Virtual Classrooms ────────────────────────────────────────────────────────
classrooms = []
for i, subj in enumerate(subjects[:5]):
    teacher = teachers[i % len(teachers)]
    existing = db.query(VirtualClassroom).filter_by(
        subject_id=subj.id, academic_term_id=term.id).first()
    if existing:
        classrooms.append(existing)
        continue
    vc = VirtualClassroom(
        name=f"{subj.name} — Grade 7 Digital Class",
        description=f"Virtual classroom for {subj.name}, Term 1",
        course_id=grade7.id,
        subject_id=subj.id,
        teacher_id=teacher.id,
        academic_year_id=year.id,
        academic_term_id=term.id,
        join_code=gen_code(),
    )
    db.add(vc); db.flush()
    classrooms.append(vc)
db.commit()
print(f"[OK] {len(classrooms)} virtual classrooms ready")

# ── Enroll students ───────────────────────────────────────────────────────────
enroll_count = 0
for vc in classrooms:
    for student in students_all:
        if not db.query(VirtualClassEnrollment).filter_by(
                classroom_id=vc.id, student_id=student.id).first():
            db.add(VirtualClassEnrollment(classroom_id=vc.id, student_id=student.id))
            enroll_count += 1
db.commit()
print(f"[OK] {enroll_count} student enrollments created")

# ── Class Posts ───────────────────────────────────────────────────────────────
POST_TEMPLATES = [
    ("Welcome to the Digital Classroom!", "This term we will be exploring exciting topics. Please check assignments regularly."),
    ("Week 1 Notes Available", "I have uploaded the Week 1 notes. Please review before our next session."),
    ("Reminder: Assignment Due Friday", "Don't forget to submit your assignment by end of day Friday."),
]
post_count = 0
for vc in classrooms:
    for title, body in POST_TEMPLATES:
        if not db.query(ClassPost).filter_by(classroom_id=vc.id, title=title).first():
            db.add(ClassPost(classroom_id=vc.id, title=title, body=body,
                             is_pinned=(title.startswith("Welcome"))))
            post_count += 1
db.commit()
print(f"[OK] {post_count} class posts created")

# ── Assignments ───────────────────────────────────────────────────────────────
assignments = []
due = datetime.utcnow() + timedelta(days=7)
for vc in classrooms:
    for j in range(1, 3):
        title = f"Assignment {j} — {vc.name[:30]}"
        existing = db.query(ClassAssignment).filter_by(
            classroom_id=vc.id, title=title).first()
        if existing:
            assignments.append(existing)
            continue
        a = ClassAssignment(
            classroom_id=vc.id,
            title=title,
            instructions=f"Complete the following tasks for assignment {j}. Show all working.",
            total_marks=30,
            due_date=due + timedelta(days=j * 3),
            is_published=True,
        )
        db.add(a); db.flush()
        assignments.append(a)
db.commit()
print(f"[OK] {len(assignments)} assignments created")

# ── Submissions ───────────────────────────────────────────────────────────────
sub_count = 0
for assignment in assignments[:5]:  # first 5 assignments get submissions
    for student in students_all[:10]:
        if not db.query(ClassAssignmentSubmission).filter_by(
                assignment_id=assignment.id, student_id=student.id).first():
            marks = round(random.uniform(15, 30), 1)
            db.add(ClassAssignmentSubmission(
                assignment_id=assignment.id,
                student_id=student.id,
                submission_text=f"My answer for {assignment.title}. I have completed all tasks as required.",
                status=AssignmentSubmissionStatus.GRADED,
                marks_obtained=marks,
                feedback="Good work. Keep it up!",
                graded_at=datetime.utcnow(),
            ))
            sub_count += 1
db.commit()
print(f"[OK] {sub_count} assignment submissions created")

# ── Quizzes + Questions ───────────────────────────────────────────────────────
quizzes = []
for vc in classrooms:
    title = f"Quiz 1 — {vc.name[:40]}"
    existing = db.query(Quiz).filter_by(classroom_id=vc.id, title=title).first()
    if existing:
        quizzes.append(existing)
        continue
    q = Quiz(
        classroom_id=vc.id,
        title=title,
        instructions="Answer all questions. Each question carries the marks shown.",
        total_marks=10,
        duration_minutes=20,
        is_published=True,
    )
    db.add(q); db.flush()
    quizzes.append(q)
db.commit()

question_count = 0
SAMPLE_QUESTIONS = [
    ("What is the capital city of Kenya?", "mcq",
     json.dumps(["Nairobi", "Mombasa", "Kisumu", "Nakuru"]), "Nairobi", 2),
    ("The Earth revolves around the Sun.", "true_false", None, "true", 2),
    ("What is 15 × 8?", "mcq",
     json.dumps(["100", "110", "120", "130"]), "120", 2),
    ("Name the three states of matter.", "short_answer", None, None, 2),
    ("Water boils at 100°C at sea level.", "true_false", None, "true", 2),
]
for quiz in quizzes:
    existing_count = db.query(QuizQuestion).filter_by(quiz_id=quiz.id).count()
    if existing_count == 0:
        for order, (text, qtype, options, answer, marks) in enumerate(SAMPLE_QUESTIONS, 1):
            db.add(QuizQuestion(
                quiz_id=quiz.id,
                question_text=text,
                question_type=QuizQuestionType(qtype),
                marks=marks,
                order=order,
                options=options,
                correct_answer=answer,
            ))
            question_count += 1
db.commit()
print(f"[OK] {len(quizzes)} quizzes, {question_count} questions created")

# ── Quiz Attempts ─────────────────────────────────────────────────────────────
attempt_count = 0
sample_answers = json.dumps({
    "1": "Nairobi", "2": "true", "3": "120",
    "4": "Solid, liquid, gas", "5": "true"
})
for quiz in quizzes[:3]:
    questions = db.query(QuizQuestion).filter_by(quiz_id=quiz.id).all()
    for student in students_all[:8]:
        if not db.query(QuizAttempt).filter_by(
                quiz_id=quiz.id, student_id=student.id).first():
            score = round(random.uniform(4, 10), 1)
            db.add(QuizAttempt(
                quiz_id=quiz.id,
                student_id=student.id,
                answers=sample_answers,
                submitted_at=datetime.utcnow(),
                score=score,
                is_submitted=True,
            ))
            attempt_count += 1
db.commit()
print(f"[OK] {attempt_count} quiz attempts seeded")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n=== Phase 3 Seed Complete ===")
print(f"  Timetable slots : {slot_count}")
print(f"  Calendar events : {len(EVENTS)}")
print(f"  Schemes of work : {schemes_created}")
print(f"  Lesson plans    : {lessons_created}")
print(f"  Resources       : {res_count}")
print(f"  Virtual classes : {len(classrooms)}")
print(f"  Enrollments     : {enroll_count}")
print(f"  Posts           : {post_count}")
print(f"  Assignments     : {len(assignments)}")
print(f"  Submissions     : {sub_count}")
print(f"  Quizzes         : {len(quizzes)}")
print(f"  Quiz attempts   : {attempt_count}")
db.close()
