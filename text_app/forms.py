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
