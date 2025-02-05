from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import StudentRegistrationForm, TeacherRegistrationForm, StudentLoginForm, TeacherLoginForm
from db_editor.models import User, Student, Rights

def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            # Проверяем, существует ли пользователь с таким логином
            if User.objects.filter(login=form.cleaned_data['login']).exists():
                messages.error(request, 'Пользователь с таким логином уже существует')
                return render(request, 'authorization/register_student.html', {'form': form})

            # Получаем права студента
            student_right = Rights.objects.get(rightsname='Студент')  

            # Создаем объект User
            user = User(
                login=form.cleaned_data['login'],
                lastname=form.cleaned_data['lastname'],
                firstname=form.cleaned_data['firstname'],
                middlename=form.cleaned_data.get('middlename'),
                birthdate=form.cleaned_data.get('birthdate'),
                gender=form.cleaned_data.get('gender'),
                idrights=student_right  
            )
            user.set_password(form.cleaned_data['password'])  
            user.save()  

            # Создаем запись в таблице Student
            Student.objects.create(
                iduser=user, 
                idgroup=form.cleaned_data['group']
            )

            messages.success(request, 'Студент успешно зарегистрирован')
            return redirect('home')  # Заменить
    else:
        form = StudentRegistrationForm()

    return render(request, 'authorization/register_student.html', {'form': form})


def register_teacher(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            # Проверяем, существует ли пользователь с таким логином
            if User.objects.filter(login=form.cleaned_data['login']).exists():
                messages.error(request, 'Пользователь с таким логином уже существует')
                return render(request, 'authorization/register_teacher.html', {'form': form})

            # Получаем права преподавателя
            teacher_right = Rights.objects.get(rightsname='Преподаватель')  # Убедитесь, что такое право существует

            # Создаем объект User
            user = User(
                login=form.cleaned_data['login'],
                lastname=form.cleaned_data['lastname'],
                firstname=form.cleaned_data['firstname'],
                middlename=form.cleaned_data.get('middlename'),
                birthdate=form.cleaned_data.get('birthdate'),
                gender=form.cleaned_data.get('gender'),
                idrights=teacher_right  
            )
            user.set_password(form.cleaned_data['password']) 
            user.save()  

            messages.success(request, 'Преподаватель успешно зарегистрирован')
            return redirect('home')  # Заменить
    else:
        form = TeacherRegistrationForm()

    return render(request, 'authorization/register_teacher.html', {'form': form})

def login_student(request):
    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            login_data = form.cleaned_data['login']
            password_data = form.cleaned_data['password']
            try:
                user = User.objects.get(login=login_data)
                if user.idrights.rightsname != 'Студент':
                    messages.error(request, 'Этот аккаунт не принадлежит студенту.')
                    return render(request, 'authorization/login_student.html', {'form': form})
            except User.DoesNotExist:
                user = None

            if user and user.check_password(password_data):
                login(request, user)
                messages.success(request, 'Вы успешно вошли в систему как студент.')
                return redirect('academic_years')  # Заменить
            else:
                messages.error(request, 'Неправильный логин или пароль.')
    else:
        form = StudentLoginForm()
    
    return render(request, 'authorization/login_student.html', {'form': form})

def login_teacher(request):
    if request.method == 'POST':
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            login_data = form.cleaned_data['login']
            password_data = form.cleaned_data['password']
            try:
                user = User.objects.get(login=login_data)
                if user.idrights.rightsname != 'Преподаватель':
                    messages.error(request, 'Этот аккаунт не принадлежит преподавателю.')
                    return render(request, 'authorization/login_teacher.html', {'form': form})
            except User.DoesNotExist:
                user = None

            if user and user.check_password(password_data):
                login(request, user)
                messages.success(request, 'Вы успешно вошли в систему как преподаватель.')
                return redirect('home')  # Заменить
            else:
                messages.error(request, 'Неправильный логин или пароль.')
    else:
        form = TeacherLoginForm()
    
    return render(request, 'authorization/login_teacher.html', {'form': form})