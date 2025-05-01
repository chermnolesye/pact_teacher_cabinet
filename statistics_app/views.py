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

from collections import defaultdict
from statistics_app import dashboards
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

    return render(request, "statistics.html", context)


##Пример для Юли
# <h1>Теги ошибок</h1>
# <ul>
#     {% for parent_tag, sub_tags in tags_error.items %}
#         <li>
#             <h2>{{ parent_tag }}</h2>
#             <ul>
#                 {% for tag in sub_tags %}
#                     <li style="background-color: {{ tag.color }}; padding: 5px; margin: 5px; border-radius: 5px;">
#                         <strong>{{ tag.nametag }}</strong> (ID: {{ tag.id }})<br>
#                         Уровень 1: {{ tag.level1 }}<br>
#                         Уровень 2: {{ tag.level2 }}<br>
#                         Уровень 3: {{ tag.level3 }}
#                     </li>
#                 {% endfor %}
#             </ul>
#         </li>
#     {% endfor %}
# </ul>


def error_stats(request):
    tags = ErrorTag.objects.all().values(
        "iderrortag",
        "tagtext",
        "tagtextrussian",
        "idtagparent",
    )

    # Считаем ошибки по тегу и уровню сложности
    error_counts = Error.objects.values("iderrortag", "iderrorlevel").annotate(
        count=Count("iderror")
    )

    # Карта: id тэга -> { уровень -> количество ошибок }
    error_count_map = defaultdict(lambda: defaultdict(int))
    for item in error_counts:
        tag_id = item["iderrortag"]
        level_id = item["iderrorlevel"]
        count = item["count"]
        error_count_map[tag_id][level_id] = count

    grouped_tags = defaultdict(list)

    for tag in tags:
        tag_id = tag["iderrortag"]
        tag_name = tag["tagtext"]
        parent_id = tag["idtagparent"]

        levels = error_count_map.get(tag_id, {})

        # Считаем активные уровни (где количество > 0)
        active_levels = [lvl for lvl, cnt in levels.items() if cnt > 0]
        num_active_levels = len(active_levels)

        # Определяем цвет
        if num_active_levels == 0 or num_active_levels == 1:
            color = "#ffffff"
        elif num_active_levels == 2:
            color = "#e8f0fe"
        else:
            color = "#cfe2ff"

        tag_info = {
            "id": tag_id,
            "nametag": tag_name,
            "color": color,
            "level1": levels.get(1, 0),
            "level2": levels.get(2, 0),
            "level3": levels.get(3, 0),
            "parent_id": parent_id,  # Добавляем информацию о родителе
        }

        if parent_id:
            parent_name = next(
                (t["tagtext"] for t in tags if t["iderrortag"] == parent_id), None
            )
            if parent_name:
                grouped_tags[parent_name].append(tag_info)
        else:
            grouped_tags[tag_name].append(tag_info)  # Родительские теги

    context = {"tags_error": dict(grouped_tags)}
    return render(request, "error_stats.html", context)


