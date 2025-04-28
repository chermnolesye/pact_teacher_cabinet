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
    ErrorLevel,
)

import numpy as np
import scipy
import pandas as pd
import math

from django.db.models import Count, Value, F, Q, IntegerField


def get_levels_dfs(v, level, max_level, h, tags):
    h[v] = 1
    level += 1

    for i in range(len(tags)):
        if tags[i]["idtagparent"] == tags[v]["iderrortag"] and h[i] == 0:
            max_level = get_levels_dfs(i, level, max_level, h, tags)

    if max_level < level:
        max_level = level

    return max_level


def get_levels():
    # Получаем все теги (ErrorTag) с их родителями
    tags = list(ErrorTag.objects.values("iderrortag", "idtagparent"))

    n = len(tags)
    h = [0 for _ in range(n)]  # Вспомогательный массив для хранения высоты каждого узла
    max_level = 0  # Максимальная глубина дерева тегов

    for i in range(n):
        # Если тег ещё не посещён и он корневой (нет родителя)
        if h[i] == 0 and tags[i]["idtagparent"] is None:
            level = get_levels_dfs(i, 0, -1, h, tags)
            if level > max_level:
                max_level = level

    levels = []
    for i in range(max_level):
        if i == 0:
            levels.append({"id_level": i, "level_text": f"{i} - верхний уровень"})
        elif i == max_level - 1:
            levels.append({"id_level": i, "level_text": f"{i} - нижний уровень"})
        else:
            levels.append({"id_level": i, "level_text": f"{i} - подуровень {i}"})

    return levels


def get_texts_id_keys(data_count, texts_id):
    """Создаёт словарь: {id тега: [id текстов]}"""
    for data in data_count:
        if data["iderrortag"] not in texts_id:
            texts_id[data["iderrortag"]] = []
    return texts_id


def get_texts_id_and_data_on_tokens(data_count, texts_id, id_data):
    """Заполняет texts_id и объединяет ошибки по id_data"""
    data_count_on_tokens = []
    id_data_count_on_tokens = []

    for data in data_count:
        if data["iderror__idtext"] not in texts_id[data["iderrortag"]]:
            texts_id[data["iderrortag"]].append(data["iderror__idtext"])

        if data[id_data] not in id_data_count_on_tokens:
            id_data_count_on_tokens.append(data[id_data])
            del data["iderror__idtext"]
            data_count_on_tokens.append(data)
        else:
            idx = 0
            while data_count_on_tokens[idx][id_data] != data[id_data]:
                idx += 1
            data_count_on_tokens[idx]["count_data"] += data["count_data"]

    return data_count_on_tokens, texts_id


def get_on_tokens(texts_id, data_count):
    """Считает процент ошибок на 100 токенов"""
    count_tokens = {}

    for tag_id in texts_id.keys():
        count_tokens_tag = Token.objects.filter(
            idsentence__idtext__in=texts_id[tag_id]
        ).aggregate(res=Count("idsentence__idtext"))
        count_tokens[tag_id] = count_tokens_tag["res"]

    for data in data_count:
        if count_tokens.get(data["iderrortag"], 0):
            data["count_data_on_tokens"] = (
                data["count_data"] * 100 / count_tokens[data["iderrortag"]]
            )
        else:
            data["count_data_on_tokens"] = 0

    return data_count


