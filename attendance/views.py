from django.shortcuts import redirect, render
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import AttendanceRecord
from django import forms

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
