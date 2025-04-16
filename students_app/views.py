from django.shortcuts import render
from django.http import JsonResponse
from core_app.models import (
    Group,
    AcademicYear,
    Student,
    User,
)


def show_students(request):
    return render(request, "show_students.html")