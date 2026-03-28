from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('report/', views.AnalyticsReportView.as_view(), name='report'),
    path('', views.DashboardView.as_view()), # Root to dashboard
]
