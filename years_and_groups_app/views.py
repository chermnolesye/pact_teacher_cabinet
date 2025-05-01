from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from core_app.models import (
    Group,
    AcademicYear,
    Student,
    User,
    Text
)
from .forms import (
    AddGroupForm,
    EditGroupForm,
    AddStudentToGroupForm,
    TransferStudentForm
)
from django.forms import formset_factory
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

def show_groups(request):
    query = request.GET.get('q', '')
    course = request.GET.get('course')
    year_str = request.GET.get('year')
    groups = Group.objects.all()

    if query:
        groups = groups.filter(groupname__icontains=query)

    if course:
        groups = groups.filter(studycourse=course)

    year = None
    if year_str:
        try:
            year = int(year_str)
            groups = groups.filter(idayear=year)  
        except ValueError:
            pass
        
    course_numbers = Group.objects.values_list('studycourse', flat=True).distinct().order_by('studycourse')
    academic_years = AcademicYear.objects.all()

    return render(request, 'show_groups.html', {
        'groups': groups,
        'query': query,
        'selected_course': course,
        'selected_year': year,
        'course_numbers': course_numbers,
        'academic_years': academic_years,
    })

def add_group(request):
    if request.method == 'POST':
        form = AddGroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_group')
        else:
            print(form.errors)  
    else:
        form = AddGroupForm()

    return render(request, 'add_group.html', {'form': form})

def edit_group(request, group_id):
    group = get_object_or_404(Group, idgroup=group_id)
    students = Student.objects.filter(idgroup=group)

    form = EditGroupForm(instance=group)
    add_form = AddStudentToGroupForm(group=group)
    transfer_form = TransferStudentForm(current_course=group.studycourse)
    same_course_groups = Group.objects.filter(studycourse=group.studycourse).exclude(idgroup=group.idgroup)

    if request.method == 'POST':
        if 'save_group' in request.POST:
            form = EditGroupForm(request.POST, instance=group)
            if form.is_valid():
                form.save()
                return redirect('edit_group', group_id=group.idgroup)

        elif 'delete_student' in request.POST and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            student_id = request.POST.get('student_id')
            try:
                student = get_object_or_404(Student, idstudent=student_id)
                has_texts = Text.objects.filter(idstudent=student).exists()
                if has_texts:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Студент имеет связанные тексты и не может быть удалён.'
                    })
                else:
                    student.delete()
                    return JsonResponse({'status': 'success'})
            except Student.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Студент не найден'
                }, status=404)

        elif 'add_student' in request.POST:
            add_form = AddStudentToGroupForm(request.POST, group=group)
            if add_form.is_valid():
                user = add_form.cleaned_data['student']
                Student.objects.create(iduser=user, idgroup=group)
                return redirect('edit_group', group_id=group.idgroup)

        elif 'delete_group' in request.POST:
            group.delete()
            return redirect('show_groups')

        elif 'transfer_student' in request.POST:
            transfer_form = TransferStudentForm(request.POST, current_course=group.studycourse)
            if transfer_form.is_valid():
                student_id = transfer_form.cleaned_data['student_id']
                new_group = transfer_form.cleaned_data['new_group']
                student = get_object_or_404(Student, idstudent=student_id, idgroup=group)
                student.idgroup = new_group
                student.save()
                return redirect('edit_group', group_id=group.idgroup)

    return render(request, 'edit_group.html', {
        'group': group,
        'form': form,
        'students': students,
        'add_form': add_form,
        'transfer_form': transfer_form,
        'same_course_groups': same_course_groups,
    })

    
# def add_academic_year(request):
#     if request.method == "POST":
#         form = AddAcademicYearForm(request.POST)
#         if form.is_valid():
#             ac = form.save()
#             return redirect("/years_groups/add_academic_year")
#     else:
#         form = AddAcademicYearForm()
#     return render(request, "add_academic_year.html", {"form": form})


# def edit_academic_year(request, academic_year_id):
#     academic_year = get_object_or_404(AcademicYear, pk=academic_year_id)
#     initial_data = int(academic_year.title.split("/")[0])
#     if request.method == "POST":
#         form = EditAcademicYearForm(request.POST, instance=academic_year)
#         if form.is_valid():
#             form.save()
#             return redirect(f"/years_groups/edit_academic_year/{academic_year_id}")
#         else:
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     messages.error(request, f"Ошибка в поле {field}: {error}")
#     else:
#         form = EditAcademicYearForm(
#             instance=academic_year, initial={"title": initial_data}
#         )

#     return render(
#         request,
#         "edit_academic_year.html",
#         {"form": form, "academic_year": academic_year, "title": academic_year.title},
#     )

# def delete_academic_year(request, academic_year_id):
#     try:
#         academic_year = get_object_or_404(AcademicYear, pk=academic_year_id)

#         academic_year.delete()
#         return redirect("/years_groups/add_academic_year")  # Изменить !!!!

#     except Exception as e:
#         messages.error(
#             request, f"Произошла ошибка при удалении учебного года: {str(e)}"
#         )
#         return redirect("/years_groups/add_academic_year")

# def show_academic_years(request):
#     years = AcademicYear.objects.all().values("idayear", "title").distinct()
#     years_data = [
#         {
#             "id": year["idayear"],
#             "name": year["title"],
#         }
#         for year in years
#     ]
#     context = {"years": years_data}
#     return render(request, "edit_group.html")  # изменить !!!!!
