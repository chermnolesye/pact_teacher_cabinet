from django.urls import path
from .views import register_student, register_teacher, user_login, logout_teacher

urlpatterns = [
    path('register_student/', register_student, name='register_student'),
    path('register_teacher/', register_teacher, name='register_teacher'),
    path('login/', user_login, name = 'login'),
    path('logout/', logout_teacher, name = 'logout'),
]
