from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import get_object_or_404
from bs4 import BeautifulSoup
from .forms import AddTextAnnotationForm, AddErrorAnnotationForm, TeacherLoadTextForm
from core_app.models import Text, Sentence, Student, TextType, WritePlace, WriteTool, Emotion, User, Group, AcademicYear, Rights

class AnnotationTest(TestCase):
    def setUp(self):
        self.client = Client() 
        self.User = get_user_model()
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

        WritePlace.objects.create(pk=1, writeplacename="TestPlace")
        WriteTool.objects.create(pk=1, writetoolname="TestTool")
        Emotion.objects.create(pk=1, emotionname="TestEmotion")
        TextType.objects.create(pk=1, texttypename="TestType")
        AcademicYear.objects.create(pk=1, title='TestYear')
        Group.objects.create(pk=1, groupname='TestGroup', studycourse=2, idayear=get_object_or_404(AcademicYear, pk=1))
        Student.objects.create(pk=1, idgroup=get_object_or_404(Group, pk=1), iduser=get_object_or_404(User, pk=1))

        self.idtext	= 2379
        self.text = 'Test тест. Есть тест.'
        self.student = get_object_or_404(Student, pk=1)
        self.texttype = get_object_or_404(TextType, pk=1)
        self.writeplace = get_object_or_404(WritePlace, pk=1)
        self.writetool = get_object_or_404(WriteTool, pk=1)
        self.emotion = get_object_or_404(Emotion, pk=1)

        self.text = Text.objects.create(
            idtext=self.idtext,
            text=self.text,
            idstudent = self.student,
            idtexttype = self.texttype,
            idwriteplace = self.writeplace,
            idwritetool = self.writetool,
            idemotion = self.emotion
        )
        self.text = Sentence.objects.create(
            idsentence = 1,
            sentensetext = 'Test тест.',
            ordernumber = 1,
            idtext=get_object_or_404(Text, pk=2379),
        )
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
        #self.client.login(username='user1', password='user1')

#annotate_text
    def test_annotate_text_page(self):
        """Проверка загрузки страницы аннотации текста по id 1 и ее наполнения контентом. В системе есть текст с id 1. Пользователь авторизирован в кабинете преподавателя."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('annotate_text'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertTemplateUsed(response, 'annotate_text.html')
        self.assertContains(response, 'class="rate-btn"')
        #ДОБАВИТЬ КНОПКИ !!!!
    
    
    def test_annotate_text_unauth(self):
        """Проверка отсутствия возможности просмотра текста в режиме аннотирования для неавторизованного пользователя."""
        response = self.client.get(reverse('annotate_text'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        
    def test_annotate_text_has_view (self):
        """Сервер возвращает статус-код 200, что подтверждает успешную загрузку страницы и ее компонентов. Проверка открытия окна Вид при нажатии на кнопку “Вид”."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('annotate_text'))
        self.assertContains(response, '<div class="menu-container">') 
        self.assertContains(response, '<div class="menu-block" data-target="view-content">') 

    def test_annotate_text_has_text  (self):
        """Сервер возвращает статус-код 200, что подтверждает успешную загрузку страницы и ее компонентов. Проверка открытия окна Текст при нажатии на кнопку “Текст”."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('annotate_text'))
        self.assertContains(response, '<div class="menu-container">')
        self.assertContains(response, ' <div class="menu-block" data-target="text-content">')
    
    def test_annotate_text_has_author (self):
        """Проверка открытия окна Автор при нажатии на кнопку “Автор”."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('annotate_text'))
        self.assertContains(response, '<div class="menu-container">')
        self.assertContains(response, '<div class="menu-block" data-target="author-content">')

    def test_annotate_text_has_mark (self):
        """Проверка открытия окна Оценка при нажатии на кнопку “Оценка”."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('annotate_text'))
        self.assertContains(response, '<div class="menu-container">')
        self.assertContains(response, '<div class="menu-block" data-target="grade-content">')

    def test_annotate_text_has_meta (self):
        """Проверка открытия окна Метаданные при нажатии на кнопку “Метаданные”."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('annotate_text'))
        self.assertContains(response, '<div class="menu-container">')
        self.assertContains(response, '<div class="menu-block" data-target="metadata-content">')

    def test_annotate_text_has_add_annotation  (self):
        """Проверка открытия окна добавления аннотации ошибки при нажатии на кнопку “Добавить аннотацию”."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('annotate_text'))
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        add_annotation_button = soup.find('button', {'id': 'add-annotation-button'})  
        #self.assertEqual(add_annotation_button.get('data-toggle'), 'modal', "У кнопки 'Доб'")
        modal_window = soup.find('div', {'id': 'annotation-modal'}) 
        self.assertIsNotNone(modal_window, "Модальное окно не найдено на странице.")

#show_texts
    def test_show_texts_page(self):
        """Проверка загрузки страницы просмотра текстов с возможностью фильтрации."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('show_texts'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.status_code, 200)
        # self.assertIsInstance(response.context['form'], TeacherLoadTextForm)
        self.assertTemplateUsed(response, 'show_texts.html')

    def test_show_texts_page_content (self):
        """Проверка наполнения контента страницы просмотра текстов с возможностью фильтрации."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('show_texts'))
        #response = self.client.get('/show_texts/?text_type=2379') 
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<div class="filter-block">')
        self.assertContains(response, '<form method="post" id="text-search-form">')

    # def test_show_texts_page_search (self):
    #     """Проверка загрузки страницы просмотра текстов после поиска по названию текста в графе поиска при нажатии кнопки “Поиск”."""
    #     response = self.client.get('/show_texts?text_name=some_text')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, "some_text")

    
    def test_show_texts_page_filter  (self):
        """Проверка просмотра текстов по введенным значениям фильтров."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('show_texts'), {'year':1})  
        self.assertEqual(response.status_code, 200)

    def test_show_texts_page_text_type  (self):
        """Проверка открытия страницы с текстами выбранного типа при нажатии кнопки “Название типа текста”."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('show_texts'), {'text_type':1})  
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TestType")


#teacher_load_text
    def test_teacher_load_text_page   (self):
        """Проверка загрузки страницы загрузки текста преподавателем от имени студента."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('teacher_load_text'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertIsInstance(response.context['form'], TeacherLoadTextForm)
        self.assertTemplateUsed(response, 'teacher_load_text.html')

    def test_teacher_load_text_page_content    (self):
        """Проверка загрузки контента страницы “загрузки текста преподавателем от имени студента”."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('teacher_load_text'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertIsInstance(response.context['form'], TeacherLoadTextForm)
        self.assertTemplateUsed(response, 'teacher_load_text.html') 
        self.assertContains(response, '<div class="horizontal-wrap">') 
        self.assertContains(response, '<div class="vertical-level">') 

    
    def test_teacher_load_text_page_unauth    (self):
        """Проверка невозможности открытия страницы загрузки текста при нажатии кнопки “Новый текст” неавторизованным пользователем."""
        
        response = self.client.get(reverse('teacher_load_text'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_teacher_load_text     (self):
        """Загрузка текста от имени студента"""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('teacher_load_text'))
        
        
        form_data = {
            'student': 1,
            'header': 'название',
            'text': 'Текст...',
            'idtexttype': 1,
            'idwriteplace': 1,
            'idwritetool': 1,
            'idemotion': 1,
            'selfassesment':1,
            'selfrating': 1,
            'createdate': '11.12.2025',
            'group':1
        }
        

        response = self.client.post(reverse('teacher_load_text'), form_data)
        
        self.assertEqual(response.status_code, 302)  
        self.assertRedirects(response, reverse('search_texts'))



