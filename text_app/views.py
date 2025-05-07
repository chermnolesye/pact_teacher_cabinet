from authorization_app.utils import has_teacher_rights
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import F
import json
from django.http import JsonResponse
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from .forms import TeacherLoadTextForm, AddTextAnnotationForm, AddErrorAnnotationForm
from nltk.tokenize import sent_tokenize, word_tokenize
from core_app.models import (
    Text,
    Token,
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
            token_order_number = token.tokenordernumber
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
                            "all_errors": errors_list,  # Все ошибки для токена
                            "error_reason": error.idreason.reasonname if error.idreason else "Не указано",
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
                    "token_order_number": token.tokenordernumber,
                    "error_reason": main_error.get("error_reason"),
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
        "fio": get_teacher_fio(request),
    }

    return render(request, "show_text_markup.html", context)


@user_passes_test(has_teacher_rights, login_url='/auth/login/')
def annotate_text(request, text_id=2379):
    text_id = request.GET.get("text_id")
    if text_id:
        text = get_object_or_404(Text, idtext=text_id)
    else:
        text = Text.objects.first()

    sentences = text.sentence_set.all()
    sentence_data = []
    selected_markup = request.GET.get("markup", "tagtext")

    for sentence in sentences:
        tokens = Token.objects.filter(idsentence=sentence).select_related("idpostag").order_by('tokenordernumber')


        tokens_data = []
        for token in tokens:
            pos_tag = token.idpostag.tagtext if token.idpostag else None
            pos_tag_russian = token.idpostag.tagtextrussian if token.idpostag else None
            pos_tag_abbrev = token.idpostag.tagtextabbrev if token.idpostag else None
            pos_tag_color = token.idpostag.tagcolor if token.idpostag else None

            error_tokens = token.errortoken_set.select_related(
                "iderror__iderrortag", "iderror__iderrorlevel", "iderror__idreason", "iderror"
            ).all()

            errors_list = []
            for et in error_tokens:
                error = et.iderror
                if error and error.iderrortag:
                    errors_list.append({
                        "error_tag_id": error.iderrortag,
                        "error_id": error.iderror,
                        "error_tag": error.iderrortag.tagtext,
                        "error_tag_russian": error.iderrortag.tagtextrussian,
                        "error_tag_abbrev": error.iderrortag.tagtextabbrev,
                        "error_color": error.iderrortag.tagcolor,
                        "error_level": error.iderrorlevel.errorlevelname if error.iderrorlevel else "Не указано",
                        "error_correct": error.correct or "Не указано",
                        "error_comment": error.comment or "Не указано",
                        "error_reason": error.idreason.reasonname if error.idreason else "Не указано",
                        "idtagparent": error.iderrortag.idtagparent,
                    })

            tokens_data.append({
                "token_id": token.idtoken,
                "token": token.tokentext,
                "pos_tag": pos_tag,
                "pos_tag_russian": pos_tag_russian,
                "pos_tag_abbrev": pos_tag_abbrev,
                "pos_tag_color": pos_tag_color,
                "token_order_number": token.tokenordernumber,
                "errors": errors_list,
            })

        sentence_data.append({
            "id_sentence": sentence.idsentence,
            "sentence": sentence,
            "tokens": tokens_data,
        })

    if request.method == "POST" and "grade-form" in request.POST:
        grade_form = AddTextAnnotationForm(request.POST, instance=text)
        if grade_form.is_valid():
            grade_form.save()
            return redirect(request.path + f"?text_id={text.idtext}&markup={selected_markup}")
    else:
        grade_form = AddTextAnnotationForm(instance=text)

    
    if request.method == "POST" and request.POST.get('action') == 'edit':
            print("Мы в функции edit")
            print(request.POST)

            error_id = request.POST.get('error_id')
            if not error_id:
                return JsonResponse({'success': False, 'error': 'Не передан ID аннотации для редактирования'})

            try:
                error = Error.objects.get(iderror=error_id)
            except Error.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Аннотация не найдена'})

            error.iderrortag_id = request.POST.get('id_iderrortag') or error.iderrortag_id
            error.idreason_id= request.POST.get('idreason') or error.idreason_id
            error.iderrorlevel_id = request.POST.get('iderrorlevel') or error.iderrorlevel_id
            error.comment = request.POST.get('comment', '')
            error.correct = request.POST.get('correct', '')
            error.save()

            return JsonResponse({'success': True})
    
    if request.method == 'POST' and request.POST.get('action') == 'delete':
        print("Мы в функции delete")
        error_id = request.POST.get('error_id')
        
        if not error_id:
            return JsonResponse({'success': False, 'error': 'ID ошибки не передан'})

        try:
            error = Error.objects.get(iderror=error_id)
        except Error.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Ошибка не найдена'})

        token_ids = list(ErrorToken.objects.filter(iderror=error).values_list('idtoken', flat=True))
        tokens_to_check = Token.objects.filter(idtoken__in=token_ids, tokentext='-EMPTY-')

        ErrorToken.objects.filter(iderror=error).delete()
        error.delete()

        for token in tokens_to_check:
            if not ErrorToken.objects.filter(idtoken=token).exists():
                sentence_id = token.idsentence
                order_number = token.tokenordernumber

                token.delete()

                Token.objects.filter(
                    idsentence=sentence_id,
                    tokenordernumber__gt=order_number
                ).update(tokenordernumber=F('tokenordernumber') - 1)

        return JsonResponse({'success': True})
                
    if request.method == "POST" and "annotation-form" in request.POST:
        print("Мы в функции добавления")
        annotation_form = AddErrorAnnotationForm(request.POST, user=request.user)

        if annotation_form.is_valid():
            try:
                chosen_ids = json.loads(request.POST.get('chosen_ids', '[]'))
                sentences_data = json.loads(request.POST.get('sentences', '[]'))

                print("Chosen IDs:", chosen_ids)
                print("Sentences data:", sentences_data)
                print("Form data:", request.POST)

                with transaction.atomic():
                    new_error = annotation_form.save(commit=False)
                    new_error.correct = annotation_form.cleaned_data.get('correct', '')
                    new_error.changedate = timezone.now()
                    new_error.save()

                    #Если есть новые пустые токены — создаём их
                    for sentence_info in sentences_data:
                        sentence_id = sentence_info['id_sentence']
                        empty_token_positions = sentence_info['empty_token_pos']

                        try:
                            sentence = Sentence.objects.get(idsentence=sentence_id)
                            for position in sorted([int(p) for p in empty_token_positions]):
                                print("Сдвигаем токены начиная с позиции:", position)
                                Token.objects.filter(
                                    idsentence=sentence,
                                    tokenordernumber__gte=position
                                ).update(tokenordernumber=F('tokenordernumber') + 1)
                                # Создаём новый токен
                                new_token = Token.objects.create(
                                    idsentence=sentence,
                                    tokentext='-EMPTY-',  
                                    tokenordernumber=position
                                )
                                print("Создан токен с порядковым номером:", new_token.tokenordernumber)

                                # Добавляем его id в список выделенных 
                                chosen_ids.append(str(new_token.idtoken))
                        except Sentence.DoesNotExist:
                            continue

                    #Привязываем ошибку ко всем выделенным 
                    for token_id in chosen_ids:
                        try:
                            token = Token.objects.get(idtoken=token_id)
                            ErrorToken.objects.create(idtoken=token, iderror=new_error)
                        except Token.DoesNotExist:
                            continue

                print("Annotation successfully saved.")
                return redirect(request.path + f"?text_id={text.idtext}&markup={selected_markup}")

            except Exception as e:
                print(f"Error saving annotation: {str(e)}")
        else:
            print("Form errors:", annotation_form.errors)
    else:
        annotation_form = AddErrorAnnotationForm()
        
    # Контекст
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
        "grade_form": grade_form,
        "annotation_form": annotation_form,
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
        "year_study_language": year_study_language if text_type == None else "Не указано",
        "self_rating": text.get_selfrating_display() if text.selfrating else "Нет данных",
        "self_assesment": text.get_selfassesment_display() if text.selfassesment else "Нет данных",
        "fio": get_teacher_fio(request),
        "textgrade": text.get_textgrade_display() if text.textgrade else "Нет данных",
        "completeness": text.get_completeness_display() if text.completeness else "Нет данных",
        "structure": text.get_structure_display() if text.structure else "Нет данных",
        "coherence": text.get_coherence_display() if text.coherence else "Нет данных",
        "poscheckflag": text.poscheckflag,
        "errorcheckflag": text.errorcheckflag,
        "usererrorcheck": text.idusererrorcheck.get_full_name() if text.idusererrorcheck else "Не указано", 
        "userteacher": text.iduserteacher.get_full_name() if text.iduserteacher else "Не указано", 
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

    # Алена, не удаляй это,пожалуйста, это надо для сохранения введенного поиска
    text_name = ""
    year_id = ""
    group_id = ""
    text_type_id = ""
    grouping = ""

    finded_text_by_name_data = []
    grouped_texts = {}
    if request.method == "POST":
        # Получаем параметры из формы
        text_name = request.POST.get("text", "")
        year_id = request.POST.get("year", "")  # id учебного года
        group_id = request.POST.get("group", "")  # id группы
        text_type_id = request.POST.get("text_type", "")  # id типа текста
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

        texts = texts.values(
            "idtext",
            "header",
            "idstudent__iduser__lastname",
            "idstudent__iduser__firstname",
            "idstudent__iduser__middlename",
            "idtexttype__texttypename",
            "modifieddate",
        )

        finded_text_by_name_data = [
            {"id": text["idtext"], "header_text": text["header"]} for text in texts
        ]

        if grouping == "fio":
            finded_text_by_name_data = []
            for text in texts:
                fio_user = (
                    f"{text['idstudent__iduser__lastname']} "
                    f"{text['idstudent__iduser__firstname']} "
                    f"{text['idstudent__iduser__middlename'] or ''}"
                )
                if fio_user not in grouped_texts:
                    grouped_texts[fio_user] = []
                else:
                    grouped_texts[fio_user].append(
                        {"id": text["idtext"], "header_text": text["header"]}
                    )

        elif grouping == "category":
            finded_text_by_name_data = []
            for text in texts:
                category = (
                    text["idtexttype__texttypename"]
                    if text["idtexttype__texttypename"]
                    else "Не указано"
                )
                if category not in grouped_texts:
                    grouped_texts[category] = []
                else:
                    grouped_texts[category].append(
                        {"id": text["idtext"], "header_text": text["header"]}
                    )

    texts = Text.objects.all()
    texts = texts.values(
        "idtext",
        "header",
        "idstudent__iduser__lastname",
        "idstudent__iduser__firstname",
        "idstudent__iduser__middlename",
        "idtexttype__texttypename",
        "modifieddate",
    )
    texts_by_types_for_folders = {}
    for text in texts:
        text_type = text["idtexttype__texttypename"]
        if text_type not in texts_by_types_for_folders:
            texts_by_types_for_folders[text_type] = []
        else:
            texts_by_types_for_folders[text_type].append(
                {
                    "id": text["idtext"],
                    "header_text": text["header"],
                    "author_lastname": text["idstudent__iduser__lastname"],
                    "author_firstname": text["idstudent__iduser__firstname"],
                    "author_middlename": text["idstudent__iduser__middlename"],
                    "date_modificate": text["modifieddate"],
                }
            )

    context = {
        "groups": group_data,
        "years": years_data,
        "text_types": text_type_data,
        "finded_text_by_name": finded_text_by_name_data,
        "grouped_texts": grouped_texts,
        "texts_type_folders": texts_by_types_for_folders,
        "selected_text": text_name,  # Алена, не удаляй это,пожалуйста, это надо для сохранения введенного поиска
        "selected_year": year_id,
        "selected_group": group_id,
        "selected_text_type": text_type_id,
        "selected_grouping": grouping,
        "fio": get_teacher_fio(request),
    }
    return render(request, "show_texts.html", context)


