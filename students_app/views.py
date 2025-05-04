from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Count, Q, F
from .forms import EditStudentForm, AddStudentForm
from core_app.models import (
    Student,
    Error,
    ErrorToken,
    Text,
    Group,
    AcademicYear,
    Student,
    User,
)

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

def student_info(request, student_id):
    query = request.GET.get('q', '').strip()

    student = get_object_or_404(Student.objects.select_related('iduser'), pk=student_id)
    user = student.iduser

    all_student_records = Student.objects.filter(iduser=user)
    texts = Text.objects.filter(idstudent__in=all_student_records).annotate(
        error_count=Count('sentence__tokens__errortoken__iderror', distinct=True),
        text_type=F('idtexttype__texttypename')
    )

    if query:
        texts = texts.filter(header__icontains=query)

    if request.method == 'POST':
        form = EditStudentForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('student_info', student_id=student.idstudent)
    else:
        form = EditStudentForm(instance=user)

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
    }

    return render(request, 'student_info.html', context)

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