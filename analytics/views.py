from django.views.generic import TemplateView, ListView
from django.utils import timezone
from .models import DailyLog
from goals.models import Goal, GoalLog
from attendance.models import AttendanceRecord
from accounts.models import UserProfile
from datetime import timedelta
from core.utils import sync_daily_logs

class AnalyticsReportView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        logs = DailyLog.objects.filter(user=user).order_by('-date')
        
        context['all_logs'] = logs
        context['avg_score'] = sum(l.total_score for l in logs) / logs.count() if logs.exists() else 0
        return context

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.localtime(timezone.now()).date()
        
        # 0. Sync logs for possible misses
        sync_daily_logs(user)
        
        # 1. Get or create today's daily log
        daily_log, created = DailyLog.objects.get_or_create(user=user, date=today)
        
        # 2. Get active goals and ensure GoalLog exists for today
        active_goals = Goal.objects.filter(user=user, is_active=True)
        goal_logs = []
        for goal in active_goals:
            glog, _ = GoalLog.objects.get_or_create(goal=goal, date=today)
            goal_logs.append(glog)
            
        # Update daily log stats
        daily_log.total_goals = len(goal_logs)
        daily_log.goals_completed = sum(1 for gl in goal_logs if gl.is_completed)
        
        # 3. Attendance records
        attendance = AttendanceRecord.objects.filter(user=user, date=today)
        daily_log.attendance_marked = attendance.count()
        daily_log.total_lectures = 4  # Should be configurable
        
        # Calculate Scored Penalties
        late_penalty = sum(2 for att in attendance if att.is_late)
        proof_penalty = sum(5 for att in attendance if not att.proof_image)
        
        # Scoring calculation (0-100)
        goal_score = (daily_log.goals_completed / daily_log.total_goals * 50) if daily_log.total_goals > 0 else 50
        attendance_score = (daily_log.attendance_marked / daily_log.total_lectures * 50) if daily_log.total_lectures > 0 else 50
        
        daily_log.total_score = max(0, min(100, goal_score + attendance_score - late_penalty - proof_penalty))
        
        # 4. Profile and Streak
        profile = user.profile
        daily_log.streak_count = profile.current_streak
        daily_log.save()
        
        # 5. Weekly stats for chart
        seven_days_ago = today - timedelta(days=7)
        weekly_logs = DailyLog.objects.filter(user=user, date__gte=seven_days_ago).order_by('date')
        
        # 5. Profile data
        profile = user.profile
        
        context.update({
            'daily_log': daily_log,
            'goal_logs': goal_logs,
            'attendance': attendance,
            'weekly_logs': weekly_logs,
            'profile': profile,
            'today': today
        })
        return context
