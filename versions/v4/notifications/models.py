from django.db import models
from accounts.models import User

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('news', 'News'),
        ('exam', 'Exam'),
        ('message', 'Message'),
        ('attendance', 'Attendance'),
        ('payment', 'Payment'),
        ('general', 'General'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    url = models.URLField(blank=True)  # Link to relevant page
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient.get_full_name()} - {self.title}"