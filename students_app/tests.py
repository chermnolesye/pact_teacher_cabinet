from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.test import RequestFactory
from core_app.models import Rights, User , AcademicYear, Group, Student
from unittest.mock import patch, Mock

class StudentsTests(TestCase):
    def setUp(self):
        self.client = Client() 
        self.factory = RequestFactory()
        #self.User = get_user_model()
        self.password = 'user1'

        Rights.objects.create(pk=1, rightsname="Студент")
        self.rights = get_object_or_404(Rights, pk=1) 

        User.objects.create_user(
            iduser = 1,
            login='user1',
            password=self.password,
            lastname='TeacherLastname',
            firstname='TeacherFirstname',
            middlename='TeacherMidName',
            idrights=self.rights 
        )
        AcademicYear.objects.create(pk=1, title='TestYear')
        self.group = Group.objects.create(pk=1, groupname='22306', studycourse=3, idayear=get_object_or_404(AcademicYear, pk=1))
        Student.objects.create(pk=1, idgroup=get_object_or_404(Group, pk=1), iduser=get_object_or_404(User, pk=1))

        
    def test_show_students_page (self):
        """Проверка загрузки страницы работы со студентами."""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('show_students'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        # self.assertIsInstance(response.context['form'], AddTextAnnotationForm)
        # self.assertIsInstance(response.context['form'], AddErrorAnnotationForm)
        self.assertTemplateUsed(response, 'show_students.html')


    def test_show_students_page_search  (self):
        response = self.client.get(reverse('show_students, args=[self.group.idgroup]'))

        self.assertEqual(response.status_code, 200)

    def test_show_new_student  (self):
        response = self.client.post(reverse('group_edit', args=[self.group.idgroup]), {'student_id': self.student.idstudent})
        
        self.assertRedirects(response, reverse('show_students'))
        self.student.refresh_from_db()
        
        self.assertEqual(self.student.group, self.group)
        
        response = self.client.get(reverse('show_students'))
        self.assertContains(response, 'Иван Иванов')
        self.assertContains(response, self.group.name)
