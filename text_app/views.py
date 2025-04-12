from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import TeacherLoadTextForm
from nltk.tokenize import sent_tokenize, word_tokenize
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


def show_text_markup(request, text_id=2379):
    if text_id is not None:
        text = get_object_or_404(Text, idtext=text_id)
    else:
        text = Text.objects.first()

    sentences = text.sentence_set.all()
    sentence_data = []

    selected_markup = request.GET.get("markup", "tagtext")

    for sentence in sentences:
        tokens = Token.objects.filter(idsentence=sentence).select_related("idpostag")

        tokens_data = []
        for token in tokens:
            # Разметка для частей речи
            pos_tag = None
            pos_tag_russian = None
            pos_tag_abbrev = None
            pos_tag_color = None
            if token.idpostag:
                pos_tag = token.idpostag.tagtext
                pos_tag_russian = token.idpostag.tagtextrussian
                pos_tag_abbrev = token.idpostag.tagtextabbrev
                pos_tag_color = token.idpostag.tagcolor

            # Разметка для ошибок
            error_tokens = token.errortoken_set.select_related(
                "iderror__iderrortag", "iderror__iderrorlevel"
            ).all()

            errors_list = []
            for error_token in error_tokens:
                error = error_token.iderror
                if error and error.iderrortag:
                    errors_list.append(
                        {
                            "error_tag": error.iderrortag.tagtext,
                            "error_tag_russian": error.iderrortag.tagtextrussian,
                            "error_tag_abbrev": error.iderrortag.tagtextabbrev,
                            "error_color": error.iderrortag.tagcolor,
                            "error_level": error.iderrorlevel.errorlevelname
                            if error.iderrorlevel
                            else "Не указано",
                            "error_correct": error.correct
                            if error.correct
                            else "Не указано",
                            "error_comment": error.comment
                            if error.comment
                            else "Не указано",
                        }
                    )

            # Основная ошибка для отображения (первая)
            main_error = errors_list[0] if errors_list else {}

            tokens_data.append(
                {
                    "token": token.tokentext,
                    "pos_tag": pos_tag,
                    "pos_tag_russian": pos_tag_russian,
                    "pos_tag_abbrev": pos_tag_abbrev,
                    "pos_tag_color": pos_tag_color,
                    "error_tag": main_error.get("error_tag"),
                    "error_tag_russian": main_error.get("error_tag_russian"),
                    "error_tag_abbrev": main_error.get("error_tag_abbrev"),
                    "error_color": main_error.get("error_color"),
                    "error_level": main_error.get("error_level"),
                    "error_correct": main_error.get("error_correct"),
                    "error_comment": main_error.get("error_comment"),
                    "all_errors": errors_list,  # Все ошибки для токена
                }
            )

        sentence_data.append(
            {
                "sentence": sentence,
                "tokens": tokens_data,
            }
        )

    student = text.idstudent
    user = student.iduser
    group = student.idgroup
    academic_year = group.idayear
    text_type = text.idtexttype
    write_place = text.idwriteplace
    write_tool = text.idwritetool
    emotion = text.idemotion
    year_study_language = text.educationlevel
    self_rating = text.selfrating
    assesment = text.selfassesment

    context = {
        "text": text,
        "sentence_data": sentence_data,
        "selected_markup": selected_markup,
        "author": f"{user.lastname} {user.firstname}",
        "group": group.groupname,
        "academic_year": academic_year.title,
        "create_date": text.createdate,
        "write_place": write_place.writeplacename if write_place else "Не указано",
        "write_tool": write_tool.writetoolname if write_tool else "Не указано",
        "text_type": text_type.texttypename if text_type else "Не указано",
        "emotion": emotion.emotionname,
        "year_study_language": year_study_language
        if text_type == None
        else "Не указано",
        "self_rating": self_rating,
        "self_assesment": assesment,
    }

    return render(request, "show_text_markup.html", context)


