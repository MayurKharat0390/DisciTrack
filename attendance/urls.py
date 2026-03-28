from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.AttendanceListView.as_view(), name='attendance_list'),
    path('mark/', views.AttendanceMarkView.as_view(), name='attendance_mark'),
]
