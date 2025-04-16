from django.urls import path
from . import views


urlpatterns = [
    path('show_students/', views.show_students, name='show_students'),
]