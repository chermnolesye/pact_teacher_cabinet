from django.urls import path
from .views import register_student, register_teacher, login_student, login_teacher

urlpatterns = [
    path('register_student/', register_student, name='register_student'),
    path('register_teacher/', register_teacher, name='register_teacher'),
    path('login_student/', login_student, name='login_student'),
    path('login_teacher/', login_teacher, name='login_teacher'),
]
