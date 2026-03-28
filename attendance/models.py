from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class AttendanceRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    lecture_name = models.CharField(max_length=200)
    
    timestamp = models.DateTimeField(default=timezone.now)
    date = models.DateField(default=timezone.now)
    
    # Binary State: Attended vs Skipped
    is_attended = models.BooleanField(default=True, help_text="Did you actually attend this session?")
    reason_for_absence = models.TextField(blank=True, null=True, help_text="If No, explain why.")
    
    # Evidence & Outcome
    proof_image = models.ImageField(upload_to='attendance_proofs/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    credibility_score = models.FloatField(default=10.0) 

    class Meta:
        unique_together = ('user', 'lecture_name', 'date')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.lecture_name} ({self.date})"

    def calculate_credibility(self):
        # NEW SIMPLIFIED LOGIC: 10 if attended, 0 if skipped
        self.credibility_score = 10.0 if self.is_attended else 0.0
        self.save()
