from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import AttendanceRecord
from django import forms

class AttendanceListView(LoginRequiredMixin, ListView):
    model = AttendanceRecord
    template_name = 'attendance/list.html'
    context_object_name = 'attendance_list'

    def get_queryset(self):
        return AttendanceRecord.objects.filter(user=self.request.user).order_by('-timestamp')

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['lecture_name', 'scheduled_time', 'proof_image', 'notes']
        widgets = {
            'scheduled_time': forms.TimeInput(attrs={'type': 'time', 'class': 'input-premium'}),
        }

class AttendanceMarkView(LoginRequiredMixin, CreateView):
    model = AttendanceRecord
    form_class = AttendanceForm
    template_name = 'attendance/mark.html'
    success_url = '/' # Dashboard

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.date = timezone.localtime(timezone.now()).date()
        
        # Lateness logic based on scheduled_time
        now = timezone.localtime(timezone.now())
        if form.instance.scheduled_time:
            # Create a full datetime for today at the scheduled time
            scheduled_dt = timezone.make_aware(timezone.datetime.combine(form.instance.date, form.instance.scheduled_time))
            # Grace period of 15 minutes
            if now > (scheduled_dt + timezone.timedelta(minutes=15)):
                form.instance.is_late = True
        
        response = super().form_valid(form)
        form.instance.calculate_credibility()
        
        # Update DailyLog score
        from analytics.models import DailyLog
        daily, _ = DailyLog.objects.get_or_create(user=self.request.user, date=form.instance.date)
        daily.update_score()
        
        return response
