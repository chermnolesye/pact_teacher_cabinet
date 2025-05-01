from django.urls import path
from . import views


urlpatterns = [
    path('', views.statistics_view, name='statistics'), 
    path('error_stats', views.error_stats, name='error_stats'), 
    path('dashboard_error_types', views.chart_types_errors, name='dashboard_error_types'),
    path("export_group_error_stats/", views.export_group_error_stats, name="export_group_error_stats"),
]