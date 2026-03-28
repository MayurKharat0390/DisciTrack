from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import UserProfile
from django import forms

class SignupView(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'registration/signup.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
        return render(request, 'registration/signup.html', {'form': form})

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['notifications_enabled', 'reminder_time']
        widgets = {
            'reminder_time': forms.TimeInput(attrs={'type': 'time', 'class': 'input-premium'}),
        }

class ProfileUpdateView(LoginRequiredMixin, View):
    def get(self, request):
        profile = request.user.profile
        form = UserProfileForm(instance=profile)
        return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})

    def post(self, request):
        profile = request.user.profile
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})
