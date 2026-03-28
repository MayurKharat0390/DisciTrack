from django.views.generic import TemplateView, ListView
from django.utils import timezone
from .models import Goal, GoalLog

class GoalListView(LoginRequiredMixin, ListView):
    model = Goal
    template_name = 'goals/list.html'
    context_object_name = 'goals'

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

class GoalCreateView(LoginRequiredMixin, CreateView):
    class Meta:
        model = Goal
        fields = ['title', 'description', 'category']

class GoalCreateView(LoginRequiredMixin, CreateView):
    model = Goal
    form_class = GoalForm
    template_name = 'goals/create.html'
    success_url = '/' # Dashboard

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class ToggleGoalLogView(LoginRequiredMixin, View):
    def post(self, request, goal_id):
        goal = get_object_or_404(Goal, id=goal_id, user=request.user)
        today = timezone.localtime(timezone.now()).date()
        
        # Check if the goal log exists for today
        log, created = GoalLog.objects.get_or_create(goal=goal, date=today)
        
        # Simple toggle
        log.is_completed = not log.is_completed
        log.save()
        
        # Update daily score
        from analytics.models import DailyLog
        daily, _ = DailyLog.objects.get_or_create(user=request.user, date=today)
        daily.update_score()
        
        return redirect('dashboard')