def annotate_text(request, text_id=2379):
    text_id = request.GET.get('text_id')
    if text_id:
        text = get_object_or_404(Text, idtext=text_id)
    else:
        text = Text.objects.first()

    sentences = text.sentence_set.all()
    sentence_data = []

    selected_markup = request.GET.get("markup", "tagtext")

    for sentence in sentences:
        tokens = Token.objects.filter(idsentence=sentence).select_related("idpostag")

        tokens_data = []
        for token in tokens:
            # Разметка для частей речи
            pos_tag = None
            pos_tag_russian = None
            pos_tag_abbrev = None
            pos_tag_color = None
            if token.idpostag:
                pos_tag = token.idpostag.tagtext
                pos_tag_russian = token.idpostag.tagtextrussian
                pos_tag_abbrev = token.idpostag.tagtextabbrev
                pos_tag_color = token.idpostag.tagcolor

            # Разметка для ошибок
            error_tokens = token.errortoken_set.select_related(
                "iderror__iderrortag", "iderror__iderrorlevel"
            ).all()

            errors_list = []
            for error_token in error_tokens:
                error = error_token.iderror
                if error and error.iderrortag:
                    errors_list.append(
                        {
                            "error_tag": error.iderrortag.tagtext,
                            "error_tag_russian": error.iderrortag.tagtextrussian,
                            "error_tag_abbrev": error.iderrortag.tagtextabbrev,
                            "error_color": error.iderrortag.tagcolor,
                            "error_level": error.iderrorlevel.errorlevelname
                            if error.iderrorlevel
                            else "Не указано",
                            "error_correct": error.correct
                            if error.correct
                            else "Не указано",
                            "error_comment": error.comment
                            if error.comment
                            else "Не указано",
                        }
                    )

            # Основная ошибка для отображения (первая)
            main_error = errors_list[0] if errors_list else {}

            tokens_data.append(
                {
                    "token": token.tokentext,
                    "pos_tag": pos_tag,
                    "pos_tag_russian": pos_tag_russian,
                    "pos_tag_abbrev": pos_tag_abbrev,
                    "pos_tag_color": pos_tag_color,
                    "error_tag": main_error.get("error_tag"),
                    "error_tag_russian": main_error.get("error_tag_russian"),
                    "error_tag_abbrev": main_error.get("error_tag_abbrev"),
                    "error_color": main_error.get("error_color"),
                    "error_level": main_error.get("error_level"),
                    "error_correct": main_error.get("error_correct"),
                    "error_comment": main_error.get("error_comment"),
                    "all_errors": errors_list,  # Все ошибки для токена
                }
            )

        sentence_data.append(
            {
                "sentence": sentence,
                "tokens": tokens_data,
            }
        )

    student = text.idstudent
    user = student.iduser
    group = student.idgroup
    academic_year = group.idayear
    text_type = text.idtexttype
    write_place = text.idwriteplace
    write_tool = text.idwritetool
    emotion = text.idemotion
    year_study_language = text.educationlevel
    self_rating = text.selfrating
    assesment = text.selfassesment

    context = {
        "text": text,
        "sentence_data": sentence_data,
        "selected_markup": selected_markup,
        "author": f"{user.lastname} {user.firstname}",
        "group": group.groupname,
        "academic_year": academic_year.title,
        "create_date": text.createdate,
        "write_place": write_place.writeplacename if write_place else "Не указано",
        "write_tool": write_tool.writetoolname if write_tool else "Не указано",
        "text_type": text_type.texttypename if text_type else "Не указано",
        "emotion": emotion.emotionname if emotion else "Не указано",
        "year_study_language": year_study_language
        if text_type == None
        else "Не указано",
        "self_rating": self_rating,
        "self_assesment": assesment,
    }

    return render(request, "annotate_text.html", context)


