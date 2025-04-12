from django import forms
from core_app.models import User, Student, Group, Rights
from datetime import date
from core_app.models import Text, TextType, WritePlace, WriteTool, Emotion, Group, Student

class TeacherLoadTextForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label="Группа")
    student = forms.ModelChoiceField(queryset=Student.objects.none(), required=True, label="Студент")
    createdate = forms.DateField(initial=date.today(), required=True, widget=forms.SelectDateWidget, label="Дата создания")

    class Meta:
        model = Text
        fields = [
            'header',         # Название текста
            'text',           # Сам текст
            'createdate',     # Дата создания
            'idtexttype',     # Тип текста
            'idemotion',      # Эмоция
            'idwriteplace',   # Место написания
            'idwritetool',    # Инструмент написания
            'educationlevel', # Год изучения языка
            'selfrating',     # Самооценка
            'selfassesment',  # Оценка
        ]

    def __init__(self, *args, **kwargs):
        super(TeacherLoadTextForm, self).__init__(*args, **kwargs)

        if 'educationlevel' in self.initial:
            self.fields['educationlevel'].initial = self.initial['educationlevel']
            self.fields['educationlevel'].widget.attrs['readonly'] = 'readonly'  
        self.fields['selfrating'].widget.attrs['min'] = '1'  
        self.fields['selfassesment'].widget.attrs['min'] = '1'  

    def clean_selfrating(self):
        """Проверяем самооценку на отрицательные значения"""
        value = self.cleaned_data.get('selfrating')
        if value is not None and value < 0:
            raise forms.ValidationError('Самооценка не может быть отрицательной.')
        return value

    def clean_selfassesment(self):
        """Проверяем оценку на отрицательные значения"""
        value = self.cleaned_data.get('selfassesment')
        if value is not None and value < 0:
            raise forms.ValidationError('Оценка не может быть отрицательной.')
        return value