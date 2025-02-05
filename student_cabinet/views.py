from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from db_editor.models import AcademicYear  


@login_required
def academic_years(request):
    years = AcademicYear.objects.all()  
    return render(request, 'student_cabinet/academic_years.html', {'years': years})

