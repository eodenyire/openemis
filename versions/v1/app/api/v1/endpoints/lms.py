"""LMS endpoints — Virtual Classrooms, Assignments, Quizzes."""
import random, string
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user, require_teacher
from app.models.lms import (
    VirtualClassroom, VirtualClassEnrollment, ClassPost, PostComment,
    ClassAssignment, ClassAssignmentSubmission, AssignmentSubmissionStatus,
    Quiz, QuizQuestion, QuizAttempt,
)

router = APIRouter()


# ── Pydantic schemas (inline) ─────────────────────────────────────────────────

class ClassroomCreate(BaseModel):
    name: str
    description: Optional[str] = None
    course_id: int
    subject_id: int
    teacher_id: int
    academic_year_id: int
    academic_term_id: int

class ClassroomOut(BaseModel):
    id: int; name: str; description: Optional[str]
    course_id: int; subject_id: int; teacher_id: int
    join_code: Optional[str]; is_active: bool
    class Config: from_attributes = True

class EnrollRequest(BaseModel):
    student_ids: List[int]

class PostCreate(BaseModel):
    title: str
    body: Optional[str] = None
    resource_url: Optional[str] = None
    is_pinned: bool = False

class PostOut(BaseModel):
    id: int; classroom_id: int; title: str; body: Optional[str]
    resource_url: Optional[str]; is_pinned: bool
    class Config: from_attributes = True

class CommentCreate(BaseModel):
    body: str

class AssignmentCreate(BaseModel):
    title: str
    instructions: Optional[str] = None
    total_marks: float = 100
    due_date: datetime
    allow_late: bool = False
    is_published: bool = False

class AssignmentOut(BaseModel):
    id: int; classroom_id: int; title: str; instructions: Optional[str]
    total_marks: float; due_date: datetime; is_published: bool
    class Config: from_attributes = True

class SubmitAssignment(BaseModel):
    submission_text: Optional[str] = None
    file_url: Optional[str] = None

class GradeSubmission(BaseModel):
    marks_obtained: float
    feedback: Optional[str] = None

class QuizCreate(BaseModel):
    title: str
    instructions: Optional[str] = None
    total_marks: float = 0
    duration_minutes: int = 30
    is_published: bool = False
    shuffle_questions: bool = False

class QuizOut(BaseModel):
    id: int; classroom_id: int; title: str
    total_marks: float; duration_minutes: int; is_published: bool
    class Config: from_attributes = True

class QuestionCreate(BaseModel):
    question_text: str
    question_type: str = "mcq"
    marks: float = 1
    order: int = 1
    options: Optional[str] = None
    correct_answer: Optional[str] = None

class AttemptSubmit(BaseModel):
    answers: str  # JSON string {question_id: answer}


# ── Virtual Classrooms ────────────────────────────────────────────────────────

def _gen_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@router.get("/classrooms", response_model=List[ClassroomOut])
def list_classrooms(skip: int = 0, limit: int = 50, db: Session = Depends(get_db),
                    _=Depends(get_current_user)):
    return db.query(VirtualClassroom).offset(skip).limit(limit).all()

@router.post("/classrooms", response_model=ClassroomOut, status_code=201)
def create_classroom(data: ClassroomCreate, db: Session = Depends(get_db),
                     _=Depends(require_teacher)):
    code = _gen_code()
    while db.query(VirtualClassroom).filter_by(join_code=code).first():
        code = _gen_code()
    obj = VirtualClassroom(**data.model_dump(), join_code=code)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/classrooms/{id}", response_model=ClassroomOut)
