from django.utils import timezone
from datetime import timedelta
from analytics.models import DailyLog

def sync_daily_logs(user):
    profile = user.profile
    today = timezone.localtime(timezone.now()).date()
    
    if not profile.last_active_date:
        profile.last_active_date = today
        profile.save()
        return

    # Check for missed days
    last_date = profile.last_active_date
    if last_date < today:
        delta = (today - last_date).days
        
        # Lock past days and fill gaps
        for i in range(1, delta):
            missed_date = last_date + timedelta(days=i)
            DailyLog.objects.get_or_create(
                user=user, 
                date=missed_date,
                defaults={'total_score': 0.0, 'is_locked': True}
            )
        
        # If gap > 1 day, streak is broken
        if delta > 1:
            profile.current_streak = 0
            profile.save()
            
        # The today log will be created by the Dashboard view or automatically here
        DailyLog.objects.get_or_create(user=user, date=today)
        profile.last_active_date = today
        profile.save()
