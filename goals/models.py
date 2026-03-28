from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Goal(models.Model):
    CATEGORY_CHOICES = (
        ('gym', 'Gym'),
        ('lecture', 'Lecture'),
        ('coding', 'Coding'),
        ('other', 'Custom'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"

class GoalLog(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField(default=timezone.now)
    is_completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('goal', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.goal.title} - {self.date} - {'Done' if self.is_completed else 'Pending'}"
