from django.db import models
from accounts.models import StudentProfile, LibrarianProfile

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=50)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    publication_year = models.PositiveIntegerField()
    added_by = models.ForeignKey(LibrarianProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} by {self.author}"

class BookRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('returned', 'Returned'),
    )
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    issue_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    actual_return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_by = models.ForeignKey(LibrarianProfile, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.book.title} - {self.status}"