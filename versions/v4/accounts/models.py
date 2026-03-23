from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator

class User(AbstractUser):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('librarian', 'Librarian'),
        ('accountant', 'Accountant'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_image = models.ImageField(
        upload_to='profiles/', 
        blank=True, 
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.user_type})"

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Admin: {self.user.get_full_name()}"

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    qualification = models.CharField(max_length=200, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    specialization = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Teacher: {self.user.get_full_name()}"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=50, unique=True)
    admission_date = models.DateField()
    guardian_name = models.CharField(max_length=100)
    guardian_phone = models.CharField(max_length=20)
    guardian_email = models.EmailField(blank=True)
    
    def __str__(self):
        return f"Student: {self.user.get_full_name()}"

class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    occupation = models.CharField(max_length=100, blank=True)
    children = models.ManyToManyField(StudentProfile, related_name='parents')
    
    def __str__(self):
        return f"Parent: {self.user.get_full_name()}"

class LibrarianProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='librarian_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return f"Librarian: {self.user.get_full_name()}"

class AccountantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='accountant_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return f"Accountant: {self.user.get_full_name()}"