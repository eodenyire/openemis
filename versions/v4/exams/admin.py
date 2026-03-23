from django.contrib import admin
from .models import (
    Exam, ExamSubject, StudentMark, OnlineExam, 
    Question, QuestionOption, OnlineExamResult, StudentAnswer
)

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'academic_year')
    list_filter = ('academic_year', 'start_date')
    filter_horizontal = ('classes',)

@admin.register(OnlineExam)
class OnlineExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'class_name', 'duration_minutes', 'is_published')
    list_filter = ('is_published', 'subject', 'class_name')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'question_type', 'marks', 'order')
    list_filter = ('question_type', 'exam')

@admin.register(OnlineExamResult)
class OnlineExamResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'percentage', 'is_passed', 'is_completed')
    list_filter = ('is_passed', 'is_completed', 'exam')