from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    current_streak = models.IntegerField(default=0)
    max_streak = models.IntegerField(default=0)
    performance_score = models.FloatField(default=0.0) # Average or cumulative
    
    last_active_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"

    def update_streak(self, date):
        # Implementation of streak logic
        if self.last_active_date:
            delta = (date - self.last_active_date).days
            if delta == 1:
                self.current_streak += 1
            elif delta > 1:
                self.current_streak = 1
        else:
            self.current_streak = 1
        
        self.last_active_date = date
        if self.current_streak > self.max_streak:
            self.max_streak = self.current_streak
        self.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
