from django import forms
from core_app.models import Group, AcademicYear, Student, User
import datetime
from django.forms import formset_factory

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
        if not AcademicYear.objects.filter(title=title).exists():
            raise forms.ValidationError("Такого учебного года нет в системе.")
        return year

    def save(self, commit=True):
        group = super().save(commit=False)
        year = self.cleaned_data['idayear']
        title = f"{year}/{year + 1}"
        group.idayear = AcademicYear.objects.get(title=title)  
        if commit:
            group.save()
        return group
    
    
class EditGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['groupname', 'studycourse']
        labels = {
            'groupname': 'Название группы',
            'studycourse': 'Курс',
            'idayear': 'Год обучения'
        }

    def clean_idayear(self):
        year_string = self.cleaned_data['idayear']
        start_year, end_year = map(int, year_string.split('/'))
        return f"{start_year}/{end_year}" 


# class AddStudentToGroupForm(forms.Form):
#     student = forms.ModelChoiceField(
#         queryset=User.objects.none(), 
#         label="Добавить студента",
#         empty_label="Выберите студента"
#     )

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         student_users = User.objects.filter(iduser__in=Student.objects.values_list('iduser', flat=True))
#         self.fields['student'].queryset = student_users
#         self.fields['student'].widget = forms.Select(
#             choices=[(user.iduser, f"{user.lastname} {user.firstname} {user.middlename or ''} ({user.login})") for user in student_users]
#         )

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
        # Если указана группа, исключаем студентов этой группы
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

class AddAcademicYearForm(forms.Form):
    current_year = datetime.datetime.now().year

    title = forms.IntegerField(label="Учебный год", required=True, min_value=current_year, max_value=current_year+1, initial=current_year, widget=forms.NumberInput(attrs={'id': 'title'}))
    title_2 = forms.CharField(initial=f"/ {current_year+1}", label="Учебный год конечный", widget=forms.TextInput(attrs={'id': 'title_2', 'readonly': 'readonly'})) # второе поле для конечного года
    
    class Meta:
        model = AcademicYear
        fields = ['title']
        
    def clean(self):
        current_year = datetime.datetime.now().year
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        
        if title:
                if str(current_year) != str(title):
                    raise forms.ValidationError(f"Учебный год должен начинаться с {current_year}.")
                try:
                    academic_year = AcademicYear.objects.get(title__startswith=str(title))
                    raise forms.ValidationError(f"Учебный год начинающийся с {title} уже существует.")
                except AcademicYear.DoesNotExist:
                    cleaned_data['title'] = title

        return cleaned_data
    def save(self):
        if self.is_valid():
            title = self.cleaned_data['title']
            ac = AcademicYear.objects.create(title=f"{title}/{int(title)+1}")
            
            return ac
        return None
    

class EditAcademicYearForm(forms.ModelForm): 
    class Meta:
        model = AcademicYear
        fields = ['title'] 

    current_year = datetime.datetime.now().year

    title = forms.IntegerField(label="Учебный год", required=True, min_value=current_year-1, max_value=current_year+1, widget=forms.NumberInput(attrs={'id': 'title'}))
    title_2 = forms.CharField(initial=f"/ {current_year+1}", label="Учебный год конечный", widget=forms.TextInput(attrs={'id': 'title_2', 'readonly': 'readonly'})) # второе поле для конечного года

    def clean_title(self):
      title = self.cleaned_data['title']
      instance_id = self.instance.pk if self.instance else None

      if AcademicYear.objects.exclude(pk=instance_id).filter(title=f"{title}/{title+1}").exists():
            raise forms.ValidationError(f"Учебный год {title}/{title+1} уже существует.")

      return title

    def save(self, commit=True):
        instance = super().save(commit=False)
        title = self.cleaned_data['title']
        instance.title = f"{title}/{int(title)+1}"
        if commit:
            instance.save()
        return instance