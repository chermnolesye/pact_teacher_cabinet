from django import forms
from core_app.models import Group, AcademicYear, Student, User
import datetime
from django.forms import formset_factory


class TransferStudentForm(forms.Form):
    student_id = forms.IntegerField(widget=forms.HiddenInput())
    new_group = forms.ModelChoiceField(
        queryset=Group.objects.none(),
        label="Перевести в группу",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        current_course = kwargs.pop('current_course', None)
        current_group = kwargs.pop('current_group', None)
        super().__init__(*args, **kwargs)
        if current_course is not None:
            queryset = Group.objects.filter(studycourse=current_course)
            if current_group is not None:
                queryset = queryset.exclude(idgroup=current_group.idgroup)
            self.fields['new_group'].queryset = queryset

class AddGroupForm(forms.ModelForm):
    idayear = forms.IntegerField(
        label='Учебный год (начало, типа 2024)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 2000,
            'max': 2100,
            'step': 1,
            'value': 2024
        })
    )

    copy_from_group = forms.ModelChoiceField(
        label='Зачислить студентов из существующей группы (необязательно)',
        queryset=Group.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Group
        fields = ['groupname', 'studycourse'] 
        labels = {
            'groupname': 'Название группы',
            'studycourse': 'Номер курса',
        }
        widgets = {
            'groupname': forms.TextInput(attrs={'class': 'form-control'}),
            'studycourse': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'step': 1,
                'value': 1
            }),
        }

    def clean_idayear(self):
        year = self.cleaned_data['idayear']
        title = f"{year}/{year + 1}"
        return year

    def save(self, commit=True):
        year = self.cleaned_data['idayear']
        title = f"{year}/{year + 1}"
        
        academic_year, created = AcademicYear.objects.get_or_create(
            title=title
        )

        group = super().save(commit=False)
        group.idayear = academic_year
        
        if commit:
            group.save()

            # Копирование студентов из существующей группы
            copy_from = self.cleaned_data.get('copy_from_group')
            if copy_from:
                students_to_copy = Student.objects.filter(idgroup=copy_from)
                Student.objects.bulk_create([
                    Student(idgroup=group, iduser=s.iduser) for s in students_to_copy
                ])

        return group
    
    
class EditGroupForm(forms.ModelForm):
    idayear = forms.CharField(label='Год обучения')  

    class Meta:
        model = Group
        fields = ['groupname', 'studycourse', 'idayear']
        labels = {
            'groupname': 'Название группы',
            'studycourse': 'Курс',
            'idayear': 'Год обучения'
        }
        widgets = {
            'groupname': forms.TextInput(attrs={'class': 'form-control'}),
            'studycourse': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'step': 1,
                'value': 1
            }),
        }

    def clean_idayear(self):
        year_string = self.cleaned_data['idayear'].strip()
        try:
            start_year, end_year = map(int, year_string.split('/'))
        except ValueError:
            raise forms.ValidationError("Год должен быть в формате ГГГГ/ГГГГ")

        title = f"{start_year}/{end_year}"

        academicyear, _ = AcademicYear.objects.get_or_create(title=title)
        return academicyear


class AddStudentToGroupForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=User.objects.none(), 
        label="Добавить студента",
        empty_label="Выберите студента"
    )

    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        student_users = User.objects.filter(
            iduser__in=Student.objects.values_list('iduser', flat=True)
        )        
        if group:
            current_group_students = Student.objects.filter(idgroup=group)
            student_users = student_users.exclude(
                iduser__in=current_group_students.values_list('iduser', flat=True)
            )
        
        self.fields['student'].queryset = student_users
        self.fields['student'].widget = forms.Select(
            choices=[(user.iduser, f"{user.lastname} {user.firstname} {user.middlename or ''} ({user.login})") 
                    for user in student_users]
        )