def get_data_on_tokens(data_count, id_data, is_unique_data, is_for_one_group):
    """Основная обработка данных по токенам"""
    texts_id = get_texts_id_keys(data_count, {})

    if is_for_one_group:
        count_errors = 0

        for data in data_count:
            if data["iderror__idtext"] not in texts_id[data["iderrortag"]]:
                texts_id[data["iderrortag"]].append(data["iderror__idtext"])
            count_errors += data["count_data"]

        count_tokens = {}
        for tag_id in texts_id.keys():
            count_tokens_tag = Token.objects.filter(
                idsentence__idtext__in=texts_id[tag_id]
            ).aggregate(res=Count("idsentence__idtext"))
            count_tokens[tag_id] = count_tokens_tag["res"]

        if count_tokens.get(data_count[0]["iderrortag"], 0):
            data_count[0]["count_data_on_tokens"] = (
                count_errors * 100 / count_tokens[data_count[0]["iderrortag"]]
            )
        else:
            data_count[0]["count_data_on_tokens"] = 0

        data_count[0]["count_data"] = count_errors

        return [data_count[0]]

    if is_unique_data:
        data_count_on_tokens, texts_id = get_texts_id_and_data_on_tokens(
            data_count, texts_id, id_data
        )
        data_count_on_tokens = get_on_tokens(texts_id, data_count_on_tokens)
        return data_count_on_tokens

    for data in data_count:
        count_tokens = Token.objects.filter(
            idsentence__idtext=data["iderror__idtext"]
        ).aggregate(res=Count("idsentence__idtext"))
        if count_tokens["res"]:
            data["count_data_on_tokens"] = (
                data["count_data"] * 100 / count_tokens["res"]
            )
        else:
            data["count_data_on_tokens"] = 0

    return data_count


def get_data_errors_dfs(v, d, d_on_tokens, level, level_input, h, flags_levels, data):
    """DFS для суммирования ошибок по иерархии тегов"""
    h[v] = 1
    level += 1

    for i in range(len(data)):
        if data[i]["idtagparent"] == data[v]["iderrortag"] and h[i] == 0:
            c, c_on_tokens = get_data_errors_dfs(
                i, d, d_on_tokens, level, level_input, h, flags_levels, data
            )
            d = c
            d_on_tokens = c_on_tokens

    if level > level_input:
        return data[v]["count_data"] + d, data[v]["count_data_on_tokens"] + d_on_tokens
    else:
        flags_levels[v] = True
        data[v]["count_data"] += d
        data[v]["count_data_on_tokens"] += d_on_tokens
        return 0, 0


def get_data_errors(data_count_errors, level, is_sorted):
    """Финальная сборка статистики по ошибкам"""
    # Extract error tag IDs from input data
    list_tags_id_in_markup = [data["iderrortag"] for data in data_count_errors]

    # Query tags not in data_count_errors, avoiding field name conflicts
    data_tags_not_in_errors = list(
        ErrorTag.objects.annotate(
            tag_id=F("iderrortag"),  # Use distinct name to avoid conflict
            parent_id=F("idtagparent"),
            text=F("tagtext"),
            text_russian=F("tagtextrussian"),
        )
        .values("tag_id", "parent_id", "text", "text_russian")
        .filter(~Q(iderrortag__in=list_tags_id_in_markup))
        .annotate(
            count_data=Value(0, output_field=IntegerField()),
            count_data_on_tokens=Value(0, output_field=IntegerField()),
        )
    )

    # Combine input data with zero-count tags, renaming keys for consistency
    data = [
        {
            "iderrortag": item.get("iderrortag", item["tag_id"]),
            "idtagparent": item.get("idtagparent", item.get("parent_id")),
            "tagtext": item.get("tagtext", item.get("text")),
            "tagtextrussian": item.get("tagtextrussian", item.get("text_russian")),
            "count_data": item["count_data"],
            "count_data_on_tokens": item.get("count_data_on_tokens", 0),
        }
        for item in data_count_errors + data_tags_not_in_errors
    ]

    # Hierarchical grouping using DFS
    n = len(data)
    h = [0] * n  # Height/depth tracker
    flags_levels = [False] * n  # Flags for level inclusion

    for i in range(n):
        if h[i] == 0 and data[i]["idtagparent"] is None:
            get_data_errors_dfs(i, 0, 0, -1, level, h, flags_levels, data)

    # Collect grouped data
    data_grouped = []
    for i in range(n):
        if flags_levels[i]:
            if data[i]["idtagparent"] is None:
                data[i]["idtagparent"] = -1
            data_grouped.append(data[i])

    # Sort data based on is_sorted flag
    if is_sorted:
        data = sorted(data_grouped, key=lambda d: d["count_data"], reverse=True)
    else:
        data = sorted(data_grouped, key=lambda d: d["iderrortag"])

    return data


