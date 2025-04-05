from django.shortcuts import render, get_object_or_404
from core_app.models import Text, Token, PosTag, Error, ErrorToken, ErrorTag

def show_text_markup(request, text_id=None):
    # Получаем текст по заданному ID или первый текст, если ID не указан
    if text_id is not None:
        text = get_object_or_404(Text, idtext=text_id)
    else:
        text = Text.objects.first()

    # Получаем предложения текста
    sentences = text.sentence_set.all()
    sentence_data = []

    # Получаем значение разметки, выбранное пользователем
    selected_markup = request.GET.get("markup", "tagtext")

    # Формируем данные для разметки по предложениям
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
            error_tag = None
            error_tag_russian = None
            error_tag_abbrev = None
            error_color = None
            error_level = None
            error_correct = None
            error_comment = None
            error_token = token.errortoken_set.first()
            if error_token:
                error = error_token.iderror
                if error:
                    error_tag_obj = error.iderrortag
                    if error_tag_obj:
                        error_tag = error_tag_obj.tagtext
                        error_tag_russian = error_tag_obj.tagtextrussian
                        error_tag_abbrev = error_tag_obj.tagtextabbrev
                        error_color = error_tag_obj.tagcolor
                        error_level = (
                            error.iderrorlevel.errorlevelname
                            if error.iderrorlevel
                            else "Не указано"
                        )
                        error_correct = error.correct if error.correct else "Не указано"
                        error_comment = error.comment if error.comment else "Не указано"

            # Добавляем информацию
            tokens_data.append(
                {
                    "token": token.tokentext,
                    "pos_tag": pos_tag,
                    "pos_tag_russian": pos_tag_russian,
                    "pos_tag_abbrev": pos_tag_abbrev,
                    "pos_tag_color": pos_tag_color,
                    "error_tag": error_tag,
                    "error_tag_russian": error_tag_russian,
                    "error_tag_abbrev": error_tag_abbrev,
                    "error_color": error_color,
                    "error_level": error_level,
                    "error_correct": error_correct,
                    "error_comment": error_comment,
                }
            )

        sentence_data.append(
            {
                "sentence": sentence,
                "tokens": tokens_data,
            }
        )

    # Получаем дополнительную информацию о тексте
    student = text.idstudent
    user = student.iduser
    group = student.idgroup
    academic_year = group.idayear
    text_type = text.idtexttype
    write_place = text.idwriteplace
    write_tool = text.idwritetool
    emotion = text.idemotion
    year_study_language = text.educationlevel
    self_farting = text.selfrating
    assesment = text.selfassesment

    # Формируем данные для отображения
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
        "self_farting": self_farting,
        "self_assesment": assesment,
    }

    return render(request, "show_text_markup.html", context)


def home_view(request):
    return render(request, "home.html")
