from django.urls import path
from . import views

urlpatterns = [
    path('add_group', views.add_group, name='add_group'),
    path('show_groups/', views.show_groups, name='show_groups'),
    path('edit_group/<int:group_id>/', views.edit_group, name='edit_group'),
]