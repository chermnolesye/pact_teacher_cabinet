from django.shortcuts import render, get_object_or_404
from core_app.models import Text, Token, PosTag, Error, ErrorToken, ErrorTag, Group


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


def annotate_text(request):
    return render(request, "annotate_text.html")


def show_texts(request):
    groups = Group.objects.select_related("idayear").all()

    group_data = [
        {"id": group.idgroup, "name": group.groupname, "year": group.idayear.title}
        for group in groups
    ]

    context = {"groups": group_data}

    return render(request, "show_texts.html", context)


def home_view(request):
    return render(request, "home.html")
