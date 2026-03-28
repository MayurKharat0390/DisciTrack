from django.shortcuts import get_object_or_404, redirect
from django.views import View
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
    # This view handles both Creating a new record or UPDATING an existing one for the same day
    model = AttendanceRecord
    form_class = AttendanceForm
    template_name = 'attendance/mark.html'
    success_url = '/' # Dashboard

    def form_valid(self, form):
        user = self.request.user
        date = timezone.localtime(timezone.now()).date()
        lecture_name = form.cleaned_data['lecture_name']
        
        # Check if record already exists for this user/lecture/date
        existing_record = AttendanceRecord.objects.filter(user=user, lecture_name=lecture_name, date=date).first()
        
        if existing_record:
            # Update the existing record instead of creating a new one
            existing_record.is_attended = form.cleaned_data['is_attended']
            existing_record.reason_for_absence = form.cleaned_data['reason_for_absence']
            existing_record.notes = form.cleaned_data['notes']
            if form.cleaned_data['proof_image']:
                existing_record.proof_image = form.cleaned_data['proof_image']
            existing_record.timestamp = timezone.now() # Update marking time
            existing_record.save()
            existing_record.calculate_credibility()
            
            # Update DailyLog score
            from analytics.models import DailyLog
            daily, _ = DailyLog.objects.get_or_create(user=user, date=date)
            daily.update_score()
            
            return redirect(self.success_url)
        else:
            # Create new record
            form.instance.user = user
            form.instance.date = date
            response = super().form_valid(form)
            form.instance.calculate_credibility()
            
            # Update DailyLog score
            from analytics.models import DailyLog
            daily, _ = DailyLog.objects.get_or_create(user=user, date=date)
            daily.update_score()
            
            return response

class AttendanceDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        record = get_object_or_404(AttendanceRecord, pk=pk, user=request.user)
        date = record.date
        record.delete()
        
        # Recalculate Score
        from analytics.models import DailyLog
        daily, _ = DailyLog.objects.get_or_create(user=request.user, date=date)
        daily.update_score()
        
        return redirect('attendance_list')
