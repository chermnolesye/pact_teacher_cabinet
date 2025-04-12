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
        if value is not None and value < 0:
            raise forms.ValidationError('Самооценка не может быть отрицательной.')
        return value

    def clean_selfassesment(self):
        value = self.cleaned_data.get('selfassesment')
        if value is not None and value < 0:
            raise forms.ValidationError('Оценка не может быть отрицательной.')
        return value