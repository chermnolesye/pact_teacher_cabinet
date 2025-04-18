from django.shortcuts import render
from django.http import JsonResponse
from core_app.models import (
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