def get_enrollment_date(list_filters):
    group = list_filters["group"]
    text = list_filters.get("text")
    text_type = list_filters.get("text_type")

    query = Group.objects.filter(groupname=group)

    if text and text_type:
        query = query.filter(
            student__text__header=text,
            student__text__idtexttype__texttypename=text_type,
            student__text__errorcheckflag=True,
        )
    elif text:
        query = query.filter(
            student__text__header=text, student__text__errorcheckflag=True
        )
    elif text_type:
        query = query.filter(
            student__text__idtexttype__texttypename=text_type,
            student__text__errorcheckflag=True,
        )
    else:
        query = query.filter(student__text__errorcheckflag=True)

    enrollment_dates = (
        query.values("idayear__title").distinct().order_by("idayear__title")
    )

    formatted_dates = []
    for date in enrollment_dates:
        year = date["idayear__title"]
        start_year = year.split("/")[0]
        end_year = str(int(start_year) + 1)
        formatted_dates.append({"enrollment_date": f"{start_year} \\ {end_year}"})

    return formatted_dates


def get_filters_for_choice_all(list_filters):
    text = list_filters.get("text")
    text_type = list_filters.get("text_type")

    if text_type:
        texts = list(
            Text.objects.filter(errorcheckflag=True, idtexttype__texttypename=text_type)
            .values("header")
            .distinct()
            .order_by("header")
        )
    else:
        texts = list(
            Text.objects.filter(errorcheckflag=True)
            .values("header")
            .distinct()
            .order_by("header")
        )

    if text:
        text_types = list(
            TextType.objects.filter(text__errorcheckflag=True, text__header=text)
            .values()
            .distinct()
            .order_by("idtexttype")
        )
    else:
        text_types = list(
            TextType.objects.filter(text__errorcheckflag=True)
            .values()
            .distinct()
            .order_by("idtexttype")
        )

    return texts, text_types


def get_filters_for_choice_group(list_filters):
    group = list_filters["group"]
    text = list_filters.get("text")
    text_type = list_filters.get("text_type")
    enrollment_date = list_filters["enrollment_date"]

    start_year = enrollment_date.split(" \\ ")[0]
    academic_year_title = f"{start_year}/{int(start_year) + 1}"

    group_obj = Group.objects.get(groupname=group, idayear__title=academic_year_title)

    if text_type:
        texts = list(
            Text.objects.filter(
                errorcheckflag=True,
                idstudent__idgroup=group_obj,
                idtexttype__texttypename=text_type,
            )
            .values("header")
            .distinct()
            .order_by("header")
        )
    else:
        texts = list(
            Text.objects.filter(errorcheckflag=True, idstudent__idgroup=group_obj)
            .values("header")
            .distinct()
            .order_by("header")
        )

    if text:
        text_types = list(
            TextType.objects.filter(
                text__errorcheckflag=True,
                text__idstudent__idgroup=group_obj,
                text__header=text,
            )
            .values()
            .distinct()
            .order_by("idtexttype")
        )
    else:
        text_types = list(
            TextType.objects.filter(
                text__errorcheckflag=True, text__idstudent__idgroup=group_obj
            )
            .values()
            .distinct()
            .order_by("idtexttype")
        )

    return texts, text_types


