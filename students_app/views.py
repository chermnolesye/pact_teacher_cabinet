from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Q, F
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

    students = Student.objects.select_related('iduser', 'idgroup')

    if group_id.isdigit():
        students = students.filter(idgroup__idgroup=int(group_id))

    if query:
        students = students.filter(
            iduser__lastname__icontains=query
        ) | students.filter(
            iduser__firstname__icontains=query
        ) | students.filter(
            iduser__middlename__icontains=query
        ) | students.filter(
            iduser__login__icontains=query
        )
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

    texts = Text.objects.filter(idstudent=student).annotate(
        error_count=Count('sentence__tokens__errortoken__iderror', distinct=True),
        errorcheckflag=F('errorcheckflag'),
        textgrade=F('textgrade'),
        createdate=F('createdate'),
        text_type=F('idtexttype__texttypename')
    )

    if query:
        texts = texts.filter(textname__icontains=query)

    full_name = student.get_full_name() 
    context = {
        'student': {
            'id': student.idstudent,
            'full_name': full_name,
        },
        'texts': texts,
        'query': query,
    }

    return render(request, 'student_info.html', context)