from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import DailyLog
from goals.models import Goal, GoalLog
from attendance.models import AttendanceRecord
from accounts.models import UserProfile
from datetime import datetime, timedelta
from core.utils import sync_daily_logs

class DailyDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/day_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        date_str = self.kwargs.get('date')
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            # Fallback to today if date is invalid
            target_date = timezone.localtime(timezone.now()).date()
            
        daily_log = DailyLog.objects.filter(user=user, date=target_date).first()
        goal_logs = GoalLog.objects.filter(goal__user=user, date=target_date)
        attendance = AttendanceRecord.objects.filter(user=user, date=target_date)
        
        context.update({
            'daily_log': daily_log,
            'goal_logs': goal_logs,
            'attendance': attendance,
            'target_date': target_date,
        })
        return context

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
        # Calculate Scored Penalties (REMOVED based on user request)
        # We no longer subtract proof or skip penalties from total_score
        
        # 1. Goal Score (Max 50)
        goal_score = (daily_log.goals_completed / daily_log.total_goals * 50) if daily_log.total_goals > 0 else 0
        
        # 2. Attendance Contribution (Max 50)
        actual_attendance_count = sum(1 for att in attendance if att.is_attended)
        attendance_contribution = (actual_attendance_count / daily_log.total_lectures * 50) if daily_log.total_lectures > 0 else 0

        # Total is now a pure sum of achievement
        daily_log.total_score = max(0, min(100, goal_score + attendance_contribution))
        
        # 4. Profile and Streak
        profile = user.profile
        daily_log.streak_count = profile.current_streak
        daily_log.save()
        
        # 5. Weekly stats for chart
        seven_days_ago = today - timedelta(days=7)
        weekly_logs = DailyLog.objects.filter(user=user, date__gte=seven_days_ago).order_by('date')
        
        # 5. Profile data
        # 6. Generate Heatmap Data (Last 182 days - 26 weeks)
        heatmap_data = []
        end_date = today
        start_date = end_date - timedelta(days=181) # 26 weeks approx
        
        # Get all logs for this range
        existing_logs = {log.date: log for log in DailyLog.objects.filter(user=user, date__range=[start_date, end_date])}
        
        current_date = start_date
        while current_date <= end_date:
            log = existing_logs.get(current_date)
            score = log.total_score if log else 0
            
            # Map score to level
            level = 0
            if score > 80: level = 4
            elif score > 60: level = 3
            elif score > 40: level = 2
            elif score > 0: level = 1
            
            heatmap_data.append({
                'date': current_date,
                'level': level,
                'score': score
            })
            current_date += timedelta(days=1)

        # 7. Weekly stats for chart (lists for JSON)
        weekly_labels = [log.date.strftime('%a') for log in weekly_logs]
        weekly_scores = [float(log.total_score) for log in weekly_logs]

        context.update({
            'daily_log': daily_log,
            'goal_logs': goal_logs,
            'attendance': attendance,
            'weekly_logs': weekly_logs,
            'weekly_labels': weekly_labels,
            'weekly_scores': weekly_scores,
            'heatmap_data': heatmap_data,
            'profile': profile,
            'today': today
        })

        # Calculate goal completion percentage for the progress bar
        if daily_log.total_goals > 0:
            context['goal_percentage'] = (daily_log.goals_completed / daily_log.total_goals) * 100
        else:
            context['goal_percentage'] = 0
            
        return context
