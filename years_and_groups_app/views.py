from django.shortcuts import render, redirect
from django.http import JsonResponse
from core_app.models import (
    Group,
    AcademicYear,
    Student,
    User,
)
from .forms import AddGroupForm, AddAcademicYearForm
from django.forms import formset_factory



def add_academic_year(request):
    if request.method == "POST":
        form = AddAcademicYearForm(request.POST)
        if form.is_valid():
            ac = form.save()
            return redirect('/years_groups/add_academic_year')
    else:
        form = AddAcademicYearForm()
    return render(request, "add_academic_year.html", {'form': form})

def add_group(request):
    if request.method == "POST":
        form = AddGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            # for form in formset:
            #     if form.cleaned_data.get('student'):
            #         student = form.cleaned_data['student']
            #         student.idgroup = group
            #         student.save()
            return redirect('/years_groups/add_group')
    else:
        form = AddGroupForm()
        students_without_group = Student.objects.filter(idgroup__isnull=True)
    return render(request, "add_group.html", {'form': form, 'students_without_group':students_without_group})

