from authorization_app.utils import has_teacher_rights
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q, F
from .forms import EditStudentForm, AddStudentForm
from core_app.models import (
    Student,
    Text,
    Group,
    Student,
    User,
)


@user_passes_test(has_teacher_rights, login_url='/auth/login/')
def show_students(request):
    query = request.GET.get('q', '').strip()
    group_id = request.GET.get('group', '').strip()

    students_qs = Student.objects.select_related('iduser', 'idgroup')

    if group_id.isdigit():
        students_qs = students_qs.filter(idgroup__idgroup=int(group_id))

    if query:
        students_qs = students_qs.filter(
            Q(iduser__lastname__icontains=query) |
            Q(iduser__firstname__icontains=query) |
            Q(iduser__middlename__icontains=query) |
            Q(iduser__login__icontains=query)
        )

    unique_users = students_qs.values('iduser').distinct()

    from django.db.models import OuterRef, Subquery

    first_student = Student.objects.filter(iduser=OuterRef('pk')).order_by('pk')
    users = User.objects.filter(iduser__in=[u['iduser'] for u in unique_users])
    users = users.annotate(student_id=Subquery(first_student.values('idstudent')[:1]))

    students = Student.objects.select_related('iduser', 'idgroup').filter(idstudent__in=[u.student_id for u in users])

    groups = Group.objects.all()

    context = {
        'students': students,
        'query': query,
        'group_id': group_id,
        'groups': groups,
    }

    return render(request, "show_students.html", context)


@user_passes_test(has_teacher_rights, login_url='/auth/login/')
def student_info(request, student_id):
    query = request.GET.get('q', '').strip()
    course_filter = request.GET.get('course', '').strip()  # Добавляем параметр для фильтрации по курсу

    student = get_object_or_404(Student.objects.select_related('iduser'), pk=student_id)
    user = student.iduser

    all_student_records = Student.objects.filter(iduser=user)
    texts = Text.objects.filter(idstudent__in=all_student_records).annotate(
        error_count=Count('sentence__tokens__errortoken__iderror', distinct=True),
        text_type=F('idtexttype__texttypename')
    )

    if query:
        texts = texts.filter(header__icontains=query)
    
    # Добавляем фильтрацию по курсу, если параметр передан
    if course_filter:
        texts = texts.filter(idstudent__idgroup__studycourse=course_filter)

    if request.method == 'POST':
        form = EditStudentForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('student_info', student_id=student.idstudent)
    else:
        form = EditStudentForm(instance=user)

    # Получаем уникальные номера курсов для фильтра
    available_courses = Group.objects.filter(
        student__in=all_student_records
    ).values_list('studycourse', flat=True).distinct().order_by('studycourse')

    context = {
        'user_id': user.iduser,
        'lastname': user.lastname,
        'firstname': user.firstname,
        'middlename': user.middlename,
        'birthdate': user.birthdate if user.birthdate else 'Не указано',
        'gender': 'Мужской' if user.gender == 1 else 'Женский',
        'student': {
            'id': student.idstudent,
            'full_name': user.get_full_name(),
        },
        'texts': texts,
        'query': query,
        'form': form,
        'available_courses': available_courses,  # Добавляем список доступных курсов
        'selected_course': course_filter,  # Добавляем выбранный курс
    }

    return render(request, 'student_info.html', context)


@user_passes_test(has_teacher_rights, login_url='/auth/login/')
def add_student(request):
    if request.method == 'POST':
        form = AddStudentForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            group = form.cleaned_data['group']
            Student.objects.create(iduser=user, idgroup=group)
            return redirect('show_students') 
    else:
        form = AddStudentForm()
    return render(request, 'add_student.html', {'form': form})