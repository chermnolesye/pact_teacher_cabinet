from django.urls import path
from . import views

urlpatterns = [
    path('add_group', views.add_group, name='add_group'),
    path('show_groups/', views.show_groups, name='show_groups'),
    path('edit_group/<int:group_id>/', views.edit_group, name='edit_group'),
    # path('add_academic_year', views.add_academic_year, name='add_academic_year'),
    # path('edit_academic_year', views.show_academic_years, name='edit_academic_year'),
    # path('edit_academic_year/<int:academic_year_id>/', views.edit_academic_year, name='edit_academic_year'),
]