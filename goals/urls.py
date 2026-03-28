from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.GoalCreateView.as_view(), name='goal_create'),
    path('toggle/<int:goal_id>/', views.ToggleGoalLogView.as_view(), name='goal_toggle'),
]
