from django.shortcuts import render, redirect , get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from core_app.models import (
    Group,
    AcademicYear,
    Student,
    User,
)
from .forms import AddGroupForm, AddAcademicYearForm, EditGroupForm, EditAcademicYearForm
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

def add_group(request): #Изменить разобраться со студентами
    if request.method == "POST":
        form = AddGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            ########
            for form in formset:
                if form.cleaned_data.get('student'):
                    student = form.cleaned_data['student']
                    student.idgroup = group
                    student.save()
            ########
            return redirect('/years_groups/add_group')
    else:
        form = AddGroupForm()
        students_without_group = Student.objects.filter(idgroup__isnull=True)
    return render(request, "add_group.html", {'form': form, 'students_without_group':students_without_group})

def edit_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if request.method == "POST":
        form = EditGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect(f'/years_groups/edit_group/{group_id}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Ошибка в поле {field}: {error}")
    else:
        form = EditGroupForm(instance=group)
    return render(request, "edit_group.html", {'form': form, 'group': group})


def delete_group(request, group_id):  #Изменить !!!!!
    try:
        group = get_object_or_404(Group, pk=group_id)
        
        group.delete()
        return redirect('/years_groups/add_group') #Изменить !!!!
    except Exception as e:
        messages.error(request, f"Произошла ошибка при удалении группы: {str(e)}")
        return redirect('/years_groups/add_group')


def edit_academic_year(request, academic_year_id):
    academic_year = get_object_or_404(AcademicYear, pk=academic_year_id)
    initial_data = int(academic_year.title.split('/')[0])
    if request.method == "POST":
        form = EditAcademicYearForm(request.POST, instance=academic_year)
        if form.is_valid():
            form.save()
            return redirect(f'/years_groups/edit_academic_year/{academic_year_id}')
        else:
            # Выводим ошибки формы
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Ошибка в поле {field}: {error}")
    else:
        form = EditAcademicYearForm(instance=academic_year, initial={'title':initial_data})

    return render(request, "edit_academic_year.html", {'form': form, 'academic_year': academic_year, 'title' : academic_year.title})


def delete_academic_year(request, academic_year_id):
    try:
        academic_year = get_object_or_404(AcademicYear, pk=academic_year_id)
        
        academic_year.delete()
        return redirect('/years_groups/add_academic_year') #Изменить !!!!
        
    except Exception as e:
        messages.error(request, f"Произошла ошибка при удалении учебного года: {str(e)}")
        return redirect('/years_groups/add_academic_year')


def show_groups(request):
    return render(request, "edit_group.html") #изменить !!!!!

def show_academic_years(request):
    return render(request, "edit_group.html") #изменить !!!!!
