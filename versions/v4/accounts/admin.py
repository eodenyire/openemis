from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, AdminProfile, TeacherProfile, StudentProfile, 
    ParentProfile, LibrarianProfile, AccountantProfile
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_active')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone', 'address', 'profile_image', 'date_of_birth')
        }),
    )

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'department')
    search_fields = ('user__username', 'employee_id')

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'qualification', 'experience_years')
    search_fields = ('user__username', 'employee_id')

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'admission_date', 'guardian_name')
    search_fields = ('user__username', 'student_id', 'guardian_name')

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'occupation')
    search_fields = ('user__username',)

@admin.register(LibrarianProfile)
class LibrarianProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id')
    search_fields = ('user__username', 'employee_id')

@admin.register(AccountantProfile)
class AccountantProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id')
    search_fields = ('user__username', 'employee_id')