from django.db import models
from accounts.models import AccountantProfile, StudentProfile
from academic.models import AcademicYear

class PaymentCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Payment(models.Model):
    PAYMENT_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPES)
    category = models.ForeignKey(PaymentCategory, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, null=True, blank=True)
    payment_date = models.DateField()
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    recorded_by = models.ForeignKey(AccountantProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.amount} ({self.payment_type})"