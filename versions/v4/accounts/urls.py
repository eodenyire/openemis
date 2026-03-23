from django.urls import path
from . import views

urlpatterns = [
    # Web URLs
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin/dashboard/', views.dashboard_view, name='admin_dashboard'),
    path('teacher/dashboard/', views.dashboard_view, name='teacher_dashboard'),
    path('student/dashboard/', views.dashboard_view, name='student_dashboard'),
    path('parent/dashboard/', views.dashboard_view, name='parent_dashboard'),
    path('librarian/dashboard/', views.dashboard_view, name='librarian_dashboard'),
    path('accountant/dashboard/', views.dashboard_view, name='accountant_dashboard'),
    
    # API URLs
    path('api/login/', views.api_login, name='api_login'),
    path('api/register/', views.api_register, name='api_register'),
    path('api/profile/', views.UserProfileView.as_view(), name='user_profile'),
]