def get_filters_for_choice_student(list_filters):
    surname = list_filters["surname"]
    name = list_filters["name"]
    text = list_filters.get("text")  # Опционально
    text_type = list_filters.get("text_type")  # Опционально

    # Базовый фильтр для студента через модель User (только фамилия и имя)
    user_filter = Q(idstudent__iduser__lastname=surname) & Q(
        idstudent__iduser__firstname=name
    )

    # Получение типов текстов
    if text:
        text_types = list(
            TextType.objects.filter(
                text__errorcheckflag=True, text__header=text, **user_filter
            )
            .values()
            .distinct()
            .order_by("idtexttype")
        )
    else:
        text_types = list(
            TextType.objects.filter(text__errorcheckflag=True, **user_filter)
            .values()
            .distinct()
            .order_by("idtexttype")
        )

    # Получение текстов (только заголовок)
    if text_type:
        texts = list(
            Text.objects.filter(
                errorcheckflag=True, idtexttype__texttypename=text_type, **user_filter
            )
            .values("header")
            .distinct()
            .order_by("header")
        )
    else:
        texts = list(
            Text.objects.filter(errorcheckflag=True, **user_filter)
            .values("header")
            .distinct()
            .order_by("header")
        )

    return texts, text_types


# Функция для фильтрации текстов и типов текстов по курсу
def get_filters_for_choice_course(list_filters):
    course = list_filters["course"]
    text = list_filters.get("text")  # Опционально
    text_type = list_filters.get("text_type")  # Опционально

    # Получение текстов (только заголовок)
    if text_type:
        texts = list(
            Text.objects.filter(
                errorcheckflag=True,
                idstudent__idgroup__studycourse=course,
                idtexttype__texttypename=text_type,
            )
            .values("header")
            .distinct()
            .order_by("header")
        )
    else:
        texts = list(
            Text.objects.filter(
                errorcheckflag=True, idstudent__idgroup__studycourse=course
            )
            .values("header")
            .distinct()
            .order_by("header")
        )

    # Получение типов текстов
    if text:
        text_types = list(
            TextType.objects.filter(
                text__errorcheckflag=True,
                text__idstudent__idgroup__studycourse=course,
                text__header=text,
            )
            .values()
            .distinct()
            .order_by("idtexttype")
        )
    else:
        text_types = list(
            TextType.objects.filter(
                text__errorcheckflag=True, text__idstudent__idgroup__studycourse=course
            )
            .values()
            .distinct()
            .order_by("idtexttype")
        )

    return texts, text_types


# Функция для фильтрации групп, курсов и типов текстов по различным параметрам
def get_filters_for_choice_text(list_filters):
    group = list_filters.get("group")
    date = list_filters.get("enrollment_date")
    surname = list_filters.get("surname")
    name = list_filters.get("name")
    course = list_filters.get("course")
    text = list_filters.get("text")
    text_type = list_filters.get("text_type")
    emotion = list_filters.get("emotion", "")
    self_rating = list_filters.get("self_rating", "")

    # Преобразование даты поступления в заголовок учебного года
    academic_year_title = None
    if date:
        start_year = date.split(" \\ ")[0]
        academic_year_title = f"{start_year}/{int(start_year) + 1}"

    # Базовый фильтр для типов текстов
    text_type_filter = Q(text__errorcheckflag=True)

    # Применение фильтров на основе параметров
    if group and academic_year_title:
        text_type_filter &= Q(text__idstudent__idgroup__groupname=group) & Q(
            text__idstudent__idgroup__idayear__title=academic_year_title
        )
    elif surname and name:
        user_filter = Q(text__idstudent__iduser__lastname=surname) & Q(
            text__idstudent__iduser__firstname=name
        )
        text_type_filter &= user_filter
    elif course:
        text_type_filter &= Q(text__idstudent__idgroup__studycourse=course)

    if text:
        text_type_filter &= Q(text__header=text)
    if emotion:
        text_type_filter &= Q(text__idemotion__emotionname=emotion)
    if self_rating:
        text_type_filter &= Q(text__selfrating=self_rating)

    text_types = list(
        TextType.objects.filter(text_type_filter)
        .values()
        .distinct()
        .order_by("idtexttype")
    )

    # Базовый фильтр для групп и курсов
    group_filter = Q(student__text__errorcheckflag=True)
    if text:
        group_filter &= Q(student__text__header=text)
    if text_type:
        group_filter &= Q(student__text__idtexttype__texttypename=text_type)
    if emotion:
        group_filter &= Q(student__text__idemotion__emotionname=emotion)
    if self_rating:
        group_filter &= Q(student__text__selfrating=self_rating)

    # Получение групп (только название группы)
    groups = list(
        Group.objects.filter(group_filter)
        .values("groupname")
        .distinct()
        .order_by("groupname")
    )

    # Получение курсов (только номер курса)
    courses = list(
        Group.objects.filter(group_filter, studycourse__gt=0)
        .values("studycourse")
        .distinct()
        .order_by("studycourse")
    )

    return groups, courses, text_types


