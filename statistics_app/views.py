from django.shortcuts import render
from core_app.models import (
    Text,
    Token,
    PosTag,
    Error,
    ErrorToken,
    ErrorTag,
    Group,
    AcademicYear,
    TextType,
    Student,
    Sentence,
    User,
)


def statistics_view(request):
    groups = (
        Group.objects.select_related("idayear")
        .all()
        .values("idgroup", "groupname", "idayear__title")
        .distinct()
    )
    group_data = [
        {
            "id": group["idgroup"],
            "name": group["groupname"],
            "year": group["idayear__title"],
        }
        for group in groups
    ]

    group_id = ""

    context = {
        "groups": group_data,
        "selected_group": group_id
    }

    return render(request, "statistics_app/statistics.html", context)



def error_stats(request):
    return render(request, "statistics_app/error_stats.html")