def get_classroom(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(VirtualClassroom).get(id)
    if not obj: raise HTTPException(404, "Classroom not found")
    return obj

@router.post("/classrooms/{id}/enroll", status_code=201)
def enroll_students(id: int, data: EnrollRequest, db: Session = Depends(get_db),
                    _=Depends(require_teacher)):
    classroom = db.query(VirtualClassroom).get(id)
    if not classroom: raise HTTPException(404, "Classroom not found")
    enrolled = []
    for sid in data.student_ids:
        exists = db.query(VirtualClassEnrollment).filter_by(
            classroom_id=id, student_id=sid).first()
        if not exists:
            db.add(VirtualClassEnrollment(classroom_id=id, student_id=sid))
            enrolled.append(sid)
    db.commit()
    return {"enrolled": len(enrolled), "student_ids": enrolled}

@router.get("/classrooms/{id}/enrollments")
def list_enrollments(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.query(VirtualClassEnrollment).filter_by(classroom_id=id, is_active=True).all()
    return [{"id": r.id, "student_id": r.student_id, "enrolled_at": r.enrolled_at} for r in rows]


# ── Class Posts ───────────────────────────────────────────────────────────────

@router.get("/classrooms/{id}/posts", response_model=List[PostOut])
def list_posts(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(ClassPost).filter_by(classroom_id=id).order_by(
        ClassPost.is_pinned.desc(), ClassPost.created_at.desc()).all()

@router.post("/classrooms/{id}/posts", response_model=PostOut, status_code=201)
def create_post(id: int, data: PostCreate, db: Session = Depends(get_db),
                _=Depends(require_teacher)):
    if not db.query(VirtualClassroom).get(id):
        raise HTTPException(404, "Classroom not found")
    obj = ClassPost(classroom_id=id, **data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.post("/posts/{post_id}/comments", status_code=201)
def add_comment(post_id: int, data: CommentCreate, db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    if not db.query(ClassPost).get(post_id):
        raise HTTPException(404, "Post not found")
    obj = PostComment(post_id=post_id, user_id=current_user.id, body=data.body)
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "body": obj.body, "created_at": obj.created_at}


# ── Assignments ───────────────────────────────────────────────────────────────

@router.get("/classrooms/{id}/assignments", response_model=List[AssignmentOut])
def list_assignments(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(ClassAssignment).filter_by(classroom_id=id).all()

@router.post("/classrooms/{id}/assignments", response_model=AssignmentOut, status_code=201)
def create_assignment(id: int, data: AssignmentCreate, db: Session = Depends(get_db),
                      _=Depends(require_teacher)):
    if not db.query(VirtualClassroom).get(id):
        raise HTTPException(404, "Classroom not found")
    obj = ClassAssignment(classroom_id=id, **data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.post("/assignments/{id}/submit", status_code=201)
def submit_assignment(id: int, data: SubmitAssignment, db: Session = Depends(get_db),
                      current_user=Depends(get_current_user)):
    assignment = db.query(ClassAssignment).get(id)
    if not assignment: raise HTTPException(404, "Assignment not found")
    # find student record linked to this user
    from app.models.people import Student
    student = db.query(Student).filter_by(user_id=current_user.id).first()
    if not student: raise HTTPException(403, "Only students can submit")
    existing = db.query(ClassAssignmentSubmission).filter_by(
        assignment_id=id, student_id=student.id).first()
    if existing: raise HTTPException(409, "Already submitted")
    now = datetime.utcnow()
    status = AssignmentSubmissionStatus.LATE if (
        assignment.due_date and now > assignment.due_date.replace(tzinfo=None)
    ) else AssignmentSubmissionStatus.SUBMITTED
    obj = ClassAssignmentSubmission(
        assignment_id=id, student_id=student.id,
        submission_text=data.submission_text, file_url=data.file_url, status=status)
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "status": obj.status, "submitted_at": obj.submitted_at}

@router.get("/assignments/{id}/submissions")
def list_submissions(id: int, db: Session = Depends(get_db), _=Depends(require_teacher)):
    rows = db.query(ClassAssignmentSubmission).filter_by(assignment_id=id).all()
    return [{"id": r.id, "student_id": r.student_id, "status": r.status,
             "marks_obtained": r.marks_obtained, "submitted_at": r.submitted_at} for r in rows]

@router.put("/assignments/{id}/submissions/{sid}/grade")
def grade_submission(id: int, sid: int, data: GradeSubmission,
                     db: Session = Depends(get_db), _=Depends(require_teacher)):
    sub = db.query(ClassAssignmentSubmission).filter_by(
        assignment_id=id, student_id=sid).first()
    if not sub: raise HTTPException(404, "Submission not found")
    sub.marks_obtained = data.marks_obtained
    sub.feedback = data.feedback
    sub.status = AssignmentSubmissionStatus.GRADED
    sub.graded_at = datetime.utcnow()
    db.commit(); db.refresh(sub)
    return {"id": sub.id, "marks_obtained": sub.marks_obtained, "status": sub.status}


# ── Quizzes ───────────────────────────────────────────────────────────────────

@router.get("/classrooms/{id}/quizzes", response_model=List[QuizOut])
def list_quizzes(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Quiz).filter_by(classroom_id=id).all()

@router.post("/classrooms/{id}/quizzes", response_model=QuizOut, status_code=201)
def create_quiz(id: int, data: QuizCreate, db: Session = Depends(get_db),
                _=Depends(require_teacher)):
    if not db.query(VirtualClassroom).get(id):
        raise HTTPException(404, "Classroom not found")
    obj = Quiz(classroom_id=id, **data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.post("/quizzes/{id}/questions", status_code=201)
def add_question(id: int, data: QuestionCreate, db: Session = Depends(get_db),
                 _=Depends(require_teacher)):
    if not db.query(Quiz).get(id): raise HTTPException(404, "Quiz not found")
    obj = QuizQuestion(quiz_id=id, **data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "question_text": obj.question_text, "marks": obj.marks}

@router.post("/quizzes/{id}/attempt", status_code=201)
def start_attempt(id: int, db: Session = Depends(get_db),
                  current_user=Depends(get_current_user)):
    quiz = db.query(Quiz).get(id)
    if not quiz: raise HTTPException(404, "Quiz not found")
    from app.models.people import Student
    student = db.query(Student).filter_by(user_id=current_user.id).first()
    if not student: raise HTTPException(403, "Only students can attempt quizzes")
    existing = db.query(QuizAttempt).filter_by(
        quiz_id=id, student_id=student.id, is_submitted=False).first()
    if existing:
        return {"id": existing.id, "started_at": existing.started_at, "resumed": True}
    obj = QuizAttempt(quiz_id=id, student_id=student.id)
    db.add(obj); db.commit(); db.refresh(obj)
    questions = db.query(QuizQuestion).filter_by(quiz_id=id).order_by(QuizQuestion.order).all()
    return {"id": obj.id, "started_at": obj.started_at,
            "questions": [{"id": q.id, "text": q.question_text,
                           "type": q.question_type, "marks": q.marks,
                           "options": q.options} for q in questions]}

@router.put("/quizzes/{id}/submit")
def submit_quiz(id: int, data: AttemptSubmit, db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    from app.models.people import Student
    student = db.query(Student).filter_by(user_id=current_user.id).first()
    if not student: raise HTTPException(403, "Only students can submit quizzes")
    attempt = db.query(QuizAttempt).filter_by(
        quiz_id=id, student_id=student.id, is_submitted=False).first()
    if not attempt: raise HTTPException(404, "No active attempt found")
    attempt.answers = data.answers
    attempt.submitted_at = datetime.utcnow()
    attempt.is_submitted = True
    # Auto-grade MCQ/True-False
    import json
    try:
        answers = json.loads(data.answers)
        questions = db.query(QuizQuestion).filter_by(quiz_id=id).all()
        score = 0.0
        for q in questions:
            ans = answers.get(str(q.id))
            if ans and q.correct_answer and str(ans).lower() == str(q.correct_answer).lower():
                score += q.marks
        attempt.score = score
    except Exception:
        attempt.score = None
    db.commit(); db.refresh(attempt)
    return {"id": attempt.id, "score": attempt.score, "submitted_at": attempt.submitted_at}
