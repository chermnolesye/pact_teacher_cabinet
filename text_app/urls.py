from django.urls import path
from . import views

urlpatterns = [
    # Добавляем маршрут для отображения текста
    path('show_text/', views.show_text, name='show_text'),
    path('show_error_markup/', views.show_error_markup, name='show_error_markup'),
    path('show_text_markup/', views.show_text_markup, name='show_text_markup')
]