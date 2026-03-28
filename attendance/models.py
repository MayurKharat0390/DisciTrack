from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class AttendanceRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    lecture_name = models.CharField(max_length=200)
    # Field to mark if it's a specific lecture from a list maybe? No, let's keep it simple.
    timestamp = models.DateTimeField(default=timezone.now)
    date = models.DateField(default=timezone.now)
    proof_image = models.ImageField(upload_to='attendance_proofs/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    scheduled_time = models.TimeField(blank=True, null=True, help_text="What time was the lecture supposed to start?")
    is_late = models.BooleanField(default=False)
    credibility_score = models.FloatField(default=10.0) # Penalty for missing proof or being late

    class Meta:
        unique_together = ('user', 'lecture_name', 'date')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.lecture_name} ({self.date})"

    def calculate_credibility(self):
        # Implementation of credibility score logic
        score = 10.0
        if not self.proof_image:
            score -= 5.0
        if self.is_late:
            score -= 2.0
        self.credibility_score = max(0, score)
        self.save()
