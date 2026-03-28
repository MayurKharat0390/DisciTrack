from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class DailyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_logs')
    date = models.DateField(default=timezone.now)
    total_score = models.FloatField(default=0.0)
    is_locked = models.BooleanField(default=False)
    
    # Track completion for statistics
    goals_completed = models.IntegerField(default=0)
    total_goals = models.IntegerField(default=0)
    attendance_marked = models.IntegerField(default=0)
    total_lectures = models.IntegerField(default=0)
    
    streak_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date} - Score: {self.total_score}"

    def update_score(self):
        # Implementation of scoring logic
        if self.is_locked:
            return

        # Example calculation
        goal_score = (self.goals_completed / self.total_goals * 50) if self.total_goals > 0 else 50
        attendance_score = (self.attendance_marked / self.total_lectures * 50) if self.total_lectures > 0 else 50
        
        self.total_score = goal_score + attendance_score
        # More complex logic with penalties will be added in views/signals
        self.save()
