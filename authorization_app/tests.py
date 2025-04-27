from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import get_object_or_404

from .forms import LoginForm
from core_app.models import Rights 


class UserLoginTest(TestCase):
    def setUp(self):
        self.client = Client() 
        self.User = get_user_model()
        self.password = 'user1'
        Rights.objects.create(pk=2, rightsname="Преподаватель")
        self.rights = get_object_or_404(Rights, pk=2) 

        # Создание тестового пользователя с правами учителя
        self.teacher = self.User.objects.create_user(
            login='user1',
            password=self.password,
            lastname='TeacherLastname',
            firstname='TeacherFirstname',
            middlename='TeacherMidName',
            idrights=self.rights 
        )


    def test_login_page(self):
        """Проверка загрузки страницы авторизации."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], LoginForm)
        self.assertTemplateUsed(response, 'authorization_app/login.html')
    
    def test_successful_login (self):
        """Проверка успешного входа пользователя в систему. В системе существует пользователь с логином user1 и паролем user1. Данный пользователь имеет роль преподаватель."""
        response = self.client.post(reverse('login'), {'login': 'user1', 'password': 'user1'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.login(username='user1', password='user1'))
        self.assertEqual(response.url, '/text/show_texts/')  
        session_response = self.client.get(reverse('show_texts'))
        self.assertIn('sessionid', response.cookies)
        self.assertEqual(session_response.context['fio'], 'TeacherLastname TeacherFirstname TeacherMidName') 

    def test_unsuccessful_login(self):
        """Проверка не успешного входа пользователя в систему. В системе нет пользователя с логином user и паролем user."""
        response = self.client.post(reverse('login'), {'login': 'user', 'password': 'user'}) 
        self.assertFalse(self.client.login(username='user', password='user'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authorization_app/login.html')
        self.assertNotIn('sessionid', response.cookies)
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertTrue(len(messages_list) > 0)
        message = [str(messag) for messag in messages_list] 
        self.assertListEqual(["Неверный логин или пароль."], message)
        session_response = self.client.get(reverse('show_texts'))
        self.assertEqual(session_response.status_code, 200) 

       
    def test_login_with_no_data (self):
        """ Проверка не успешного входа пользователя в систему. Поля с логином и паролем не заполнены."""
        response = self.client.post(reverse('login'), {'login': '', 'password': ''}) 
        self.assertFalse(self.client.login(username='', password=''))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authorization_app/login.html')
        self.assertNotIn('sessionid', response.cookies)
        self.assertIsInstance(response.context['form'], LoginForm)
        self.assertTrue(response.context['form'].errors)


