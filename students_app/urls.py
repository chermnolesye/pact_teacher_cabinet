from django.urls import path
from . import views


urlpatterns = [
    path('show_students/', views.show_students, name='show_students'),
    path('student/<int:student_id>/', views.student_info, name='student_info'),
    path('add_student/', views.add_student, name='add_student'),
]