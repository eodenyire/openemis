from django.contrib import admin
from .models import StudentAttendance, TeacherAttendance

@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'class_name', 'section')
    list_filter = ('status', 'date', 'class_name')
    search_fields = ('student__user__first_name', 'student__user__last_name')

@admin.register(TeacherAttendance)
class TeacherAttendanceAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'date', 'status', 'check_in_time', 'check_out_time')
    list_filter = ('status', 'date')
    search_fields = ('teacher__user__first_name', 'teacher__user__last_name')