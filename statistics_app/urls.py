from django.urls import path
from . import views


urlpatterns = [
    # Главная страница статистики
    path('', views.statistics_view, name='statistics'),
    # Суммарная статитсика по ошибкам
    path('error_stats', views.error_stats, name='error_stats'),
    # Экспорт статистики по группам
    path("export_group_error_stats/", views.export_group_error_stats, name="export_group_error_stats"),
    # То, что пытались сделать Юля и Алена
    path('dashboard_error_types', views.chart_types_errors2, name='dashboard_error_types'),
    # URLS старого пакта:
    # Визуализация статистик
    path('types_errors/', views.chart_types_errors, name='types_errors'),
    path('grade_errors/', views.chart_grade_errors, name='grade_errors'),
    path('types_grade_errors/', views.chart_types_grade_errors, name='types_grade_errors'),
    path('student_dynamics/', views.chart_student_dynamics, name='student_dynamics'),
    path('groups_errors/', views.chart_groups_errors, name='groups_errors'),
    path('emotions_errors/', views.chart_emotions_errors, name='emotions_errors'),
    path('self_rating_errors/', views.chart_self_rating_errors, name='self_rating_errors'), 
    path('relation_assessment_self_rating/', views.chart_relation_assessment_self_rating,
         name='relation_assessment_self_rating'),
    # Поиск зависимостей
    path('relation_emotions_self_rating/', views.relation_emotions_self_rating,
         name='relation_emotions_self_rating'),
    path('relation_emotions_assessment/', views.relation_emotions_assessment,
         name='relation_emotions_assessment'),
    path('relation_self_rating_assessment/', views.relation_self_rating_assessment,
         name='relation_self_rating_assessment'),
    path('relation_course_errors/', views.relation_course_errors, name='relation_course_errors')
]