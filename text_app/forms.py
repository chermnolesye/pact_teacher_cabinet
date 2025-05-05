from django import forms
from core_app.models import ErrorTag, User, Student, Group, Rights
#from text_app.models import ErrorTagHierarcal
from datetime import date
from core_app.models import Text, TextType, WritePlace, WriteTool, Emotion, Group, Student, Error, ErrorTag, ErrorLevel, Reason
from django.utils.translation import gettext_lazy as _
#from mptt.forms import TreeNodeChoiceField

class TeacherLoadTextForm(forms.ModelForm):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="Группа"
    )
    student = forms.ModelChoiceField(
        queryset=Student.objects.none(),
        label="Студент"
    )
    createdate = forms.DateField(
        initial=date.today(),
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        ),
        label="Дата создания"
    )

    selfrating = forms.TypedChoiceField(
        choices=Text.TASK_RATES,
        coerce=int,
        label="Самооценка",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    selfassesment = forms.TypedChoiceField(
        choices=Text.RATES,
        coerce=int,
        label="Оценка",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Text
        fields = [
            'header',
            'text',
            'createdate',
            'idtexttype',
            'idemotion',
            'idwriteplace',
            'idwritetool',
            'educationlevel',
            'selfrating',      
            'selfassesment',   
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Если есть 'group' в данных (POST)
        if 'group' in self.data:
            try:
                group_id = int(self.data.get('group'))
                self.fields['student'].queryset = Student.objects.filter(idgroup=group_id)
                group = Group.objects.get(idgroup=group_id)
                self.initial['educationlevel'] = group.studycourse  
            except (ValueError, TypeError, Group.DoesNotExist):
                self.fields['student'].queryset = Student.objects.none()

        #Если есть student в initial (GET)
        elif 'student' in self.initial:
            try:
                student = Student.objects.select_related('idgroup').get(idstudent=self.initial['student'])
                self.fields['student'].queryset = Student.objects.filter(idgroup=student.idgroup)
                self.initial['group'] = student.idgroup.idgroup  
                self.initial['educationlevel'] = student.idgroup.studycourse  
            except Student.DoesNotExist:
                self.fields['student'].queryset = Student.objects.none()

        # По умолчанию 
        else:
            self.fields['student'].queryset = Student.objects.none()

        self.fields['student'].queryset = Student.objects.all().order_by('iduser__lastname')
        self.fields['student'].label_from_instance = lambda obj: obj.get_full_name()

class AddTextAnnotationForm(forms.ModelForm):
    textgrade = forms.ChoiceField(
        choices=Text.TASK_RATES,
        label="Оценка",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    completeness = forms.ChoiceField(
        choices=Text.TASK_RATES,
        label="Полнота раскрытия",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    structure = forms.ChoiceField(
        choices=Text.TASK_RATES,
        label="Структура",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    coherence = forms.ChoiceField(
        choices=Text.TASK_RATES,
        label="Связность",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    poscheckflag = forms.TypedChoiceField(
        choices=[(None, "Не указано"), (True, "Проверено")],
        coerce=lambda x: x == 'True',
        required=False,
        label="Проверка частеречной разметки"
    )

    errorcheckflag = forms.TypedChoiceField(
        choices=[(None, "Не указано"), (True, "Проверено")],
        coerce=lambda x: x == 'True',
        required=False,
        label="Проверка разметки ошибок"
    )

    class Meta:
        model = Text
        fields = [
            'textgrade',
            'completeness',
            'structure',
            'coherence',
            'poscheckflag',
            'errorcheckflag'
        ]

class AddErrorAnnotationForm(forms.ModelForm):
    iderrortag = forms.ModelChoiceField(
        queryset=ErrorTag.objects.all(),
        label="Выберите тег",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    idreason = forms.ModelChoiceField(
        queryset=Reason.objects.all(),
        label="Причина ошибки",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    iderrorlevel = forms.ModelChoiceField(
        queryset=ErrorLevel.objects.all(),
        label="Степень грубости",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    correct = forms.CharField(
        label="Исправление",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    comment = forms.CharField(
        label="Комментарий",
        widget=forms.Textarea(attrs={'class': 'form-control', "style": "height:50px; min-height:10px;"}),
        required=False
    )

    class Meta:
        model = Error
        fields = ['iderrortag', 'idreason', 'iderrorlevel', 'comment', 'correct']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def get_display_info(self):
        selected_tag = self.cleaned_data.get('iderrortag')
        creator_name = (
            f"{self.user.firstname} {self.user.lastname}"
            if self.user and hasattr(self.user, 'firstname') and hasattr(self.user, 'lastname')
            else "Неизвестный пользователь"
        )
        return {
            'selected_tag': selected_tag.tagtext if selected_tag else '',
            'creator': creator_name
        }
