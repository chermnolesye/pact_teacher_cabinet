from django import forms
from core_app.models import User, Student, Group, Rights
from datetime import date

class AddStudentForm(forms.Form):
    lastname = "d"

class EditStudentForm(forms.ModelForm):
    GENDER_CHOICES = (
        (True, 'Мужской'),
        (False, 'Женский'),
    )

    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        label='Пол'
    )

    class Meta:
        model = User
        fields = ['lastname', 'firstname', 'middlename', 'birthdate', 'gender']
        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'lastname': 'Фамилия',
            'firstname': 'Имя',
            'middlename': 'Отчество',
            'birthdate': 'Дата рождения'
        }