def chart_types_errors(request):
    if request.method != "POST":
        levels = dashboards.get_levels()

        groups = list(
            Group.objects.values("groupname", "idayear")
            .distinct()
            .order_by("groupname")
        )

        courses = list(
            Group.objects.values("studycourse", "idayear")
            .filter(studycourse__gt=0)
            .distinct()
            .order_by("studycourse")
        )

        texts = list(
            Text.objects.values("header")
            .filter(errorcheckflag=True)
            .distinct()
            .order_by("header")
        )

        text_types = list(
            TextType.objects.filter(text__errorcheckflag=True)
            .distinct()
            .order_by("idtexttype")
            .values()
        )

        # Подсчёт ошибок по тегам
        data_count_errors = list(
            ErrorToken.objects.values(
                "iderror__iderrortag__iderrortag",
                "iderror__iderrortag__idtagparent",
                "iderror__iderrortag__tagtext",
                "iderror__iderrortag__tagtextrussian",
                "iderror__iderrortag__tagcolor",
                "iderror__iderrortag__idtagparent",
            )
            .filter(
                Q(iderror__iderrortag__isnull=False)
                & Q(iderror__iderrorlevel__isnull=False)
                & Q(iderror__iderrorlevel__errorlevelvalue=1)
                & Q(iderror__iderrorlevel__isnull=False)
            )
            .annotate(count_data=Count("iderror__iderrortag"))
        )

        # Пересчёт процента ошибок на токены

        data_on_tokens = dashboards.get_data_on_tokens(
            data_count_errors,
            id_data="iderrortag",
            is_unique_data=True,
            is_for_one_group=False,
        )

        # Построение иерархии ошибок
        data = dashboards.get_data_errors(data_on_tokens, level=0, is_sorted=True)

        # Получение словарей родителей и детей тегов
        tag_parents, dict_children = dashboards.get_dict_children()

        return render(
            request,
            "dashboard_error_types.html",
            {
                "right": True,
                "levels": levels,
                "groups": groups,
                "courses": courses,
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

        if flag_post == "enrollment_date":
            enrollment_date = dashboards.get_enrollment_date(list_filters)
            return JsonResponse({"enrollment_date": enrollment_date}, status=200)

        if flag_post == "choice_all":
            texts, text_types = dashboards.get_filters_for_choice_all(list_filters)
            return JsonResponse({"texts": texts, "text_types": text_types}, status=200)

        if flag_post == "choice_group":
            texts, text_types = dashboards.get_filters_for_choice_group(list_filters)
            return JsonResponse({"texts": texts, "text_types": text_types}, status=200)

        if flag_post == "choice_student":
            texts, text_types = dashboards.get_filters_for_choice_student(list_filters)
            return JsonResponse({"texts": texts, "text_types": text_types}, status=200)

        if flag_post == "choice_course":
            texts, text_types = dashboards.get_filters_for_choice_course(list_filters)
            return JsonResponse({"texts": texts, "text_types": text_types}, status=200)

        if flag_post == "choice_text":
            groups, courses, text_types = dashboards.get_filters_for_choice_text(
                list_filters
            )
            return JsonResponse(
                {"groups": groups, "courses": courses, "text_types": text_types},
                status=200,
            )

        if flag_post == "choice_text_type":
            groups, courses, texts = dashboards.get_filters_for_choice_text_type(
                list_filters
            )
            return JsonResponse(
                {"groups": groups, "courses": courses, "texts": texts}, status=200
            )

        if flag_post == "update_diagrams":
            group = list_filters.get("group")
            date = list_filters.get("enrollment_date")
            surname = list_filters.get("surname")
            name = list_filters.get("name")
            course = list_filters.get("course")
            text = list_filters.get("text")
            text_type = list_filters.get("text_type")
            level = int(list_filters.get("level", 0))

            academic_year_title = None
            if date:
                start_year = date.split(" \\ ")[0]
                academic_year_title = f"{start_year}/{int(start_year) + 1}"

            base_filter = Q(iderrortag__markuptype=1) & Q(
                idsentence__idtext__errorcheckflag=True
            )

            if surname and name and text and text_type:
                base_filter &= (
                    Q(idsentence__idtext__idstudent__iduser__lastname=surname)
                    & Q(idsentence__idtext__idstudent__iduser__firstname=name)
                    & Q(idsentence__idtext__header=text)
                    & Q(idsentence__idtext__idtexttype__texttypename=text_type)
                )
            elif surname and name and text:
                base_filter &= (
                    Q(idsentence__idtext__idstudent__iduser__lastname=surname)
                    & Q(idsentence__idtext__idstudent__iduser__firstname=name)
                    & Q(idsentence__idtext__header=text)
                )
            elif surname and name and text_type:
                base_filter &= (
                    Q(idsentence__idtext__idstudent__iduser__lastname=surname)
                    & Q(idsentence__idtext__idstudent__iduser__firstname=name)
                    & Q(idsentence__idtext__idtexttype__texttypename=text_type)
                )
            elif surname and name:
                base_filter &= Q(
                    idsentence__idtext__idstudent__iduser__lastname=surname
                ) & Q(idsentence__idtext__idstudent__iduser__firstname=name)
            elif course and text and text_type:
                base_filter &= (
                    Q(idsentence__idtext__idstudent__idgroup__studycourse=course)
                    & Q(idsentence__idtext__header=text)
                    & Q(idsentence__idtext__idtexttype__texttypename=text_type)
                )
            elif course and text:
                base_filter &= Q(
                    idsentence__idtext__idstudent__idgroup__studycourse=course
                ) & Q(idsentence__idtext__header=text)
            elif course and text_type:
                base_filter &= Q(
                    idsentence__idtext__idstudent__idgroup__studycourse=course
                ) & Q(idsentence__idtext__idtexttype__texttypename=text_type)
            elif course:
                base_filter &= Q(
                    idsentence__idtext__idstudent__idgroup__studycourse=course
                )
            elif group and text and text_type and academic_year_title:
                base_filter &= (
                    Q(idsentence__idtext__idstudent__idgroup__groupname=group)
                    & Q(
                        idsentence__idtext__idstudent__idgroup__idayear__title=academic_year_title
                    )
                    & Q(idsentence__idtext__header=text)
                    & Q(idsentence__idtext__idtexttype__texttypename=text_type)
                )
            elif group and text and academic_year_title:
                base_filter &= (
                    Q(idsentence__idtext__idstudent__idgroup__groupname=group)
                    & Q(
                        idsentence__idtext__idstudent__idgroup__idayear__title=academic_year_title
                    )
                    & Q(idsentence__idtext__header=text)
                )
            elif group and text_type and academic_year_title:
                base_filter &= (
                    Q(idsentence__idtext__idstudent__idgroup__groupname=group)
                    & Q(
                        idsentence__idtext__idstudent__idgroup__idayear__title=academic_year_title
                    )
                    & Q(idsentence__idtext__idtexttype__texttypename=text_type)
                )
            elif group and academic_year_title:
                base_filter &= Q(
                    idsentence__idtext__idstudent__idgroup__groupname=group
                ) & Q(
                    idsentence__idtext__idstudent__idgroup__idayear__title=academic_year_title
                )
            elif text and text_type:
                base_filter &= Q(idsentence__idtext__header=text) & Q(
                    idsentence__idtext__idtexttype__texttypename=text_type
                )
            elif text_type:
                base_filter &= Q(idsentence__idtext__idtexttype__texttypename=text_type)
            elif text:
                base_filter &= Q(idsentence__idtext__header=text)

            data_count_errors = list(
                Sentence.objects.filter(base_filter)
                .values(
                    "iderrortag__iderrortag",
                    "iderrortag__idtagparent",
                    "iderrortag__tagtext",
                    "iderrortag__tagtextrussian",
                    "idtext",
                )
                .annotate(count_data=Count("iderrortag__iderrortag"))
            )

            data_on_tokens = dashboards.get_data_on_tokens(
                data_count_errors, "iderrortag__iderrortag", None, True, False
            )
            data = dashboards.get_data_errors(data_on_tokens, level, True)

            return JsonResponse({"data_type_errors": data}, status=200)


from django.shortcuts import render
