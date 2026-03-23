from django.db import models
from accounts.models import StudentProfile, TeacherProfile
from academic.models import Class, Section, AcademicYear

class StudentAttendance(models.Model):
    ATTENDANCE_STATUS = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    )
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS)
    marked_by = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    remarks = models.TextField(blank=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'date', 'academic_year']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.date} - {self.status}"

class TeacherAttendance(models.Model):
    ATTENDANCE_STATUS = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
        ('leave', 'On Leave'),
    )
    
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    marked_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['teacher', 'date']
    
    def __str__(self):
        return f"{self.teacher.user.get_full_name()} - {self.date} - {self.status}"