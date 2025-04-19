from django.urls import path
from . import views

urlpatterns = [
    path('add_academic_year', views.add_academic_year, name='add_academic_year'),
    path('add_group', views.add_group, name='add_group'),
]