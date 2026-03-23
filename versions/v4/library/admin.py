from django.contrib import admin
from .models import Book, BookRequest

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'category', 'total_copies', 'available_copies')
    list_filter = ('category', 'publication_year')
    search_fields = ('title', 'author', 'isbn')

@admin.register(BookRequest)
class BookRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'book', 'status', 'request_date', 'issue_date', 'return_date')
    list_filter = ('status', 'request_date')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'book__title')