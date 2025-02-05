from django.urls import path
from .views import academic_years

urlpatterns = [
    path('academic_years/', academic_years, name='academic_years'),
]
