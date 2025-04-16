from django.shortcuts import render
from django.http import JsonResponse
from core_app.models import (
    Group,
    AcademicYear,
    Student,
    User,
)


def add_academic_year(request):
    return render(request, "add_academic_year.html")

def add_group(request):
    return render(request, "add_group.html")