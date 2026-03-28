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
        fields = ['lecture_name', 'proof_image', 'notes']

class AttendanceMarkView(LoginRequiredMixin, CreateView):
    model = AttendanceRecord
    form_class = AttendanceForm
    template_name = 'attendance/mark.html'
    success_url = '/' # Dashboard

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.date = timezone.localtime(timezone.now()).date()
        
        # Determine if it's late (Mock logic: if mark > 16:00 (4pm) after default)
        # In real case, user would set their lecture time
        now = timezone.localtime(timezone.now())
        if now.hour > 16:
            form.instance.is_late = True
        
        response = super().form_valid(form)
        form.instance.calculate_credibility()
        
        # Update DailyLog score
        from analytics.models import DailyLog
        daily, _ = DailyLog.objects.get_or_create(user=self.request.user, date=form.instance.date)
        daily.update_score()
        
        return response
