from django.urls import path
from . import views

urlpatterns = [
    path('show_text_markup/', views.show_text_markup, name='show_text_markup')
]