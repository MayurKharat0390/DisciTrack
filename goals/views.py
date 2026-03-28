from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import Goal, GoalLog

class GoalListView(LoginRequiredMixin, ListView):
    model = Goal
    template_name = 'goals/list.html'
    context_object_name = 'goals'

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

class GoalCreateView(LoginRequiredMixin, CreateView):
    model = Goal
    fields = ['title', 'description', 'category']
    template_name = 'goals/create.html'
    success_url = '/analytics/dashboard/' # Explicit target

    def form_valid(self, form):
        form.status = 'active'
        form.instance.user = self.request.user
        return super().form_valid(form)

class ToggleGoalLogView(LoginRequiredMixin, View):
    def post(self, request, goal_id):
        goal = get_object_or_404(Goal, id=goal_id, user=request.user)
        today = timezone.localtime(timezone.now()).date()
        
        # Check if the goal log exists for today
        log, _ = GoalLog.objects.get_or_create(goal=goal, date=today)
        
        # Simple toggle
        log.is_completed = not log.is_completed
        log.save()
        
        # Update daily score
        from analytics.models import DailyLog
        daily, _ = DailyLog.objects.get_or_create(user=request.user, date=today)
        daily.update_score()
        
        return redirect('dashboard')
