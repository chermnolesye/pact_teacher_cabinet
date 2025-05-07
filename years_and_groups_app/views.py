from authorization_app.utils import has_teacher_rights
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
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

@user_passes_test(has_teacher_rights, login_url='/auth/login/')
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


@user_passes_test(has_teacher_rights, login_url='/auth/login/')
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


@user_passes_test(has_teacher_rights, login_url='/auth/login/')
def edit_group(request, group_id):
    group = get_object_or_404(Group, idgroup=group_id)
    students = Student.objects.filter(idgroup=group)

    form = EditGroupForm(instance=group)
    add_form = AddStudentToGroupForm(group=group)
    transfer_form = TransferStudentForm(current_course=group.studycourse, current_group=group)
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

