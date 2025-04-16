from django import forms
from core_app.models import User, Student, Group, Rights
from datetime import date

class AddStudentForm(forms.Form):
    lastname = "d"

class EditStudentForm(forms.Form):
    lastname = "d"