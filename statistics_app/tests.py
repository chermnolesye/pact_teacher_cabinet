from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.test import RequestFactory
from core_app.models import Rights, User , AcademicYear, Group, Student
from unittest.mock import patch, Mock

class GroupsTest(TestCase):
    def setUp(self):
        self.client = Client() 
        self.factory = RequestFactory()
        #self.User = get_user_model()
        
        self.password = 'user1'

        Rights.objects.create(pk=1, rightsname="Студент")
        self.rights = get_object_or_404(Rights, pk=1) 

        User.objects.create_user(
            iduser = 1,
            login='user2',
            password=self.password,
            lastname='TeacherLastname',
            firstname='TeacherFirstname',
            middlename='TeacherMidName',
            idrights=self.rights 
        )
        AcademicYear.objects.create(pk=1, title='TestYear')
        self.group = Group.objects.create(pk=1, groupname='22306', studycourse=3, idayear=get_object_or_404(AcademicYear, pk=1))
        Student.objects.create(pk=1, idgroup=get_object_or_404(Group, pk=1), iduser=get_object_or_404(User, pk=1))

        Rights.objects.create(pk=2, rightsname="Преподаватель")
        self.rights = get_object_or_404(Rights, pk=2) 

        # Создание тестового пользователя с правами учителя
        self.teacher = User.objects.create_user(
            login='user1',
            password=self.password,
            lastname='TeacherLastname',
            firstname='TeacherFirstname',
            middlename='TeacherMidName',
            idrights=self.rights 
        )
        self.teacher.save()

    def test_statistics_page_content(self):
        """Проверка загрузки страницы аннотации текста по id 1 и ее наполнения контентом. В системе есть текст с id 1. Пользователь авторизирован в кабинете преподавателя."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('statistics'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertTemplateUsed(response, 'statistics.html')

    def test_statistics_page_content (self):
        """Проверка загрузки страницы аннотации текста по id 1 и ее наполнения контентом. В системе есть текст с id 1. Пользователь авторизирован в кабинете преподавателя."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('statistics'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertTemplateUsed(response, 'statistics.html')
        self.assertContains(response, 'div class="groups-stat"') 
        self.assertContains(response, 'div class="stat-body"') 
        self.assertContains(response, 'div class="summary-stat"')
        self.assertContains(response, 'div class="dashboards"') 
    
    def test_statistics_download  (self):
        """Проверка загрузки страницы аннотации текста по id 1 и ее наполнения контентом. В системе есть текст с id 1. Пользователь авторизирован в кабинете преподавателя."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('export_group_error_stats'), {'group': self.group.idgroup})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        #self.assertTemplateUsed(response, 'dashboard_error_grade.html')
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  
        self.assertIn('attachment; filename="22306 (TestYear).xlsx"', response['Content-Disposition'])

# 
    def test_incorrect_statistics_download  (self):
        """Невозможность скачать документ со статистикой по несуществующей в системе группе."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('export_group_error_stats'), {'group': 22})
        self.assertEqual(response.status_code, 404)  
        self.assertEqual(response.content.decode('utf-8'), "Группа не найдена")  


    def test_summary_statistics_page (self):
            """Проверка загрузки страницы работы с суммарной статистикой"""
            self.client.login(username='user1', password='user1')
            response = self.client.get(reverse('error_stats'))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.wsgi_request.user.is_authenticated)
            self.assertTemplateUsed(response, 'error_stats.html')

    def test_summary_statistics_page_content(self):
            """Проверка загрузки всех элементов страницы суммарной статистики"""
            self.client.login(username='user1', password='user1')
            response = self.client.get(reverse('error_stats'))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.wsgi_request.user.is_authenticated)
            self.assertTemplateUsed(response, 'error_stats.html')
            self.assertContains(response, '<table class="errors-table">') 
            self.assertContains(response, '<div class="legend">') 


    def test_dashboards_page (self):
            """Проверка загрузки страницы работы с дашбордами."""
            self.client.login(username='user1', password='user1')
            response = self.client.get(reverse('grade_errors'))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.wsgi_request.user.is_authenticated)
            self.assertTemplateUsed(response, 'dashboard_error_grade.html')

    def test_dashboards_download  (self):
        """ Проверка скачивания документа со статистикой."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('export_group_error_stats'), {'group': self.group.idgroup})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        #self.assertTemplateUsed(response, 'dashboard_error_grade.html')
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  
        self.assertIn('attachment; filename="22306 (TestYear).xlsx"', response['Content-Disposition'])




