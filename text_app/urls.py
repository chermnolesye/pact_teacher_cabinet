from django.urls import path
from . import views


urlpatterns = [
    path('show_text_markup/', views.show_text_markup, name='show_text_markup'),
    path('annotate_text/', views.annotate_text, name='annotate_text'),
    path('show_texts/', views.show_texts, name='show_texts')
]