def get_filters_for_choice_text_type(list_filters):
    # Extract parameters from the input dictionary with .get() to handle missing keys
    group = list_filters.get("group")
    date = list_filters.get("enrollment_date")
    surname = list_filters.get("surname")
    name = list_filters.get("name")
    course = list_filters.get("course")
    text_type = list_filters.get("text_type")
    text = list_filters.get("text")
    emotion = list_filters.get("emotion", "")
    self_rating = list_filters.get("self_rating", "")

    # Convert enrollment date to academic year title (e.g., "2023/2024")
    academic_year_title = None
    if date:
        start_year = date.split(" \\ ")[0]
        academic_year_title = f"{start_year}/{int(start_year) + 1}"

    # Base filter for texts: only those with errorcheckflag=True
    text_filter = Q(errorcheckflag=True)

    # Apply filters based on provided parameters
    if group and academic_year_title:
        text_filter &= Q(idstudent__idgroup__groupname=group) & Q(
            idstudent__idgroup__idayear__title=academic_year_title
        )
    elif surname and name:
        text_filter &= Q(idstudent__iduser__lastname=surname) & Q(
            idstudent__iduser__firstname=name
        )
    elif course:
        text_filter &= Q(idstudent__idgroup__studycourse=course)

    if text_type:
        text_filter &= Q(idtexttype__texttypename=text_type)
    if text:
        text_filter &= Q(header=text)
    if emotion:
        text_filter &= Q(idemotion__emotionname=emotion)
    if self_rating:
        text_filter &= Q(selfrating=self_rating)

    texts = list(
        Text.objects.filter(text_filter).values("header").distinct().order_by("header")
    )

    # Base filter for groups and courses
    group_filter = Q(student__text__errorcheckflag=True)
    if text:
        group_filter &= Q(student__text__header=text)
    if text_type:
        group_filter &= Q(student__text__idtexttype__texttypename=text_type)
    if emotion:
        group_filter &= Q(student__text__idemotion__emotionname=emotion)
    if self_rating:
        group_filter &= Q(student__text__selfrating=self_rating)

    # Retrieve distinct group names
    groups = list(
        Group.objects.filter(group_filter)
        .values("groupname")
        .distinct()
        .order_by("groupname")
    )

    # Retrieve distinct course numbers (excluding 0)
    courses = list(
        Group.objects.filter(group_filter, studycourse__gt=0)
        .values("studycourse")
        .distinct()
        .order_by("studycourse")
    )

    return groups, courses, texts


def get_zero_count_grade_errors(data_count_errors):
    # Extract error level IDs from the input data
    list_grades_id_in_markup = [
        data["errorlevel__iderrorlevel"] for data in data_count_errors
    ]

    # Fetch error levels not in the markup, annotating with zero counts
    data_grades_not_in_errors = list(
        ErrorLevel.objects.filter(~Q(iderrorlevel__in=list_grades_id_in_markup))
        .annotate(
            errorlevel__iderrorlevel=F("iderrorlevel"),
            errorlevel__errorlevelname=F("errorlevelname"),
        )
        .values("errorlevel__iderrorlevel", "errorlevel__errorlevelname")
        .annotate(
            count_data=Value(0, output_field=IntegerField()),
            count_data_on_tokens=Value(0, output_field=IntegerField()),
        )
    )

    # Combine original data with zero-count entries
    data = data_count_errors + data_grades_not_in_errors
    return data


