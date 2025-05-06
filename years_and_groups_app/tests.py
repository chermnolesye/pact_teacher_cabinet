from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.test import RequestFactory
from core_app.models import Rights, User , AcademicYear, Group
from unittest.mock import patch, Mock
from .forms import AddGroupForm

class GroupsTest(TestCase):
    def setUp(self):
        self.client = Client() 
        self.factory = RequestFactory()
        #self.User = get_user_model()
        self.password = 'user1'
        Rights.objects.create(pk=2, rightsname="Преподаватель")
        self.rights = get_object_or_404(Rights, pk=2) 

        AcademicYear.objects.create(pk=1, title='TestYear')
        Group.objects.create(pk=1, groupname='22306', studycourse=3, idayear=get_object_or_404(AcademicYear, pk=1))

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
        


    # def test_add_academic_year_page (self):
    #     """Проверка загрузки страницы аннотации текста по id 1 и ее наполнения контентом. В системе есть текст с id 1. Пользователь авторизирован в кабинете преподавателя."""
    #     self.client.login(username='user1', password='user1')
    #     response = self.client.get(reverse('add_academic_year'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(response.wsgi_request.user.is_authenticated)
    #     # self.assertIsInstance(response.context['form'], AddTextAnnotationForm)
    #     # self.assertIsInstance(response.context['form'], AddErrorAnnotationForm)
    #     self.assertTemplateUsed(response, 'add_academic_year.html')
    #     #ДОБАВИТЬ КНОПКИ !!!!

    def test_add_group_page  (self):
        """Проверка загрузки страницы аннотации текста по id 1 и ее наполнения контентом. В системе есть текст с id 1. Пользователь авторизирован в кабинете преподавателя."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('add_group'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        # self.assertIsInstance(response.context['form'], AddTextAnnotationForm)
        # self.assertIsInstance(response.context['form'], AddErrorAnnotationForm)
        self.assertTemplateUsed(response, 'add_group.html')
        #ДОБАВИТЬ КНОПКИ !!!!

    def test_show_added_group   (self):
        """Проверка загрузки страницы аннотации текста по id 1 и ее наполнения контентом. В системе есть текст с id 1. Пользователь авторизирован в кабинете преподавателя."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('add_group'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertTemplateUsed(response, 'add_group.html')
        self.client.login(login="user1", password="user1")   
        #Group.objects.create(groupname=22306, studycourse=3, idayear=AcademicYear.objects.get(idayear=1))
        

        form_data = {
            'groupname': 22305,
            'studycourse': 3,
            'idayear': 1,
        }
        response = self.client.post(reverse('add_group'), form_data)
        form = AddGroupForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertTrue(Group.objects.filter(groupname=22305).exists())
        response = self.client.post(reverse('add_group'), form_data)
                
        self.assertEqual(response.status_code, 302)  
        #self.assertRedirects(response, reverse('show_texts'))
        # self.assertTrue(Text.objects.filter(academic_group="22305").exists())


    def test_add_incorrect_group(self):
        """Проверка, что группу нельзя добавить с некорректными данными."""
        self.client.login(username='user1', password='user1')

        form_data = {
            'groupname': 'invalid_group_name',  
            'studycourse': -1,  
            'idayear': 'fvgbh',  
        }

        response = self.client.post(reverse('add_group'), form_data)
        form = AddGroupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertFalse(Group.objects.filter(groupname='invalid_group_name').exists())
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'add_group.html')  

   
    def test_add_existing_group(self):
        """Проверка добавления существующей группы."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('add_group'))
        self.assertTrue(self.teacher.is_authenticated) 
        self.assertTemplateUsed(response, 'add_group.html')
        Group.objects.create(groupname=22306, studycourse=3, idayear=AcademicYear.objects.get(idayear=1))

        form_data = {
            'groupname': 22306,
            'studycourse': 3,
            'idayear': 1,
        }

        response = self.client.post(reverse('add_group'), form_data)
        self.assertTrue(Group.objects.filter(groupname=22306, studycourse=3, idayear=1).exists()) 
  