def show_texts(request):
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

    years = AcademicYear.objects.all().values("idayear", "title").distinct()
    years_data = [
        {
            "id": year["idayear"],
            "name": year["title"],
        }
        for year in years
    ]

    text_types = TextType.objects.all().values("idtexttype", "texttypename").distinct()
    text_type_data = [
        {
            "id": text_type["idtexttype"],
            "name": text_type["texttypename"],
        }
        for text_type in text_types
    ]

    finded_text_by_name_data = []
    if request.method == "POST":
        # Получаем параметры из формы
        text_name = request.POST.get("text", "")
        year_id = request.POST.get("year", "")         # id учебного года
        group_id = request.POST.get("group", "")         # id группы
        text_type_id = request.POST.get("text_type", "") # id типа текста
        grouping = request.POST.get("grouping", "")

        # Начинаем с выборки всех текстов
        texts = Text.objects.all()

        if text_name:
            texts = texts.filter(header__icontains=text_name)
        if year_id:
            # идём по связям: текст -> студент -> группа -> академ. год
            texts = texts.filter(idstudent__idgroup__idayear=year_id)
        if group_id:
            # фильтруем по группе студента
            texts = texts.filter(idstudent__idgroup=group_id)
        if text_type_id:
            texts = texts.filter(idtexttype_id=text_type_id)

        texts = texts.values("idtext", "header")
        finded_text_by_name_data = [
            {"id": text["idtext"], "header_text": text["header"]} for text in texts
        ]

    context = {
        "groups": group_data,
        "years": years_data,
        "text_types": text_type_data,
        "finded_text_by_name": finded_text_by_name_data,
    }
    return render(request, "show_texts.html", context)


def teacher_load_text(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and "group_id" in request.GET:
        group_id = request.GET.get("group_id")
        students = Student.objects.filter(idgroup=group_id).select_related('iduser')
        students_data = [
            {
                'id': s.idstudent, 
                'name': f"{s.iduser.firstname} {s.iduser.lastname}"
            } 
            for s in students
        ]

        try:
            group = Group.objects.get(idgroup=group_id)
            course = group.studycourse  
        except Group.DoesNotExist:
            course = None

        return JsonResponse({'students': students_data, 'course': course})

    if request.method == "POST":
        form = TeacherLoadTextForm(request.POST)
        if form.is_valid():
            text_obj = form.save(commit=False)

            selected_student_id = request.POST.get("student")
            group_id = request.POST.get("group")

            if not selected_student_id:
                form.add_error('student', 'Не выбран студент')
                return render(request, 'teacher_load_text.html', {'form': form})

            text_obj.idstudent = get_object_or_404(Student, idstudent=selected_student_id)

            default_teacher, created = User.objects.get_or_create(login='teacher_default')
            text_obj.iduserteacher = default_teacher

            if group_id:
                try:
                    group = Group.objects.get(idgroup=group_id)
                    text_obj.educationlevel = group.studycourse
                except Group.DoesNotExist:
                    pass
            
            text_obj.save()

            print(f"Текст успешно сохранен для студента {text_obj.idstudent.idstudent}, "
                  f"с ID текста: {text_obj.idtext}. Текст: {text_obj.text[:100]}...")

            from nltk.tokenize import sent_tokenize, word_tokenize
            sentences = sent_tokenize(text_obj.text, language='german')
            
            print(f"Начинаем токенизацию текста. Количество предложений: {len(sentences)}")
            
            for order, sentence_text in enumerate(sentences, start=1):
                if sentence_text.strip():
                    sentence_obj = Sentence.objects.create(
                        sentensetext=sentence_text,
                        ordernumber=order,
                        idtext=text_obj
                    )
                    print(f"Добавлено предложение {order}: {sentence_text}")

                    tokens = word_tokenize(sentence_text, language='german')
                    print(f"Токенизируем предложение {order}, количество слов: {len(tokens)}")

                    for t_order, token_text in enumerate(tokens, start=1):
                        Token.objects.create(
                            tokentext=token_text,
                            tokenordernumber=t_order,
                            idsentence=sentence_obj
                        )
                        print(f"Добавлен токен {t_order}: {token_text}")

            print(f"Токенизация завершена для текста с ID {text_obj.idtext}. "
                  f"Всего предложений: {len(sentences)}, слов: {sum(len(word_tokenize(s, language='german')) for s in sentences)}.")

            return redirect('show_texts')
        else:
            print(f"Форма невалидна. Ошибки: {form.errors}")
    else:
        form = TeacherLoadTextForm()

    return render(request, 'teacher_load_text.html', {'form': form})
def home_view(request):
    return render(request, "home.html")
