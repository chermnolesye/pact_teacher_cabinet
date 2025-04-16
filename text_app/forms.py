from django import forms
from core_app.models import User, Student, Group, Rights
from datetime import date
from core_app.models import Text, TextType, WritePlace, WriteTool, Emotion, Group, Student

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

class AddTextAnnotationForm(forms.Form):
    text_grade = 1