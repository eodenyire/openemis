from django.db import models
from accounts.models import User, StudentProfile, TeacherProfile

class AcademicYear(models.Model):
    name = models.CharField(max_length=20, unique=True)  # e.g., "2023-2024"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.is_current:
            # Ensure only one academic year is current
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

class Class(models.Model):
    name = models.CharField(max_length=50)  # e.g., "Grade 1", "Class X"
    numeric_name = models.IntegerField()  # 1, 2, 3, etc.
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Classes"
        ordering = ['numeric_name']
    
    def __str__(self):
        return self.name

class Section(models.Model):
    name = models.CharField(max_length=10)  # e.g., "A", "B", "C"
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='sections')
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True)
    capacity = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['name', 'class_name']
    
    def __str__(self):
        return f"{self.class_name.name} - {self.name}"
    
    @property
    def current_enrollment(self):
        return self.enrollments.filter(academic_year__is_current=True).count()

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    classes = models.ManyToManyField(Class, related_name='subjects')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class SubjectTeacher(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['subject', 'class_name', 'section', 'academic_year']
    
    def __str__(self):
        section_str = f" - {self.section.name}" if self.section else ""
        return f"{self.teacher.user.get_full_name()} - {self.subject.name} - {self.class_name.name}{section_str}"

class Enrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='enrollments')
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='enrollments')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['student', 'academic_year']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.class_name.name} {self.section.name} ({self.academic_year.name})"

class Grade(models.Model):
    name = models.CharField(max_length=5)  # A+, A, B+, etc.
    min_marks = models.DecimalField(max_digits=5, decimal_places=2)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2)
    description = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['-min_marks']
    
    def __str__(self):
        return f"{self.name} ({self.min_marks}-{self.max_marks})"