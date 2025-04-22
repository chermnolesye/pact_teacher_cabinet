from django import forms
from core_app.models import Group, AcademicYear, Student
import datetime
from django.forms import formset_factory

class AddGroupForm(forms.ModelForm):
    idayear = forms.ModelChoiceField(
        queryset=AcademicYear.objects.all().order_by('-title'),
        label='Учебный год',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 2000,
            'max': 2100,
            'step': 1,
            'value': 2024
        }),
        empty_label=None  
    )

    class Meta:
        model = Group
        fields = ['groupname', 'studycourse', 'idayear']
        labels = {
            'groupname': 'Название группы',
            'studycourse': 'Номер курса',
            'idayear': 'Год обучения',
        }
        widgets = {
            'groupname': forms.TextInput(attrs={'class': 'form-control'}),
            'studycourse': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
                'step': 1,
                'value': 1
            }),
        }

    def clean_idayear(self):
        year = self.cleaned_data['idayear']
        return year
    
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

class AddStudentToGroupForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),  
        label="Добавить студента",
        to_field_name='idstudent',  
        empty_label="Выберите студента"  
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.all()
        self.fields['student'].widget = forms.Select(
            choices=[(student.idstudent, f"{student.get_full_name()} ({student.iduser.login})") for student in Student.objects.all()]
        )

# ФОРМА КАК В СТАРОМ ПАКТЕ - ВОЗМОЖНО, СРАБОТАЕТ
# def get_default_academic_year():
#     default = datetime.datetime.now()
#     if 0 < default.month < 9:
#         default_year = default.year - 1
#     else:
#         default_year = default.year
    
#     return f"{default_year}-{default_year + 1}"

# class AddGroupForm(forms.ModelForm):
#     idayear = forms.ModelChoiceField(
#         queryset=AcademicYear.objects.all().order_by('-title'),
#         label='Учебный год',
#         widget=forms.Select(attrs={
#             'class': 'form-control',
#         }),
#         empty_label=None,
#         initial=AcademicYear.objects.filter(title=get_default_academic_year()).first()  
#     )

#     class Meta:
#         model = Group
#         fields = ['groupname', 'studycourse', 'idayear']
#         labels = {
#             'groupname': 'Название группы',
#             'studycourse': 'Курс',
#             'idayear': 'Учебный год',
#         }
#         widgets = {
#             'groupname': forms.TextInput(attrs={'class': 'form-control'}),
#             'studycourse': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'min': 1,
#                 'max': 5,
#                 'step': 1,
#                 'value': 1
#             }),
#         }

#     def clean_idayear(self):
#         year = self.cleaned_data['idayear']
#         return year


# class AddGroupForm(forms.Form):
#     class Meta:
#         model = Group
#         fields = ['groupname', 'title', 'studycourse']
        
#     groupname = forms.CharField(label="Название группы", required=True)
#     studycourse = forms.IntegerField(label="Курс обучения", required = True, widget=forms.NumberInput(attrs={'id': 'studycourse'}), min_value=1, max_value=5)
#     current_year = datetime.datetime.now().year
#     title = forms.IntegerField(label="Учебный год", required=True, min_value=current_year, max_value=current_year+1, initial=current_year, widget=forms.NumberInput(attrs={'id': 'title'}))
#     title_2 = forms.CharField(initial=f"/ {current_year+1}", label="Учебный год конечный", widget=forms.TextInput(attrs={'id': 'title_2', 'readonly': 'readonly'})) # второе поле для конечного года    
#     idayear = forms.ModelChoiceField(label="Id года", required = False, widget=forms.HiddenInput(), queryset=AcademicYear.objects.all()) # для id FK
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         ###########
#         self.available_students = self.get_available_students()
#         self.initial_student_field_count = 1
        
#         for i in range(1, self.initial_student_field_count + 1):
#             self.fields[f'student_{i}'] = self.get_student_field(i)
        
    
#     def get_available_students(self):
#         students = Student.objects.filter(idgroup=81).select_related('iduser') #надо изменить id группы на что-то
#         return [(s.idstudent, f"{s.iduser.firstname} {s.iduser.lastname}  {s.iduser.middlename}") for s in students]

#     def get_student_field(self, index):
#         return forms.ChoiceField(
#             choices=[('', 'Выберите студента')] + self.available_students,
#             required=False,
#             label=f"Студент {index}"
#         )
#         ############
#     def clean(self):
#         cleaned_data = super().clean()
#         groupname = cleaned_data.get('groupname')
#         title = cleaned_data.get('title')
#         studycourse = cleaned_data.get('studycourse')

#         if groupname and title and studycourse:
#             current_year = datetime.datetime.now().year
#             if title < current_year:
#                 raise forms.ValidationError("Группу можно создавать только для текущего учебного года или последующих годов.")
#             try:
#                 academic_year = AcademicYear.objects.get(title__startswith=str(title))

#             except AcademicYear.DoesNotExist:
#                 academic_year = AcademicYear.objects.create(title=f"{title}/{title+1}")
#             cleaned_data['idayear'] = academic_year
#             ##########
#             selected_students = []
#             for field_name in self.fields:
#                 if field_name.startswith('student_'):
#                     student = cleaned_data.get(field_name)
#                     if student:
#                         selected_students.append(student)

#             if len(selected_students) != len(set(selected_students)):
#                 raise forms.ValidationError("Вы не можете выбрать одного и того же студента несколько раз.")
#             ############
#         return cleaned_data
    
#     def save(self):
#         if self.is_valid():
#             groupname = self.cleaned_data['groupname']
#             studycourse = self.cleaned_data['studycourse']
#             idayear = self.cleaned_data['idayear']
#             student_id = self.cleaned_data.get('student')
#             try:
#                 Group.objects.get(groupname=groupname, studycourse=studycourse, idayear=idayear)
#             except Group.DoesNotExist:
#                 group = group = Group.objects.create(groupname=groupname, studycourse=studycourse, idayear=idayear)
#                 ###########
#                 for field_name in self.fields:
#                     if field_name.startswith('student_'):
#                         student = self.cleaned_data.get(field_name)
#                         #student = form.cleaned_data.get('student')
#                         if student:
#                             try:
#                                 student = Student.objects.get(pk=student) #надо изменить id группы на что-то
#                                 student.idgroup = group
#                                 student.save()
#                             except:
#                                 raise forms.ValidationError("Такого судента нет")
#                 #########
#                 return group
#         return None



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