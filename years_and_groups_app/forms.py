from django import forms
from core_app.models import Group, AcademicYear, Student
import datetime
from django.forms import formset_factory

class AddGroupForm(forms.Form):
    class Meta:
        model = Group
        fields = ['groupname', 'title', 'studycourse']
        
    groupname = forms.CharField(label="Название группы", required=True)
    studycourse = forms.IntegerField(label="Курс обучения", required = True, widget=forms.NumberInput(attrs={'id': 'studycourse'}), min_value=1, max_value=4)
    current_year = datetime.datetime.now().year
    title = forms.IntegerField(label="Учебный год", required=True, min_value=current_year, max_value=current_year+1, initial=current_year, widget=forms.NumberInput(attrs={'id': 'title'}))
    title_2 = forms.CharField(initial=f"/ {current_year+1}", label="Учебный год конечный", widget=forms.TextInput(attrs={'id': 'title_2', 'readonly': 'readonly'})) # второе поле для конечного года    
    idayear = forms.ModelChoiceField(label="Id года", required = False, widget=forms.HiddenInput(), queryset=AcademicYear.objects.all()) # для id FK
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # students = Student.objects.filter(idgroup=47).select_related('iduser')
        # students_data = [
        #     {"id": s.idstudent, "name": f"{s.iduser.firstname} {s.iduser.lastname}"}
        #     for s in students
        # ]
        # self.fields['student'] = forms.TypedChoiceField(
        #     choices=[('', 'Выберите студента')] + students_data,
        #     coerce=int,  
        #     empty_value=None,  
        #     required=False,
        #     label="Студент"
        # )
        # self.student_fields = []

    def clean(self):
        cleaned_data = super().clean()
        groupname = cleaned_data.get('groupname')
        title = cleaned_data.get('title')
        studycourse = cleaned_data.get('studycourse')

        if groupname and title and studycourse:
            current_year = datetime.datetime.now().year
            if title < current_year:
                raise forms.ValidationError("Группу можно создавать только для текущего учебного года или последующих годов.")
            try:
                academic_year = AcademicYear.objects.get(title__startswith=str(title))

            except AcademicYear.DoesNotExist:
                academic_year = AcademicYear.objects.create(title=f"{title}/{title+1}")
            cleaned_data['idayear'] = academic_year

            #selected_students = []
            # for field_name in self.student_fields:
            #     student = cleaned_data.get(field_name)
            #     if student:
            #         selected_students.append(student)

            # if len(selected_students) != len(set(selected_students)):
            #     raise forms.ValidationError("Вы не можете выбрать одного и того же студента несколько раз.")
        return cleaned_data
    
    def save(self):
        if self.is_valid():
            groupname = self.cleaned_data['groupname']
            studycourse = self.cleaned_data['studycourse']
            idayear = self.cleaned_data['idayear']

            group = group = Group.objects.create(groupname=groupname, studycourse=studycourse, idayear=idayear)
            # for field_name in self.student_fields:
            #     student = self.cleaned_data.get(field_name)
            #     student = form.cleaned_data.get('student')
            #     if student:
            #         student.idgroup = group
            #         student.save()
            return group
        return None



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
    

class EditGroupForm(forms.ModelForm):  
    class Meta:
        model = Group
        fields = ['groupname', 'title', 'studycourse']
        
    groupname = forms.CharField(label="Название группы", required=True)
    studycourse = forms.IntegerField(label="Курс обучения", required = True, widget=forms.NumberInput(attrs={'id': 'studycourse'}), min_value=1, max_value=4)
    current_year = datetime.datetime.now().year
    title = forms.IntegerField(label="Учебный год", required=True, min_value=current_year, max_value=current_year+1, initial=current_year, widget=forms.NumberInput(attrs={'id': 'title'}))
    title_2 = forms.CharField(initial=f"/ {current_year+1}", label="Учебный год конечный", widget=forms.TextInput(attrs={'id': 'title_2', 'readonly': 'readonly'})) # второе поле для конечного года    
    idayear = forms.ModelChoiceField(label="Id года", required = False, widget=forms.HiddenInput(), queryset=AcademicYear.objects.all()) # для id FK
    


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