def get_tag_children(tag_parent):
    tags = list(
        ErrorTag.objects.values("iderrortag", "idtagparent").order_by("iderrortag")
    )
    grouped_tags = [tag_parent]

    for tag_in_group in grouped_tags:
        for tag in tags:
            if tag["idtagparent"] == tag_in_group:
                grouped_tags.append(tag["iderrortag"])

    return grouped_tags


def get_dict_children():
    tag_parents = list(
        ErrorTag.objects.values("iderrortag", "tagtext", "tagtextrussian")
        .filter(idtagparent__isnull=True)
        .order_by("iderrortag")
    )

    dict_children = {}
    for tag in tag_parents:
        grouped_tags = get_tag_children(tag["iderrortag"])
        dict_children[tag["iderrortag"]] = grouped_tags

    return tag_parents, dict_children


def get_stat(
    data_relation,
    param_one_text,
    param_one_name,
    param_two_text,
    param_two_name,
    is_emotion,
):
    # Retrieve assessment types from the new Text model
    asses_types = Text.TASK_RATES

    # Retrieve emotions from the new Emotion model
    list_emotions = list(Emotion.objects.values("idemotion", "emotionname"))

    # Initialize data structures
    param_one = []
    param_two = []

    # Populate param_one and param_two with data from data_relation
    for data in data_relation:
        param_one.append(data[param_one_text])
        param_two.append(data[param_two_text])

    # Convert to numpy arrays
    param_one = np.array(param_one)
    param_two = np.array(param_two)

    # Create contingency table
    contingency_table = pd.crosstab(param_one, param_two, dropna=False, margins=True)

    # Get dimensions
    num_rows = len(contingency_table) - 1
    num_col = len(contingency_table.columns) - 1
    N = contingency_table["All"].iloc[num_rows]

    # Initialize expected values array
    except_values = np.zeros((num_rows, num_col))

    # Prepare data for output
    data = []
    for row in range(num_rows):
        row_name = contingency_table.index[row]

        if is_emotion:
            # Find emotion name based on idemotion
            emotion = next(
                (
                    item["emotionname"]
                    for item in list_emotions
                    if item["idemotion"] == row_name
                ),
                "",
            )
            for col in range(num_col):
                count = contingency_table.iloc[row, col]
                col_name = contingency_table.columns[col]
                dict_item = {
                    param_one_text: int(row_name),
                    param_two_text: int(col_name),
                    param_one_name: emotion,
                    param_two_name: asses_types[col_name - 1][
                        1
                    ],  # Assuming asses_types is 1-indexed
                    "count": int(count),
                }
                data.append(dict_item)
                except_values[row][col] = (
                    contingency_table.iloc[row, num_col]
                    * contingency_table.iloc[num_rows, col]
                    / N
                )
        else:
            for col in range(num_col):
                count = contingency_table.iloc[row, col]
                col_name = contingency_table.columns[col]
                dict_item = {
                    param_one_text: int(row_name),
                    param_two_text: int(col_name),
                    param_one_name: asses_types[row_name - 1][
                        1
                    ],  # Assuming asses_types is 1-indexed
                    param_two_name: asses_types[col_name - 1][1],
                    "count": int(count),
                }
                data.append(dict_item)
                except_values[row][col] = (
                    contingency_table.iloc[row, num_col]
                    * contingency_table.iloc[num_rows, col]
                    / N
                )

    # Calculate the percentage of expected values less than 5
    count_less_than_5 = np.sum(except_values < 5)
    per_less = (
        (count_less_than_5 / (num_rows * num_col)) * 100
        if num_rows * num_col > 0
        else 0
    )

    # Determine the statistical test
    n = len(param_one)
    relation = {}
    data_fisher = []
    critical_stat_level = 0.05
    method = "Pirson"

    if n < 2:
        relation = {"res": "-", "stat": "-", "pvalue": "-", "N": n}
    else:
        if N <= 20 or per_less > 20:
            # Use Fisher's exact test for small samples or many small expected values
            sum_0_0 = sum_0_1 = sum_1_0 = sum_1_1 = 0

            for row in range(num_rows):
                row_name = contingency_table.index[row]
                for col in range(num_col):
                    count = contingency_table.iloc[row, col]
                    col_name = contingency_table.columns[col]
                    if is_emotion:
                        if row_name in [3, 5]:  # Assuming these are negative emotions
                            if col_name > 7:  # Assuming >7 is successful
                                sum_0_0 += count
                            else:
                                sum_0_1 += count
                        else:
                            if col_name > 7:
                                sum_1_0 += count
                            else:
                                sum_1_1 += count
                    else:
                        if row_name > 7:  # Assuming >7 is successful
                            if col_name > 7:
                                sum_0_0 += count
                            else:
                                sum_0_1 += count
                        else:
                            if col_name > 7:
                                sum_1_0 += count
                            else:
                                sum_1_1 += count

            table = np.array([[sum_0_0, sum_0_1], [sum_1_0, sum_1_1]])
            result = scipy.stats.fisher_exact(table)
            method = "Fisher"

            # Prepare data_fisher
            if is_emotion:
                data_fisher.extend(
                    [
                        {
                            "param_one": 1,
                            "param_one_text": "Положительные",
                            "param_two": 2,
                            "param_two_text": "Успешно",
                            "count": int(table[0][0]),
                        },
                        {
                            "param_one": 2,
                            "param_one_text": "Отрицательные",
                            "param_two": 2,
                            "param_two_text": "Успешно",
                            "count": int(table[0][1]),
                        },
                        {
                            "param_one": 1,
                            "param_one_text": "Положительные",
                            "param_two": 1,
                            "param_two_text": "Не успешно",
                            "count": int(table[1][0]),
                        },
                        {
                            "param_one": 2,
                            "param_one_text": "Отрицательные",
                            "param_two": 1,
                            "param_two_text": "Не успешно",
                            "count": int(table[1][1]),
                        },
                    ]
                )
            else:
                data_fisher.extend(
                    [
                        {
                            "param_one": 1,
                            "param_one_text": "Успешно",
                            "param_two": 2,
                            "param_two_text": "Успешно",
                            "count": int(table[0][0]),
                        },
                        {
                            "param_one": 2,
                            "param_one_text": "Не успешно",
                            "param_two": 2,
                            "param_two_text": "Успешно",
                            "count": int(table[0][1]),
                        },
                        {
                            "param_one": 1,
                            "param_one_text": "Успешно",
                            "param_two": 1,
                            "param_two_text": "Не успешно",
                            "count": int(table[1][0]),
                        },
                        {
                            "param_one": 2,
                            "param_one_text": "Не успешно",
                            "param_two": 1,
                            "param_two_text": "Не успешно",
                            "count": int(table[1][1]),
                        },
                    ]
                )
        else:
            # Use chi-square test
            result = scipy.stats.chi2_contingency(
                contingency_table.iloc[:-1, :-1]
            )  # Exclude margins

        # Handle statistic and p-value
        stat = (
            "Inf"
            if math.isinf(result.statistic)
            else "Nan"
            if math.isnan(result.statistic)
            else result.statistic
        )
        pvalue = result.pvalue

        # Determine relationship based on p-value
        if pvalue < critical_stat_level:
            relation = {
                "result": "связь между признаками есть, они не независимы",
                "stat": stat,
                "pvalue": pvalue,
                "N": n,
                "method": method,
            }
        else:
            relation = {
                "result": "связи между признаками нет, они независимы",
                "stat": stat,
                "pvalue": pvalue,
                "N": n,
                "method": method,
            }

    return data, relation, data_fisher
