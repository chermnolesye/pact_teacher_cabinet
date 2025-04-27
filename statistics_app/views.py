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
import dashboards

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Q
import json


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

    context = {"groups": group_data, "selected_group": group_id}

    return render(request, "statistics_app/statistics.html", context)


def error_stats(request):
    return render(request, "statistics_app/error_stats.html")


def chart_types_errors(request):
    if not (
        request.user.is_authenticated
        and hasattr(request.user, "idrights")
        and request.user.idrights.rightsname == "teacher"
    ):
        return render(request, "access_denied.html", status=403)

    if request.method != "POST":
        groups = list(
            Group.objects.values("groupname").distinct().order_by("groupname")
        )
        texts = list(
            Text.objects.filter(errorcheckflag=True)
            .values("header")
            .distinct()
            .order_by("header")
        )
        text_types = list(
            TextType.objects.filter(text__errorcheckflag=True)
            .distinct()
            .values("idtexttype", "texttypename")
            .order_by("idtexttype")
        )

        errors = Error.objects.filter(iderrorlevel__isnull=False).select_related(
            "iderrortag", "iderrorlevel"
        )

        data_count_errors = (
            errors.values(
                "iderrortag__iderrortag",
                "iderrortag__tagtext",
                "iderrortag__tagtextrussian",
            )
            .annotate(count_data=Count("iderrortag"))
            .order_by("iderrortag__iderrortag")
        )

        data_on_tokens = dashboards.get_data_on_tokens(
            data_count_errors, "tag__id_tag", "tag__tag_language", True, False
        )
        data = dashboards.get_data_errors(data_on_tokens, 0, True)

        ###########
        tag_parents, dict_children = dashboards.get_dict_children()

        data = list(data_count_errors)

        return render(
            request,
            "dashboard_error_types.html",
            {
                "right": True,
                "groups": groups,
                "texts": texts,
                "text_types": text_types,
                "data": data,
                "tag_parents": tag_parents,
                "dict_children": dict_children,
            },
        )
    else:
        list_filters = json.loads(request.body)
        flag_post = list_filters["flag_post"]

        if flag_post == "choice_all":
            texts = list(
                Text.objects.filter(errorcheckflag=True)
                .values("header")
                .distinct()
                .order_by("header")
            )
            text_types = list(
                TextType.objects.filter(text__errorcheckflag=True)
                .distinct()
                .values("idtexttype", "texttypename")
                .order_by("idtexttype")
            )
            return JsonResponse({"texts": texts, "text_types": text_types}, status=200)

        if flag_post == "update_diagrams":
            # Фильтры
            group = list_filters.get("group")
            surname = list_filters.get("surname")
            name = list_filters.get("name")
            patronymic = list_filters.get("patronymic")
            text = list_filters.get("text")
            text_type = list_filters.get("text_type")

            errors = Error.objects.filter(iderrorlevel__isnull=False)

            if surname and name:
                errors = errors.filter(
                    iderrortoken__idtoken__idsentence__idtext__idstudent__iduser__lastname__iexact=surname,
                    iderrortoken__idtoken__idsentence__idtext__idstudent__iduser__firstname__iexact=name,
                )
                if patronymic:
                    errors = errors.filter(
                        iderrortoken__idtoken__idsentence__idtext__idstudent__iduser__middlename__iexact=patronymic
                    )

            if text:
                errors = errors.filter(
                    iderrortoken__idtoken__idsentence__idtext__header__iexact=text
                )

            if text_type:
                errors = errors.filter(
                    iderrortoken__idtoken__idsentence__idtext__idtexttype=text_type
                )

            if group:
                errors = errors.filter(
                    iderrortoken__idtoken__idsentence__idtext__idstudent__idgroup__groupname__iexact=group
                )

            errors = errors.select_related("iderrortag", "iderrorlevel")

            data_count_errors = (
                errors.values(
                    "iderrortag__iderrortag",
                    "iderrortag__tagtext",
                    "iderrortag__tagtextrussian",
                )
                .annotate(count_data=Count("iderrortag"))
                .order_by("iderrortag__iderrortag")
            )

            data = list(data_count_errors)

            return JsonResponse({"data_type_errors": data}, status=200)

        return JsonResponse({"error": "Unknown flag_post"}, status=400)
