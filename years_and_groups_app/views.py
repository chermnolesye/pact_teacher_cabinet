from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from core_app.models import (
    Group,
    AcademicYear,
    Student,
    User,
)
from .forms import (
    AddGroupForm,
    AddAcademicYearForm,
    EditGroupForm,
    EditAcademicYearForm,
    AddStudentToGroupForm
)
from django.forms import formset_factory

def show_groups(request):
    query = request.GET.get('q', '')  
    groups = Group.objects.filter(groupname__icontains=query)  

    return render(request, 'show_groups.html', {
        'groups': groups,  
        'query': query  
    })

def add_group(request):
    if request.method == 'POST':
        form = AddGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.idayear = form.cleaned_data['idayear']
            group.save()
            return redirect('add_group')  
    else:
        form = AddGroupForm()

    return render(request, 'add_group.html', {'form': form})

def edit_group(request, group_id):
    group = get_object_or_404(Group, idgroup=group_id)
    students = Student.objects.filter(idgroup=group)

    if request.method == 'POST':
        if 'save_group' in request.POST:
            form = EditGroupForm(request.POST, instance=group)
            if form.is_valid():
                form.save()
                return redirect('edit_group', group_id=group.idgroup)

        elif 'delete_student' in request.POST:
            student_id = request.POST.get('student_id')
            student = get_object_or_404(Student, idstudent=student_id)
            student.idgroup = None
            student.save()
            return redirect('edit_group', group_id=group.idgroup)

        elif 'add_student' in request.POST:
            add_form = AddStudentToGroupForm(request.POST)
            if add_form.is_valid():
                student = add_form.cleaned_data['student']
                student.idgroup = group
                student.save()
                return redirect('edit_group', group_id=group.idgroup)

        elif 'delete_group' in request.POST:
            group.delete()
            return redirect('show_groups')

    else:
        form = EditGroupForm(instance=group)
        add_form = AddStudentToGroupForm()

    return render(request, 'edit_group.html', {
        'group': group,
        'form': form,
        'students': students, 
        'add_form': add_form,
    })

def add_academic_year(request):
    if request.method == "POST":
        form = AddAcademicYearForm(request.POST)
        if form.is_valid():
            ac = form.save()
            return redirect("/years_groups/add_academic_year")
    else:
        form = AddAcademicYearForm()
    return render(request, "add_academic_year.html", {"form": form})

# def add_group(request):  # Изменить разобраться со студентами
#     if request.method == "POST":
#         form = AddGroupForm(request.POST)
#         if form.is_valid():
#             group = form.save()
#             return redirect('/years_groups/add_group')
#     else:
#         form = AddGroupForm()
#         students_without_group = Student.objects.filter(idgroup__isnull=True)
#     return render(
#         request,
#         "add_group.html",
#         {"form": form, "students_without_group": students_without_group},
#     )


# def edit_group(request, group_id):
#     group = get_object_or_404(Group, pk=group_id)
#     if request.method == "POST":
#         form = EditGroupForm(request.POST, instance=group)
#         if form.is_valid():
#             form.save()
#             return redirect(f"/years_groups/edit_group/{group_id}")
#         else:
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     messages.error(request, f"Ошибка в поле {field}: {error}")
#     else:
#         form = EditGroupForm(instance=group)
#     return render(request, "edit_group.html", {'form': form, 'group': group, 'group_students': form.group_students})

####### не работает в связи с невозможностью поставить null пока изменяет группу на 95, хз есть ли такая у вас, если нет создайте или поменяйте id 
# скорее всего придется создавть url для него хз
def remove_student_from_group(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':  
        student_id = request.POST.get('student_id')
        try:
            student = Student.objects.get(pk=student_id)
            # так как нельзя установить null проверяем по изменению руппы - хз как иначе
            group = Group.objects.get(pk=95)
            student.idgroup = group  # Удаляем студента из группы (или student.delete() для полного удаления)
            student.save()
            return JsonResponse({'status': 'success'})
        except Student.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Студент не найден'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Неверный запрос'}, status=400)

def delete_group(request, group_id):  # Изменить !!!!!
    try:
        group = get_object_or_404(Group, pk=group_id)

        group.delete()
        return redirect("/years_groups/add_group")  # Изменить !!!!
    except Exception as e:
        messages.error(request, f"Произошла ошибка при удалении группы: {str(e)}")
        return redirect("/years_groups/add_group")


def edit_academic_year(request, academic_year_id):
    academic_year = get_object_or_404(AcademicYear, pk=academic_year_id)
    initial_data = int(academic_year.title.split("/")[0])
    if request.method == "POST":
        form = EditAcademicYearForm(request.POST, instance=academic_year)
        if form.is_valid():
            form.save()
            return redirect(f"/years_groups/edit_academic_year/{academic_year_id}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Ошибка в поле {field}: {error}")
    else:
        form = EditAcademicYearForm(
            instance=academic_year, initial={"title": initial_data}
        )

    return render(
        request,
        "edit_academic_year.html",
        {"form": form, "academic_year": academic_year, "title": academic_year.title},
    )


def delete_academic_year(request, academic_year_id):
    try:
        academic_year = get_object_or_404(AcademicYear, pk=academic_year_id)

        academic_year.delete()
        return redirect("/years_groups/add_academic_year")  # Изменить !!!!

    except Exception as e:
        messages.error(
            request, f"Произошла ошибка при удалении учебного года: {str(e)}"
        )
        return redirect("/years_groups/add_academic_year")


# def show_groups(request):
#     groups = (
#         Group.objects.select_related("idayear")
#         .all()
#         .values("idgroup", "groupname", "idayear__title")
#         .distinct()
#     )
#     group_data = [
#         {
#             "id": group["idgroup"],
#             "name": group["groupname"],
#             "year": group["idayear__title"],
#         }
#         for group in groups
#     ]
#     context = {"groups": group_data}
#     return render(request, "edit_group.html", context)  # изменить !!!!!


def show_academic_years(request):
    years = AcademicYear.objects.all().values("idayear", "title").distinct()
    years_data = [
        {
            "id": year["idayear"],
            "name": year["title"],
        }
        for year in years
    ]
    context = {"years": years_data}
    return render(request, "edit_group.html")  # изменить !!!!!
