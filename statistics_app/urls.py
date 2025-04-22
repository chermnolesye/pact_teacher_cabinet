from django.urls import path
from . import views


urlpatterns = [
    path('', views.statistics_view, name='statistics'), 
    path('/error_stats', views.error_stats, name='error_stats'), 
]