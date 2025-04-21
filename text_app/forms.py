from django import forms
from core_app.models import User, Student, Group, Rights
from datetime import date
from core_app.models import Text, TextType, WritePlace, WriteTool, Emotion, Group, Student, Error, ErrorTag, ErrorLevel, Reason

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
        initial=date.today,
        widget=forms.SelectDateWidget,
        label="Дата создания"
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
        if 'group' in self.data:
            try:
                group_id = int(self.data.get('group'))
                self.fields['student'].queryset = Student.objects.filter(idgroup=group_id)
            except (ValueError, TypeError):
                self.fields['student'].queryset = Student.objects.none()

    def clean_selfrating(self):
        value = self.cleaned_data.get('selfrating')
        if value is not None:
            if value < 1:
                raise forms.ValidationError('Самооценка не может быть меньше 1.')
            if value > 10:
                raise forms.ValidationError('Самооценка не может быть больше 10.')
        return value

    def clean_selfassesment(self):
        value = self.cleaned_data.get('selfassesment')
        if value is not None:
            if value < 1:
                raise forms.ValidationError('Оценка не может быть меньше 1.')
            if value > 10:
                raise forms.ValidationError('Оценка не может быть больше 10.')
        return value

    selfrating = forms.IntegerField(
        label="Самооценка",
        min_value=1,
        max_value=10,
        required=True,
        widget=forms.NumberInput(attrs={'min': 1, 'max': 10, 'step': 1})  
    )

    selfassesment = forms.IntegerField(
        label="Оценка",
        min_value=1,
        max_value=10,
        required=True,
        widget=forms.NumberInput(attrs={'min': 1, 'max': 10, 'step': 1}) 
    )


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
        required=True
    )

    comment = forms.CharField(
        label="Комментарий",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

    class Meta:
        model = Error
        fields = ['iderrortag', 'idreason', 'iderrorlevel', 'comment']

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
