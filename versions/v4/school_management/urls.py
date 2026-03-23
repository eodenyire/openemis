from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/academic/', include('academic.urls')),
    path('api/attendance/', include('attendance.urls')),
    path('api/exams/', include('exams.urls')),
    path('api/messaging/', include('messaging.urls')),
    path('api/library/', include('library.urls')),
    path('api/finance/', include('finance.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('', include('accounts.urls')),  # For web views
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)