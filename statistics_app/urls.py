from django.urls import path
from . import views


urlpatterns = [
    path('', views.statistics_view, name='statistics'), 
    path('/error_stats', views.error_stats, name='error_stats'), 
    path('dashboard_error_types/', views.chart_types_errors, name='dashboard_error_types'),
    path('by_severity_levels/', views.by_severity_levels, name='by_severity_levels'),
    path('by_error_types_and_severity/', views.by_error_types_and_severity, name='by_error_types_and_severity'),
    path('student_progress_by_error_type/', views.student_progress_by_error_type, name='student_progress_by_error_type'),
    path('error_count_by_type_and_groups/', views.error_count_by_type_and_groups, name='error_count_by_type_and_groups'),
    path('error_types_by_emotional_state/', views.error_types_by_emotional_state, name='error_types_by_emotional_state'),
    path('error_types_by_self_assessment/', views.error_types_by_self_assessment, name='error_types_by_self_assessment'),
    path('evaluation_vs_self_assessment/', views.evaluation_vs_self_assessment, name='evaluation_vs_self_assessment'),
    path('emotional_state_vs_self_assessment/', views.emotional_state_vs_self_assessment, name='emotional_state_vs_self_assessment'),
    path('emotional_state_vs_evaluation/', views.emotional_state_vs_evaluation, name='emotional_state_vs_evaluation'),
    path('self_assessment_vs_evaluation/', views.self_assessment_vs_evaluation, name='self_assessment_vs_evaluation'),
    path('year_of_study_vs_error_count/', views.year_of_study_vs_error_count, name='year_of_study_vs_error_count'),
]