@user_passes_test(has_teacher_rights, login_url='/auth/login/')
def teacher_load_text(request):
    if (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        and "group_id" in request.GET
    ):
        group_id = request.GET.get("group_id")
        students = Student.objects.filter(idgroup=group_id).select_related("iduser")
        students_data = [
            {"id": s.idstudent, "name": f"{s.iduser.firstname} {s.iduser.lastname}"}
            for s in students
        ]

        try:
            group = Group.objects.get(idgroup=group_id)
            course = group.studycourse
        except Group.DoesNotExist:
            course = None

        return JsonResponse({"students": students_data, "course": course})

    if request.method == "POST":
        form = TeacherLoadTextForm(request.POST)
        if form.is_valid():
            text_obj = form.save(commit=False)

            selected_student_id = request.POST.get("student")
            group_id = request.POST.get("group")

            if not selected_student_id:
                form.add_error("student", "Не выбран студент")
                return render(request, "teacher_load_text.html", {"form": form})

            text_obj.idstudent = get_object_or_404(
                Student, idstudent=selected_student_id
            )

            default_teacher, _ = User.objects.get_or_create(login="teacher_default")
            text_obj.iduserteacher = default_teacher

            if group_id:
                try:
                    group = Group.objects.get(idgroup=group_id)
                    text_obj.educationlevel = group.studycourse
                except Group.DoesNotExist:
                    pass

            text_obj.save()

            print(
                f"Текст успешно сохранен для студента {text_obj.idstudent.idstudent}, "
                f"с ID текста: {text_obj.idtext}. Текст: {text_obj.text[:100]}..."
            )

            sentences = sent_tokenize(text_obj.text, language="german")

            print(
                f"Начинаем токенизацию текста. Количество предложений: {len(sentences)}"
            )

            for order, sentence_text in enumerate(sentences, start=0):
                if sentence_text.strip():
                    sentence_obj = Sentence.objects.create(
                        sentensetext=sentence_text,
                        ordernumber=order,
                        idtext=text_obj,
                    )
                    print(f"Добавлено предложение {order}: {sentence_text}")

                    tokens = word_tokenize(sentence_text, language="german")
                    print(
                        f"Токенизируем предложение {order}, количество слов: {len(tokens)}"
                    )

                    for t_order, token_text in enumerate(tokens, start=0):
                        Token.objects.create(
                            tokentext=token_text,
                            tokenordernumber=t_order,
                            idsentence=sentence_obj,
                        )
                        print(f"Добавлен токен {t_order}: {token_text}")

            print(
                f"Токенизация завершена для текста с ID {text_obj.idtext}. "
                f"Всего предложений: {len(sentences)}, слов: {sum(len(word_tokenize(s, language='german')) for s in sentences)}."
            )

            return redirect("search_texts")
        else:
            print(f"Форма невалидна. Ошибки: {form.errors}")
    else:
        initial_data = {}
        student_id = request.GET.get("student_id")
        if student_id:
            initial_data["student"] = student_id
        form = TeacherLoadTextForm(initial=initial_data)

    return render(
        request,
        "teacher_load_text.html",
        {"form": form, "fio": get_teacher_fio(request)},
    )


