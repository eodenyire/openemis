from django.db import models
from accounts.models import StudentProfile, TeacherProfile
from academic.models import Class, Section, Subject, AcademicYear

class Exam(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    classes = models.ManyToManyField(Class, related_name='exams')
    created_by = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.academic_year.name})"

class ExamSubject(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    exam_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    total_marks = models.PositiveIntegerField(default=100)
    pass_marks = models.PositiveIntegerField(default=40)
    
    class Meta:
        unique_together = ['exam', 'subject', 'class_name']
    
    def __str__(self):
        return f"{self.exam.name} - {self.subject.name} - {self.class_name.name}"

class StudentMark(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    exam_subject = models.ForeignKey(ExamSubject, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5, blank=True)
    remarks = models.TextField(blank=True)
    entered_by = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'exam_subject']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.exam_subject} - {self.marks_obtained}"
    
    @property
    def percentage(self):
        return (self.marks_obtained / self.exam_subject.total_marks) * 100
    
    @property
    def is_pass(self):
        return self.marks_obtained >= self.exam_subject.pass_marks

class OnlineExam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True)
    duration_minutes = models.PositiveIntegerField()
    total_marks = models.PositiveIntegerField()
    pass_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=40.00)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.class_name.name}"

class Question(models.Model):
    QUESTION_TYPES = (
        ('mcq', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('fill_blank', 'Fill in the Blank'),
        ('short_answer', 'Short Answer'),
    )
    
    exam = models.ForeignKey(OnlineExam, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    marks = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."

class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.option_text} ({'Correct' if self.is_correct else 'Incorrect'})"

class OnlineExamResult(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    exam = models.ForeignKey(OnlineExam, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    total_marks = models.PositiveIntegerField()
    obtained_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_passed = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['student', 'exam']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.exam.title} - {self.percentage}%"

class StudentAnswer(models.Model):
    result = models.ForeignKey(OnlineExamResult, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(QuestionOption, on_delete=models.CASCADE, null=True, blank=True)
    text_answer = models.TextField(blank=True)  # For fill-in-the-blank or short answer
    is_correct = models.BooleanField(default=False)
    marks_awarded = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.result.student.user.get_full_name()} - Q{self.question.order}"