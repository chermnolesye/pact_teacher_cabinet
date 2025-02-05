from django import forms
from db_editor.models import User, Student, Group, Rights

class StudentRegistrationForm(forms.ModelForm):
    login = forms.CharField(max_length=100, required=True, label='Логин')
    password = forms.CharField(widget=forms.PasswordInput, required=True, label='Пароль')
    lastname = forms.CharField(max_length=100, required=True, label='Фамилия')
    firstname = forms.CharField(max_length=100, required=True, label='Имя')
    middlename = forms.CharField(max_length=100, required=False, label='Отчество')
    birthdate = forms.DateField(required=False, label='Дата рождения', input_formats=['%d.%m.%Y'])
    gender = forms.ChoiceField(choices=[(True, 'Мужской'), (False, 'Женский')], required=False, label='Пол')
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label='Группа')

    class Meta:
        model = User
        fields = ['login', 'password', 'lastname', 'firstname', 'middlename', 'birthdate', 'gender', 'group']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  

        if commit:
            user.save()
            student_right = Rights.objects.get(rightsname='Студент')  
            user.idrights = student_right  
            user.save()
        return user

class TeacherRegistrationForm(forms.ModelForm):
    login = forms.CharField(max_length=100, required=True, label='Логин')
    password = forms.CharField(widget=forms.PasswordInput, required=True, label='Пароль')
    lastname = forms.CharField(max_length=100, required=True, label='Фамилия')
    firstname = forms.CharField(max_length=100, required=True, label='Имя')
    middlename = forms.CharField(max_length=100, required=False, label='Отчество')
    birthdate = forms.DateField(required=False, label='Дата рождения', input_formats=['%d.%m.%Y'])
    gender = forms.ChoiceField(choices=[(True, 'Мужской'), (False, 'Женский')], required=False, label='Пол')

    class Meta:
        model = User
        fields = ['login', 'password', 'lastname', 'firstname', 'middlename', 'birthdate', 'gender']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  

        if commit:
            user.save()
            teacher_right = Rights.objects.get(rightsname='Преподаватель')  
            user.idrights = teacher_right  
            user.save()
        return user

class StudentLoginForm(forms.Form):
    login = forms.CharField(max_length=100, required=True, label='Логин')
    password = forms.CharField(widget=forms.PasswordInput, required=True, label='Пароль')

class TeacherLoginForm(forms.Form):
    login = forms.CharField(max_length=100, required=True, label='Логин')
    password = forms.CharField(widget=forms.PasswordInput, required=True, label='Пароль')