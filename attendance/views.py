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
        fields = ['lecture_name', 'is_attended', 'reason_for_absence', 'proof_image', 'notes']
        widgets = {
            'is_attended': forms.CheckboxInput(attrs={'class': 'w-6 h-6 rounded bg-slate-800 border-slate-700 text-indigo-500 focus:ring-indigo-500'}),
            'reason_for_absence': forms.Textarea(attrs={'rows': 2, 'class': 'input-premium', 'placeholder': 'Optional if skipped...'}),
        }

class AttendanceMarkView(LoginRequiredMixin, CreateView):
    model = AttendanceRecord
    form_class = AttendanceForm
    template_name = 'attendance/mark.html'
    success_url = '/' # Dashboard

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.date = timezone.localtime(timezone.now()).date()
        
        response = super().form_valid(form)
        form.instance.calculate_credibility()
        
        # Update DailyLog score
        from analytics.models import DailyLog
        daily, _ = DailyLog.objects.get_or_create(user=self.request.user, date=form.instance.date)
        daily.update_score()
        
        return response