@user_passes_test(has_teacher_rights, login_url='/auth/login/')
def home_view(request):
    return render(request, "home.html")


def get_teacher_fio(request):
    return request.session.get("teacher_fio", "")


def get_tags(request):
    # Получаем все теги из базы данных
    tags = ErrorTag.objects.all().values(
        'iderrortag', 
        'tagtext', 
        'tagtextrussian', 
        'tagcolor',
        'idtagparent'
    )
    
    tags_info = []
    if tags.exists():
        for element in tags:
            parent_id = element['idtagparent'] if element['idtagparent'] else 0
            
            # Проверяем, есть ли у тега дочерние элементы
            has_children = tags.filter(idtagparent=element['iderrortag']).exists()
            
            tags_info.append({
                'has_children': has_children,
                'tag_id': element['iderrortag'],
                'tag_text': element['tagtext'],
                'tag_text_russian': element['tagtextrussian'],
                'parent_id': parent_id,
                'tag_color': element['tagcolor']
            })
    
    sorted_tags = sorted(list(tags_info), key=lambda d: d['parent_id'])

    context = {
        'tags_info': sorted_tags,  # преобразуем QuerySet в список
    }
    
    return JsonResponse(context)


@user_passes_test(has_teacher_rights, login_url='/auth/login/')
def search_texts(request):
    text_type_id = request.GET.get('text_type', '')
    
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

    # Если выбран конкретный тип текста
    if text_type_id:
        texts = Text.objects.filter(idtexttype_id=text_type_id)
        texts = texts.values(
            "idtext",
            "header",
            "idstudent__iduser__lastname",
            "idstudent__iduser__firstname",
            "idstudent__iduser__middlename",
            "idtexttype__texttypename",
            "modifieddate",
        )
        
        texts_of_type = [
            {
                "id": text["idtext"],
                "header_text": text["header"],
                "author_lastname": text["idstudent__iduser__lastname"],
                "author_firstname": text["idstudent__iduser__firstname"],
                "author_middlename": text["idstudent__iduser__middlename"],
                "date_modificate": text["modifieddate"],
                "text_type": text["idtexttype__texttypename"],
            }
            for text in texts
        ]
        
        context = {
            "texts_of_type": texts_of_type,
            "selected_text_type": text_type_id,
            "text_types": text_type_data,
            "fio": get_teacher_fio(request),
        }
        return render(request, "search_texts.html", context)

    # Если выполняется поиск (POST-запрос)
    text_name = ""
    year_id = ""
    group_id = ""
    text_type_id = ""
    grouping = ""

    finded_text_by_name_data = []
    grouped_texts = {}
    if request.method == "POST":
        # Получаем параметры из формы
        text_name = request.POST.get("text", "")
        year_id = request.POST.get("year", "")
        group_id = request.POST.get("group", "")
        text_type_id = request.POST.get("text_type", "")
        grouping = request.POST.get("grouping", "")

        # Начинаем с выборки всех текстов
        texts = Text.objects.exclude(idtexttype__isnull=True)


        if text_name:
            texts = texts.filter(header__icontains=text_name)
        if year_id:
            texts = texts.filter(idstudent__idgroup__idayear=year_id)
        if group_id:
            texts = texts.filter(idstudent__idgroup=group_id)
        if text_type_id:
            texts = texts.filter(idtexttype_id=text_type_id)

        texts = texts.values(
            "idtext",
            "header",
            "idstudent__iduser__lastname",
            "idstudent__iduser__firstname",
            "idstudent__iduser__middlename",
            "idtexttype__texttypename",
            "modifieddate",
        )

        # Обновляем структуру данных для результатов поиска
        finded_text_by_name_data = [
            {
                "id": text["idtext"],
                "header_text": text["header"],
                "author_lastname": text["idstudent__iduser__lastname"],
                "author_firstname": text["idstudent__iduser__firstname"],
                "author_middlename": text["idstudent__iduser__middlename"],
                "date_modificate": text["modifieddate"],
            }
            for text in texts
        ]

        if grouping == "fio":
            finded_text_by_name_data = []
            grouped_texts = {}
            for text in texts:
                fio_user = (
                    f"{text['idstudent__iduser__lastname']} "
                    f"{text['idstudent__iduser__firstname']} "
                    f"{text['idstudent__iduser__middlename'] or ''}"
                )
                if fio_user not in grouped_texts:
                    grouped_texts[fio_user] = []
                grouped_texts[fio_user].append({
                    "id": text["idtext"],
                    "header_text": text["header"],
                    "author_lastname": text["idstudent__iduser__lastname"],
                    "author_firstname": text["idstudent__iduser__firstname"],
                    "date_modificate": text["modifieddate"],
                })

        elif grouping == "category":
            finded_text_by_name_data = []
            grouped_texts = {}
            for text in texts:
                category = (
                    text["idtexttype__texttypename"]
                    if text["idtexttype__texttypename"]
                    else "Не указано"
                )
                if category not in grouped_texts:
                    grouped_texts[category] = []
                grouped_texts[category].append({
                    "id": text["idtext"],
                    "header_text": text["header"],
                    "author_lastname": text["idstudent__iduser__lastname"],
                    "author_firstname": text["idstudent__iduser__firstname"],
                    "date_modificate": text["modifieddate"],
                })

    # Получаем тексты сгруппированные по типам для главной страницы
    texts = Text.objects.exclude(idtexttype__isnull=True)
    texts = texts.values(
        "idtext",
        "header",
        "idstudent__iduser__lastname",
        "idstudent__iduser__firstname",
        "idstudent__iduser__middlename",
        "idtexttype__texttypename",
        "modifieddate",
    )
    texts_by_types_for_folders = {}
    for text in texts:
        text_type = text["idtexttype__texttypename"]
        if text_type not in texts_by_types_for_folders:
            texts_by_types_for_folders[text_type] = []
        texts_by_types_for_folders[text_type].append(
            {
                "id": text["idtext"],
                "header_text": text["header"],
                "author_lastname": text["idstudent__iduser__lastname"],
                "author_firstname": text["idstudent__iduser__firstname"],
                "author_middlename": text["idstudent__iduser__middlename"],
                "date_modificate": text["modifieddate"],
            }
        )

    context = {
        "groups": group_data,
        "years": years_data,
        "text_types": text_type_data,
        "finded_text_by_name": finded_text_by_name_data,
        "grouped_texts": grouped_texts,
        "texts_type_folders": texts_by_types_for_folders,
        "selected_text": text_name,  
        "selected_year": year_id,
        "selected_group": group_id,
        "selected_text_type": text_type_id,
        "selected_grouping": grouping,
        "fio": get_teacher_fio(request),
    }
    return render(request, "search_texts.html", context)