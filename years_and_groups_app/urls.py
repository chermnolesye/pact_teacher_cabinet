from django.urls import path
from . import views

urlpatterns = [
    path('add_academic_year', views.add_academic_year, name='add_academic_year'),
    path('add_group', views.add_group, name='add_group'),
    path('edit_group', views.show_groups, name=' edit_group'), #страница просмотра и управления????
    path('edit_academic_year', views.show_academic_years, name='edit_academic_year'),
    path('edit_group/<int:group_id>/', views.edit_group, name=' edit_group'), # редактирование конкретной
    path('edit_academic_year/<int:academic_year_id>/', views.edit_academic_year, name='edit_academic_year'),
    path('edit_academic_year/delete_academic_year/<int:academic_year_id>/', views.delete_academic_year, name='delete_academic_year'), #удаление
    path('edit_group/delete_group/<int:group_id>/', views.delete_group, name=' delete_group'), 
    path('show_groups/', views.show_groups, name='show_groups'),
]