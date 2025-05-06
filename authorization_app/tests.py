from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.test import RequestFactory
from .forms import LoginForm
from core_app.models import Rights, User 
from .views import user_login
from unittest.mock import patch, Mock

class UserLoginTest(TestCase):
    def setUp(self):
        self.client = Client() 
        self.factory = RequestFactory()
        #self.User = get_user_model()
        self.password = 'user1'
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
        

    # def tearDown(self):
    #     User.objects.filter(login='user1').delete()

    # def test_login_with_valid_credentials_module(self):
    #     """Тест: Проверка блочного теста успешного входа с существующими логином и паролем."""

    # def test_user_login_valid_form(self, mock_render, mock_redirect, mock_login, mock_authenticate):
    #     """
    #     Модульный тест: Проверяет, что при валидной форме происходит аутентификация, вход и редирект.
    #     (Требует мокирования всех зависимостей).
    #     """
    #     # Создаем Mock request
    #     request = Mock()
    #     request.method = "POST"
    #     request.POST = {'login': 'user1', 'password': 'user1'}

    #     # Мокируем LoginForm, чтобы он всегда был валидным
    #     form = LoginForm(request.POST)
    #     form.is_valid = Mock(return_value=True) # Всегда возвращает True

    #     # Мокируем cleaned_data
    #     form.cleaned_data = {'login': 'user1', 'password': 'user1'}

    #     # Мокируем authenticate, чтобы возвращал пользователя
    #     mock_authenticate.return_value = Mock()  # Поддельный пользователь

    #     # Вызываем view
    #     user_login(request)

    #     # Проверяем, что authenticate был вызван с правильными аргументами
    #     mock_authenticate.assert_called_once_with(request, login='testuser', password='testpassword')

    #     # Проверяем, что login был вызван
    #     mock_login.assert_called_once()

    #     # Проверяем, что redirect был вызван
    #     mock_redirect.assert_called_once()

    #     # Проверяем, что render не был вызван (т.к. успешный логин)
    #     mock_render.assert_not_called()



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


