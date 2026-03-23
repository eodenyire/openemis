from django.contrib import admin
from .models import AcademicYear, Class, Section, Subject, SubjectTeacher, Enrollment, Grade

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'numeric_name')
    ordering = ('numeric_name',)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'class_name', 'teacher', 'capacity', 'current_enrollment')
    list_filter = ('class_name',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    filter_horizontal = ('classes',)

@admin.register(SubjectTeacher)
class SubjectTeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'class_name', 'section', 'academic_year')
    list_filter = ('academic_year', 'class_name', 'subject')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_name', 'section', 'academic_year', 'is_active')
    list_filter = ('academic_year', 'class_name', 'is_active')
    search_fields = ('student__user__first_name', 'student__user__last_name')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_marks', 'max_marks', 'grade_point')
    ordering = ('-min_marks',)